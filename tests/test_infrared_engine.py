"""
Unit and Integration Tests for Mid-Infrared Excess (Dyson Swarm) Engine & WISE Provider.
"""

import numpy as np
import pandas as pd
import pytest

from core.infrared_engine import (
    calculate_infrared_colors,
    estimate_expected_w3_w4_color,
    evaluate_dyson_swarm_excess,
)
from providers.wise_provider import WISEProvider


def test_calculate_infrared_colors():
    df = pd.DataFrame(
        {
            "w1mpro": [10.0],
            "w2mpro": [9.9],
            "w3mpro": [8.0],
            "w4mpro": [6.0],
        }
    )
    colored_df = calculate_infrared_colors(df)
    assert pytest.approx(colored_df["w1_w2"].iloc[0], 0.001) == 0.1
    assert pytest.approx(colored_df["w2_w3"].iloc[0], 0.001) == 1.9
    assert pytest.approx(colored_df["w3_w4"].iloc[0], 0.001) == 2.0
    assert pytest.approx(colored_df["w1_w4"].iloc[0], 0.001) == 4.0


def test_evaluate_dyson_swarm_excess():
    df = pd.DataFrame(
        {
            "source_id": ["STAR_NORMAL", "STAR_DYSON"],
            "w1mpro": [10.0, 10.0],
            "w2mpro": [10.0, 10.0],
            "w3mpro": [9.9, 7.5],
            "w4mpro": [9.8, 4.5],
        }
    )
    evaluated = evaluate_dyson_swarm_excess(df)
    assert "is_dyson_candidate" in evaluated.columns
    assert "ir_excess_score" in evaluated.columns

    dyson_star = evaluated[evaluated["source_id"] == "STAR_DYSON"].iloc[0]
    normal_star = evaluated[evaluated["source_id"] == "STAR_NORMAL"].iloc[0]

    assert dyson_star["is_dyson_candidate"] == True
    assert normal_star["is_dyson_candidate"] == False
    assert dyson_star["ir_excess_score"] > 1.0


def test_wise_provider_photometry_generation():
    provider = WISEProvider(use_mock=True)
    stars_df = pd.DataFrame(
        {
            "source_id": ["STAR_1", "STAR_2"],
            "ra": [10.0, 20.0],
            "dec": [5.0, 15.0],
            "dist_pc": [100.0, 200.0],
            "phot_g_mean_mag": [12.0, 14.0],
        }
    )
    wise_df = provider.get_wise_photometry(stars_df, inject_dyson_candidates=True, dyson_fraction=0.5)

    assert "w1mpro" in wise_df.columns
    assert "w4mpro" in wise_df.columns
    assert len(wise_df) == 2
