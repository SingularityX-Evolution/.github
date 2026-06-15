"""
校准验证模块：Brier Score / 可靠性图 / 分桶校准

校准验证的核心目标：
- 评估聚合模型输出的置信度是否"可信赖"
- 即：如果模型说某事件有 80% 的概率发生，
  实际上是否真的有 80% 的概率发生？

本模块实现：
- BrierScore：Brier Score 计算（越接近 0 越好）
- ReliabilityDiagram：可靠性图生成
- BucketedCalibration：分桶校准分析
- CalibrationValidator：综合校准验证器
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from .aggregator import AggregatorBase


class BrierScore:
    """
    Brier Score（布里尔分数）

    BS = (1/N) · Σ (predicted_prob - actual_outcome)²

    - BS = 0: 完美校准
    - BS = 0.25: 随机预测（50% 预测时）
    - BS 越接近 0 越好

    分解（Brier Score Decomposition）：
    BS = Reliability - Resolution + Uncertainty

    其中：
    - Reliability（可靠性）：预测概率与实际观测频率的接近程度
    - Resolution（分辨率）：预测的极端程度，越极端分辨率越高
    - Uncertainty（不确定性）：结果分布的熵，固定值

    S 档标准：Brier Score < 0.15
    """

    name = "BrierScore"

    def __init__(self):
        self.history = []

    def score(self, predicted_prob: float, actual_outcome: bool) -> float:
        """计算单个预测的 Brier Score"""
        actual = 1.0 if actual_outcome else 0.0
        return (predicted_prob - actual) ** 2

    def add(self, predicted_prob: float, actual_outcome: bool):
        """添加一个预测-结果对"""
        self.history.append((predicted_prob, actual_outcome))

    def compute(self) -> float:
        """计算累积 Brier Score"""
        if not self.history:
            return 1.0
        total = sum(self.score(p, y) for p, y in self.history)
        return total / len(self.history)

    def decompose(self) -> Dict[str, float]:
        """
        Brier Score 分解

        Returns:
            dict with 'brier', 'reliability', 'resolution', 'uncertainty'
        """
        if not self.history:
            return {"brier": 1.0, "reliability": 0.0, "resolution": 0.0, "uncertainty": 0.0}

        probs = np.array([p for p, _ in self.history])
        outcomes = np.array([1.0 if y else 0.0 for _, y in self.history])

        # Uncertainty: H(p_bar) 其中 p_bar 是结果的基础率
        p_bar = outcomes.mean()
        uncertainty = -p_bar * np.log(p_bar + 1e-9) - (1 - p_bar) * np.log(1 - p_bar + 1e-9)

        # Reliability: E[|P(Y=1|p) - p|²]
        bins = np.linspace(0.0, 1.0, 11)
        reliability = 0.0
        total_count = 0

        for i in range(len(bins) - 1):
            mask = (probs >= bins[i]) & (probs < bins[i + 1])
            count = mask.sum()
            if count > 0:
                avg_prob = probs[mask].mean()
                avg_outcome = outcomes[mask].mean()
                reliability += count * (avg_prob - avg_outcome) ** 2
                total_count += count

        if total_count > 0:
            reliability /= total_count

        resolution = self.compute() - reliability + uncertainty

        return {
            "brier": self.compute(),
            "reliability": reliability,
            "resolution": resolution,
            "uncertainty": uncertainty,
        }

    def reset(self):
        self.history = []


class ReliabilityDiagram:
    """
    可靠性图（Reliability Diagram）

    将预测概率分成多个桶，绘制：
    - X 轴：每个桶内的平均预测概率
    - Y 轴：每个桶内的实际观测频率

    完美校准：所有点都在对角线上。

    额外输出：
    - 分辨率统计（每个桶的样本数）
    - 校准误差（ECE：Expected Calibration Error）
    """

    name = "ReliabilityDiagram"

    def __init__(self, n_bins: int = 10):
        self.n_bins = n_bins
        self.history = []

    def add(self, predicted_prob: float, actual_outcome: bool):
        self.history.append((predicted_prob, 1.0 if actual_outcome else 0.0))

    def plot(self, title: str = "Reliability Diagram", save_path: Optional[str] = None) -> plt.Figure:
        """
        绘制可靠性图并保存

        Returns:
            matplotlib Figure
        """
        if not self.history:
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.text(0.5, 0.5, "No data", ha="center", va="center")
            return fig

        probs = np.array([p for p, _ in self.history])
        outcomes = np.array([y for _, y in self.history])

        bin_edges = np.linspace(0.0, 1.0, self.n_bins + 1)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        bin_frequencies = []
        bin_counts = []
        bin_accuracies = []

        for i in range(self.n_bins):
            mask = (probs >= bin_edges[i]) & (probs < bin_edges[i + 1])
            count = mask.sum()
            bin_counts.append(count)
            if count > 0:
                freq = probs[mask].mean()
                acc = outcomes[mask].mean()
            else:
                freq = bin_centers[i]
                acc = 0.0
            bin_frequencies.append(freq)
            bin_accuracies.append(acc)

        # ECE 计算
        ece = sum(
            c / len(probs) * abs(f - a)
            for c, f, a in zip(bin_counts, bin_frequencies, bin_accuracies)
            if c > 0
        )

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot([0, 1], [0, 1], "k--", lw=2, label="Perfect calibration")

        # 绘制桶（用柱状图）
        widths = 1.0 / self.n_bins
        for i, (center, freq, acc, count) in enumerate(
            zip(bin_centers, bin_frequencies, bin_accuracies, bin_counts)
        ):
            color = "#4C72B0" if count > 0 else "#CCCCCC"
            ax.bar(center, acc, width=widths * 0.8, color=color, alpha=0.8, edgecolor="black")
            if count > 0:
                ax.text(center, acc + 0.02, f"n={count}\nECE+={abs(freq-acc):.3f}", 
                       ha="center", va="bottom", fontsize=7)

        ax.set_xlabel("Average Predicted Probability", fontsize=12)
        ax.set_ylabel("Fraction of Positives (Actual Frequency)", fontsize=12)
        ax.set_title(f"{title}\nECE = {ece:.4f}", fontsize=14)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1.1)
        ax.legend(loc="upper left")
        ax.grid(True, alpha=0.3)

        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches="tight")

        return fig

    def compute_ece(self) -> float:
        """计算 Expected Calibration Error"""
        if not self.history:
            return 1.0

        probs = np.array([p for p, _ in self.history])
        outcomes = np.array([y for _, y in self.history])

        bin_edges = np.linspace(0.0, 1.0, self.n_bins + 1)
        ece = 0.0
        total = len(probs)

        for i in range(self.n_bins):
            mask = (probs >= bin_edges[i]) & (probs < bin_edges[i + 1])
            count = mask.sum()
            if count > 0:
                freq = probs[mask].mean()
                acc = outcomes[mask].mean()
                ece += (count / total) * abs(freq - acc)

        return ece

    def reset(self):
        self.history = []


class BucketedCalibration:
    """
    分桶校准表

    将预测按概率区间分桶，报告每个桶的：
    - 预测概率范围
    - 样本数
    - 平均预测概率
    - 实际胜率
    - 校准误差
    """

    name = "BucketedCalibration"

    def __init__(self, n_bins: int = 10):
        self.n_bins = n_bins
        self.history = []

    def add(self, predicted_prob: float, actual_outcome: bool):
        self.history.append((predicted_prob, 1.0 if actual_outcome else 0.0))

    def table(self) -> pd.DataFrame:
        """生成校准表格"""
        if not self.history:
            return pd.DataFrame()

        probs = np.array([p for p, _ in self.history])
        outcomes = np.array([y for _, y in self.history])

        bin_edges = np.linspace(0.0, 1.0, self.n_bins + 1)
        rows = []

        for i in range(self.n_bins):
            mask = (probs >= bin_edges[i]) & (probs < bin_edges[i + 1])
            count = mask.sum()
            if count > 0:
                avg_prob = probs[mask].mean()
                actual_freq = outcomes[mask].mean()
            else:
                avg_prob = (bin_edges[i] + bin_edges[i + 1]) / 2
                actual_freq = 0.0

            rows.append(
                {
                    "bin_range": f"[{bin_edges[i]:.1f}, {bin_edges[i+1]:.1f})",
                    "n_samples": count,
                    "avg_predicted": round(avg_prob, 4),
                    "actual_frequency": round(actual_freq, 4),
                    "calibration_error": round(abs(avg_prob - actual_freq), 4),
                }
            )

        return pd.DataFrame(rows)

    def reset(self):
        self.history = []


from .aggregator import AggregatorBase


class CalibrationValidator:
    """
    综合校准验证器

    在标注链数据集上执行完整校准验证：
    1. 对每条链运行各聚合器
    2. 收集 (predicted_prob, actual_outcome) 对
    3. 计算 Brier Score、ECE、可靠性图、分桶校准表
    4. 分析不同跳数下的胜率衰减趋势
    """

    name = "CalibrationValidator"

    def __init__(self, n_bins: int = 10):
        self.n_bins = n_bins
        self.results = {}

    def validate(
        self,
        chains: List[Dict],
        aggregator_name: str,
        aggregator,
    ) -> Dict:
        """
        对标注链数据执行完整校准验证

        Args:
            chains: 标注链列表，每条链包含 hops 和 label
            aggregator_name: 聚合器名称
            aggregator: 聚合器实例

        Returns:
            包含所有校准指标的字典
        """
        brier = BrierScore()
        reliability = ReliabilityDiagram(n_bins=self.n_bins)
        bucketed = BucketedCalibration(n_bins=self.n_bins)

        hop1_preds, hop1_labels = [], []
        hop2_preds, hop2_labels = [], []
        hop3_preds, hop3_labels = [], []
        hop4p_preds, hop4p_labels = [], []

        results_per_hop = {}

        for chain in chains:
            hop_confidences = chain.get("confidence_per_hop", [])
            label = chain.get("label", False)

            if not hop_confidences:
                continue

            # 聚合
            mean, lower, upper = aggregator.aggregate_with_ci(hop_confidences)

            # 记录全局
            brier.add(mean, label)
            reliability.add(mean, label)
            bucketed.add(mean, label)

            # 按跳数分组
            n_hops = len(hop_confidences)
            pred_list = hop1_preds if n_hops == 1 else hop2_preds if n_hops == 2 else hop3_preds if n_hops == 3 else hop4p_preds
            label_list = hop1_labels if n_hops == 1 else hop2_labels if n_hops == 2 else hop3_labels if n_hops == 3 else hop4p_labels
            pred_list.append(mean)
            label_list.append(label)

        # 计算不同跳数的胜率
        def win_rate(preds, labels):
            if not preds:
                return None
            preds = np.array(preds)
            labels = np.array(labels)
            pred_01 = (preds > 0.5).astype(float)
            hits = (pred_01 == labels).astype(float)
            return float(hits.mean())

        for n, preds, labels in [
            (1, hop1_preds, hop1_labels),
            (2, hop2_preds, hop2_labels),
            (3, hop3_preds, hop3_labels),
            (4, hop4p_preds, hop4p_labels),
        ]:
            if preds:
                results_per_hop[f"hop_{n}"] = {
                    "n_samples": len(preds),
                    "win_rate": win_rate(preds, labels),
                    "avg_confidence": round(float(np.mean(preds)), 4),
                }

        return {
            "aggregator": aggregator_name,
            "overall": {
                "brier_score": brier.compute(),
                "brier_decomposition": brier.decompose(),
                "ece": reliability.compute_ece(),
            },
            "per_hop": results_per_hop,
        }

    def generate_report(
        self,
        chains: List[Dict],
        aggregators: Dict[str, AggregatorBase],
        output_dir: str = "data/results",
    ) -> pd.DataFrame:
        """
        对比所有聚合器并生成报告

        Returns:
            对比表格 DataFrame
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        rows = []
        reliability_plots = {}

        for name, agg in aggregators.items():
            result = self.validate(chains, name, agg)
            rows.append(
                {
                    "aggregator": name,
                    "brier_score": result["overall"]["brier_score"],
                    "ece": result["overall"]["ece"],
                    "reliability": result["overall"]["brier_decomposition"]["reliability"],
                    "resolution": result["overall"]["brier_decomposition"]["resolution"],
                    "per_hop": result["per_hop"],
                }
            )

            # 生成可靠性图
            reliability = ReliabilityDiagram(n_bins=self.n_bins)
            for chain in chains:
                hop_confidences = chain.get("confidence_per_hop", [])
                label = chain.get("label", False)
                if hop_confidences:
                    mean, _, _ = agg.aggregate_with_ci(hop_confidences)
                    reliability.add(mean, label)

            fig = reliability.plot(
                title=f"Reliability: {name}",
                save_path=f"{output_dir}/reliability_{name}.png",
            )
            plt.close(fig)
            reliability_plots[name] = f"{output_dir}/reliability_{name}.png"

        df = pd.DataFrame(rows)
        df = df.sort_values("brier_score")
        df.to_csv(f"{output_dir}/calibration_comparison.csv", index=False)

        return df
