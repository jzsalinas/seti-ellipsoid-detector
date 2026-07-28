"""
Unit Tests for Pulsed Optical Laser Engine & APF Provider.
"""

import numpy as np
import pandas as pd
import pytest

from core.optical_engine import evaluate_optical_technosignatures
from providers.apf_provider import APFProvider


def test_evaluate_optical_technosignatures():
    df = pd.DataFrame(
        {
            "source_id": ["NATURAL_LINE", "LASER_PULSE"],
            "peak_wavelength_a": [5000.0, 5320.0],
            "linewidth_a": [1.5, 0.02],
            "peak_to_continuum_ratio": [1.2, 15.0],
            "pulse_sigma": [2.0, 18.0],
        }
    )
    evaluated = evaluate_optical_technosignatures(df)
    assert "is_monochromatic" in evaluated.columns
    assert "is_high_contrast" in evaluated.columns
    assert "is_optical_candidate" in evaluated.columns

    laser_row = evaluated[evaluated["source_id"] == "LASER_PULSE"].iloc[0]
    natural_row = evaluated[evaluated["source_id"] == "NATURAL_LINE"].iloc[0]

    assert laser_row["is_optical_candidate"] == True
    assert natural_row["is_optical_candidate"] == False
    assert laser_row["optical_technosignature_score"] > 0.0


def test_apf_provider():
    provider = APFProvider(use_mock=True)
    stars_df = pd.DataFrame(
        {
            "source_id": ["STAR_1", "STAR_2"],
            "ra": [10.0, 20.0],
            "dec": [5.0, 15.0],
            "dist_pc": [100.0, 200.0],
        }
    )
    spectra_df = provider.get_optical_spectra(stars_df, inject_laser_pulses=True)

    assert "peak_wavelength_a" in spectra_df.columns
    assert "linewidth_a" in spectra_df.columns
    assert "pulse_sigma" in spectra_df.columns
    assert len(spectra_df) == 2
