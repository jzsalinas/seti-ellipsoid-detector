"""
Live Continuous SETI Ellipsoid Alert Monitoring & Telegram Dispatcher Daemon.

Usage:
    python scripts/run_live_monitor.py [--once]
"""

import argparse
from datetime import datetime, timezone
import os
import sys
import time
import pandas as pd

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import DEFAULT_MAX_MAGNITUDE
from core.anchor import AlienLatencyProfile, get_latency_tolerance_days
from core.master_catalog import MasterCatalogGenerator, PriorityTier
from notifier.telegram_bot import send_alert
from providers.gaia_provider import get_candidate_stars


def run_monitoring_iteration(
    use_mock: bool,
    latency_profile: str,
    anomaly_threshold: float,
    bot_token: str,
    chat_id: str,
):
    current_time_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"\n================================================================================")
    print(f"🛰️ SETI Ellipsoid Monitoring Iteration | {current_time_str}")
    print(f"================================================================================")

    profile_enum = AlienLatencyProfile.BUREAUCRATIC
    if latency_profile.upper() in AlienLatencyProfile.__members__:
        profile_enum = AlienLatencyProfile[latency_profile.upper()]

    generator = MasterCatalogGenerator(latency_profile=profile_enum, use_mock=use_mock)

    print(f"1. Querying Gaia DR3 target stars (Mock: {use_mock})...")
    stars_df = get_candidate_stars(
        ra_center=83.8667,
        dec_center=-69.2697,
        radius_deg=2.0,
        max_magnitude=DEFAULT_MAX_MAGNITUDE,
        use_mock=use_mock,
    )

    if stars_df.empty:
        print("No Gaia DR3 stars returned in query region.")
        return

    print(f"2. Synthesizing 5-Layer Master Catalog for {len(stars_df)} candidate stars...")
    master_df = generator.build_catalog(stars_df, inject_synthetic_signals=use_mock)

    if master_df.empty:
        print("No candidate stars currently crossing active ellipsoid shells.")
        return

    print(f"✨ Evaluated {len(master_df)} active shell stars. Top candidates:\n")
    cols = ["source_id", "dist_pc", "anchors_hit_count", "is_dyson_candidate", "is_radio_candidate", "priority_score", "priority_tier"]
    print(master_df[cols].head(5).to_string(index=False))

    # Identify targets exceeding alert threshold or classified as CRITICAL/HIGH_PRIORITY
    alerts_df = master_df[master_df["priority_score"] >= (anomaly_threshold * 100.0)]

    if alerts_df.empty:
        print("\nℹ️ No candidate surpassed priority alert threshold.")
    else:
        print(f"\n🚨 {len(alerts_df)} HIGH PRIORITY SETI ANOMALIES DETECTED!")
        for _, row in alerts_df.iterrows():
            star_id = str(row["source_id"])
            score = float(row["priority_score"]) / 100.0
            ra = float(row["ra"])
            dec = float(row["dec"])

            # Dummy lightcurve df for Telegram plot generation
            lc_df = pd.DataFrame(
                {
                    "jd": [2460000.5 + i for i in range(10)],
                    "magpsf": [14.0 + (0.1 * (i % 3)) for i in range(10)],
                    "sigmagpsf": [0.02] * 10,
                    "filter": ["g" if i % 2 == 0 else "r" for i in range(10)],
                }
            )

            print(f"  -> Dispatching Telegram Alert for {star_id} (Score: {score:.4f})...")
            send_alert(
                star_id=star_id,
                anomaly_score=score,
                lightcurve_df=lc_df,
                ra=ra,
                dec=dec,
                bot_token=bot_token,
                chat_id=chat_id,
            )


def main():
    parser = argparse.ArgumentParser(description="Live SETI Ellipsoid Alert Monitoring Daemon")
    parser.add_argument("--once", action="store_true", help="Run a single iteration and exit")
    args = parser.parse_args()

    # Read settings from environment (.env)
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    latency_profile = os.environ.get("OBSERVATION_LATENCY_PROFILE", "bureaucratic")
    anomaly_threshold = float(os.environ.get("ANOMALY_THRESHOLD", "0.40"))
    poll_interval = int(os.environ.get("POLL_INTERVAL_SECONDS", "300"))
    use_mock_str = os.environ.get("USE_MOCK_DATA", "true").lower()
    use_mock = use_mock_str in ("true", "1", "yes")

    print("================================================================================")
    print("🛰️ SETI Ellipsoid Detector Continuous Live Monitoring Daemon")
    print("================================================================================")
    print(f"Telegram Config : Token={'[CONFIGURED]' if bot_token and 'your_' not in bot_token else '[MISSING]'}, ChatID={'[CONFIGURED]' if chat_id and 'your_' not in chat_id else '[MISSING]'}")
    print(f"Latency Profile : {latency_profile}")
    print(f"Alert Threshold : {anomaly_threshold}")
    print(f"Poll Interval   : {poll_interval} seconds")
    print(f"Mock Data Mode  : {use_mock}")
    print("================================================================================\n")

    if args.once:
        run_monitoring_iteration(use_mock, latency_profile, anomaly_threshold, bot_token, chat_id)
        return

    print("🔄 Starting live continuous monitoring loop (Ctrl+C to stop)...")
    try:
        while True:
            run_monitoring_iteration(use_mock, latency_profile, anomaly_threshold, bot_token, chat_id)
            print(f"\n💤 Sleeping for {poll_interval} seconds until next iteration...")
            time.sleep(poll_interval)
    except KeyboardInterrupt:
        print("\n🛑 Monitoring daemon stopped by user.")


if __name__ == "__main__":
    main()
