#!/usr/bin/env python3
"""跑完整评估 + 生成报告"""

import sys, os, ast
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
import numpy as np

# Load chains
df = pd.read_csv("data/annotated_chains.csv")
chains = []
for _, row in df.iterrows():
    chain = {
        "chain_id": row["chain_id"],
        "hops": ast.literal_eval(row["hops"]),
        "label": row["label"] in ("True", True, "true"),
        "domain": row["domain"],
        "notes": row["notes"],
        "confidence_per_hop": ast.literal_eval(row["confidence_per_hop"]),
    }
    chains.append(chain)

print(f"Loaded {len(chains)} chains")

from src.evaluator import CausalChainEvaluator
from src.calibrator import BrierScore, ReliabilityDiagram, BucketedCalibration
from src.aggregator import get_all_aggregators

np.random.seed(42)
evaluator = CausalChainEvaluator()

print("\n=== Aggregator Comparison on 50 Synthetic Chains ===")
results_by_agg = {}

for agg_name in ["NaiveMultiplier", "LogOdds", "BayesianUpdater", "NoisyOR", "DampedMultiplier"]:
    evaluator.aggregator_name = agg_name
    evaluator.aggregator = get_all_aggregators()[agg_name]

    chain_results = evaluator.evaluate_batch(chains)
    brier = BrierScore()
    for r in chain_results:
        brier.add(r.end_to_end_confidence, r.label)

    bs = brier.compute()
    dec = brier.decompose()

    # Per-hop win rates
    hop_groups = {2: [], 3: [], 4: [], 5: []}
    for r in chain_results:
        n = min(r.n_hops, 5)
        hop_groups[n].append(r)

    hop_stats = {}
    for n, group in hop_groups.items():
        if group:
            correct = sum(1 for r in group if r.prediction_correct)
            avg_conf = np.mean([r.end_to_end_confidence for r in group])
            hop_stats[f"{n}hop"] = {
                "n": len(group),
                "win_rate": round(correct / len(group), 3),
                "avg_conf": round(avg_conf, 3),
            }

    results_by_agg[agg_name] = {
        "brier": bs,
        "dec": dec,
        "hop_stats": hop_stats,
        "results": chain_results,
    }
    rel = dec["reliability"]
    print(f"  {agg_name:<20} Brier={bs:.4f}  Reliability={rel:.4f}")

# Best
best = min(results_by_agg.items(), key=lambda x: x[1]["brier"])
print(f"\nBest aggregator: {best[0]} (Brier={best[1]['brier']:.4f})")
if best[1]["brier"] < 0.15:
    print("==> S档标准达成 (Brier < 0.15)")
elif best[1]["brier"] < 0.20:
    print("==> A档标准达成 (Brier < 0.20)")
else:
    print("==> 未达A档标准，需进一步优化")

print("\n=== Per-Hop Win Rate Trend ===")
for agg_name, data in sorted(results_by_agg.items(), key=lambda x: x[1]["brier"]):
    hops_line = "  ".join(
        f"{k}:{v['win_rate']:.2f}(n={v['n']})"
        for k, v in sorted(data["hop_stats"].items())
    )
    print(f"  {agg_name:<20}: {hops_line}")

print("\n=== Baseline Comparison (NaiveMultiplier) ===")
naive_brier = results_by_agg["NaiveMultiplier"]["brier"]
for agg_name, data in results_by_agg.items():
    diff = data["brier"] - naive_brier
    arrow = "BETTER" if diff < 0 else "WORSE"
    print(f"  {agg_name:<20}: Brier={data['brier']:.4f}  vs Naive {arrow} {abs(diff):.4f}")

print("\n=== Generating full validation report ===")
result = evaluator.run_full_validation(chains, output_dir="data/results")
print(f"\nReport saved to: {result['output_dir']}")

print("\nFinal summary:")
for row in result["summary"]:
    print(f"  {row['aggregator']:<20} Brier={row['brier_score']:.4f}")

print("\n--- All done ---")
