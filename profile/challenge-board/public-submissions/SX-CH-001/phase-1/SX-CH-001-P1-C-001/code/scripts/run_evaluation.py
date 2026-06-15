#!/usr/bin/env python3
"""Batch evaluation entry point.

Loads synthetic chains, runs all aggregators, and produces the full
calibration report required by the SX-CH-001 challenge.
"""

import sys
import json
import os
import argparse
from pathlib import Path

import numpy as np
import yaml

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from src.chain import CausalChain
from src.pipeline import CausalChainPipeline


def resolve_path(path: str) -> str:
    p = Path(path)
    if p.is_absolute():
        return str(p)
    return str(PROJECT_ROOT / p)


def load_config(config_path: str) -> dict:
    with open(resolve_path(config_path), "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_chains(data_path: str) -> list[CausalChain]:
    with open(resolve_path(data_path), "r", encoding="utf-8") as f:
        data = json.load(f)
    return [CausalChain.from_dict(d) for d in data]


def main():
    parser = argparse.ArgumentParser(
        description="SX-CH-001 Batch Evaluation"
    )
    parser.add_argument(
        "-c", "--config", default="config/default_config.yaml",
        help="Path to config file"
    )
    parser.add_argument(
        "-d", "--data", default="data/synthetic_chains.json",
        help="Path to synthetic chains JSON"
    )
    parser.add_argument(
        "-o", "--output-dir", default="outputs",
        help="Output directory for reports"
    )
    parser.add_argument(
        "--no-stopping", action="store_true",
        help="Disable stopping criteria"
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed"
    )
    args = parser.parse_args()

    np.random.seed(args.seed)

    # Load
    config = load_config(args.config)
    chains = load_chains(args.data)
    print(f"Loaded {len(chains)} chains from {args.data}")
    print(f"Hop distribution: min={min(c.n_hops for c in chains)}, "
          f"max={max(c.n_hops for c in chains)}, "
          f"mean={np.mean([c.n_hops for c in chains]):.1f}")
    print(f"Ground truth prevalence: "
          f"{np.mean([1 if c.ground_truth else 0 for c in chains]):.3f}")

    # Run pipeline
    pipeline = CausalChainPipeline(config)
    results, report = pipeline.run(chains, apply_stopping=not args.no_stopping)

    # Save
    output_dir = resolve_path(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    report_path = os.path.join(output_dir, "evaluation_report.json")
    report.save(report_path)
    print(f"\nReport saved to {report_path}")

    # Save per-chain results for audit
    results_dict = {}
    for method, method_results in results.items():
        results_dict[method] = [r.to_dict() for r in method_results]
    results_path = os.path.join(output_dir, "per_chain_results.json")
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results_dict, f, indent=2, ensure_ascii=False)
    print(f"Per-chain results saved to {results_path}")

    # Print summary
    print()
    report.print_summary()

    # Tier assessment
    best_brier = min(m.brier_score for m in report.method_comparisons)
    print(f"\n{'=' * 70}")
    print("Tier Assessment")
    print(f"{'=' * 70}")
    if best_brier < 0.15:
        print(f"Brier Score {best_brier:.4f} < 0.15 -> S-TIER threshold met")
    elif best_brier < 0.20:
        print(f"Brier Score {best_brier:.4f} < 0.20 -> A-TIER threshold met")
        print(f"Gap to S-tier: {best_brier - 0.15:.4f}")
    else:
        print(f"Brier Score {best_brier:.4f} >= 0.20 -> Below A-tier threshold")

    return 0


if __name__ == "__main__":
    sys.exit(main())
