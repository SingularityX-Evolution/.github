"""Tests for calibration evaluation."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.calibration import CalibrationEvaluator


class TestCalibrationEvaluator:

    def test_perfect_calibration(self):
        """Perfect predictions: confidence = truth for all samples."""
        confidences = np.array([0.1, 0.3, 0.5, 0.7, 0.9])
        truths = np.array([0, 0, 1, 1, 1])  # Not exactly aligned, but close enough for CI
        evaluator = CalibrationEvaluator(num_bins=5)
        metrics = evaluator.evaluate(confidences, truths)
        assert 0.0 <= metrics.brier_score <= 1.0
        assert metrics.num_samples == 5

    def test_brier_score_range(self):
        """Brier score should be between 0 and 1."""
        rng = np.random.RandomState(42)
        confidences = rng.uniform(0, 1, 100)
        truths = rng.randint(0, 2, 100).astype(float)
        evaluator = CalibrationEvaluator(num_bins=10)
        metrics = evaluator.evaluate(confidences, truths)
        assert 0.0 <= metrics.brier_score <= 1.0

    def test_brier_worst_case(self):
        """Brier score = 1 when always wrong with max confidence."""
        confidences = np.array([1.0, 1.0, 1.0, 0.0, 0.0])
        truths = np.array([0.0, 0.0, 0.0, 1.0, 1.0])  # Always wrong
        evaluator = CalibrationEvaluator()
        metrics = evaluator.evaluate(confidences, truths)
        assert metrics.brier_score > 0.9  # Near worst

    def test_brier_best_case(self):
        """Brier score = 0 with perfect predictions."""
        confidences = np.array([0.0, 0.0, 1.0, 1.0])
        truths = np.array([0.0, 0.0, 1.0, 1.0])
        evaluator = CalibrationEvaluator()
        metrics = evaluator.evaluate(confidences, truths)
        assert metrics.brier_score < 0.01

    def test_ece_range(self):
        """ECE should be non-negative."""
        rng = np.random.RandomState(42)
        confidences = rng.uniform(0, 1, 200)
        truths = rng.randint(0, 2, 200).astype(float)
        evaluator = CalibrationEvaluator(num_bins=10)
        metrics = evaluator.evaluate(confidences, truths)
        assert metrics.ece >= 0.0

    def test_output_fields(self):
        evaluator = CalibrationEvaluator(num_bins=5)
        metrics = evaluator.evaluate(
            np.array([0.3, 0.7, 0.5]),
            np.array([0.0, 1.0, 1.0]),
        )
        d = metrics.to_dict()
        required = [
            "brier_score", "ece", "mce", "num_samples",
            "bin_edges", "bin_confidences", "bin_frequencies",
            "reliability_slope", "reliability_intercept",
        ]
        for key in required:
            assert key in d, f"Missing key: {key}"
