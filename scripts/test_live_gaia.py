"""
Live Field Test: Real Gaia DR3 Query & SETI Ellipsoid Shell Crossing.

Queries the live ESA Gaia DR3 archive via astroquery around SN 1987A coordinates
and evaluates real star positions against the current active 3D SETI Ellipsoid shell.
"""

from datetime import datetime, timezone
import os
import sys
import pandas as pd

# Add root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import SN1987A_RA_DEG, SN1987A_DEC_DEG, DEFAULT_TOLERANCE_DAYS
from core.geometry import is_in_ellipsoid_shell
from providers.gaia_provider import get_candidate_stars


def main():
    current_date = datetime.now(timezone.utc).isoformat()
    ra = SN1987A_RA_DEG
    dec = SN1987A_DEC_DEG
    radius_deg = 1.5  # 1.5 degree cone search around SN 1987A

    print(f"=== LIVE FIELD TEST: GAIA DR3 QUERY ===")
    print(f"Target Event: SN 1987A (RA: {ra}°, Dec: {dec}°)")
    print(f"Cone Radius: {radius_deg}°")
    print(f"Current Date: {current_date}")
    print(f"Connecting to ESA Gaia Archive via ADQL...\n")

    try:
        df = get_candidate_stars(
            ra_center=ra,
            dec_center=dec,
            radius_deg=radius_deg,
            max_magnitude=16.0,
            row_limit=500,
            use_mock=False,
        )

        if df.empty:
            print("No stars returned from Gaia query matching quality filters.")
            return

        print(f"✅ Successfully retrieved {len(df)} real stars from Gaia DR3.")
        print(f"Distance range: {df['dist_pc'].min():.1f} pc to {df['dist_pc'].max():.1f} pc (Median: {df['dist_pc'].median():.1f} pc)\n")

        # Test shell crossings with multiple tolerances
        for tol_days in [30.0, 90.0, 365.0, 1000.0]:
            is_inside, delay_days = is_in_ellipsoid_shell(
                ra_deg=df["ra"],
                dec_deg=df["dec"],
                dist_pc=df["dist_pc"],
                current_date=current_date,
                tolerance_days=tol_days,
            )
            df_inside = df[is_inside].copy()
            df_inside["delay_days"] = delay_days[is_inside]

            print(f"--- Shell Tolerance ±{tol_days:.0f} days ---")
            print(f"Active Stars on Shell: {len(df_inside)} / {len(df)}")
            if not df_inside.empty:
                print(df_inside[["source_id", "ra", "dec", "dist_pc", "phot_g_mean_mag", "delay_days"]].head(10))
            print()

        # Find the star closest to the exact ellipsoid surface today
        all_delays = is_in_ellipsoid_shell(
            ra_deg=df["ra"],
            dec_deg=df["dec"],
            dist_pc=df["dist_pc"],
            current_date=current_date,
            tolerance_days=1e9,
        )[1]

        df["abs_delay_days"] = pd.Series(all_delays).abs()
        df["delay_days"] = all_delays
        df_sorted = df.sort_values(by="abs_delay_days").head(5)

        print("=== Top 5 Closest Gaia Stars to the SETI Ellipsoid Surface Today ===")
        for idx, row in df_sorted.iterrows():
            print(
                f"Star ID: {int(row['source_id'])} | RA: {row['ra']:.4f}° | Dec: {row['dec']:.4f}° | "
                f"Dist: {row['dist_pc']:.1f} pc | G mag: {row['phot_g_mean_mag']:.2f} | "
                f"Delay: {row['delay_days']:+.1f} days"
            )

    except Exception as err:
        print(f"❌ Gaia DR3 query error: {err}")


if __name__ == "__main__":
    main()
