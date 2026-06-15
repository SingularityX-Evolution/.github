"""Noisy-OR / multi-path aggregation model.

Models the chain as: even if one hop "fails", other causal paths may still
lead to the same conclusion. This avoids the naive product's over-penalization.

P(effect) = 1 - prod(1 - qi)
where qi = pi * (1 - P_interrupt_i) is the probability that hop i
successfully propagates the causal signal.
"""

import numpy as np
from ..chain import CausalChain, AggregationResult


class NoisyOrAggregator:

    def __init__(self, independence_threshold: float = 0.3):
        self.independence_threshold = independence_threshold

    def _effective_prob(self, hop_confidence: float, interrupt_prob: float) -> float:
        """Probability that this hop successfully propagates the signal."""
        return hop_confidence * (1 - interrupt_prob)

    def aggregate(
        self,
        chain: CausalChain,
        interrupt_probs: list[float] | None = None,
        **_kwargs,
    ) -> AggregationResult:
        n = len(chain.confidences)
        if interrupt_probs is None:
            interrupt_probs = [0.0] * n

        # Compute effective per-hop propagation probabilities
        q_values = np.array(
            [self._effective_prob(p, r) for p, r in zip(chain.confidences, interrupt_probs)]
        )

        # Noisy-OR: P = 1 - prod(1 - qi)
        # Handles the case where multiple causal paths reinforce each other
        complement = np.prod(1 - q_values)
        final = float(1 - complement)

        # Per-hop marginal contribution
        per_hop = []
        running_complement = 1.0
        for q in q_values:
            prev = 1 - running_complement
            running_complement *= (1 - q)
            new = 1 - running_complement
            per_hop.append(float(new - prev))

        # Intermediates
        intermediates = []
        running_complement = 1.0
        for q in q_values:
            running_complement *= (1 - q)
            intermediates.append(float(1 - running_complement))

        # CI on log(1-P) scale, then transform back
        # Var[log(1-P)] = sum Var[log(1-qi)]
        log_complement = np.log(max(complement, 1e-10))
        var_log = n * 0.05
        std_log = np.sqrt(var_log)
        # Upper CI of log(1-P) -> larger complement -> LOWER confidence
        log_comp_upper = log_complement + 1.645 * std_log
        # Lower CI of log(1-P) -> smaller complement -> HIGHER confidence
        log_comp_lower = log_complement - 1.645 * std_log
        ci_lower = 1.0 - min(np.exp(log_comp_upper), 1.0)
        ci_upper = 1.0 - max(np.exp(log_comp_lower), 0.0)

        return AggregationResult(
            chain_id=chain.chain_id,
            method="noisy_or",
            final_confidence=final,
            confidence_interval=(max(0.0, ci_lower), min(1.0, ci_upper)),
            per_hop_contributions=per_hop,
            intermediate_confidences=intermediates,
            metadata={
                "n_hops": n,
                "q_values": q_values.tolist(),
                "independence_threshold": self.independence_threshold,
            },
        )
