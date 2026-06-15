"""
置信度聚合模型：实现多种非朴素连乘聚合方案

理论背景：
朴素连乘 P_total = ∏ P(hops) 失效的原因：
1. 独立性假设不成立：各跳之间存在共同因果因素或混淆变量
2. 外部截断事件：跳之间可能发生外部事件打断因果链（如 OPEC 增产对冲供应紧张）
3. 长链过度衰减：3 跳后置信度往往远低于实际
4. 相关性放大：链中各跳的小相关性在乘法下被放大

本模块实现：
- NaiveMultiplier：朴素连乘 baseline
- LogOddsAggregator：对数几率聚合（减少长链衰减）
- BayesianUpdater：贝叶斯逐跳更新（引入先验和证据更新）
- NoisyOR：Noisy-OR 模型（建模外部抑制因素）
- DampedMultiplier：带衰减因子的朴素连乘（简单实用）
"""

import numpy as np
from scipy.special import logit, expit, beta as beta_func
from scipy import stats
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Optional


class AggregatorBase(ABC):
    """所有聚合器的基类"""

    name: str  # 聚合器名称

    @abstractmethod
    def aggregate(self, hop_confidences: List[float]) -> float:
        """聚合多跳置信度，返回端到端置信度"""
        pass

    @abstractmethod
    def aggregate_with_ci(
        self, hop_confidences: List[float], n_samples: int = 10000
    ) -> Tuple[float, float, float]:
        """
        聚合并计算置信区间
        返回: (mean, lower_95, upper_95)
        """
        pass

    def describe(self) -> str:
        return f"Aggregator: {self.name}"


class NaiveMultiplier(AggregatorBase):
    """
    朴素连乘 baseline
    P_total = ∏_{i=1}^{n} P(hop_i)

    优点：简单直观
    缺点：长链衰减过快，各跳独立性假设通常不成立
    """

    name = "NaiveMultiplier"

    def aggregate(self, hop_confidences: List[float]) -> float:
        if not hop_confidences:
            return 0.0
        return np.prod(hop_confidences)

    def aggregate_with_ci(
        self, hop_confidences: List[float], n_samples: int = 10000
    ) -> Tuple[float, float, float]:
        if not hop_confidences:
            return (0.0, 0.0, 0.0)

        mean = np.prod(hop_confidences)
        # 假设每个 hop_confidence 有 ±0.05 的标准差，通过蒙特卡洛传播
        eps = 1e-6
        p_clipped = np.clip(np.array(hop_confidences), eps, 1 - eps)
        std_per_hop = 0.05
        samples = np.zeros(n_samples)
        for i in range(n_samples):
            perturbed = np.clip(
                p_clipped + np.random.randn(len(p_clipped)) * std_per_hop,
                eps, 1 - eps
            )
            samples[i] = np.prod(perturbed)

        return (float(mean), float(np.percentile(samples, 2.5)), float(np.percentile(samples, 97.5)))


class LogOddsAggregator(AggregatorBase):
    """
    对数几率聚合（Log-Odds Aggregation）

    将概率转换为 log-odds 后求均值，再转回概率：
    P_total = sigmoid(mean(logit(P(hops))))

    相比朴素连乘，在长链场景下不会过度衰减。
    数学性质：等价于对各跳 logit 值做加权平均，
    当各跳独立时，聚合结果介于朴素乘积和最大跳之间。

    参考文献：K十和 K十 (2005) on aggregating probabilistic beliefs
    """

    name = "LogOddsAggregator"

    def __init__(self, weights: Optional[List[float]] = None, temperature: float = 1.0):
        """
        Args:
            weights: 各跳权重，默认等权重
            temperature: 温度参数 > 1 时增加保守性，< 1 时增加激进性
        """
        self.weights = weights
        self.temperature = temperature

    def aggregate(self, hop_confidences: List[float]) -> float:
        if not hop_confidences:
            return 0.0

        hop_confidences = np.array(hop_confidences)
        # 裁剪到 (ε, 1-ε) 避免 logit(0) 和 logit(1) 无定义
        eps = 1e-6
        p = np.clip(hop_confidences, eps, 1 - eps)

        logits = logit(p)

        if self.weights is not None:
            w = np.array(self.weights)
            w = w / w.sum()
            logits = w * logits

        mean_logit = logits.mean() / self.temperature
        return float(expit(mean_logit))

    def aggregate_with_ci(
        self, hop_confidences: List[float], n_samples: int = 10000
    ) -> Tuple[float, float, float]:
        if not hop_confidences:
            return (0.0, 0.0, 0.0)

        eps = 1e-6
        p_clipped = np.clip(np.array(hop_confidences), eps, 1 - eps)

        logits = logit(p_clipped)

        # 各跳 logit 的标准差估计（假设各跳独立下的 logit 方差）
        logit_stds = np.sqrt(p_clipped**2 * (1 - p_clipped) / (p_clipped * (1 - p_clipped)**2 + 1e-9))

        # 蒙特卡洛采样
        samples = []
        for _ in range(n_samples):
            sampled_logits = logits + np.random.randn(len(logits)) * logit_stds * 0.1
            if self.weights is not None:
                w = np.array(self.weights)
                w = w / w.sum()
                mean_logit = np.sum(w * sampled_logits) / self.temperature
            else:
                mean_logit = sampled_logits.mean() / self.temperature
            samples.append(expit(mean_logit))

        samples = np.array(samples)
        return (float(np.mean(samples)), float(np.percentile(samples, 2.5)), float(np.percentile(samples, 97.5)))


class BayesianUpdater(AggregatorBase):
    """
    贝叶斯逐跳更新

    将每跳视为对当前信念的贝叶斯更新：
    - 初始先验：P(H) = 0.5
    - 似然：P(E_i | H) = hop_confidence_i
    - 后验：P(H | E_i) ∝ P(E_i | H) · P(H)

    同时引入"干扰因子" d_i ∈ [0,1]，表示第 i 跳到 i+1 跳之间
    受到外部干扰的概率，d_i 越大说明链越脆弱。

    P_total = Posterior_{n}(H) = Beta(α + Σw_i, β + Σw'_i)

    其中 w_i 与 hop_confidence 相关，w'_i 与干扰因子相关。
    """

    name = "BayesianUpdater"

    def __init__(
        self,
        prior_alpha: float = 1.0,
        prior_beta: float = 1.0,
        interference_factors: Optional[List[float]] = None,
    ):
        """
        Args:
            prior_alpha: Beta 先验的 alpha 参数
            prior_beta: Beta 先验的 beta 参数
            interference_factors: 各跳之间的干扰因子，默认全部为 0（无干扰）
                                 干扰因子 d_i ∈ [0,1]，表示外部事件打断链路的概率
        """
        self.prior_alpha = prior_alpha
        self.prior_beta = prior_beta
        self.interference_factors = interference_factors or []

    def aggregate(self, hop_confidences: List[float]) -> float:
        if not hop_confidences:
            return 0.0

        n = len(hop_confidences)
        alpha = self.prior_alpha
        beta = self.prior_beta

        for i, p in enumerate(hop_confidences):
            # 将置信度映射到 Beta 参数更新
            # P(E|H) ∝ p^γ, P(E|¬H) ∝ (1-p)^γ
            gamma = 2.0  # 强度参数
            alpha += p**gamma
            beta += (1 - p) ** gamma

            # 如果有干扰因子，逐次衰减信念
            if i < len(self.interference_factors):
                interference = self.interference_factors[i]
                decay = 1 - interference * 0.5  # 干扰越大，衰减越多
                alpha *= decay
                beta *= (2 - decay)

        # 返回后验均值
        return alpha / (alpha + beta)

    def aggregate_with_ci(
        self, hop_confidences: List[float], n_samples: int = 10000
    ) -> Tuple[float, float, float]:
        if not hop_confidences:
            return (0.0, 0.0, 0.0)

        # Beta 后验采样
        alpha = self.prior_alpha
        beta = self.prior_beta

        for i, p in enumerate(hop_confidences):
            gamma = 2.0
            alpha += p**gamma
            beta += (1 - p) ** gamma

            if i < len(self.interference_factors):
                interference = self.interference_factors[i]
                decay = 1 - interference * 0.5
                alpha *= decay
                beta *= (2 - decay)

        samples = np.random.beta(alpha, beta, n_samples)
        return (float(np.mean(samples)), float(np.percentile(samples, 2.5)), float(np.percentile(samples, 97.5)))


class NoisyOR(AggregatorBase):
    """
    Noisy-OR 模型

    Noisy-OR 建模了"因果抑制"机制：每一跳有一个抑制概率（inhibition），
    只有当所有跳都没有被抑制时，端到端因果才成立。

    P(E) = 1 - ∏_{i=1}^{n} (1 - λ_i · θ_i)

    其中：
    - θ_i: 第 i 跳的因果强度（对应 hop_confidence）
    - λ_i: 第 i 跳的因果有效性系数（默认 λ_i = 1）
    - λ: 泄漏概率（背景激活概率）

    这个模型自然地处理了"部分跳较弱但链仍然成立"的情况。

    同时支持外部截断建模：当某跳较弱时，允许链提前断裂。
    """

    name = "NoisyOR"

    def __init__(
        self,
        leak_prob: float = 0.0,
        inhibition_base: float = 0.1,
    ):
        """
        Args:
            leak_prob: 泄漏概率 λ，即背景激活概率
            inhibition_base: 基础抑制率，影响弱跳的衰减程度
        """
        self.leak_prob = leak_prob
        self.inhibition_base = inhibition_base

    def aggregate(self, hop_confidences: List[float]) -> float:
        if not hop_confidences:
            return 0.0

        # Noisy-OR: P(E) = 1 - ∏(1 - λ_i·θ_i)
        prob_not_caused = 1.0
        for i, theta in enumerate(hop_confidences):
            # λ_i = 1 - inhibition^i，体现"抑制积累"
            # 越靠后的跳，抑制积累越多
            length_penalty = (self.inhibition_base ** (i + 1)) * (1 - theta**0.5)
            lambda_i = max(0.0, min(1.0, 1 - length_penalty))
            prob_not_caused *= (1 - lambda_i * theta)

        return 1 - prob_not_caused + self.leak_prob * (1 - prob_not_caused)

    def aggregate_with_ci(
        self, hop_confidences: List[float], n_samples: int = 10000
    ) -> Tuple[float, float, float]:
        if not hop_confidences:
            return (0.0, 0.0, 0.0)

        hop_confidences = np.array(hop_confidences)

        # 假设 hop_confidences ~ Beta(α, β) 分布
        # 用均值=hop_confidence, std=0.05 估计 α, β
        std = 0.05
        mean = hop_confidences
        alpha_est = mean**2 * (1 - mean) / std**2 - mean
        beta_est = alpha_est * (1 - mean) / mean
        alpha_est = np.maximum(alpha_est, 0.1)
        beta_est = np.maximum(beta_est, 0.1)

        samples = np.zeros(n_samples)
        for i in range(n_samples):
            sampled_thetas = np.random.beta(alpha_est, beta_est)
            prob_not_caused = 1.0
            for j, theta in enumerate(sampled_thetas):
                length_penalty = (self.inhibition_base ** (j + 1)) * (1 - theta**0.5)
                lambda_i = max(0.0, min(1.0, 1 - length_penalty))
                prob_not_caused *= (1 - lambda_i * theta)
            samples[i] = 1 - prob_not_caused + self.leak_prob * (1 - prob_not_caused)

        mean_val = float(np.mean(samples))
        lower_val = float(np.percentile(samples, 2.5))
        upper_val = float(np.percentile(samples, 97.5))
        # 防止零宽度 CI（当置信度极高时，采样可能全为1）
        if upper_val - lower_val < 0.01:
            upper_val = min(1.0, mean_val + 0.01)
            lower_val = max(0.0, mean_val - 0.01)
        return (mean_val, lower_val, upper_val)


class DampedMultiplier(AggregatorBase):
    """
    带衰减因子的朴素连乘

    P_total = ∏_{i=1}^{n} p_i^{1/δ^i}

    其中 δ > 1 是衰减参数，δ^i 使得靠后的跳衰减更少。
    这与朴素连乘相反——因为直觉上第3跳到第4跳之间的
    干扰比第1跳到第2跳之间更多，所以早期跳应该衰减更多。

    实际上我们用：
    P_total = ∏ p_i · (1 + α·i) 或
    P_total = ∏ p_i^{exp(-β·i)}

    这里实现的是：基于跳序的加权衰减，减弱早期跳的主导权。
    """

    name = "DampedMultiplier"

    def __init__(self, decay_rate: float = 0.05, power: float = 0.5):
        """
        Args:
            decay_rate: 每跳衰减率（加法模型）
            power: 指数衰减的幂次（乘法模型）
        """
        self.decay_rate = decay_rate
        self.power = power

    def aggregate(self, hop_confidences: List[float]) -> float:
        if not hop_confidences:
            return 0.0

        result = 1.0
        for i, p in enumerate(hop_confidences):
            # 跳序调整因子：早期跳 i=0,1 影响力打折扣
            hop_weight = 1.0 / (1.0 + self.decay_rate * i)
            result *= p ** (hop_weight * self.power)
            # 加法衰减：后期跳保留更多权重
            result *= (1.0 + self.decay_rate * i / len(hop_confidences))

        return float(np.clip(result, 0.0, 1.0))

    def aggregate_with_ci(
        self, hop_confidences: List[float], n_samples: int = 10000
    ) -> Tuple[float, float, float]:
        if not hop_confidences:
            return (0.0, 0.0, 0.0)

        eps = 1e-6
        p_clipped = np.clip(np.array(hop_confidences), eps, 1 - eps)

        # 蒙特卡洛：假设每个 hop_confidence ± 0.05 扰动
        samples = []
        for _ in range(n_samples):
            perturbed = np.clip(
                p_clipped + np.random.randn(len(p_clipped)) * 0.05,
                eps, 1 - eps
            )
            result = 1.0
            n = len(perturbed)
            for i, p in enumerate(perturbed):
                hop_weight = 1.0 / (1.0 + self.decay_rate * i)
                result *= p ** (hop_weight * self.power)
                result *= (1.0 + self.decay_rate * i / n)
            samples.append(np.clip(result, 0.0, 1.0))

        samples = np.array(samples)
        return (float(np.mean(samples)), float(np.percentile(samples, 2.5)), float(np.percentile(samples, 97.5)))


def get_all_aggregators() -> Dict[str, AggregatorBase]:
    """返回所有可用聚合器实例"""
    return {
        "NaiveMultiplier": NaiveMultiplier(),
        "LogOdds": LogOddsAggregator(temperature=1.0),
        "BayesianUpdater": BayesianUpdater(prior_alpha=1.0, prior_beta=1.0),
        "NoisyOR": NoisyOR(leak_prob=0.01, inhibition_base=0.1),
        "DampedMultiplier": DampedMultiplier(decay_rate=0.05, power=0.5),
    }


def compare_aggregators(
    hop_confidences: List[float], label: bool = True
) -> Dict[str, Dict]:
    """
    比较所有聚合器在给定链上的输出

    Returns:
        Dict[str, Dict] — 每个聚合器的置信度和置信区间
    """
    results = {}
    for name, agg in get_all_aggregators().items():
        mean, lower, upper = agg.aggregate_with_ci(hop_confidences)
        results[name] = {
            "confidence": mean,
            "ci_lower": lower,
            "ci_upper": upper,
            "ci_width": upper - lower,
            "hit": (mean > 0.5) == label,
        }
    return results
