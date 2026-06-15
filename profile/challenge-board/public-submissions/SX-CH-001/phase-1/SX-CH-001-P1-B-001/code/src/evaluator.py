"""
端到端评估器：整合聚合器 + 停止准则 + 校准验证

这是用户的主要入口模块。给定一条因果链：
1. 使用选定的聚合器计算端到端置信度
2. 使用停止准则决定是否继续推理
3. 输出结构化结果
"""

import json
import pandas as pd
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import numpy as np

from .aggregator import (
    NaiveMultiplier,
    LogOddsAggregator,
    BayesianUpdater,
    NoisyOR,
    DampedMultiplier,
    get_all_aggregators,
)
from .stopping import (
    StoppingCriteria,
    CompositeStopper,
    MaxHopStopper,
    CIWidthStopper,
    InfoGainStopper,
    FloorConfidenceStopper,
    get_default_stopper,
)
from .calibrator import CalibrationValidator, BrierScore


@dataclass
class ChainResult:
    """单条因果链的评估结果"""

    chain_id: str
    aggregator_name: str
    n_hops: int

    # 置信度
    end_to_end_confidence: float
    ci_lower: float
    ci_upper: float
    ci_width: float

    # 停止判断
    should_stop: bool
    stop_reason: str
    stop_at_hop: int

    # 中间量
    hop_confidences: List[float]
    intermediate_confidences: List[float] = field(default_factory=list)

    # 标签
    label: bool = False
    prediction_correct: bool = False

    def to_dict(self) -> Dict:
        return asdict(self)


class CausalChainEvaluator:
    """
    端到端因果链评估器

    用法：
    ```python
    evaluator = CausalChainEvaluator(aggregator_name="NoisyOR")
    result = evaluator.evaluate(chain_data)
    print(result.end_to_end_confidence)
    print(result.should_stop, result.stop_reason)
    ```
    """

    AGGREGATOR_MAP = {
        "NaiveMultiplier": NaiveMultiplier,
        "LogOdds": LogOddsAggregator,
        "BayesianUpdater": BayesianUpdater,
        "NoisyOR": NoisyOR,
        "DampedMultiplier": DampedMultiplier,
    }

    def __init__(
        self,
        aggregator_name: str = "NoisyOR",
        stopping_criteria: Optional[StoppingCriteria] = None,
        n_samples: int = 10000,
    ):
        """
        Args:
            aggregator_name: 聚合器名称（NaiveMultiplier/LogOdds/BayesianUpdater/NoisyOR/DampedMultiplier）
            stopping_criteria: 停止准则，默认使用组合准则
            n_samples: 蒙特卡洛采样次数（用于 CI 计算）
        """
        self.aggregator_name = aggregator_name
        agg_cls = self.AGGREGATOR_MAP.get(aggregator_name, NoisyOR)
        self.aggregator = agg_cls()
        self.stopping = stopping_criteria or get_default_stopper()
        self.n_samples = n_samples

    def evaluate(
        self,
        chain: Dict,
        return_intermediate: bool = True,
    ) -> ChainResult:
        """
        对单条因果链进行端到端评估

        Args:
            chain: 因果链数据，包含 hops, label, confidence_per_hop 等字段
            return_intermediate: 是否返回中间跳的置信度

        Returns:
            ChainResult
        """
        chain_id = chain.get("chain_id", "unknown")
        hop_confidences = chain.get("confidence_per_hop", [])
        label = chain.get("label", False)

        if not hop_confidences:
            return ChainResult(
                chain_id=chain_id,
                aggregator_name=self.aggregator_name,
                n_hops=0,
                end_to_end_confidence=0.0,
                ci_lower=0.0,
                ci_upper=0.0,
                ci_width=0.0,
                should_stop=True,
                stop_reason="No hops provided",
                stop_at_hop=0,
                hop_confidences=[],
                label=label,
                prediction_correct=False,
            )

        # 逐跳评估 + 停止判断
        intermediate = []
        should_stop = False
        stop_reason = ""
        stop_at_hop = len(hop_confidences)

        for i in range(1, len(hop_confidences) + 1):
            current_hops = hop_confidences[:i]
            mean, lower, upper = self.aggregator.aggregate_with_ci(
                current_hops, n_samples=self.n_samples
            )

            if return_intermediate:
                intermediate.append({
                    "hop": i,
                    "confidence": mean,
                    "ci_lower": lower,
                    "ci_upper": upper,
                })

            stop, reason = self.stopping.should_stop(
                current_hops, mean, (lower, upper), i - 1
            )

            if stop:
                should_stop = True
                stop_reason = reason
                stop_at_hop = i
                break

        # 最终置信度
        if intermediate:
            final = intermediate[-1]
            end_conf = final["confidence"]
            ci_lower = final["ci_lower"]
            ci_upper = final["ci_upper"]
        else:
            mean, ci_lower, ci_upper = self.aggregator.aggregate_with_ci(
                hop_confidences, n_samples=self.n_samples
            )
            end_conf = mean
            stop_at_hop = len(hop_confidences)

        return ChainResult(
            chain_id=chain_id,
            aggregator_name=self.aggregator_name,
            n_hops=len(hop_confidences),
            end_to_end_confidence=end_conf,
            ci_lower=ci_lower,
            ci_upper=ci_upper,
            ci_width=ci_upper - ci_lower,
            should_stop=should_stop,
            stop_reason=stop_reason,
            stop_at_hop=stop_at_hop,
            hop_confidences=hop_confidences,
            intermediate_confidences=intermediate,
            label=label,
            prediction_correct=(end_conf > 0.5) == label,
        )

    def evaluate_batch(
        self,
        chains: List[Dict],
        aggregator_name: Optional[str] = None,
    ) -> List[ChainResult]:
        """
        批量评估多条因果链

        Args:
            chains: 因果链列表
            aggregator_name: 可选，覆盖初始化时的聚合器

        Returns:
            ChainResult 列表
        """
        if aggregator_name and aggregator_name != self.aggregator_name:
            agg_cls = self.AGGREGATOR_MAP.get(aggregator_name, NoisyOR)
            self.aggregator = agg_cls()

        return [self.evaluate(chain) for chain in chains]

    def evaluate_all_aggregators(
        self,
        chain: Dict,
    ) -> Dict[str, ChainResult]:
        """
        对单条链评估所有聚合器并比较结果
        """
        results = {}
        for name in self.AGGREGATOR_MAP:
            agg_cls = self.AGGREGATOR_MAP[name]
            self.aggregator = agg_cls()
            results[name] = self.evaluate(chain)
        return results

    def run_full_validation(
        self,
        chains: List[Dict],
        output_dir: Optional[str] = None,
    ) -> Dict:
        """
        在标注数据集上运行完整校准验证

        Args:
            chains: 标注链列表
            output_dir: 可选，结果输出目录

        Returns:
            验证结果字典
        """
        output_dir = Path(output_dir) if output_dir else Path("data/results")
        output_dir.mkdir(parents=True, exist_ok=True)

        summary_rows = []

        for agg_name, agg_cls in self.AGGREGATOR_MAP.items():
            self.aggregator = agg_cls()
            self.aggregator_name = agg_name

            results = self.evaluate_batch(chains)
            brier = BrierScore()

            hop_groups = {1: [], 2: [], 3: [], 4: []}
            for r in results:
                brier.add(r.end_to_end_confidence, r.label)
                n = min(r.n_hops, 4)
                hop_groups[n].append(r)

            # 不同跳数的胜率
            hop_win_rates = {}
            for n, group in hop_groups.items():
                if group:
                    correct = sum(1 for r in group if r.prediction_correct)
                    avg_conf = np.mean([r.end_to_end_confidence for r in group])
                    hop_win_rates[f"hop_{n}"] = {
                        "n": len(group),
                        "win_rate": round(correct / len(group), 4),
                        "avg_confidence": round(avg_conf, 4),
                    }

            summary_rows.append(
                {
                    "aggregator": agg_name,
                    "brier_score": round(brier.compute(), 4),
                    "brier_decomposition": brier.decompose(),
                    "total_samples": len(results),
                    "overall_win_rate": round(
                        sum(1 for r in results if r.prediction_correct) / len(results), 4
                    ),
                    "per_hop": hop_win_rates,
                }
            )

        # 保存详细结果
        all_results = []
        for agg_name in self.AGGREGATOR_MAP:
            self.aggregator = self.AGGREGATOR_MAP[agg_name]()
            for chain in chains:
                r = self.evaluate(chain)
                all_results.append(r.to_dict())

        results_df = pd.DataFrame([r.to_dict() if isinstance(r, ChainResult) else r for r in all_results])
        results_df.to_csv(output_dir / "detailed_results.csv", index=False)

        summary_df = pd.DataFrame(summary_rows)
        summary_df = summary_df.sort_values("brier_score")
        summary_df.to_csv(output_dir / "summary.csv", index=False)

        # 生成报告（传入已排序的）
        report = self._make_report(summary_df.to_dict(orient="records"))
        with open(output_dir / "report.md", "w", encoding="utf-8") as f:
            f.write(report)

        return {
            "summary": summary_rows,
            "summary_df": summary_df,
            "output_dir": str(output_dir),
        }

    def _make_report(self, summary_rows: List[Dict]) -> str:
        """生成 Markdown 评估报告"""
        lines = [
            "# 因果链不确定性量化评估报告\n",
            f"## 聚合器对比\n",
            "| 聚合器 | Brier Score | 总体胜率 | 2跳胜率 | 3跳胜率 | 4+跳胜率 |",
            "|--------|------------|---------|--------|--------|--------|",
        ]

        for row in summary_rows:
            ph = row.get("per_hop", {})
            hop_rates = []
            for n in [2, 3, 4]:
                k = f"hop_{n}"
                if k in ph:
                    rate = ph[k]["win_rate"]
                    n_samp = ph[k]["n"]
                    hop_rates.append(f"{rate:.3f} (n={n_samp})")
                else:
                    hop_rates.append("N/A")
            lines.append(
                f"| {row['aggregator']} | {row['brier_score']:.4f} | "
                f"{row['overall_win_rate']:.3f} | "
                + " | ".join(hop_rates)
                + " |"
            )

        lines.append("\n## 结论\n")
        best = summary_rows[0]
        lines.append(f"**最优聚合器**: {best['aggregator']}（Brier Score = {best['brier_score']:.4f}）\n")

        if best["brier_score"] < 0.15:
            lines.append("达到 S 档标准（Brier Score < 0.15）\n")
        elif best["brier_score"] < 0.20:
            lines.append("达到 A 档标准（Brier Score < 0.20）\n")
        else:
            lines.append("未达到 A 档标准，需要进一步优化\n")

        return "\n".join(lines)


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="因果链不确定性量化评估")
    parser.add_argument("--input", required=True, help="标注链 CSV 文件路径")
    parser.add_argument("--output", default="data/results", help="结果输出目录")
    parser.add_argument(
        "--aggregator",
        default="all",
        choices=["all", "NaiveMultiplier", "LogOdds", "BayesianUpdater", "NoisyOR", "DampedMultiplier"],
        help="使用的聚合器",
    )
    args = parser.parse_args()

    # 读取数据
    chains_df = pd.read_csv(args.input)

    # 转换为链字典列表
    chains = []
    for _, row in chains_df.iterrows():
        import ast
        chain = {
            "chain_id": row["chain_id"],
            "hops": ast.literal_eval(row["hops"]),
            "label": row["label"],
            "domain": row["domain"],
            "notes": row["notes"],
        }
        if "confidence_per_hop" in row:
            chain["confidence_per_hop"] = ast.literal_eval(row["confidence_per_hop"])
        elif "hop_confidences" in row:
            chain["confidence_per_hop"] = ast.literal_eval(row["hop_confidences"])
        chains.append(chain)

    # 评估
    evaluator = CausalChainEvaluator()

    if args.aggregator == "all":
        result = evaluator.run_full_validation(chains, output_dir=args.output)
        print(f"评估完成，结果保存至 {result['output_dir']}")
        print("\n最优聚合器:", result["summary"][0]["aggregator"])
        print("Brier Score:", result["summary"][0]["brier_score"])
    else:
        evaluator.aggregator_name = args.aggregator
        aggregator = evaluator.AGGREGATOR_MAP[args.aggregator]()
        evaluator.aggregator = aggregator
        results = evaluator.evaluate_batch(chains)
        brier = BrierScore()
        for r in results:
            brier.add(r.end_to_end_confidence, r.label)
        print(f"Brier Score: {brier.compute():.4f}")


if __name__ == "__main__":
    main()
