#!/usr/bin/env python3
"""
SX-CH-001 因果链不确定性量化 - 主运行脚本

用法:
  python run.py                                    # 评估所有聚合器
  python run.py --aggregator NoisyOR               # 评估指定聚合器
  python run.py --chain "[0.9, 0.8, 0.7]" --label 1  # 单条链快速评估
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

import argparse
import json
import ast
from pathlib import Path

from src.evaluator import CausalChainEvaluator, ChainResult
from src.aggregator import get_all_aggregators


def print_result(r: ChainResult, verbose: bool = False):
    print(f"\n{'='*60}")
    print(f"Chain: {r.chain_id} | Aggregator: {r.aggregator_name}")
    print(f"{'='*60}")
    print(f"  跳数: {r.n_hops}")
    print(f"  各跳置信度: {r.hop_confidences}")
    print(f"  端到端置信度: {r.end_to_end_confidence:.4f}")
    print(f"  置信区间: [{r.ci_lower:.4f}, {r.ci_upper:.4f}]  (宽度: {r.ci_width:.4f})")
    print(f"  是否停止: {r.should_stop}  |  原因: {r.stop_reason}")
    print(f"  停止于第 {r.stop_at_hop} 跳")
    print(f"  标签: {r.label}  |  预测正确: {r.prediction_correct}")

    if verbose and r.intermediate_confidences:
        print(f"\n  中间结果:")
        for step in r.intermediate_confidences:
            print(f"    跳 {step['hop']}: conf={step['confidence']:.4f}, "
                  f"CI=[{step['ci_lower']:.4f}, {step['ci_upper']:.4f}]")


def main():
    parser = argparse.ArgumentParser(description="SX-CH-001 因果链不确定性量化")
    parser.add_argument("--chain", type=str, help='JSON 格式链数据, 如 \'{"hops": [0.9, 0.8], "label": true}\'')
    parser.add_argument("--chain-json", type=str, help="链数据 JSON 文件路径")
    parser.add_argument("--input", type=str, help="标注链 CSV 文件路径")
    parser.add_argument("--output", default="data/results", help="输出目录")
    parser.add_argument(
        "--aggregator",
        default="all",
        choices=["all", "NaiveMultiplier", "LogOdds", "BayesianUpdater", "NoisyOR", "DampedMultiplier"],
        help="使用的聚合器",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细输出")
    args = parser.parse_args()

    # 单链快速评估
    if args.chain:
        chain = json.loads(args.chain)
        evaluator = CausalChainEvaluator(aggregator_name=args.aggregator if args.aggregator != "all" else "NoisyOR")

        if args.aggregator == "all":
            results = evaluator.evaluate_all_aggregators(chain)
            for name, r in results.items():
                print_result(r, verbose=args.verbose)
        else:
            r = evaluator.evaluate(chain)
            print_result(r, verbose=args.verbose)
        return

    # CSV 文件批量评估
    if args.input:
        import pandas as pd

        chains_df = pd.read_csv(args.input)

        chains = []
        for _, row in chains_df.iterrows():
            chain = {
                "chain_id": row["chain_id"],
                "hops": ast.literal_eval(row["hops"]) if isinstance(row["hops"], str) else row["hops"],
                "label": bool(row["label"]) if isinstance(row["label"], (bool, int)) else row["label"] in (True, 1, "True", "true", "1"),
                "domain": row.get("domain", "unknown"),
                "notes": row.get("notes", ""),
            }
            if "confidence_per_hop" in row:
                cph = row["confidence_per_hop"]
                chain["confidence_per_hop"] = ast.literal_eval(cph) if isinstance(cph, str) else cph
            chains.append(chain)

        print(f"加载了 {len(chains)} 条标注链")

        evaluator = CausalChainEvaluator()
        result = evaluator.run_full_validation(chains, output_dir=args.output)

        print(f"\n评估完成，结果保存至 {result['output_dir']}")
        print(f"\n{'聚合器对比':^40}")
        print(f"{'聚合器':<20} {'Brier Score':>12} {'总体胜率':>10}")
        print("-" * 44)
        for row in result["summary"]:
            print(f"{row['aggregator']:<20} {row['brier_score']:>12.4f} {row['overall_win_rate']:>10.3f}")

        best = result["summary"][0]
        print(f"\n最优: {best['aggregator']} (Brier Score = {best['brier_score']:.4f})")

        if best["brier_score"] < 0.15:
            print("达到 S 档标准 (Brier Score < 0.15)")
        elif best["brier_score"] < 0.20:
            print("达到 A 档标准 (Brier Score < 0.20)")
        return

    # 无参数时运行内置示例
    print("无参数运行，运行内置示例...\n")

    example_chains = [
        {"chain_id": "EX_001_macro", "label": True, "confidence_per_hop": [0.95, 0.88, 0.80, 0.75], "domain": "macro"},
        {"chain_id": "EX_002_commodity", "label": False, "confidence_per_hop": [0.90, 0.60], "domain": "commodity"},
        {"chain_id": "EX_003_equity", "label": True, "confidence_per_hop": [0.95, 0.85, 0.80, 0.75], "domain": "equity"},
        {"chain_id": "EX_004_forex", "label": True, "confidence_per_hop": [0.90, 0.85, 0.80], "domain": "forex"},
        {"chain_id": "EX_005_crypto", "label": False, "confidence_per_hop": [0.85, 0.70, 0.50], "domain": "crypto"},
    ]

    evaluator = CausalChainEvaluator()

    print("\n" + "="*70)
    print("所有聚合器对比（示例链）")
    print("="*70)

    all_agg_results = {}
    for agg_name in get_all_aggregators().keys():
        evaluator.aggregator_name = agg_name
        evaluator.aggregator = get_all_aggregators()[agg_name]

        agg_results = evaluator.evaluate_batch(example_chains, aggregator_name=agg_name)
        all_agg_results[agg_name] = agg_results

        from src.calibrator import BrierScore
        brier = BrierScore()
        for r in agg_results:
            brier.add(r.end_to_end_confidence, r.label)
        print(f"  {agg_name:<20}: Brier Score = {brier.compute():.4f}")

    print("\n详细结果（NoisyOR 聚合器）:")
    evaluator = CausalChainEvaluator(aggregator_name="NoisyOR")
    for chain in example_chains:
        r = evaluator.evaluate(chain)
        print_result(r, verbose=True)


if __name__ == "__main__":
    main()
