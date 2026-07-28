"""
Interactive 3D SETI Ellipsoid Generator Script.

Queries Gaia DR3 (or synthetic mock data) around SN 1987A or Tycho SN 1572
and generates a standalone 3D interactive Plotly HTML file.
"""

from datetime import datetime, timezone
import argparse
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import HISTORIC_SUPERNOVAE
from core.geometry import is_in_ellipsoid_shell
from core.visualizer import generate_interactive_3d_ellipsoid
from providers.gaia_provider import get_candidate_stars


def main():
    parser = argparse.ArgumentParser(description="Generate Interactive 3D SETI Ellipsoid Visualization")
    parser.add_argument(
        "--sn",
        type=str,
        default="SN1572",
        choices=list(HISTORIC_SUPERNOVAE.keys()),
        help="Supernova anchor key (SN1987A, SN1572, SN1604, SN1054)",
    )
    parser.add_argument("--radius", type=float, default=2.0, help="Search cone radius in degrees")
    parser.add_argument("--mock", action="store_true", help="Use synthetic mock data instead of live Gaia DR3 TAP query")
    args = parser.parse_args()

    sn_info = HISTORIC_SUPERNOVAE[args.sn]
    name = sn_info["name"]
    ra = sn_info["ra_deg"]
    dec = sn_info["dec_deg"]
    d0 = sn_info["distance_pc"]
    epoch = sn_info["epoch"]

    current_date = datetime.now(timezone.utc).isoformat()

    print(f"=== GENERATING INTERACTIVE 3D VISUALIZATION ===")
    print(f"Anchor: {name}")
    print(f"Coordinates: RA={ra}°, Dec={dec}° | Dist={d0} pc")
    print(f"Fetching stars (mock={args.mock})...")

    df = get_candidate_stars(
        ra_center=ra,
        dec_center=dec,
        radius_deg=args.radius,
        max_magnitude=16.0,
        row_limit=500,
        use_mock=args.mock,
    )

    if df.empty:
        print("No stars retrieved.")
        return

    # Calculate delay
    is_inside, delay_days = is_in_ellipsoid_shell(
        ra_deg=df["ra"],
        dec_deg=df["dec"],
        dist_pc=df["dist_pc"],
        current_date=current_date,
        sn_ra=ra,
        sn_dec=dec,
        sn_dist_pc=d0,
        sn_epoch=epoch,
    )

    df["delay_days"] = delay_days
    df["is_inside"] = is_inside

    html_path = os.path.abspath(f"scratch/seti_ellipsoid_{args.sn}_3d.html")

    generate_interactive_3d_ellipsoid(
        stars_df=df,
        sn_ra=ra,
        sn_dec=dec,
        sn_dist_pc=d0,
        sn_epoch=epoch,
        sn_name=name,
        current_date=current_date,
        output_html=html_path,
    )

    print(f"\n🎉 Done! Open the file in your browser:")
    print(f"file://{html_path}")


if __name__ == "__main__":
    main()
