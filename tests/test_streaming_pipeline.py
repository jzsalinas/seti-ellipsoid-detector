"""
Unit and Integration Tests for Fink Streaming Ingestion and End-to-End Pipeline.
"""

import pandas as pd
import pytest
from providers.fink_provider import FinkProvider, fetch_alerts_for_coordinates
from pipeline import run_pipeline


def test_fink_provider_streaming():
    provider = FinkProvider(use_mock=True)
    candidates_df = pd.DataFrame(
        {
            "source_id": ["STAR_A", "STAR_B"],
            "ra": [83.8667, 128.836],
            "dec": [-69.2697, -45.176],
        }
    )
    streams = provider.stream_candidate_alerts(candidates_df)
    assert len(streams) == 2
    assert "STAR_A" in streams
    assert isinstance(streams["STAR_A"], pd.DataFrame)
    assert not streams["STAR_A"].empty


def test_end_to_end_pipeline_execution():
    results = run_pipeline(
        radius_deg=1.0,
        tolerance_days=100000.0,  # Force shell hits for testing
        anomaly_threshold=0.50,
        use_mock=True,
    )
    assert isinstance(results, pd.DataFrame)
    assert not results.empty
    assert "is_inside_shell" in results.columns
    assert "anomaly_score" in results.columns
    assert "alert_triggered" in results.columns
