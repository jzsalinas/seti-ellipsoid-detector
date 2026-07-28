"""
Unit tests for providers/gaia_provider.py.
"""

import pandas as pd
import pytest

from core.geometry import is_in_ellipsoid_shell
from providers.gaia_provider import get_candidate_stars


def test_mock_gaia_provider():
    ra_center = 83.8667
    dec_center = -69.2697
    radius_deg = 1.0

    df = get_candidate_stars(
        ra_center=ra_center,
        dec_center=dec_center,
        radius_deg=radius_deg,
        use_mock=True,
    )

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    expected_columns = [
        "source_id",
        "ra",
        "dec",
        "parallax",
        "dist_pc",
        "pmra",
        "pmdec",
        "phot_g_mean_mag",
    ]
    for col in expected_columns:
        assert col in df.columns

    # Verify parallax -> distance conversion
    assert (df["dist_pc"] > 0).all()
    assert (df["dist_pc"] == (1000.0 / df["parallax"])).all()


def test_gaia_integration_with_geometry():
    df = get_candidate_stars(
        ra_center=83.8667,
        dec_center=-69.2697,
        radius_deg=2.0,
        row_limit=30,
        use_mock=True,
    )

    is_inside, delay_days = is_in_ellipsoid_shell(
        ra_deg=df["ra"],
        dec_deg=df["dec"],
        dist_pc=df["dist_pc"],
        current_date="2026-07-28T00:00:00",
        tolerance_days=1000.0,
    )

    df["is_inside"] = is_inside
    df["delay_days"] = delay_days

    assert "is_inside" in df.columns
    assert "delay_days" in df.columns
    assert len(df) == 30
