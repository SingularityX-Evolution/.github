"""Tests for stopping criteria."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.stopping import StoppingCriteria


class TestStoppingCriteria:

    def test_max_hops_stops(self):
        sc = StoppingCriteria(max_hops=3)
        decision = sc.evaluate(hop_index=3, current_confidence=0.8, ci_width=0.1)
        assert decision.should_stop
        assert decision.reason == "max_hops_reached"

    def test_confidence_floor_stops(self):
        sc = StoppingCriteria(confidence_floor=0.15)
        decision = sc.evaluate(hop_index=2, current_confidence=0.10, ci_width=0.1)
        assert decision.should_stop
        assert decision.reason == "confidence_below_floor"

    def test_ci_width_stops(self):
        sc = StoppingCriteria(ci_width_threshold=0.30)
        decision = sc.evaluate(hop_index=1, current_confidence=0.5, ci_width=0.50)
        assert decision.should_stop
        assert decision.reason == "uncertainty_too_high"

    def test_low_ig_stops(self):
        sc = StoppingCriteria(min_information_gain=0.05)
        # A next hop with confidence 0.5 gives very little IG when current is 0.5
        decision = sc.evaluate(hop_index=1, current_confidence=0.5, ci_width=0.1, next_hop_confidence=0.5001)
        assert decision.should_stop
        assert decision.reason == "insufficient_information_gain"

    def test_no_stop_when_all_ok(self):
        sc = StoppingCriteria(
            confidence_floor=0.05,
            ci_width_threshold=0.50,
            min_information_gain=0.001,
            max_hops=10,
        )
        decision = sc.evaluate(hop_index=2, current_confidence=0.7, ci_width=0.1, next_hop_confidence=0.8)
        assert not decision.should_stop

    def test_stop_reasons_are_descriptive(self):
        sc = StoppingCriteria(max_hops=1)
        decision = sc.evaluate(hop_index=1, current_confidence=0.5, ci_width=0.1)
        assert decision.reason is not None
        assert len(decision.reason) > 0
