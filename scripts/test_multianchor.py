"""
Multi-Anchor Historic Supernovae Live Field Test.

Evaluates Gaia DR3 stars against multiple historical supernova anchors:
- SN 1987A (LMC)
- SN 1572 (Tycho's Supernova)
- SN 1604 (Kepler's Supernova)
- SN 1054 (Crab Supernova)
"""

from datetime import datetime, timezone
import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import HISTORIC_SUPERNOVAE
from core.geometry import is_in_ellipsoid_shell
from providers.gaia_provider import get_candidate_stars


def main():
    current_date = datetime.now(timezone.utc).isoformat()

    print("=== MULTI-ANCHOR HISTORIC SUPERNOVAE LIVE FIELD TEST ===")
    print(f"Observation Date: {current_date}\n")

    summary_rows = []

    for sn_id, sn_info in HISTORIC_SUPERNOVAE.items():
        name = sn_info["name"]
        ra = sn_info["ra_deg"]
        dec = sn_info["dec_deg"]
        d0 = sn_info["distance_pc"]
        epoch = sn_info["epoch"]

        print(f"📡 Querying Gaia DR3 for Anchor: {name}")
        print(f"   Coords: RA={ra:.4f}°, Dec={dec:.4f}° | Dist: {d0:.0f} pc | Epoch: {epoch.strftime('%Y-%m-%d')}")

        try:
            df = get_candidate_stars(
                ra_center=ra,
                dec_center=dec,
                radius_deg=2.0,
                max_magnitude=15.5,
                row_limit=500,
                use_mock=False,
            )

            if df.empty:
                print("   No stars returned for this cone.")
                continue

            # Evaluate ellipsoid delay for this supernova
            is_inside, delay_days = is_in_ellipsoid_shell(
                ra_deg=df["ra"],
                dec_deg=df["dec"],
                dist_pc=df["dist_pc"],
                current_date=current_date,
                tolerance_days=365.0,  # 1 year shell tolerance window
                sn_ra=ra,
                sn_dec=dec,
                sn_dist_pc=d0,
                sn_epoch=epoch,
            )

            df["delay_days"] = delay_days
            df["is_inside_shell"] = is_inside
            active_count = sum(is_inside)

            min_delay = df["delay_days"].abs().min()

            print(f"   Fetched {len(df)} stars | Active in ±1 year shell: {active_count}")
            print(f"   Closest star to exact surface delay: {min_delay:.1f} days\n")

            summary_rows.append(
                {
                    "Anchor": sn_id,
                    "Name": name,
                    "Total Stars": len(df),
                    "Active Shell Stars (±1yr)": active_count,
                    "Min Delay (days)": round(min_delay, 1),
                }
            )

        except Exception as err:
            print(f"   ❌ Query failed for {name}: {err}\n")

    summary_df = pd.DataFrame(summary_rows)
    print("=== MULTI-ANCHOR SUMMARY RESULTS ===")
    print(summary_df.to_string(index=False))


if __name__ == "__main__":
    main()
