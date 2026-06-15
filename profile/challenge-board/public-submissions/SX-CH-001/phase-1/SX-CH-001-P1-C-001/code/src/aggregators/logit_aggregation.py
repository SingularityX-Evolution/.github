"""Logit-space weighted aggregation.

Operates in log-odds space, allowing:
- Per-hop weighting (recent hops can have different weights)
- Correlation penalty between adjacent hops
- Prior anchoring to prevent over-decay

logit(c_final) = prior_weight * logit(prior) + sum(wi * logit(pi))
where wi incorporates correlation penalties.
"""

import numpy as np
from scipy.special import logit, expit
from ..chain import CausalChain, AggregationResult


class LogitAggregator:

    def __init__(self, prior_weight: float = 1.0, correlation_penalty: float = 0.1):
        self.prior_weight = prior_weight
        self.correlation_penalty = correlation_penalty

    def _hop_weights(self, n: int) -> np.ndarray:
        """Compute per-hop weights with correlation penalty.

        Adjacent hops in a causal chain tend to be correlated. We apply a
        mild decay so that each additional hop contributes slightly less
        weight, reducing the over-penalization of long chains.
        """
        base_weights = np.ones(n)
        for i in range(1, n):
            # Each subsequent hop's weight is reduced by the penalty
            # to account for shared information with prior hops
            base_weights[i] = base_weights[i - 1] * (1 - self.correlation_penalty)
        # Normalize so total weight = n (preserving scale)
        base_weights = base_weights / base_weights.sum() * n
        return base_weights

    def aggregate(self, chain: CausalChain, prior: float = 0.5, **_kwargs) -> AggregationResult:
        confidences = chain.confidences
        n = len(confidences)

        # Clamp confidences away from 0 and 1 for logit stability
        eps = 1e-8
        clamped = np.clip(confidences, eps, 1 - eps)

        # Convert to logit space
        logits = logit(clamped)
        prior_logit = logit(max(prior, eps))

        # Weighted sum with prior anchor
        weights = self._hop_weights(n)
        weighted_sum = np.sum(weights * logits)
        total_weight = self.prior_weight + np.sum(weights)
        aggregate_logit = (self.prior_weight * prior_logit + weighted_sum) / total_weight

        final = float(expit(aggregate_logit))

        # Per-hop contributions (incremental change in aggregate)
        per_hop = []
        running_logit = self.prior_weight * prior_logit
        running_total = self.prior_weight
        for i, (w, lt) in enumerate(zip(weights, logits)):
            prev_logit = running_logit / running_total
            running_logit += w * lt
            running_total += w
            new_logit = running_logit / running_total
            per_hop.append(float(expit(new_logit) - expit(prev_logit)))

        # Intermediate confidences
        intermediates = []
        running_logit = self.prior_weight * prior_logit
        running_total = self.prior_weight
        for i, (w, lt) in enumerate(zip(weights, logits)):
            running_logit += w * lt
            running_total += w
            intermediates.append(float(expit(running_logit / running_total)))

        # CI via delta method on logit scale
        # Approximate variance from per-hop variance
        logit_variance = np.sum((weights / total_weight) ** 2) * 0.1
        logit_std = np.sqrt(logit_variance)
        lower = float(expit(aggregate_logit - 1.645 * logit_std))
        upper = float(expit(aggregate_logit + 1.645 * logit_std))

        return AggregationResult(
            chain_id=chain.chain_id,
            method="logit_aggregation",
            final_confidence=final,
            confidence_interval=(lower, upper),
            per_hop_contributions=per_hop,
            intermediate_confidences=intermediates,
            metadata={
                "n_hops": n,
                "prior_weight": self.prior_weight,
                "correlation_penalty": self.correlation_penalty,
                "hop_weights": weights.tolist(),
                "aggregate_logit": float(aggregate_logit),
            },
        )
