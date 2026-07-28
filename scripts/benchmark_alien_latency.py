"""
Benchmark Script: ETI Reaction Latency & Shell Thickness Sensitivity Benchmark.

Evaluates stellar candidate search counts in Gaia DR3 space across different Alien ETI
reaction latency profiles: AUTOMATED_BEACON (60 days), BUREAUCRATIC (730 days), and GENERATIONAL (1825 days).
"""

from datetime import datetime
import os
import sys
import numpy as np
import pandas as pd

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.anchor import (
    AlienLatencyProfile,
    get_latency_tolerance_days,
    latency_days_to_shell_thickness_pc,
)
from providers.pulsar_provider import PulsarProvider
from core.geometry import find_multi_anchor_intersections
from core.visualizer import generate_multi_anchor_3d_map


def generate_synthetic_star_field(n_stars: int = 2000, max_dist_pc: float = 4000.0) -> pd.DataFrame:
    """Generates synthetic stellar catalog distribution for latency sensitivity benchmarking."""
    np.random.seed(101)
    ra = np.random.uniform(0, 360, n_stars)
    dec = np.random.uniform(-90, 90, n_stars)
    dist = np.random.uniform(50, max_dist_pc, n_stars)
    source_ids = [f"GAIA_DR3_{2000000 + i}" for i in range(n_stars)]

    return pd.DataFrame(
        {
            "source_id": source_ids,
            "ra": ra,
            "dec": dec,
            "dist_pc": dist,
            "phot_g_mean_mag": np.random.uniform(9.0, 16.5, n_stars),
        }
    )


def run_latency_benchmark():
    print("================================================================================")
    print("👽 SETI Ellipsoid Detector: ETI Reaction Latency Sensitivity Benchmark (EXP-007)")
    print("================================================================================\n")

    provider = PulsarProvider()
    anchors = provider.list_anchors()

    print(f"🛰️ Loaded {len(anchors)} Cosmic Anchors (Supernovae, Pulsar Glitches, Magnetar Flares):")
    for a in anchors:
        print(f"  - [{a.anchor_type.value:17s}] {a.id:20s}: {a.name}")

    print("\n🌟 Generating benchmark stellar distribution (2,000 stars up to 4,000 pc)...")
    stars_df = generate_synthetic_star_field(n_stars=2000, max_dist_pc=4000.0)

    obs_date = "2026-07-28T00:00:00"
    profiles = [
        ("AUTOMATED_BEACON", AlienLatencyProfile.AUTOMATED_BEACON),
        ("BUREAUCRATIC", AlienLatencyProfile.BUREAUCRATIC),
        ("GENERATIONAL", AlienLatencyProfile.GENERATIONAL),
    ]

    print("\n📊 Benchmarking Candidate Search Counts vs. ETI Reaction Latency Profiles:\n")
    print(f"{'Profile Name':20s} | {'Days':7s} | {'Thickness (pc)':14s} | {'Single Hits (>=1)':17s} | {'Multi Hits (>=2)':16s}")
    print("-" * 84)

    results = []
    for name, profile in profiles:
        days = get_latency_tolerance_days(profile)
        thickness_pc = latency_days_to_shell_thickness_pc(days)

        single_hits = find_multi_anchor_intersections(
            df=stars_df,
            current_date=obs_date,
            anchors=anchors,
            tolerance_days=days,
            min_anchors_hit=1,
        )

        multi_hits = find_multi_anchor_intersections(
            df=stars_df,
            current_date=obs_date,
            anchors=anchors,
            tolerance_days=days,
            min_anchors_hit=2,
        )

        print(
            f"{name:20s} | ±{days:5.0f}d | {thickness_pc:10.4f} pc | {len(single_hits):17d} | {len(multi_hits):16d}"
        )

        # Generate HTML visualization for each profile
        out_html = os.path.abspath(f"scratch/latency_benchmark_{name.lower()}.html")
        generate_multi_anchor_3d_map(
            anchors=anchors,
            stars_df=stars_df,
            current_date=obs_date,
            tolerance_days=days,
            min_anchors_hit=2,
            output_html=out_html,
        )

        results.append(
            {
                "profile": name,
                "tolerance_days": days,
                "thickness_pc": thickness_pc,
                "single_anchor_hits": len(single_hits),
                "multi_anchor_hits": len(multi_hits),
                "html_path": out_html,
            }
        )

    print("\n✅ Benchmark completed successfully! WebGL maps saved to scratch/")
    return pd.DataFrame(results)


if __name__ == "__main__":
    run_latency_benchmark()
