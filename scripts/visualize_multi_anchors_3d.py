"""
CLI Script to Visualize 3D Cosmic Anchors (Supernovae + Pulsars + Flares) Intersection Map.

Usage:
    python scripts/visualize_multi_anchors_3d.py [--date 2026-07-28] [--tolerance 30] [--min-hits 2]
"""

import argparse
from datetime import datetime, timezone
import os
import sys
import pandas as pd
import numpy as np

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.anchor import DEFAULT_COSMIC_ANCHORS, AnchorType, CosmicAnchor
from providers.pulsar_provider import PulsarProvider
from core.geometry import find_multi_anchor_intersections
from core.visualizer import generate_multi_anchor_3d_map


def generate_synthetic_stars(n_stars: int = 500, max_dist_pc: float = 3000.0) -> pd.DataFrame:
    """Generates synthetic stars for demonstration of 3D multi-anchor intersection map."""
    np.random.seed(42)
    ra = np.random.uniform(0, 360, n_stars)
    dec = np.random.uniform(-90, 90, n_stars)
    dist = np.random.uniform(50, max_dist_pc, n_stars)
    source_ids = [f"GAIA_DR3_{1000000 + i}" for i in range(n_stars)]

    df = pd.DataFrame(
        {
            "source_id": source_ids,
            "ra": ra,
            "dec": dec,
            "dist_pc": dist,
            "phot_g_mean_mag": np.random.uniform(8.0, 16.0, n_stars),
        }
    )
    return df


def main():
    parser = argparse.ArgumentParser(description="SETI Ellipsoid Multi-Anchor 3D Visualizer")
    parser.add_argument("--date", type=str, default="2026-07-28T00:00:00", help="Observation ISO date")
    parser.add_argument("--tolerance", type=float, default=365.0, help="Tolerance window in days (+/- days)")
    parser.add_argument("--min-hits", type=int, default=2, help="Minimum number of anchor shell hits")
    parser.add_argument("--output", type=str, default="scratch/multi_anchor_intersection_3d.html", help="HTML output path")

    args = parser.parse_args()

    provider = PulsarProvider()
    anchors = provider.list_anchors()

    print(f"🛰️ Loaded {len(anchors)} Cosmic Anchors (Supernovae, Pulsar Glitches, Magnetar Flares):")
    for a in anchors:
        print(f"  - [{a.anchor_type.value}] {a.id}: {a.name} (Epoch: {a.epoch.strftime('%Y-%m-%d')}, Dist: {a.distance_pc:.0f} pc)")

    print("\n🌟 Generating synthetic Gaia catalog stars...")
    stars_df = generate_synthetic_stars(n_stars=1000, max_dist_pc=5000.0)

    print(f"\n🔍 Searching for multi-anchor intersections (Tolerance: ±{args.tolerance} days, Min Hits: {args.min_hits})...")
    candidates = find_multi_anchor_intersections(
        stars_df,
        current_date=args.date,
        anchors=anchors,
        tolerance_days=args.tolerance,
        min_anchors_hit=args.min_hits,
    )

    print(f"✨ Found {len(candidates)} candidate stars intersecting >= {args.min_hits} anchor shells!")
    if not candidates.empty:
        print(candidates[["source_id", "ra", "dec", "dist_pc", "anchors_hit_count", "rms_delay_days"]].head(10))

    output_path = os.path.abspath(args.output)
    generate_multi_anchor_3d_map(
        anchors=anchors,
        stars_df=stars_df,
        current_date=args.date,
        tolerance_days=args.tolerance,
        min_anchors_hit=args.min_hits,
        output_html=output_path,
    )
    print(f"🎉 Saved 3D WebGL Multi-Anchor Map to: {output_path}")


if __name__ == "__main__":
    main()
