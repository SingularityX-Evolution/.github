"""
停止准则模块：实现原则性停止规则

核心问题：什么时候应该停止推理？
- 无限跳跃：模型永远不停，推理链越来越长，噪声越来越多
- 过早停止：遗漏了关键推理步骤，结论不够完整

本模块实现以下停止准则：
- CIWidthStopper：置信区间宽度阈值
- InfoGainStopper：期望信息增益阈值
- MaxHopStopper：最大跳数约束
- CompositeStopper：组合停止准则（AND / OR 逻辑）
"""

import numpy as np
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Dict


class StoppingCriteria(ABC):
    """停止准则基类"""

    name: str

    @abstractmethod
    def should_stop(
        self,
        hop_confidences: List[float],
        current_confidence: float,
        ci: Tuple[float, float],
        hop_index: int,
    ) -> Tuple[bool, str]:
        """
        判断是否应停止推理

        Args:
            hop_confidences: 到当前跳为止的所有跳置信度
            current_confidence: 当前端到端置信度
            ci: 当前置信区间 (lower, upper)
            hop_index: 当前跳的索引（0-based）

        Returns:
            (should_stop: bool, reason: str)
        """
        pass

    @abstractmethod
    def describe(self) -> str:
        """返回准则描述"""
        pass


class CIWidthStopper(StoppingCriteria):
    """
    置信区间宽度停止准则

    当置信区间宽度低于阈值时，说明当前置信度已经足够精确，
    继续跳跃可能引入更多噪声而不提升精度。

    停止条件：ci_upper - ci_lower < threshold

    优点：与置信度精度直接挂钩，有统计意义
    缺点：需要 CI 计算（依赖蒙特卡洛采样）
    """

    name = "CIWidthStopper"

    def __init__(self, width_threshold: float = 0.10, min_hops: int = 1):
        """
        Args:
            width_threshold: 停止的置信区间宽度阈值
            min_hops: 最少执行的跳数（防止过早停止）
        """
        self.width_threshold = width_threshold
        self.min_hops = min_hops

    def should_stop(
        self,
        hop_confidences: List[float],
        current_confidence: float,
        ci: Tuple[float, float],
        hop_index: int,
    ) -> Tuple[bool, str]:
        ci_width = ci[1] - ci[0]

        if hop_index < self.min_hops:
            return (False, "Minimum hops not reached")

        if ci_width < self.width_threshold:
            return (True, f"CI width {ci_width:.4f} < threshold {self.width_threshold:.4f}")

        return (False, "CI width above threshold")

    def describe(self) -> str:
        return (
            f"CIWidthStopper(width_threshold={self.width_threshold}, "
            f"min_hops={self.min_hops})"
        )


class InfoGainStopper(StoppingCriteria):
    """
    期望信息增益停止准则

    当增加下一跳的期望信息增益低于阈值时，说明继续跳跃
    不会带来足够的信息量，停止推理。

    期望信息增益 = P(下一跳成立) × (-log P(当前置信度))
              ≈ hop_confidence × 当前的不确定性

    优点：直接量化"继续推理的收益"
    缺点：需要估计下一跳的置信度
    """

    name = "InfoGainStopper"

    def __init__(
        self,
        info_gain_threshold: float = 0.01,
        min_hops: int = 2,
        expected_next_confidence: Optional[float] = None,
    ):
        """
        Args:
            info_gain_threshold: 停止的信息增益阈值
            min_hops: 最少执行的跳数
            expected_next_confidence: 估计的下一跳置信度（默认使用当前置信度）
        """
        self.info_gain_threshold = info_gain_threshold
        self.min_hops = min_hops
        self.expected_next_confidence = expected_next_confidence

    def _uncertainty(self, p: float) -> float:
        """计算熵 H(P) = -p log p - (1-p) log (1-p)"""
        eps = 1e-9
        p = np.clip(p, eps, 1 - eps)
        return -p * np.log(p) - (1 - p) * np.log(1 - p)

    def should_stop(
        self,
        hop_confidences: List[float],
        current_confidence: float,
        ci: Tuple[float, float],
        hop_index: int,
    ) -> Tuple[bool, str]:
        if hop_index < self.min_hops:
            return (False, "Minimum hops not reached")

        # 估计下一跳的置信度
        next_conf = (
            self.expected_next_confidence
            if self.expected_next_confidence is not None
            else current_confidence
        )

        # 期望信息增益 ≈ P(下一跳成立) × H(当前置信度)
        info_gain = next_conf * self._uncertainty(current_confidence)

        if info_gain < self.info_gain_threshold:
            return (True, f"Info gain {info_gain:.4f} < threshold {self.info_gain_threshold:.4f}")

        return (False, f"Info gain {info_gain:.4f} >= threshold")

    def describe(self) -> str:
        return (
            f"InfoGainStopper(threshold={self.info_gain_threshold}, "
            f"min_hops={self.min_hops})"
        )


class MaxHopStopper(StoppingCriteria):
    """
    最大跳数约束

    最简单的停止准则：跳数达到上限时强制停止。
    作为硬约束，通常与其他准则组合使用。

    优点：简单、防止无限递归
    缺点：不灵活，不能自适应
    """

    name = "MaxHopStopper"

    def __init__(self, max_hops: int = 5, min_hops: int = 1):
        """
        Args:
            max_hops: 最大允许跳数
            min_hops: 最少执行的跳数
        """
        self.max_hops = max_hops
        self.min_hops = min_hops

    def should_stop(
        self,
        hop_confidences: List[float],
        current_confidence: float,
        ci: Tuple[float, float],
        hop_index: int,
    ) -> Tuple[bool, str]:
        if hop_index < self.min_hops:
            return (False, "Minimum hops not reached")

        if hop_index + 1 >= self.max_hops:
            return (True, f"Max hops {self.max_hops} reached (hop {hop_index + 1})")

        return (False, f"Current hop {hop_index + 1} < max {self.max_hops}")

    def describe(self) -> str:
        return f"MaxHopStopper(max_hops={self.max_hops}, min_hops={self.min_hops})"


class FloorConfidenceStopper(StoppingCriteria):
    """
    置信度下限停止准则

    当端到端置信度低于某个下限值时，继续推理意义不大，停止。

    优点：直接反映"这条链还有没有价值继续"
    缺点：下限阈值需要校准
    """

    name = "FloorConfidenceStopper"

    def __init__(self, floor: float = 0.05, min_hops: int = 1):
        """
        Args:
            floor: 停止的置信度下限
            min_hops: 最少执行的跳数
        """
        self.floor = floor
        self.min_hops = min_hops

    def should_stop(
        self,
        hop_confidences: List[float],
        current_confidence: float,
        ci: Tuple[float, float],
        hop_index: int,
    ) -> Tuple[bool, str]:
        if hop_index < self.min_hops:
            return (False, "Minimum hops not reached")

        if current_confidence < self.floor:
            return (True, f"Confidence {current_confidence:.4f} < floor {self.floor:.4f}")

        return (False, "Confidence above floor")

    def describe(self) -> str:
        return f"FloorConfidenceStopper(floor={self.floor}, min_hops={self.min_hops})"


class CompositeStopper(StoppingCriteria):
    """
    组合停止准则

    将多个停止准则用 AND / OR 逻辑组合。

    AND: 所有准则都同意停止时才停止（保守策略）
    OR:  任一准则同意停止时就停止（激进策略）
    """

    name = "CompositeStopper"

    def __init__(
        self,
        criteria: List[StoppingCriteria],
        mode: str = "AND",
    ):
        """
        Args:
            criteria: 停止准则列表
            mode: "AND" 或 "OR"
        """
        if mode not in ("AND", "OR"):
            raise ValueError("mode must be 'AND' or 'OR'")
        self.criteria = criteria
        self.mode = mode

    def should_stop(
        self,
        hop_confidences: List[float],
        current_confidence: float,
        ci: Tuple[float, float],
        hop_index: int,
    ) -> Tuple[bool, str]:
        reasons = []
        stop_votes = []

        for criterion in self.criteria:
            stop, reason = criterion.should_stop(
                hop_confidences, current_confidence, ci, hop_index
            )
            stop_votes.append(stop)
            reasons.append(f"[{criterion.name}] {reason}")

        if self.mode == "AND":
            should_stop = all(stop_votes)
        else:  # OR
            should_stop = any(stop_votes)

        all_reasons = " | ".join(reasons)
        return (should_stop, all_reasons)

    def describe(self) -> str:
        criteria_str = ", ".join(c.describe() for c in self.criteria)
        return f"CompositeStopper({self.mode}, [{criteria_str}])"


def get_default_stopper() -> CompositeStopper:
    """获取默认组合停止准则（OR 组合，四种准则）"""
    return CompositeStopper(
        criteria=[
            MaxHopStopper(max_hops=5, min_hops=1),
            FloorConfidenceStopper(floor=0.05, min_hops=2),
            CIWidthStopper(width_threshold=0.15, min_hops=2),
            InfoGainStopper(info_gain_threshold=0.01, min_hops=2),
        ],
        mode="OR",
    )
