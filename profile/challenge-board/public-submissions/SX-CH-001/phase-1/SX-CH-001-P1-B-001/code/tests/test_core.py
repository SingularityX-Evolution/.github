"""
核心功能测试用例
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import numpy as np
from src.aggregator import (
    NaiveMultiplier,
    LogOddsAggregator,
    BayesianUpdater,
    NoisyOR,
    DampedMultiplier,
    get_all_aggregators,
    compare_aggregators,
)
from src.stopping import (
    MaxHopStopper,
    CIWidthStopper,
    InfoGainStopper,
    FloorConfidenceStopper,
    CompositeStopper,
    get_default_stopper,
)
from src.calibrator import BrierScore, ReliabilityDiagram, BucketedCalibration
from src.evaluator import CausalChainEvaluator, ChainResult


class TestAggregators:
    """聚合器测试"""

    def test_naive_multiplier_basic(self):
        agg = NaiveMultiplier()
        result = agg.aggregate([0.9, 0.9, 0.9])
        assert 0.0 <= result <= 1.0
        # 三跳 0.9 的乘积 = 0.729
        assert 0.72 < result < 0.74

    def test_naive_multiplier_empty(self):
        agg = NaiveMultiplier()
        assert agg.aggregate([]) == 0.0

    def test_log_odds_less_decay(self):
        """对数几率聚合应比朴素连乘衰减更慢"""
        naive = NaiveMultiplier()
        log_odds = LogOddsAggregator()

        hops = [0.9, 0.9, 0.9, 0.9]
        naive_result = naive.aggregate(hops)
        log_odds_result = log_odds.aggregate(hops)

        # 4 跳后，朴素连乘 = 0.656，但 log-odds 不应衰减那么快
        assert log_odds_result > naive_result

    def test_log_odds_temperature(self):
        """温度参数调节激进程度"""
        agg_conservative = LogOddsAggregator(temperature=2.0)
        agg_aggressive = LogOddsAggregator(temperature=0.5)

        hops = [0.7, 0.8, 0.9]
        result_conservative = agg_conservative.aggregate(hops)
        result_aggressive = agg_aggressive.aggregate(hops)

        assert result_conservative < result_aggressive

    def test_bayesian_updater(self):
        """贝叶斯更新应输出有效概率"""
        agg = BayesianUpdater()
        result = agg.aggregate([0.8, 0.8, 0.8])
        assert 0.0 <= result <= 1.0
        # 强置信度应导致高聚合结果
        assert result > 0.7

    def test_bayesian_with_interference(self):
        """干扰因子应降低结果"""
        agg_no_interference = BayesianUpdater(interference_factors=[0.0, 0.0])
        agg_with_interference = BayesianUpdater(interference_factors=[0.5, 0.5])

        hops = [0.9, 0.9]
        result_no_interference = agg_no_interference.aggregate(hops)
        result_with_interference = agg_with_interference.aggregate(hops)

        assert result_with_interference < result_no_interference

    def test_noisy_or_basic(self):
        """Noisy-OR 应输出有效概率"""
        agg = NoisyOR()
        result = agg.aggregate([0.8, 0.8, 0.8])
        assert 0.0 <= result <= 1.0
        assert result > 0.5

    def test_noisy_or_leak(self):
        """泄漏概率应使低置信度链也有基础概率"""
        agg_no_leak = NoisyOR(leak_prob=0.0)
        agg_with_leak = NoisyOR(leak_prob=0.1)

        hops = [0.1, 0.1]
        result_no_leak = agg_no_leak.aggregate(hops)
        result_with_leak = agg_with_leak.aggregate(hops)

        assert result_with_leak > result_no_leak

    def test_damped_multiplier(self):
        """衰减乘数应合理处理长链"""
        agg = DampedMultiplier(decay_rate=0.1, power=0.5)
        result = agg.aggregate([0.8, 0.8, 0.8, 0.8])
        assert 0.0 <= result <= 1.0

    def test_ci_computation(self):
        """所有聚合器都应能计算置信区间"""
        hops = [0.8, 0.9, 0.85]
        for name, agg in get_all_aggregators().items():
            mean, lower, upper = agg.aggregate_with_ci(hops, n_samples=1000)
            assert 0.0 <= mean <= 1.0
            assert 0.0 <= lower <= 1.0
            assert 0.0 <= upper <= 1.0
            # CI lower may equal mean for very high confidence, but upper must >= mean
            assert lower <= upper

    def test_compare_aggregators(self):
        """比较函数应返回所有聚合器结果"""
        hops = [0.85, 0.80, 0.90]
        results = compare_aggregators(hops, label=True)
        assert len(results) == 5
        for name, r in results.items():
            assert "confidence" in r
            assert "ci_lower" in r
            assert "ci_upper" in r
            assert "hit" in r


class TestStoppingCriteria:
    """停止准则测试"""

    def test_max_hop_stopper(self):
        stopper = MaxHopStopper(max_hops=3, min_hops=1)

        # 第 1 跳不应停止
        stop, _ = stopper.should_stop([0.9], 0.9, (0.8, 1.0), 0)
        assert stop is False

        # 第 3 跳（索引2）应停止
        stop, reason = stopper.should_stop([0.9] * 3, 0.6, (0.5, 0.7), 2)
        assert stop is True

    def test_ci_width_stopper(self):
        stopper = CIWidthStopper(width_threshold=0.1, min_hops=0)

        # 宽 CI 不应停止
        stop, _ = stopper.should_stop([0.9], 0.9, (0.5, 1.0), 0)
        assert stop is False

        # 窄 CI 应停止
        stop, reason = stopper.should_stop([0.9], 0.9, (0.85, 0.95), 0)
        assert stop is True

    def test_floor_confidence_stopper(self):
        stopper = FloorConfidenceStopper(floor=0.1, min_hops=2)

        # 高置信度不应停止
        stop, _ = stopper.should_stop([0.9, 0.8], 0.7, (0.5, 0.9), 1)
        assert stop is False

        # 低置信度应停止（hop_index=2 >= min_hops=2）
        stop, reason = stopper.should_stop([0.9, 0.2, 0.1], 0.05, (0.0, 0.15), 2)
        assert stop is True

    def test_composite_and_mode(self):
        """AND 模式下所有准则都同意才停止"""
        stopper = CompositeStopper(
            criteria=[
                MaxHopStopper(max_hops=3),
                CIWidthStopper(width_threshold=0.1),
            ],
            mode="AND",
        )

        # 只有 max_hops 触发，CIWidth 没触发 -> 不停止
        stop, _ = stopper.should_stop([0.9, 0.9], 0.8, (0.7, 0.9), 1)
        assert stop is False

    def test_composite_or_mode(self):
        """OR 模式下任一准则同意就停止"""
        stopper = CompositeStopper(
            criteria=[
                MaxHopStopper(max_hops=2),
                CIWidthStopper(width_threshold=0.5),
            ],
            mode="OR",
        )

        # max_hops 触发 -> 停止
        stop, _ = stopper.should_stop([0.9, 0.9], 0.8, (0.5, 1.0), 1)
        assert stop is True

    def test_default_stopper(self):
        """默认停止准则应合理配置"""
        stopper = get_default_stopper()
        assert isinstance(stopper, CompositeStopper)
        assert stopper.mode == "OR"


class TestCalibration:
    """校准验证测试"""

    def test_brier_score_perfect(self):
        """完美预测的 Brier Score 应为 0"""
        brier = BrierScore()
        brier.add(1.0, True)
        brier.add(0.0, False)
        assert abs(brier.compute()) < 1e-6

    def test_brier_score_random(self):
        """随机预测的 Brier Score 应在 0.2-0.25 左右"""
        brier = BrierScore()
        for _ in range(100):
            import random
            p = random.random()
            y = random.choice([True, False])
            brier.add(p, y)
        score = brier.compute()
        assert 0.10 < score < 0.40

    def test_brier_decomposition(self):
        """Brier Score 分解"""
        brier = BrierScore()
        for i in range(20):
            brier.add(0.9, True)
            brier.add(0.1, False)
        dec = brier.decompose()
        assert "brier" in dec
        assert "reliability" in dec
        assert "resolution" in dec

    def test_reliability_diagram(self):
        """可靠性图应能正常生成"""
        rd = ReliabilityDiagram(n_bins=5)
        for i in range(50):
            import random
            p = random.random()
            y = random.choice([True, False])
            rd.add(p, y)

        fig = rd.plot(save_path=None)
        assert fig is not None
        ece = rd.compute_ece()
        assert 0.0 <= ece <= 1.0

    def test_bucketed_calibration(self):
        """分桶校准表"""
        bc = BucketedCalibration(n_bins=5)
        for _ in range(30):
            import random
            p = random.random()
            y = random.choice([True, False])
            bc.add(p, y)

        table = bc.table()
        assert not table.empty
        assert "bin_range" in table.columns
        assert "n_samples" in table.columns


class TestEvaluator:
    """端到端评估器测试"""

    def test_evaluator_basic(self):
        """评估器应能处理标准链数据"""
        evaluator = CausalChainEvaluator(aggregator_name="NoisyOR")

        chain = {
            "chain_id": "TEST_001",
            "label": True,
            "confidence_per_hop": [0.95, 0.88, 0.80, 0.75],
        }

        result = evaluator.evaluate(chain)

        assert isinstance(result, ChainResult)
        assert result.chain_id == "TEST_001"
        assert 0.0 <= result.end_to_end_confidence <= 1.0
        assert 0.0 <= result.ci_lower <= 1.0
        assert 0.0 <= result.ci_upper <= 1.0
        assert result.ci_lower <= result.end_to_end_confidence <= result.ci_upper

    def test_evaluator_empty_hops(self):
        """空跳列表应返回零结果"""
        evaluator = CausalChainEvaluator()
        chain = {"chain_id": "TEST_EMPTY", "label": True, "confidence_per_hop": []}

        result = evaluator.evaluate(chain)
        assert result.end_to_end_confidence == 0.0
        assert result.should_stop is True

    def test_evaluator_batch(self):
        """批量评估应返回正确数量"""
        evaluator = CausalChainEvaluator(aggregator_name="DampedMultiplier")

        chains = [
            {"chain_id": f"CH_{i}", "label": i % 2 == 0, "confidence_per_hop": [0.8, 0.8]}
            for i in range(10)
        ]

        results = evaluator.evaluate_batch(chains)
        assert len(results) == 10

    def test_evaluator_all_aggregators(self):
        """评估所有聚合器"""
        evaluator = CausalChainEvaluator()
        chain = {
            "chain_id": "TEST_COMPARE",
            "label": True,
            "confidence_per_hop": [0.9, 0.85, 0.80],
        }

        results = evaluator.evaluate_all_aggregators(chain)
        assert len(results) == 5
        for name, r in results.items():
            assert isinstance(r, ChainResult)

    def test_prediction_correct(self):
        """预测正确性判断"""
        evaluator = CausalChainEvaluator()

        # 正例，置信度高 -> 正确
        result = evaluator.evaluate({"chain_id": "T1", "label": True, "confidence_per_hop": [0.9, 0.9]})
        assert result.prediction_correct is True

        # 正例，置信度低 -> 错误
        result = evaluator.evaluate({"chain_id": "T2", "label": True, "confidence_per_hop": [0.2, 0.2]})
        assert result.prediction_correct is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
