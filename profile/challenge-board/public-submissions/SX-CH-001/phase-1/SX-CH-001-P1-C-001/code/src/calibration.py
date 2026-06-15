"""Calibration validation for confidence estimates.

Measures how well predicted confidences align with actual outcome frequencies.
A well-calibrated model: predicted 0.7 confidence means ~70% of such predictions are correct.
"""

from dataclasses import dataclass
import numpy as np
from scipy.stats import binned_statistic


@dataclass
class CalibrationMetrics:
    brier_score: float
    ece: float  # Expected Calibration Error
    mce: float  # Maximum Calibration Error
    num_samples: int
    bin_edges: list[float]
    bin_confidences: list[float]  # mean predicted confidence per bin
    bin_frequencies: list[float]  # observed frequency per bin
    bin_counts: list[int]
    reliability_slope: float
    reliability_intercept: float

    def to_dict(self) -> dict:
        return {
            "brier_score": self.brier_score,
            "ece": self.ece,
            "mce": self.mce,
            "num_samples": self.num_samples,
            "bin_edges": self.bin_edges,
            "bin_confidences": self.bin_confidences,
            "bin_frequencies": self.bin_frequencies,
            "bin_counts": self.bin_counts,
            "reliability_slope": self.reliability_slope,
            "reliability_intercept": self.reliability_intercept,
        }


class CalibrationEvaluator:
    """Evaluate calibration of confidence predictions against ground truth."""

    def __init__(self, num_bins: int = 10, min_samples_per_bin: int = 5):
        self.num_bins = num_bins
        self.min_samples_per_bin = min_samples_per_bin

    def evaluate(
        self, confidences: np.ndarray, ground_truths: np.ndarray
    ) -> CalibrationMetrics:
        """
        Args:
            confidences: Predicted confidence values [0, 1], shape (N,)
            ground_truths: Binary outcomes {0, 1}, shape (N,)
        """
        confidences = np.asarray(confidences, dtype=float)
        ground_truths = np.asarray(ground_truths, dtype=float)
        n = len(confidences)

        # Brier Score: (1/N) * sum((p_i - o_i)^2)
        brier = float(np.mean((confidences - ground_truths) ** 2))

        # Binned calibration
        bins = np.linspace(0, 1, self.num_bins + 1)
        bin_indices = np.digitize(confidences, bins) - 1
        bin_indices = np.clip(bin_indices, 0, self.num_bins - 1)

        bin_confidences = []
        bin_frequencies = []
        bin_counts = []
        bin_edges = []

        for i in range(self.num_bins):
            mask = bin_indices == i
            count = mask.sum()
            if count >= self.min_samples_per_bin:
                bin_confidences.append(float(confidences[mask].mean()))
                bin_frequencies.append(float(ground_truths[mask].mean()))
                bin_counts.append(int(count))
                bin_edges.append(float(bins[i]))

        # ECE: weighted average of |confidence - frequency|
        ece = 0.0
        mce = 0.0
        total = sum(bin_counts)
        for conf, freq, cnt in zip(bin_confidences, bin_frequencies, bin_counts):
            ece += (cnt / total) * abs(conf - freq)
            mce = max(mce, abs(conf - freq))

        # Reliability regression: frequency ~ a * confidence + b
        if len(bin_confidences) >= 2:
            bc = np.array(bin_confidences)
            bf = np.array(bin_frequencies)
            # Simple linear regression
            A = np.vstack([bc, np.ones_like(bc)]).T
            slope, intercept = np.linalg.lstsq(A, bf, rcond=None)[0]
        else:
            slope, intercept = 0.0, 0.0

        return CalibrationMetrics(
            brier_score=brier,
            ece=ece,
            mce=mce,
            num_samples=n,
            bin_edges=bin_edges,
            bin_confidences=bin_confidences,
            bin_frequencies=bin_frequencies,
            bin_counts=bin_counts,
            reliability_slope=float(slope),
            reliability_intercept=float(intercept),
        )
