"""Evaluation report generation.

Produces the required deliverables:
1. Brier Score comparison across methods
2. Reliability diagram data (binned calibration table)
3. Win-rate trend by hop count
4. Baseline vs proposed method comparison
5. Failure case analysis
"""

from dataclasses import dataclass, field
from typing import Optional
import json

import numpy as np
from .chain import AggregationResult
from .calibration import CalibrationMetrics


@dataclass
class MethodComparison:
    method: str
    brier_score: float
    ece: float
    mean_confidence: float
    accuracy: float  # how often high-confidence predictions match outcomes
    ci_coverage: float  # how often true outcome falls within CI

    def to_dict(self) -> dict:
        return {
            "method": self.method,
            "brier_score": self.brier_score,
            "ece": self.ece,
            "mean_confidence": self.mean_confidence,
            "accuracy": self.accuracy,
            "ci_coverage": self.ci_coverage,
        }


@dataclass
class HopCountTrend:
    """Win-rate (actual frequency of outcome) by hop count."""

    entries: list[dict] = field(default_factory=list)  # {n_hops, n_samples, win_rate, mean_conf}

    def to_dict(self) -> dict:
        return {"entries": self.entries}


@dataclass
class EvaluationReport:
    method_comparisons: list[MethodComparison]
    hop_count_trend: HopCountTrend
    calibration_by_method: dict[str, CalibrationMetrics]
    best_method: str
    summary: str
    failure_cases: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "method_comparisons": [m.to_dict() for m in self.method_comparisons],
            "hop_count_trend": self.hop_count_trend.to_dict(),
            "calibration_by_method": {
                k: v.to_dict() for k, v in self.calibration_by_method.items()
            },
            "best_method": self.best_method,
            "summary": self.summary,
            "failure_cases": self.failure_cases,
        }

    def save(self, path: str):
        import os
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        # Also save reliability diagram
        png_path = path.replace(".json", "_reliability.png")
        self._save_reliability_diagram(png_path)

    def _save_reliability_diagram(self, path: str):
        """Render reliability diagram as PNG."""
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            n_methods = len(self.calibration_by_method)
            if n_methods == 0:
                return
            cols = min(2, n_methods)
            rows = (n_methods + cols - 1) // cols
            fig, axes = plt.subplots(rows, cols, figsize=(6 * cols, 5 * rows))
            if n_methods == 1:
                axes = [axes]
            elif rows == 1:
                axes = axes.flatten()
            else:
                axes = axes.flatten() if hasattr(axes, "flatten") else axes

            for idx, (method, cal) in enumerate(self.calibration_by_method.items()):
                ax = axes[idx] if idx < len(axes) else axes[-1]
                bin_conf = cal.bin_confidences
                bin_freq = cal.bin_frequencies
                bin_counts = cal.bin_counts

                # Perfect calibration line
                ax.plot([0, 1], [0, 1], "k--", alpha=0.3, label="Perfect calibration")

                # Reliability curve (bubble size = sample count)
                if bin_conf and bin_freq and bin_counts:
                    sizes = [max(20, c * 3) for c in bin_counts]
                    ax.scatter(bin_conf, bin_freq, s=sizes, alpha=0.7, c="steelblue",
                              edgecolors="navy", linewidth=0.5, zorder=5)

                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.set_xlabel("Predicted confidence")
                ax.set_ylabel("Observed frequency")
                ax.set_title(f"{method}\nBrier={cal.brier_score:.4f}  ECE={cal.ece:.4f}")
                ax.legend(loc="upper left", fontsize=8)
                ax.set_aspect("equal")
                ax.grid(True, alpha=0.2)

            # Hide unused axes
            for idx in range(n_methods, len(axes)):
                axes[idx].set_visible(False)

            plt.tight_layout()
            plt.savefig(path, dpi=120, bbox_inches="tight")
            plt.close()
            print(f"Reliability diagram saved to {path}")
        except Exception as e:
            print(f"Could not render reliability diagram: {e}")

    def print_summary(self):
        print("=" * 70)
        print("SX-CH-001 Evaluation Report")
        print("=" * 70)
        print(f"\nBest method: {self.best_method}\n")
        print(f"{'Method':<25} {'Brier':>8} {'ECE':>8} {'MeanConf':>8} {'CICov':>8}")
        print("-" * 57)
        for mc in self.method_comparisons:
            print(
                f"{mc.method:<25} {mc.brier_score:>8.4f} {mc.ece:>8.4f} "
                f"{mc.mean_confidence:>8.4f} {mc.ci_coverage:>8.4f}"
            )
        print("-" * 57)

        # Hop count trend
        if self.hop_count_trend.entries:
            print(f"\nHop count win-rate trend:")
            print(f"{'Hops':>5} {'Samples':>8} {'WinRate':>10} {'MeanConf':>10}")
            print("-" * 38)
            for e in self.hop_count_trend.entries:
                print(
                    f"{e['n_hops']:>5} {e['n_samples']:>8} "
                    f"{e['win_rate']:>10.4f} {e['mean_conf']:>10.4f}"
                )
            print("-" * 38)

        # Summary
        print(f"\n{self.summary}")

        if self.failure_cases:
            print(f"\nFailure cases ({len(self.failure_cases)}):")
            for fc in self.failure_cases[:5]:
                print(f"  {fc['chain_id']}: {fc['reason']}")


class ReportGenerator:
    """Generates the full evaluation report."""

    def generate(
        self,
        results_by_method: dict[str, list[AggregationResult]],
        ground_truths: np.ndarray,
        chain_n_hops: np.ndarray,
        calibration_by_method: dict[str, CalibrationMetrics],
        failure_cases: list[dict] | None = None,
        calibrated_results: dict[str, np.ndarray] | None = None,
    ) -> EvaluationReport:
        method_comparisons = []
        best_method = ""
        best_brier = float("inf")

        for method, results in results_by_method.items():
            confidences = np.array([r.final_confidence for r in results])

            # CI coverage
            ci_hits = 0
            for r, gt in zip(results, ground_truths):
                lower, upper = r.confidence_interval
                if lower <= r.final_confidence <= upper:
                    ci_hits += 1
            ci_coverage = ci_hits / max(len(results), 1)

            mc = MethodComparison(
                method=method,
                brier_score=calibration_by_method[method].brier_score,
                ece=calibration_by_method[method].ece,
                mean_confidence=float(np.mean(confidences)),
                accuracy=float(np.mean((confidences > 0.5) == (ground_truths > 0.5))),
                ci_coverage=ci_coverage,
            )
            method_comparisons.append(mc)

            if mc.brier_score < best_brier:
                best_brier = mc.brier_score
                best_method = method

        # Hop count trend
        trend = HopCountTrend()
        best_results = results_by_method[best_method]
        unique_hops = sorted(set(chain_n_hops))
        for nh in unique_hops:
            mask = chain_n_hops == nh
            n_samples = mask.sum()
            if n_samples > 0:
                # Per-hop-count mean confidence
                hop_confs = [best_results[i].final_confidence
                            for i in range(len(best_results)) if mask[i]]
                trend.entries.append({
                    "n_hops": int(nh),
                    "n_samples": int(n_samples),
                    "win_rate": float(ground_truths[mask].mean()),
                    "mean_conf": float(np.mean(hop_confs)),
                })

        # Summary
        best_mc = [m for m in method_comparisons if m.method == best_method][0]
        summary = (
            f"Best method '{best_method}' achieves Brier Score {best_mc.brier_score:.4f}, "
            f"ECE {best_mc.ece:.4f}. "
        )
        if best_mc.brier_score < 0.15:
            summary += "Meets S-tier threshold (Brier < 0.15). "
        elif best_mc.brier_score < 0.20:
            summary += "Meets A-tier threshold (Brier < 0.20). "
        else:
            summary += "Does not yet meet A-tier threshold. "

        # Check win-rate decay via Spearman correlation with hop count
        if len(trend.entries) >= 4:
            from scipy.stats import spearmanr
            hops_arr = [e["n_hops"] for e in trend.entries]
            rates_arr = [e["win_rate"] for e in trend.entries]
            rho, _p = spearmanr(hops_arr, rates_arr)
            if rho < -0.7:
                summary += (
                    f" Strong win-rate decay confirmed (Spearman rho={rho:.2f}): "
                    "win rate decreases as hop count increases."
                )
            elif rho < -0.3:
                summary += (
                    f" Moderate win-rate decay (Spearman rho={rho:.2f}). "
                )
            else:
                summary += " Win-rate decay trend not monotonic; check calibration."

        return EvaluationReport(
            method_comparisons=method_comparisons,
            hop_count_trend=trend,
            calibration_by_method=calibration_by_method,
            best_method=best_method,
            summary=summary,
            failure_cases=failure_cases or [],
        )
