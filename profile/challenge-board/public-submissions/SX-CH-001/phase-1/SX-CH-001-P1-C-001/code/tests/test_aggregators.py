"""Tests for all four aggregation methods."""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.chain import CausalChain, Hop
from src.aggregators import (
    NaiveProductAggregator,
    LogitAggregator,
    BayesianUpdateAggregator,
    NoisyOrAggregator,
)


DEFAULT_HOP_TYPES = ["geopolitical", "macroeconomic", "sector", "company", "technical", "sentiment"]


def make_chain(n_hops: int = 3, confidences=None, hop_types=None) -> CausalChain:
    if confidences is None:
        confidences = [0.8, 0.7, 0.6]
    if hop_types is None:
        hop_types = (DEFAULT_HOP_TYPES * (n_hops // len(DEFAULT_HOP_TYPES) + 1))[:n_hops]
    hops = [
        Hop(hop_id=i, description=f"Hop {i}", confidence=c, hop_type=ht)
        for i, (c, ht) in enumerate(zip(confidences, hop_types))
    ]
    return CausalChain(
        chain_id="TEST-001",
        trigger_event="Test trigger",
        hops=hops,
    )


class TestNaiveProduct:

    def test_single_hop(self):
        chain = make_chain(1, [0.8])
        agg = NaiveProductAggregator()
        result = agg.aggregate(chain)
        assert abs(result.final_confidence - 0.8) < 1e-10

    def test_three_hops(self):
        chain = make_chain(3, [0.8, 0.7, 0.6])
        agg = NaiveProductAggregator()
        result = agg.aggregate(chain)
        assert abs(result.final_confidence - 0.8 * 0.7 * 0.6) < 1e-10

    def test_perfect_confidence(self):
        chain = make_chain(3, [1.0, 1.0, 1.0])
        agg = NaiveProductAggregator()
        result = agg.aggregate(chain)
        assert abs(result.final_confidence - 1.0) < 1e-10

    def test_long_chain_decay(self):
        """Naive product should heavily penalize long chains."""
        chain = make_chain(8, [0.75] * 8)
        agg = NaiveProductAggregator()
        result = agg.aggregate(chain)
        assert result.final_confidence < 0.2  # 0.75^8 ≈ 0.10

    def test_ci_bounds(self):
        chain = make_chain(3, [0.8, 0.7, 0.6])
        agg = NaiveProductAggregator()
        result = agg.aggregate(chain)
        lower, upper = result.confidence_interval
        assert 0 <= lower <= result.final_confidence <= upper <= 1.0


class TestLogitAggregator:

    def test_single_hop(self):
        chain = make_chain(1, [0.8])
        agg = LogitAggregator()
        result = agg.aggregate(chain)
        assert 0 < result.final_confidence < 1

    def test_less_decay_than_naive(self):
        """Logit aggregation should produce higher confidence than naive for 3+ hops."""
        chain = make_chain(6, [0.75] * 6)
        naive = NaiveProductAggregator().aggregate(chain)
        logit = LogitAggregator(prior_weight=0.5, correlation_penalty=0.1).aggregate(chain)
        assert logit.final_confidence > naive.final_confidence

    def test_correlation_penalty_effect(self):
        """Higher correlation penalty should reduce confidence (more conservative)."""
        chain = make_chain(5, [0.8] * 5)
        low_penalty = LogitAggregator(correlation_penalty=0.0).aggregate(chain)
        high_penalty = LogitAggregator(correlation_penalty=0.5).aggregate(chain)
        assert high_penalty.final_confidence < low_penalty.final_confidence


class TestBayesianUpdate:

    def test_single_hop(self):
        chain = make_chain(1, [0.8])
        agg = BayesianUpdateAggregator(prior_belief=0.5)
        result = agg.aggregate(chain, interrupt_probs=[0.0])
        assert result.final_confidence > 0.5  # Should update upward from prior

    def test_interrupt_reduces_confidence(self):
        chain = make_chain(3, [0.8, 0.8, 0.8])
        agg = BayesianUpdateAggregator(prior_belief=0.5)
        no_int = agg.aggregate(chain, interrupt_probs=[0.0, 0.0, 0.0])
        with_int = agg.aggregate(chain, interrupt_probs=[0.3, 0.3, 0.3])
        assert with_int.final_confidence < no_int.final_confidence

    def test_prior_convergence(self):
        """With strong evidence, posterior should converge away from prior."""
        chain = make_chain(5, [0.9] * 5)
        agg = BayesianUpdateAggregator(prior_belief=0.5)
        result = agg.aggregate(chain, interrupt_probs=[0.0] * 5)
        assert result.final_confidence > 0.8  # Strong evidence overwhelms prior


class TestNoisyOr:

    def test_single_hop(self):
        chain = make_chain(1, [0.8])
        agg = NoisyOrAggregator()
        result = agg.aggregate(chain, interrupt_probs=[0.0])
        assert abs(result.final_confidence - 0.8) < 1e-10

    def test_multi_path_reinforcement(self):
        """Multiple paths should reinforce each other (higher than naive product)."""
        chain = make_chain(3, [0.7, 0.7, 0.7])
        naive = NaiveProductAggregator().aggregate(chain)
        noisy = NoisyOrAggregator().aggregate(chain, interrupt_probs=[0.0] * 3)
        assert noisy.final_confidence > naive.final_confidence

    def test_interrupt_effect(self):
        chain = make_chain(3, [0.8, 0.8, 0.8])
        agg = NoisyOrAggregator()
        result = agg.aggregate(chain, interrupt_probs=[0.5, 0.5, 0.5])
        assert result.final_confidence < 0.8


class TestAllAggregators:

    @pytest.mark.parametrize("agg_class,init_kwargs", [
        (NaiveProductAggregator, {}),
        (LogitAggregator, {}),
        (BayesianUpdateAggregator, {}),
        (NoisyOrAggregator, {}),
    ])
    def test_output_range(self, agg_class, init_kwargs):
        """All aggregators must output confidence in [0, 1]."""
        chain = make_chain(5, [0.7] * 5)
        agg = agg_class(**init_kwargs)
        kwargs = {}
        if agg_class in (BayesianUpdateAggregator, NoisyOrAggregator):
            kwargs["interrupt_probs"] = [0.05] * 5
        result = agg.aggregate(chain, **kwargs)
        assert 0.0 <= result.final_confidence <= 1.0
        assert len(result.intermediate_confidences) == 5
        assert len(result.per_hop_contributions) == 5
        ci_lower, ci_upper = result.confidence_interval
        assert 0.0 <= ci_lower <= result.final_confidence <= ci_upper <= 1.0
