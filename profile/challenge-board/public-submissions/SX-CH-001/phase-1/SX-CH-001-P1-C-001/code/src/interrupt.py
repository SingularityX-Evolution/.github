"""External interrupt probability estimator.

Estimates P(external interrupt | hop metadata) for each hop in a causal chain.
External interrupts are events outside the chain that can break or override the
causal link (e.g., OPEC increasing production to offset a supply shock).
"""

import numpy as np
from .chain import CausalChain


class InterruptModel:
    """Estimates interrupt probability per hop based on hop type and time span."""

    def __init__(
        self,
        type_priors: dict[str, float] | None = None,
        time_factor_per_day: float = 0.003,
        time_factor_cap: float = 1.0,
    ):
        self.type_priors = type_priors or {
            "geopolitical": 0.12,
            "macroeconomic": 0.08,
            "sector": 0.05,
            "company": 0.03,
            "technical": 0.02,
            "sentiment": 0.06,
            "unknown": 0.08,
        }
        self.time_factor_per_day = time_factor_per_day
        self.time_factor_cap = time_factor_cap

    def estimate(self, chain: CausalChain) -> np.ndarray:
        """Estimate interrupt probability for each hop."""
        probs = []
        for hop in chain.hops:
            base = self.type_priors.get(hop.hop_type, self.type_priors["unknown"])
            time_factor = min(hop.time_span_days * self.time_factor_per_day, self.time_factor_cap)
            probs.append(base * (1 + time_factor))
        return np.clip(np.array(probs), 0.0, 1.0)

    def estimate_single(self, hop_type: str, time_span_days: float) -> float:
        base = self.type_priors.get(hop_type, self.type_priors["unknown"])
        time_factor = min(time_span_days * self.time_factor_per_day, self.time_factor_cap)
        return float(np.clip(base * (1 + time_factor), 0.0, 1.0))
