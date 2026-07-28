"""
Interactive Multi-Supernova 3D Map Generator.

Queries Gaia DR3 stars around all historic supernova anchors (SN 1987A, SN 1572 Tycho,
SN 1604 Kepler, SN 1054 Crab) and renders a 3D WebGL galactic map with superposed ellipsoids.
"""

from datetime import datetime, timezone
import argparse
import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import HISTORIC_SUPERNOVAE
from core.visualizer import generate_multi_supernovae_3d_map
from providers.gaia_provider import get_candidate_stars


def main():
    parser = argparse.ArgumentParser(description="Generate Multi-Supernova 3D Superposition Map")
    parser.add_argument("--mock", action="store_true", help="Use synthetic mock data instead of live Gaia queries")
    args = parser.parse_args()

    current_date = datetime.now(timezone.utc).isoformat()

    print("=== GENERATING MULTI-SUPERNOVA 3D MAP ===")
    print("Fetching Gaia DR3 candidate stars around historic supernova anchors...\n")

    all_dfs = []

    for sn_key, sn_info in HISTORIC_SUPERNOVAE.items():
        name = sn_info["name"]
        ra = sn_info["ra_deg"]
        dec = sn_info["dec_deg"]
        print(f"Fetching candidates around {name}...")

        try:
            df = get_candidate_stars(
                ra_center=ra,
                dec_center=dec,
                radius_deg=1.5,
                max_magnitude=15.5,
                row_limit=200,
                use_mock=args.mock,
            )
            if not df.empty:
                df["anchor_sn"] = sn_key
                all_dfs.append(df)
        except Exception as err:
            print(f"Warning: Failed to fetch stars for {name}: {err}")

    combined_df = pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()
    print(f"\nTotal catalog stars loaded: {len(combined_df)}")

    html_path = os.path.abspath("scratch/seti_multi_supernovae_3d_map.html")

    generate_multi_supernovae_3d_map(
        stars_df=combined_df,
        supernovae_dict=HISTORIC_SUPERNOVAE,
        current_date=current_date,
        output_html=html_path,
    )

    print(f"\n🎉 Done! Open the multi-supernova map in your browser:")
    print(f"file://{html_path}")


if __name__ == "__main__":
    main()
