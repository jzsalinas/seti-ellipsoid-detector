"""
Unit tests for core/anomaly_engine.py.
"""

import numpy as np
import pandas as pd
import pytest

from core.anomaly_engine import AnomalyEvaluator
from providers.fink_provider import fetch_alerts_for_coordinates


def test_feature_extraction():
    evaluator = AnomalyEvaluator()

    # Empty input
    empty_features = evaluator.extract_features(pd.DataFrame())
    assert empty_features["mag_std"] == 0.0

    # Mock lightcurve
    df_lc = fetch_alerts_for_coordinates(83.8667, -69.2697, use_mock=True)
    features = evaluator.extract_features(df_lc)

    assert "mag_std" in features
    assert "mag_range" in features
    assert "skewness" in features
    assert "color_g_r" in features
    assert "residuals_std" in features
    assert features["mag_std"] > 0.0


def test_anomaly_scoring_bounds():
    evaluator = AnomalyEvaluator()

    # Stable lightcurve metrics
    stable_metrics = {
        "mag_std": 0.01,
        "mag_range": 0.03,
        "skewness": 0.0,
        "color_g_r": 0.1,
        "residuals_std": 0.01,
    }
    stable_score = evaluator.compute_anomaly_score(stable_metrics)

    # Highly anomalous metrics (wild spikes)
    anomalous_metrics = {
        "mag_std": 1.5,
        "mag_range": 4.2,
        "skewness": 3.5,
        "color_g_r": 2.1,
        "residuals_std": 1.2,
    }
    anomalous_score = evaluator.compute_anomaly_score(anomalous_metrics)

    assert 0.0 <= stable_score <= 1.0
    assert 0.0 <= anomalous_score <= 1.0
    # Anomalous score should be significantly higher than stable score
    assert anomalous_score > stable_score
