"""
Unit Tests for Radio Technosignature Engine & Breakthrough Listen Provider.
"""

import numpy as np
import pandas as pd
import pytest

from core.radio_engine import (
    calculate_doppler_drift_rate,
    evaluate_radio_technosignatures,
)
from providers.breakthrough_provider import BreakthroughListenProvider


def test_calculate_doppler_drift_rate():
    # 1420.40575 MHz signal under 0.1 m/s^2 line-of-sight acceleration
    drift = calculate_doppler_drift_rate(f0_mhz=1420.40575, accel_m_s2=0.1)
    # expected drift = -1.4204e9 * 0.1 / 2.99792e8 ~ -0.4738 Hz/s
    assert pytest.approx(abs(drift), 0.01) == 0.4738


def test_evaluate_radio_technosignatures():
    df = pd.DataFrame(
        {
            "source_id": ["NATURAL_SIGNAL", "TECHNOSIGNATURE_SIGNAL"],
            "bandwidth_hz": [50000.0, 1.2],
            "drift_rate_hz_s": [0.0001, 0.45],
            "snr": [5.0, 25.0],
        }
    )
    evaluated = evaluate_radio_technosignatures(df)
    assert "is_narrowband" in evaluated.columns
    assert "is_drifting" in evaluated.columns
    assert "is_radio_candidate" in evaluated.columns

    techno_row = evaluated[evaluated["source_id"] == "TECHNOSIGNATURE_SIGNAL"].iloc[0]
    natural_row = evaluated[evaluated["source_id"] == "NATURAL_SIGNAL"].iloc[0]

    assert techno_row["is_radio_candidate"] == True
    assert natural_row["is_radio_candidate"] == False
    assert techno_row["radio_technosignature_score"] > 0.0


def test_breakthrough_provider():
    provider = BreakthroughListenProvider(use_mock=True)
    stars_df = pd.DataFrame(
        {
            "source_id": ["STAR_1", "STAR_2"],
            "ra": [10.0, 20.0],
            "dec": [5.0, 15.0],
            "dist_pc": [100.0, 200.0],
        }
    )
    radio_df = provider.get_radio_observations(stars_df, receiver_band="L_band", inject_technosignatures=True)

    assert "bandwidth_hz" in radio_df.columns
    assert "drift_rate_hz_s" in radio_df.columns
    assert "snr" in radio_df.columns
    assert len(radio_df) == 2
