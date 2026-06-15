"""Parameter sensitivity analysis for SX-CH-001.

Varies key hyperparameters and measures their effect on Brier score.
Outputs a sensitivity report showing which parameters matter most.
"""

import sys
import json
import os
import argparse
from pathlib import Path
from copy import deepcopy

import numpy as np
import yaml

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from src.chain import CausalChain
from src.pipeline import CausalChainPipeline


def resolve_path(path: str) -> str:
    p = Path(path)
    return str(p if p.is_absolute() else PROJECT_ROOT / p)


def load_config(path: str) -> dict:
    with open(resolve_path(path), "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_chains(path: str) -> list[CausalChain]:
    with open(resolve_path(path), "r", encoding="utf-8") as f:
        return [CausalChain.from_dict(d) for d in json.load(f)]


def run_sensitivity(
    base_config: dict,
    chains: list[CausalChain],
    param_path: str,
    values: list[float],
    param_label: str,
) -> list[dict]:
    """Run pipeline for each parameter value, return Brier scores."""
    results = []
    for val in values:
        cfg = deepcopy(base_config)
        # Navigate to nested key
        keys = param_path.split(".")
        target = cfg
        for k in keys[:-1]:
            target = target[k]
        target[keys[-1]] = val

        pipeline = CausalChainPipeline(cfg)
        _, report = pipeline.run(chains, apply_stopping=False)
        brier = min(m.brier_score for m in report.method_comparisons)
        results.append({
            "param": param_label,
            "value": val,
            "best_brier": brier,
            "best_method": report.best_method,
        })
    return results


def main():
    parser = argparse.ArgumentParser(description="SX-CH-001 Sensitivity Analysis")
    parser.add_argument("-c", "--config", default="config/default_config.yaml")
    parser.add_argument("-d", "--data", default="data/synthetic_chains.json")
    parser.add_argument("-o", "--output", default="outputs/sensitivity_report.json")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    np.random.seed(args.seed)
    config = load_config(args.config)
    chains = load_chains(args.data)
    print(f"Loaded {len(chains)} chains for sensitivity analysis\n")

    # Parameter sweep definitions
    sweeps = [
        {
            "path": "aggregators.bayesian.prior_belief",
            "label": "Bayesian prior_belief",
            "values": [0.15, 0.25, 0.35, 0.45, 0.55, 0.65],
        },
        {
            "path": "aggregators.bayesian.likelihood_strength",
            "label": "Bayesian likelihood_strength",
            "values": [0.20, 0.35, 0.50, 0.70, 0.85, 1.00],
        },
        {
            "path": "aggregators.logit.correlation_penalty",
            "label": "Logit correlation_penalty",
            "values": [0.00, 0.05, 0.10, 0.15, 0.20, 0.30, 0.50],
        },
        {
            "path": "aggregators.logit.prior_weight",
            "label": "Logit prior_weight",
            "values": [0.2, 0.5, 1.0, 1.5, 2.0, 3.0],
        },
        {
            "path": "stopping.confidence_floor",
            "label": "Stopping confidence_floor",
            "values": [0.02, 0.05, 0.10, 0.15, 0.20, 0.30],
        },
        {
            "path": "stopping.ci_width_threshold",
            "label": "Stopping CI width threshold",
            "values": [0.15, 0.25, 0.35, 0.45, 0.55, 0.65],
        },
    ]

    all_results = {}
    for sweep in sweeps:
        print(f"Testing {sweep['label']}: ", end="", flush=True)
        results = run_sensitivity(
            config, chains, sweep["path"], sweep["values"], sweep["label"]
        )
        all_results[sweep["label"]] = results
        briers = [r["best_brier"] for r in results]
        best_val = sweep["values"][np.argmin(briers)]
        print(f"best={best_val}, Brier range=[{min(briers):.4f}, {max(briers):.4f}]")

    # Sensitivity summary
    print(f"\n{'='*70}")
    print("Sensitivity Summary (Brier range = max - min across parameter sweep)")
    print(f"{'='*70}")
    print(f"{'Parameter':<35} {'Range':>10} {'Impact'}")
    print("-" * 60)
    sensitivities = []
    for label, results in all_results.items():
        briers = [r["best_brier"] for r in results]
        brier_range = max(briers) - min(briers)
        sensitivity = "HIGH" if brier_range > 0.03 else ("MEDIUM" if brier_range > 0.01 else "LOW")
        sensitivities.append((label, brier_range, sensitivity))
        print(f"{label:<35} {brier_range:>10.4f}  {sensitivity}")
    print("-" * 60)

    # Key finding
    high_impact = [s for s in sensitivities if s[2] == "HIGH"]
    if high_impact:
        print(f"\nMost sensitive parameters ({len(high_impact)} HIGH impact):")
        for label, rng, _ in high_impact:
            print(f"  - {label} (Brier range: {rng:.4f})")
        print("\nRecommendation: tune these parameters on a validation set for best results.")
    else:
        print("\nNo single parameter dominates. The ensemble method provides the most robust calibration.")

    # Save
    os.makedirs(os.path.dirname(resolve_path(args.output)), exist_ok=True)
    with open(resolve_path(args.output), "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\nFull results saved to {args.output}")


if __name__ == "__main__":
    main()
