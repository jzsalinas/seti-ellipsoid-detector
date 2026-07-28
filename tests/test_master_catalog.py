"""
Unit Tests for SETI Master Catalog Synthesizer & Priority Scoring.
"""

import os
import pandas as pd
import pytest

from core.anchor import AlienLatencyProfile
from core.master_catalog import (
    MasterCatalogGenerator,
    calculate_composite_priority_score,
    PriorityTier,
)


def test_calculate_composite_priority_score():
    df = pd.DataFrame(
        {
            "source_id": ["STAR_A", "STAR_B"],
            "anchors_hit_count": [2, 1],
            "ir_excess_score": [1.5, 0.0],
            "anomaly_score": [0.85, 0.20],
            "radio_technosignature_score": [20.0, 0.0],
            "optical_technosignature_score": [10.0, 0.0],
        }
    )
    scored = calculate_composite_priority_score(df)
    assert "priority_score" in scored.columns
    assert "priority_tier" in scored.columns

    star_a = scored[scored["source_id"] == "STAR_A"].iloc[0]
    star_b = scored[scored["source_id"] == "STAR_B"].iloc[0]

    assert star_a["priority_score"] > star_b["priority_score"]
    assert star_a["priority_tier"] in [PriorityTier.CRITICAL_TARGET.value, PriorityTier.HIGH_PRIORITY.value]


def test_master_catalog_generator(tmp_path):
    generator = MasterCatalogGenerator(use_mock=True)
    # Set wide tolerance for unit test to guarantee shell hits
    generator.tolerance_days = 100000.0

    stars_df = pd.DataFrame(
        {
            "source_id": ["STAR_1", "STAR_2"],
            "ra": [83.8667, 128.836],
            "dec": [-69.2697, -45.176],
            "dist_pc": [100.0, 200.0],
            "phot_g_mean_mag": [12.0, 14.0],
        }
    )

    master_df = generator.build_catalog(stars_df, current_date="2026-07-28T00:00:00", inject_synthetic_signals=True)
    assert isinstance(master_df, pd.DataFrame)
    assert not master_df.empty
    assert "priority_score" in master_df.columns

    csv_p = os.path.join(tmp_path, "master.csv")
    json_p = os.path.join(tmp_path, "master.json")
    out_csv, out_json = generator.export_catalog(master_df, csv_path=csv_p, json_path=json_p)

    assert os.path.exists(out_csv)
    assert os.path.exists(out_json)
    assert os.path.getsize(out_csv) > 100
    assert os.path.getsize(out_json) > 100
