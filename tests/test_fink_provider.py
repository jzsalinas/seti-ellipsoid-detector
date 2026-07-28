"""
Unit tests for providers/fink_provider.py.
"""

import pandas as pd
import pytest

from providers.fink_provider import fetch_alerts_for_coordinates, fetch_latest_anomalies


def test_mock_fink_alerts():
    ra = 83.8667
    dec = -69.2697

    df = fetch_alerts_for_coordinates(ra=ra, dec=dec, use_mock=True)

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    expected_cols = ["objectId", "jd", "ra", "dec", "fid", "filter", "magpsf", "sigmagpsf"]
    for col in expected_cols:
        assert col in df.columns

    assert set(df["filter"].unique()).issubset({"g", "r"})


def test_mock_fink_latests():
    df = fetch_latest_anomalies(n_alerts=30, use_mock=True)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 30
    assert "classification" in df.columns
    assert (df["classification"] == "Anomaly").all()
