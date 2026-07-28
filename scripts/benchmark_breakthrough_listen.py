"""
Benchmark Script: Breakthrough Listen Radio Technosignature Pipeline (EXP-010).

Cross-matches active SETI Ellipsoid candidate stars with Breakthrough Listen GBT / Parkes radio archives,
evaluates narrowband signal width (Hz), Doppler drift rate (Hz/s), and SNR.
"""

import os
import sys
import numpy as np
import pandas as pd

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.anchor import AlienLatencyProfile
from providers.pulsar_provider import PulsarProvider
from providers.wise_provider import WISEProvider
from providers.breakthrough_provider import BreakthroughListenProvider
from core.geometry import find_multi_anchor_intersections
from core.infrared_engine import evaluate_dyson_swarm_excess
from core.radio_engine import evaluate_radio_technosignatures


def generate_synthetic_gaia_catalog(n_stars: int = 500) -> pd.DataFrame:
    """Generates synthetic Gaia stars for radio benchmark testing."""
    np.random.seed(404)
    ra = np.random.uniform(0, 360, n_stars)
    dec = np.random.uniform(-90, 90, n_stars)
    dist = np.random.uniform(50, 2000.0, n_stars)
    source_ids = [f"GAIA_DR3_{5000000 + i}" for i in range(n_stars)]

    return pd.DataFrame(
        {
            "source_id": source_ids,
            "ra": ra,
            "dec": dec,
            "dist_pc": dist,
            "phot_g_mean_mag": np.random.uniform(8.5, 15.0, n_stars),
        }
    )


def run_breakthrough_listen_benchmark():
    print("================================================================================")
    print("📻 SETI Ellipsoid Detector: Breakthrough Listen Radio Benchmark (EXP-010)")
    print("================================================================================\n")

    provider = PulsarProvider()
    anchors = provider.list_anchors()

    print(f"🛰️ Loaded {len(anchors)} Cosmic Anchors:")
    for a in anchors:
        print(f"  - [{a.anchor_type.value:17s}] {a.id:20s}: {a.name}")

    print("\n🌟 Generating synthetic Gaia stellar catalog (500 stars up to 2,000 pc)...")
    stars_df = generate_synthetic_gaia_catalog(n_stars=500)

    obs_date = "2026-07-28T00:00:00"
    tolerance_days = AlienLatencyProfile.BUREAUCRATIC.value  # ±730 days (~2 years)

    print(f"\n🔍 [Layer 1] Filtering active SETI Ellipsoid candidates (Tolerance: ±{tolerance_days:.0f} days)...")
    ellipsoid_candidates = find_multi_anchor_intersections(
        df=stars_df,
        current_date=obs_date,
        anchors=anchors,
        tolerance_days=tolerance_days,
        min_anchors_hit=1,
    )
    print(f"✨ Found {len(ellipsoid_candidates)} stars currently crossing active ellipsoid shells.")

    print("\n🔭 [Layer 2] Querying AllWISE mid-IR photometry...")
    wise_provider = WISEProvider(use_mock=True)
    wise_df = wise_provider.get_wise_photometry(ellipsoid_candidates, inject_dyson_candidates=True, dyson_fraction=0.50)
    ir_df = evaluate_dyson_swarm_excess(wise_df)

    print("\n📻 [Layer 4] Cross-matching with Breakthrough Listen GBT/Parkes Radio Archives (L-band)...")
    bl_provider = BreakthroughListenProvider(use_mock=True)
    radio_obs_df = bl_provider.get_radio_observations(
        ir_df,
        receiver_band="L_band",
        inject_technosignatures=True,
        technosignature_fraction=0.33,
    )

    print("\n⚡ Evaluating narrow-band width (Hz), Doppler drift rate (Hz/s), and SNR...")
    scored_df = evaluate_radio_technosignatures(radio_obs_df)

    radio_candidates = scored_df[scored_df["is_radio_candidate"]]

    print(f"\n📻 Identified {len(radio_candidates)} Narrow-Band Drifting Radio Technosignature Candidates!")
    print("-" * 92)
    if not scored_df.empty:
        cols = [
            "source_id",
            "dist_pc",
            "telescope",
            "bandwidth_hz",
            "drift_rate_hz_s",
            "snr",
            "is_radio_candidate",
            "radio_technosignature_score",
        ]
        print(scored_df[cols].to_string(index=False))

    out_csv = os.path.abspath("scratch/radio_technosignature_candidates_exp010.csv")
    scored_df.to_csv(out_csv, index=False)
    print(f"\n✅ Radio Benchmark Complete! Results exported to: {out_csv}")
    return scored_df


if __name__ == "__main__":
    run_breakthrough_listen_benchmark()
