"""
Unit and Integration Tests for Phase 6: CosmicAnchors & Multi-Anchor Ellipsoid Intersections.
"""

from datetime import datetime, timezone
import os
import numpy as np
import pandas as pd
import pytest

from core.anchor import CosmicAnchor, AnchorType, SN_1987A, VELA_GLITCH_1969, SGR_1806_2004
from providers.pulsar_provider import PulsarProvider
from core.geometry import (
    calculate_multi_anchor_delays,
    calculate_multi_anchor_rms_delay,
    find_multi_anchor_intersections,
)
from core.visualizer import generate_multi_anchor_3d_map


def test_cosmic_anchor_instantiation():
    anchor = CosmicAnchor(
        id="TEST_ANCHOR",
        name="Test Magnetar",
        ra_deg=100.0,
        dec_deg=-10.0,
        distance_pc=500.0,
        epoch=datetime(2020, 1, 1),  # Naive datetime
        anchor_type=AnchorType.MAGNETAR_FLARE,
    )
    assert anchor.epoch.tzinfo is not None
    assert anchor.epoch.tzinfo == timezone.utc
    assert anchor.anchor_type == AnchorType.MAGNETAR_FLARE


def test_pulsar_provider_queries():
    provider = PulsarProvider()
    anchors = provider.list_anchors()
    assert len(anchors) >= 6

    glitches = provider.list_anchors(anchor_types=[AnchorType.PULSAR_GLITCH])
    assert len(glitches) >= 2
    assert all(a.anchor_type == AnchorType.PULSAR_GLITCH for a in glitches)

    near_anchors = provider.list_anchors(max_distance_pc=1000.0)
    assert len(near_anchors) > 0
    assert all(a.distance_pc <= 1000.0 for a in near_anchors)

    df = provider.to_dataframe()
    assert isinstance(df, pd.DataFrame)
    assert "anchor_id" in df.columns


def test_multi_anchor_delays_vectorized():
    anchors = [SN_1987A, VELA_GLITCH_1969, SGR_1806_2004]
    ra = np.array([83.8667, 128.836, 0.0])
    dec = np.array([-69.2697, -45.176, 0.0])
    dist = np.array([51200.0, 287.0, 100.0])

    delays_df = calculate_multi_anchor_delays(
        ra_deg=ra,
        dec_deg=dec,
        dist_pc=dist,
        current_date="2026-07-28T00:00:00",
        anchors=anchors,
    )
    assert isinstance(delays_df, pd.DataFrame)
    assert delays_df.shape == (3, 3)
    assert f"delay_{SN_1987A.id}" in delays_df.columns

    rms_delays = calculate_multi_anchor_rms_delay(delays_df)
    assert len(rms_delays) == 3
    assert np.all(rms_delays >= 0)


def test_find_multi_anchor_intersections():
    anchors = [SN_1987A, VELA_GLITCH_1969]
    df_stars = pd.DataFrame(
        {
            "source_id": ["STAR_1", "STAR_2"],
            "ra": [83.8667, 0.0],
            "dec": [-69.2697, 0.0],
            "dist_pc": [10.0, 1000.0],
        }
    )

    result = find_multi_anchor_intersections(
        df=df_stars,
        current_date="2026-07-28T00:00:00",
        anchors=anchors,
        tolerance_days=100000.0,  # Generous tolerance to force hits
        min_anchors_hit=1,
    )
    assert not result.empty
    assert "anchors_hit_count" in result.columns
    assert "rms_delay_days" in result.columns


def test_multi_anchor_visualizer_generation(tmp_path):
    anchors = [SN_1987A, VELA_GLITCH_1969]
    df_stars = pd.DataFrame(
        {
            "source_id": ["STAR_1"],
            "ra": [10.0],
            "dec": [10.0],
            "dist_pc": [100.0],
        }
    )
    out_file = os.path.join(tmp_path, "multi_anchor_test.html")
    res_path = generate_multi_anchor_3d_map(
        anchors=anchors,
        stars_df=df_stars,
        current_date="2026-07-28T00:00:00",
        output_html=out_file,
    )
    assert os.path.exists(res_path)
    assert os.path.getsize(res_path) > 1000
