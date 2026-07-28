"""
CLI Script to Build and Export the Public SETI Ellipsoid Candidate Master Catalog (EXP-012).

Usage:
    python scripts/build_master_catalog.py [--date 2026-07-28] [--profile bureaucratic] [--n-stars 1000]
"""

import argparse
import os
import sys
import numpy as np
import pandas as pd

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.anchor import AlienLatencyProfile
from core.master_catalog import MasterCatalogGenerator, PriorityTier


def generate_synthetic_gaia_catalog(n_stars: int = 1000) -> pd.DataFrame:
    """Generates synthetic Gaia DR3 catalog stars for master catalog build testing."""
    np.random.seed(707)
    ra = np.random.uniform(0, 360, n_stars)
    dec = np.random.uniform(-90, 90, n_stars)
    dist = np.random.uniform(50, 2000.0, n_stars)
    source_ids = [f"GAIA_DR3_{7000000 + i}" for i in range(n_stars)]

    return pd.DataFrame(
        {
            "source_id": source_ids,
            "ra": ra,
            "dec": dec,
            "dist_pc": dist,
            "phot_g_mean_mag": np.random.uniform(8.0, 15.0, n_stars),
        }
    )


def main():
    parser = argparse.ArgumentParser(description="SETI Ellipsoid Candidate Master Catalog Builder")
    parser.add_argument("--date", type=str, default="2026-07-28T00:00:00", help="Observation ISO date")
    parser.add_argument("--profile", type=str, default="bureaucratic", help="Alien ETI Latency Profile")
    parser.add_argument("--n-stars", type=int, default=1000, help="Number of synthetic stars to evaluate")
    parser.add_argument("--output-csv", type=str, default="scratch/seti_ellipsoid_master_catalog.csv", help="CSV export path")
    parser.add_argument("--output-json", type=str, default="scratch/seti_ellipsoid_master_catalog.json", help="JSON export path")

    args = parser.parse_args()

    print("================================================================================")
    print("🌟 SETI Ellipsoid Detector: Public Master Catalog Synthesizer (EXP-012)")
    print("================================================================================\n")

    profile_enum = AlienLatencyProfile.BUREAUCRATIC
    if args.profile.upper() in AlienLatencyProfile.__members__:
        profile_enum = AlienLatencyProfile[args.profile.upper()]

    generator = MasterCatalogGenerator(latency_profile=profile_enum, use_mock=True)

    print(f"🛰️ Initialized 5-Layer Generator (Latency Profile: {profile_enum.name})...")
    print(f"🌟 Generating synthetic Gaia stellar catalog ({args.n_stars} stars)...")
    stars_df = generate_synthetic_gaia_catalog(n_stars=args.n_stars)

    print("\n⚙️ Synthesizing Layer 1 (Geometry), Layer 2 (IR Excess), Layer 3 (Optical Anomaly),")
    print("   Layer 4 (Radio Drift), and Layer 5 (Optical Laser) into Master Catalog...")

    master_df = generator.build_catalog(stars_df, current_date=args.date, inject_synthetic_signals=True)

    if master_df.empty:
        print("No active candidates found crossing ellipsoid shells.")
        return

    csv_path, json_path = generator.export_catalog(
        master_df,
        csv_path=os.path.abspath(args.output_csv),
        json_path=os.path.abspath(args.output_json),
    )

    print(f"\n✅ Successfully generated SETI Ellipsoid Master Catalog! Total Candidates: {len(master_df)}")
    print(f"📄 CSV Artifact : {csv_path}")
    print(f"📦 JSON Artifact: {json_path}\n")

    print("📊 Top Ranked Master Catalog Candidates:")
    print("-" * 110)
    cols = [
        "source_id",
        "dist_pc",
        "anchors_hit_count",
        "is_dyson_candidate",
        "is_radio_candidate",
        "is_optical_candidate",
        "priority_score",
        "priority_tier",
    ]
    print(master_df[cols].head(10).to_string(index=False))


if __name__ == "__main__":
    main()
