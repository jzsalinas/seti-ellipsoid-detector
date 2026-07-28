"""
Anomaly Evaluator Engine.

Extracts photometric features from light curves (magnitude variance, peak-to-peak range,
color indices, skewness, fit residuals) and calculates an anomaly score using IsolationForest.
"""

from typing import Dict, Union, Optional
import numpy as np
import pandas as pd
from scipy.stats import skew
from sklearn.ensemble import IsolationForest


class AnomalyEvaluator:
    """Evaluates light curve feature vectors to score non-standard transient activity."""

    def __init__(self, contamination: float = 0.1, random_state: int = 42):
        self.model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
        )
        self.is_fitted = False
        self._fit_default_baseline()

    def _fit_default_baseline(self):
        """Fits a baseline normal distribution of light curve metrics for instant scoring."""
        np.random.seed(42)
        n_samples = 200
        # Synthetic baseline: stable stars with low variance, near-zero skewness
        baseline_features = np.column_stack(
            [
                np.random.gamma(shape=1.5, scale=0.02, size=n_samples),  # mag_std
                np.random.uniform(0.01, 0.15, size=n_samples),            # mag_range
                np.random.normal(0.0, 0.05, size=n_samples),             # skewness
                np.random.normal(0.5, 0.2, size=n_samples),              # color_g_r
                np.random.gamma(shape=1.0, scale=0.01, size=n_samples),  # residuals_std
            ]
        )
        self.model.fit(baseline_features)
        self.is_fitted = True

    def fit(self, feature_matrix: Union[np.ndarray, pd.DataFrame]):
        """Fits the IsolationForest model on a provided training matrix of stellar features."""
        if isinstance(feature_matrix, pd.DataFrame):
            X = feature_matrix.values
        else:
            X = feature_matrix

        self.model.fit(X)
        self.is_fitted = True

    def extract_features(self, df_lightcurve: pd.DataFrame) -> Dict[str, float]:
        """
        Extracts photometric metric vector from a lightcurve DataFrame.
        Expected columns: ['magpsf', 'filter'] (or 'mag')
        """
        if df_lightcurve.empty or "magpsf" not in df_lightcurve.columns:
            return {
                "mag_std": 0.0,
                "mag_range": 0.0,
                "skewness": 0.0,
                "color_g_r": 0.0,
                "residuals_std": 0.0,
            }

        mags = df_lightcurve["magpsf"].values
        mag_std = float(np.std(mags))
        mag_range = float(np.ptp(mags))
        skewness_val = float(skew(mags)) if len(mags) > 2 else 0.0

        # Mean color g - r index
        if "filter" in df_lightcurve.columns:
            g_mags = df_lightcurve[df_lightcurve["filter"] == "g"]["magpsf"]
            r_mags = df_lightcurve[df_lightcurve["filter"] == "r"]["magpsf"]
            if not g_mags.empty and not r_mags.empty:
                color_g_r = float(g_mags.mean() - r_mags.mean())
            else:
                color_g_r = 0.0
        else:
            color_g_r = 0.0

        # Fit residuals relative to median baseline
        residuals_std = float(np.std(mags - np.median(mags)))

        return {
            "mag_std": mag_std,
            "mag_range": mag_range,
            "skewness": skewness_val,
            "color_g_r": color_g_r,
            "residuals_std": residuals_std,
        }

    def compute_anomaly_score(self, metrics: Dict[str, float]) -> float:
        """
        Calculates an anomaly score between 0.0 (perfectly normal) and 1.0 (highly anomalous).
        Uses IsolationForest decision_function.
        """
        if not self.is_fitted:
            self._fit_default_baseline()

        feature_vector = np.array(
            [
                [
                    metrics.get("mag_std", 0.0),
                    metrics.get("mag_range", 0.0),
                    metrics.get("skewness", 0.0),
                    metrics.get("color_g_r", 0.0),
                    metrics.get("residuals_std", 0.0),
                ]
            ]
        )

        # IsolationForest decision_function returns lower values for anomalies (can be negative)
        raw_score = self.model.decision_function(feature_vector)[0]

        # Map raw decision score (typically between -0.5 and +0.5) to [0, 1] range
        # Lower raw_score means higher anomaly
        anomaly_score = 1.0 / (1.0 + np.exp(4.0 * raw_score))
        return float(np.clip(anomaly_score, 0.0, 1.0))
