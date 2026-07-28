"""
Benchmark Script: APF / Lick Observatory Pulsed Optical Technosignature Pipeline (EXP-011).

Cross-matches active SETI Ellipsoid candidate stars with APF Levy Spectrograph optical archives,
evaluates monochromatic emission linewidth (Angstroms), peak-to-continuum ratio, and pulse significance.
"""

import os
import sys
import numpy as np
import pandas as pd

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.anchor import AlienLatencyProfile
from providers.pulsar_provider import PulsarProvider
from providers.apf_provider import APFProvider
from core.geometry import find_multi_anchor_intersections
from core.optical_engine import evaluate_optical_technosignatures


def generate_synthetic_gaia_catalog(n_stars: int = 500) -> pd.DataFrame:
    """Generates synthetic Gaia stars for optical laser benchmark testing."""
    np.random.seed(606)
    ra = np.random.uniform(0, 360, n_stars)
    dec = np.random.uniform(-90, 90, n_stars)
    dist = np.random.uniform(50, 1500.0, n_stars)
    source_ids = [f"GAIA_DR3_{6000000 + i}" for i in range(n_stars)]

    return pd.DataFrame(
        {
            "source_id": source_ids,
            "ra": ra,
            "dec": dec,
            "dist_pc": dist,
            "phot_g_mean_mag": np.random.uniform(8.0, 14.5, n_stars),
        }
    )


def run_pulsed_optical_benchmark():
    print("================================================================================")
    print("🔦 SETI Ellipsoid Detector: APF Pulsed Optical Laser Benchmark (EXP-011)")
    print("================================================================================\n")

    provider = PulsarProvider()
    anchors = provider.list_anchors()

    print(f"🛰️ Loaded {len(anchors)} Cosmic Anchors:")
    for a in anchors:
        print(f"  - [{a.anchor_type.value:17s}] {a.id:20s}: {a.name}")

    print("\n🌟 Generating synthetic Gaia stellar catalog (500 stars up to 1,500 pc)...")
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

    print("\n🔦 [Layer 5] Querying APF / Lick Observatory High-Resolution Optical Spectra...")
    apf_provider = APFProvider(use_mock=True)
    optical_obs_df = apf_provider.get_optical_spectra(
        ellipsoid_candidates,
        inject_laser_pulses=True,
        laser_fraction=0.50,
    )

    print("\n⚡ Evaluating monochromatic linewidth (Å), peak-to-continuum ratio, and significance (sigma)...")
    scored_df = evaluate_optical_technosignatures(optical_obs_df)

    optical_candidates = scored_df[scored_df["is_optical_candidate"]]

    print(f"\n🔦 Identified {len(optical_candidates)} Monochromatic Pulsed Optical Laser Technosignature Candidates!")
    print("-" * 96)
    if not scored_df.empty:
        cols = [
            "source_id",
            "dist_pc",
            "peak_wavelength_a",
            "linewidth_a",
            "peak_to_continuum_ratio",
            "pulse_sigma",
            "is_optical_candidate",
            "optical_technosignature_score",
        ]
        print(scored_df[cols].to_string(index=False))

    out_csv = os.path.abspath("scratch/pulsed_optical_candidates_exp011.csv")
    scored_df.to_csv(out_csv, index=False)
    print(f"\n✅ Optical Laser Benchmark Complete! Results exported to: {out_csv}")
    return scored_df


if __name__ == "__main__":
    run_pulsed_optical_benchmark()
