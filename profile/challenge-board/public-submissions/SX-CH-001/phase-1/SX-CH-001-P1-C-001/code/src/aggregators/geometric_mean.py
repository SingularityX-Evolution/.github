"""Geometric mean aggregator.

c = exp(mean(log(p_i)))

This sits naturally between naive product (too conservative) and
logit aggregation (can be too permissive). The geometric mean
preserves per-hop contributions while avoiding exponential decay.
For n hops with average confidence 0.72: geo_mean = 0.72 (stable),
vs naive_product = 0.72^n → 0 (decaying rapidly).
"""

import numpy as np
from ..chain import CausalChain, AggregationResult


class GeometricMeanAggregator:

    def aggregate(self, chain: CausalChain, **_kwargs) -> AggregationResult:
        confidences = chain.confidences
        n = len(confidences)
        clamped = np.clip(confidences, 1e-8, 1 - 1e-8)

        # Geometric mean: exp(mean(log(p)))
        log_mean = np.mean(np.log(clamped))
        final = float(np.exp(log_mean))

        # Per-hop contribution: how each hop shifts the geometric mean
        per_hop = []
        running_log_sum = 0.0
        for i, p in enumerate(clamped):
            prev_mean = np.exp(running_log_sum / max(i, 1)) if i > 0 else 0.5
            running_log_sum += np.log(p)
            new_mean = np.exp(running_log_sum / (i + 1))
            per_hop.append(float(new_mean - prev_mean))

        # Intermediates
        intermediates = []
        running_log_sum = 0.0
        for i, p in enumerate(clamped):
            running_log_sum += np.log(p)
            intermediates.append(float(np.exp(running_log_sum / (i + 1))))

        # CI: standard error of log-mean
        log_values = np.log(clamped)
        log_std = np.std(log_values, ddof=1) / np.sqrt(n) if n > 1 else 0.1
        lower = float(np.exp(log_mean - 1.645 * log_std))
        upper = float(np.exp(log_mean + 1.645 * log_std))

        return AggregationResult(
            chain_id=chain.chain_id,
            method="geometric_mean",
            final_confidence=final,
            confidence_interval=(max(0.0, lower), min(1.0, upper)),
            per_hop_contributions=per_hop,
            intermediate_confidences=intermediates,
            metadata={"n_hops": n, "log_mean": float(log_mean), "log_std": float(log_std)},
        )
