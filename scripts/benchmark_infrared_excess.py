"""
Benchmark Script: Gaia DR3 + AllWISE Infrared Excess Candidate Search Pipeline (EXP-008).

Evaluates target stars crossing active SETI Ellipsoid shells for mid-infrared excess (W3 - W4, W1 - W4)
indicative of ETI waste-heat megastructures (Dyson Swarms / Spheres).
"""

import os
import sys
import numpy as np
import pandas as pd

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.anchor import CosmicAnchor, AnchorType, DEFAULT_COSMIC_ANCHORS, AlienLatencyProfile
from providers.pulsar_provider import PulsarProvider
from providers.wise_provider import WISEProvider
from core.geometry import find_multi_anchor_intersections
from core.infrared_engine import evaluate_dyson_swarm_excess


def generate_synthetic_gaia_field(n_stars: int = 1000, max_dist_pc: float = 3000.0) -> pd.DataFrame:
    """Generates synthetic Gaia catalog stars for testing infrared excess pipeline."""
    np.random.seed(202)
    ra = np.random.uniform(0, 360, n_stars)
    dec = np.random.uniform(-90, 90, n_stars)
    dist = np.random.uniform(50, max_dist_pc, n_stars)
    source_ids = [f"GAIA_DR3_{3000000 + i}" for i in range(n_stars)]

    return pd.DataFrame(
        {
            "source_id": source_ids,
            "ra": ra,
            "dec": dec,
            "dist_pc": dist,
            "phot_g_mean_mag": np.random.uniform(8.0, 16.0, n_stars),
        }
    )


def run_infrared_excess_benchmark():
    print("================================================================================")
    print("🛸 SETI Ellipsoid Detector: Infrared Excess (Dyson Swarms) Benchmark (EXP-008)")
    print("================================================================================\n")

    provider = PulsarProvider()
    anchors = provider.list_anchors()

    print(f"🛰️ Loaded {len(anchors)} Cosmic Anchors:")
    for a in anchors:
        print(f"  - [{a.anchor_type.value:17s}] {a.id:20s}: {a.name}")

    print("\n🌟 Generating synthetic Gaia stellar catalog (1,000 stars up to 3,000 pc)...")
    stars_df = generate_synthetic_gaia_field(n_stars=1000, max_dist_pc=3000.0)

    obs_date = "2026-07-28T00:00:00"
    tolerance_days = AlienLatencyProfile.BUREAUCRATIC.value  # ±730 days (~2 years)

    print(f"\n🔍 Searching for active SETI Ellipsoid candidates (Tolerance: ±{tolerance_days:.0f} days)...")
    ellipsoid_candidates = find_multi_anchor_intersections(
        df=stars_df,
        current_date=obs_date,
        anchors=anchors,
        tolerance_days=tolerance_days,
        min_anchors_hit=1,
    )

    print(f"✨ Found {len(ellipsoid_candidates)} stars currently crossing active ellipsoid shells.")

    print("\n🔭 Querying AllWISE mid-IR photometry (W1, W2, W3, W4) and injecting Dyson Swarm excess...")
    wise_provider = WISEProvider(use_mock=True)
    wise_df = wise_provider.get_wise_photometry(
        ellipsoid_candidates,
        inject_dyson_candidates=True,
        dyson_fraction=0.20,  # Inject Dyson excess into subset for demonstration
    )

    print("\n🔥 Evaluating mid-infrared excess significance (W3 - W4, W1 - W4)...")
    scored_df = evaluate_dyson_swarm_excess(wise_df)

    dyson_candidates = scored_df[scored_df["is_dyson_candidate"]]

    print(f"\n🛸 Identified {len(dyson_candidates)} Dyson Swarm Technosignature Candidates!")
    print("-" * 88)
    if not dyson_candidates.empty:
        cols = ["source_id", "dist_pc", "w1mpro", "w3mpro", "w4mpro", "excess_w3_w4", "ir_excess_score"]
        print(dyson_candidates[cols].head(10).to_string(index=False))

    out_csv = os.path.abspath("scratch/dyson_swarm_candidates_exp008.csv")
    scored_df.to_csv(out_csv, index=False)
    print(f"\n✅ Results exported to: {out_csv}")

    return scored_df


if __name__ == "__main__":
    run_infrared_excess_benchmark()
