"""Principled stopping criteria for multi-hop causal chains.

Each criterion answers: should we stop extending this chain?
Stopping too early loses valuable inference; stopping too late adds noise.
"""

from dataclasses import dataclass
from typing import Optional
import numpy as np


@dataclass
class StopDecision:
    should_stop: bool
    reason: Optional[str] = None
    confidence_at_stop: float = 1.0
    ci_width: float = 0.0
    expected_ig: float = 0.0


class StoppingCriteria:
    """Composite stopping rule with multiple sub-criteria."""

    def __init__(
        self,
        confidence_floor: float = 0.10,
        ci_width_threshold: float = 0.40,
        min_information_gain: float = 0.01,
        max_hops: int = 8,
    ):
        self.confidence_floor = confidence_floor
        self.ci_width_threshold = ci_width_threshold
        self.min_information_gain = min_information_gain
        self.max_hops = max_hops

    def evaluate(
        self,
        hop_index: int,
        current_confidence: float,
        ci_width: float,
        next_hop_confidence: float | None = None,
    ) -> StopDecision:
        """Evaluate all stopping criteria. Returns True if ANY criterion is met."""

        # Criterion 1: max hop count (hard safety limit)
        if hop_index >= self.max_hops:
            return StopDecision(
                should_stop=True,
                reason="max_hops_reached",
                confidence_at_stop=current_confidence,
                ci_width=ci_width,
            )

        # Criterion 2: confidence floor
        if current_confidence < self.confidence_floor:
            return StopDecision(
                should_stop=True,
                reason="confidence_below_floor",
                confidence_at_stop=current_confidence,
                ci_width=ci_width,
            )

        # Criterion 3: uncertainty too wide
        if ci_width > self.ci_width_threshold:
            return StopDecision(
                should_stop=True,
                reason="uncertainty_too_high",
                confidence_at_stop=current_confidence,
                ci_width=ci_width,
            )

        # Criterion 4: expected information gain too low
        if next_hop_confidence is not None:
            expected_ig = self._estimate_information_gain(
                current_confidence, next_hop_confidence
            )
            if expected_ig < self.min_information_gain:
                return StopDecision(
                    should_stop=True,
                    reason="insufficient_information_gain",
                    confidence_at_stop=current_confidence,
                    ci_width=ci_width,
                    expected_ig=expected_ig,
                )

        return StopDecision(should_stop=False, confidence_at_stop=current_confidence, ci_width=ci_width)

    def _estimate_information_gain(
        self, current_confidence: float, next_hop_confidence: float
    ) -> float:
        """Estimate expected information gain from adding a hop.

        Uses Kullback-Leibler divergence between current belief and
        expected posterior after observing the next hop.
        """
        p = max(min(current_confidence, 0.999), 0.001)
        q = max(min(next_hop_confidence, 0.999), 0.001)

        # Expected posterior if hop confirms: belief moves toward q
        p_confirm = p * q / (p * q + (1 - p) * (1 - q))
        # Expected posterior if hop disconfirms:
        p_disconfirm = p * (1 - q) / (p * (1 - q) + (1 - p) * q)

        # KL divergence for confirm case
        kl_confirm = p_confirm * np.log(p_confirm / p) + (1 - p_confirm) * np.log(
            (1 - p_confirm) / (1 - p)
        )
        # Expected KL (weighted by probability of each outcome)
        prob_confirm = p * q + (1 - p) * (1 - q)
        expected_kl = prob_confirm * kl_confirm

        return float(np.clip(expected_kl, 0.0, 10.0))
