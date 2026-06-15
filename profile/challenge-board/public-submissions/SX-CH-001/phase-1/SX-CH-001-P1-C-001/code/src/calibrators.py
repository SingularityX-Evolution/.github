"""Post-hoc calibration for confidence estimates.

Converts raw aggregator outputs into well-calibrated probabilities using
isotonic regression. This is a standard technique: raw model scores are
often miscalibrated (too high or too low), and isotonic regression learns
a monotonic mapping from raw score to calibrated probability.
"""

import numpy as np
from sklearn.isotonic import IsotonicRegression


class IsotonicCalibrator:
    """Isotonic regression calibrator for confidence scores."""

    def __init__(self, y_min: float = 0.0, y_max: float = 1.0):
        self.y_min = y_min
        self.y_max = y_max
        self._model: IsotonicRegression | None = None
        self._fitted = False

    def fit(self, raw_confidences: np.ndarray, ground_truths: np.ndarray):
        """Fit isotonic regression on calibration data."""
        self._model = IsotonicRegression(
            y_min=self.y_min,
            y_max=self.y_max,
            increasing=True,
            out_of_bounds="clip",
        )
        self._model.fit(raw_confidences, ground_truths)
        self._fitted = True
        return self

    def calibrate(self, raw_confidences: np.ndarray) -> np.ndarray:
        """Transform raw confidences to calibrated probabilities."""
        if not self._fitted:
            raise RuntimeError("Calibrator not fitted. Call fit() first.")
        return self._model.predict(raw_confidences)

    def fit_calibrate(
        self,
        train_conf: np.ndarray,
        train_gt: np.ndarray,
        test_conf: np.ndarray,
    ) -> np.ndarray:
        """Fit on training data and calibrate test data."""
        self.fit(train_conf, train_gt)
        return self.calibrate(test_conf)


def calibration_split(
    confidences: np.ndarray,
    ground_truths: np.ndarray,
    test_ratio: float = 0.3,
    seed: int = 42,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Split data for calibration: train calibrator on part, evaluate on held-out."""
    rng = np.random.RandomState(seed)
    n = len(confidences)
    n_test = max(int(n * test_ratio), 10)
    indices = rng.permutation(n)
    test_idx = indices[:n_test]
    train_idx = indices[n_test:]
    return (
        confidences[train_idx],
        ground_truths[train_idx],
        confidences[test_idx],
        ground_truths[test_idx],
    )
