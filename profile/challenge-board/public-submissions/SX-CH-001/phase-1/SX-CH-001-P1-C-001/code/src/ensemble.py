"""Ensemble calibrator using per-hop features + aggregator outputs.

Extracts discriminative features from individual hop confidences rather than
relying solely on aggregate scores, which are often compressed to narrow ranges.
"""

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


class EnsembleCalibrator:
    """Multi-feature calibrator using per-hop statistics for better discrimination."""

    def __init__(self, C: float = 0.5):
        self.C = C
        self._scaler = StandardScaler()
        self._model = LogisticRegression(C=C, max_iter=2000)
        self._fitted = False

    def _build_features(
        self,
        results_by_method: dict[str, np.ndarray],
        chain_n_hops: np.ndarray,
        per_chain_stats: dict[str, np.ndarray] | None = None,
    ) -> np.ndarray:
        features = []

        # Aggregator outputs + logit transforms
        for method, confs in results_by_method.items():
            features.append(confs.reshape(-1, 1))
            eps = 1e-8
            clamped = np.clip(confs, eps, 1 - eps)
            logit = np.log(clamped / (1 - clamped))
            features.append(logit.reshape(-1, 1))

        # Per-chain statistics (these are much more discriminative)
        if per_chain_stats:
            for name, values in per_chain_stats.items():
                v = np.asarray(values, dtype=float).reshape(-1, 1)
                features.append(v)

        # Hop count features
        n_hops = chain_n_hops.reshape(-1, 1).astype(float)
        features.append(n_hops)
        features.append(np.log1p(n_hops))
        features.append(1.0 / np.maximum(n_hops, 1.0))

        return np.hstack(features)

    def fit(
        self,
        results_by_method: dict[str, np.ndarray],
        chain_n_hops: np.ndarray,
        ground_truths: np.ndarray,
        per_chain_stats: dict[str, np.ndarray] | None = None,
    ):
        X = self._build_features(results_by_method, chain_n_hops, per_chain_stats)
        X_scaled = self._scaler.fit_transform(X)
        self._model.fit(X_scaled, ground_truths)
        self._fitted = True
        return self

    def predict_proba(self, results_by_method, chain_n_hops,
                      per_chain_stats=None):
        if not self._fitted:
            raise RuntimeError("Not fitted")
        X = self._build_features(results_by_method, chain_n_hops, per_chain_stats)
        X_scaled = self._scaler.transform(X)
        return self._model.predict_proba(X_scaled)[:, 1]

    def fit_calibrate(
        self,
        results_by_method: dict[str, np.ndarray],
        chain_n_hops: np.ndarray,
        ground_truths: np.ndarray,
        per_chain_stats: dict[str, np.ndarray] | None = None,
    ) -> np.ndarray:
        self.fit(results_by_method, chain_n_hops, ground_truths, per_chain_stats)
        return self.predict_proba(results_by_method, chain_n_hops, per_chain_stats)
