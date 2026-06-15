"""Naive product baseline aggregator.

This is the baseline: final confidence = product of all per-hop confidences.
It assumes independence and no external interrupts, which makes it overly conservative
for long chains.
"""

import numpy as np
from ..chain import CausalChain, AggregationResult


class NaiveProductAggregator:

    def aggregate(self, chain: CausalChain, **_kwargs) -> AggregationResult:
        confidences = chain.confidences
        n = len(confidences)

        # Simple product
        final = float(np.prod(confidences))

        # Per-hop incremental contribution (how much this hop changed the aggregate)
        per_hop = []
        running = 1.0
        for p in confidences:
            prev = running
            running *= p
            per_hop.append(running - prev)

        # CI using log-normal approximation on log(confidence)
        # Var[log(c)] = sum Var[log(pi)] assuming independence
        # Use 0.05 as proxy for Var[log(pi)] per hop (conservative)
        log_variance = n * 0.05
        log_std = np.sqrt(log_variance)
        log_final = np.log(max(final, 1e-10))
        lower = np.exp(log_final - 1.645 * log_std)
        upper = np.exp(log_final + 1.645 * log_std)

        return AggregationResult(
            chain_id=chain.chain_id,
            method="naive_product",
            final_confidence=final,
            confidence_interval=(max(0.0, lower), min(1.0, upper)),
            per_hop_contributions=per_hop,
            intermediate_confidences=[float(np.prod(confidences[: i + 1])) for i in range(n)],
            metadata={"n_hops": n, "log_variance": log_variance},
        )
