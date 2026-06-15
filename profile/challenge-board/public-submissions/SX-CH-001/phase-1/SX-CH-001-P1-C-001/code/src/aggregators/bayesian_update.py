"""Bayesian sequential update aggregator.

Models confidence as P(C | e1, e2, ..., en) using sequential Bayesian updating.
Each hop provides evidence ei with some likelihood ratio, and the prior gets
updated step by step. External interrupts are modelled as reducing the effective
likelihood of each hop.

Key insight: this naturally handles non-independence because the prior at each
step already incorporates all previous evidence.
"""

import numpy as np
from ..chain import CausalChain, AggregationResult


class BayesianUpdateAggregator:

    def __init__(self, prior_belief: float = 0.5, likelihood_strength: float = 1.0):
        self.prior_belief = prior_belief
        self.likelihood_strength = likelihood_strength

    def _hop_likelihood_ratio(self, hop_confidence: float, interrupt_prob: float) -> float:
        """Convert hop confidence + interrupt prob to a likelihood ratio.

        A hop with confidence p and interrupt probability r means:
        - P(evidence | C) = p * (1 - r)  (chain holds AND not interrupted)
        - P(evidence | not C) = (1 - p) * (1 - r) + r  (false positive or interrupt)

        LR = P(e|C) / P(e|not C)
        """
        p = hop_confidence
        r = interrupt_prob
        p_e_given_c = p * (1 - r)
        p_e_given_not_c = (1 - p) * (1 - r) + r
        # Avoid division by zero
        p_e_given_not_c = max(p_e_given_not_c, 1e-10)
        lr = p_e_given_c / p_e_given_not_c
        # Dampen extreme likelihood ratios
        lr = lr ** self.likelihood_strength
        return lr

    def _update_belief(self, prior: float, lr: float) -> float:
        """Bayesian update: posterior odds = prior odds * LR."""
        prior_odds = prior / max(1 - prior, 1e-10)
        posterior_odds = prior_odds * lr
        return posterior_odds / (1 + posterior_odds)

    def aggregate(
        self,
        chain: CausalChain,
        interrupt_probs: list[float] | None = None,
        **_kwargs,
    ) -> AggregationResult:
        n = len(chain.confidences)
        if interrupt_probs is None:
            interrupt_probs = [0.0] * n

        belief = self.prior_belief
        intermediates = []
        per_hop = []

        for i, (p, r) in enumerate(zip(chain.confidences, interrupt_probs)):
            prev_belief = belief
            lr = self._hop_likelihood_ratio(p, r)
            belief = self._update_belief(belief, lr)
            intermediates.append(belief)
            per_hop.append(belief - prev_belief)

        # CI via Beta approximation: alpha, beta from belief and effective sample size
        effective_n = n * 2
        alpha = belief * effective_n + 1
        beta_param = (1 - belief) * effective_n + 1
        # Beta quantiles
        from scipy.stats import beta as beta_dist

        lower = beta_dist.ppf(0.05, alpha, beta_param)
        upper = beta_dist.ppf(0.95, alpha, beta_param)

        return AggregationResult(
            chain_id=chain.chain_id,
            method="bayesian_update",
            final_confidence=belief,
            confidence_interval=(float(lower), float(upper)),
            per_hop_contributions=per_hop,
            intermediate_confidences=intermediates,
            metadata={
                "n_hops": n,
                "prior_belief": self.prior_belief,
                "effective_sample_size": effective_n,
                "alpha": alpha,
                "beta": beta_param,
            },
        )
