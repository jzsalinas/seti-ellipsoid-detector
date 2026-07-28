"""
Unit and end-to-end integration tests for pipeline.py and notifier/telegram_bot.py.
"""

import os
import pandas as pd
import pytest

from pipeline import run_pipeline
from notifier.telegram_bot import generate_lightcurve_plot, send_alert
from providers.fink_provider import fetch_alerts_for_coordinates


def test_plot_generation():
    df_lc = fetch_alerts_for_coordinates(83.8667, -69.2697, use_mock=True)
    img_path = generate_lightcurve_plot(
        star_id="TEST_STAR_001",
        lightcurve_df=df_lc,
        anomaly_score=0.92,
    )

    assert os.path.exists(img_path)
    assert img_path.endswith(".png")


def test_pipeline_end_to_end_mock():
    df_results = run_pipeline(
        radius_deg=2.0,
        tolerance_days=10000.0,
        anomaly_threshold=0.50,
        use_mock=True,
    )

    assert isinstance(df_results, pd.DataFrame)
    assert not df_results.empty
    expected_cols = [
        "source_id",
        "ra",
        "dec",
        "dist_pc",
        "is_inside_shell",
        "delay_days",
        "anomaly_score",
        "alert_triggered",
    ]
    for col in expected_cols:
        assert col in df_results.columns

    assert (df_results["anomaly_score"] >= 0.0).all()
    assert (df_results["anomaly_score"] <= 1.0).all()
