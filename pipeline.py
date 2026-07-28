"""
SETI Ellipsoid Detector Main Pipeline Orchestrator.

Integrates 3D geometry engine, Gaia DR3 provider, Fink Broker alerts,
IsolationForest anomaly detection, and Telegram notifications into a unified workflow.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
import pandas as pd

from config import (
    SN1987A_RA_DEG,
    SN1987A_DEC_DEG,
    SN1987A_DISTANCE_PC,
    SN1987A_EPOCH,
    DEFAULT_TOLERANCE_DAYS,
    DEFAULT_MAX_MAGNITUDE,
)
from core.geometry import is_in_ellipsoid_shell
from core.anomaly_engine import AnomalyEvaluator
from providers.gaia_provider import get_candidate_stars
from providers.fink_provider import fetch_alerts_for_coordinates
from notifier.telegram_bot import send_alert


def run_pipeline(
    ra_center: float = SN1987A_RA_DEG,
    dec_center: float = SN1987A_DEC_DEG,
    radius_deg: float = 1.0,
    current_date: Optional[str] = None,
    tolerance_days: float = DEFAULT_TOLERANCE_DAYS,
    anomaly_threshold: float = 0.85,
    max_magnitude: float = DEFAULT_MAX_MAGNITUDE,
    use_mock: bool = False,
    telegram_bot_token: Optional[str] = None,
    telegram_chat_id: Optional[str] = None,
) -> pd.DataFrame:
    """
    Runs the end-to-end SETI Ellipsoid Detector pipeline.

    1. Fetches candidate stars from Gaia DR3.
    2. Filters stars located on the active SETI Ellipsoid shell today.
    3. Fetches photometric lightcurve history from Fink Broker for shell candidates.
    4. Evaluates anomaly scores using IsolationForest.
    5. Dispatches alerts for candidates surpassing the anomaly threshold.

    Returns:
        pandas.DataFrame with full evaluation results.
    """
    if current_date is None:
        current_date = datetime.now(timezone.utc).isoformat()

    print(f"=== Starting SETI Ellipsoid Detector Pipeline ===")
    print(f"Target Center: RA={ra_center}°, Dec={dec_center}°, Radius={radius_deg}°")
    print(f"Observation Date: {current_date}")
    print(f"Shell Tolerance: ±{tolerance_days} days | Anomaly Threshold: {anomaly_threshold}")
    print(f"Mock Mode: {use_mock}\n")

    # Step 1: Query Gaia DR3 candidate stars
    print("[1/4] Querying Gaia DR3 candidates...")
    candidates_df = get_candidate_stars(
        ra_center=ra_center,
        dec_center=dec_center,
        radius_deg=radius_deg,
        max_magnitude=max_magnitude,
        use_mock=use_mock,
    )

    if candidates_df.empty:
        print("No candidates found from Gaia query.")
        return pd.DataFrame()

    print(f"Retrieved {len(candidates_df)} stars from Gaia.")

    # Step 2: Compute 3D SETI Ellipsoid Geometry
    print("[2/4] Computing 3D SETI Ellipsoid shell crossing...")
    is_inside, delay_days = is_in_ellipsoid_shell(
        ra_deg=candidates_df["ra"],
        dec_deg=candidates_df["dec"],
        dist_pc=candidates_df["dist_pc"],
        current_date=current_date,
        tolerance_days=tolerance_days,
    )

    candidates_df["is_inside_shell"] = is_inside
    candidates_df["delay_days"] = delay_days

    shell_candidates = candidates_df[candidates_df["is_inside_shell"]].copy()
    print(f"Found {len(shell_candidates)} / {len(candidates_df)} stars active on the SETI Ellipsoid shell.")

    if shell_candidates.empty:
        print("No candidates currently fall on the active shell. Pipeline execution complete.")
        candidates_df["anomaly_score"] = 0.0
        candidates_df["alert_triggered"] = False
        return candidates_df

    # Step 3: Fetch Fink photometric light curves & Evaluate Anomalies
    print("[3/4] Fetching light curves and scoring anomalies...")
    evaluator = AnomalyEvaluator()

    anomaly_scores = []
    alerts_triggered = []

    for idx, row in shell_candidates.iterrows():
        star_id = str(row["source_id"])
        ra = float(row["ra"])
        dec = float(row["dec"])

        # Fetch Fink light curve
        lc_df = fetch_alerts_for_coordinates(ra=ra, dec=dec, use_mock=use_mock)

        # Extract features and compute anomaly score
        features = evaluator.extract_features(lc_df)
        score = evaluator.compute_anomaly_score(features)
        anomaly_scores.append(score)

        # Step 4: Dispatch alert if score exceeds threshold
        triggered = score >= anomaly_threshold
        alerts_triggered.append(triggered)

        if triggered:
            print(f"🚨 ANOMALY DETECTED! Star {star_id} (Score: {score:.4f} >= {anomaly_threshold})")
            send_alert(
                star_id=star_id,
                anomaly_score=score,
                lightcurve_df=lc_df,
                ra=ra,
                dec=dec,
                bot_token=telegram_bot_token,
                chat_id=telegram_chat_id,
            )

    shell_candidates["anomaly_score"] = anomaly_scores
    shell_candidates["alert_triggered"] = alerts_triggered

    print(f"\n[4/4] Pipeline Complete. {sum(alerts_triggered)} alerts dispatched.")
    return shell_candidates


if __name__ == "__main__":
    # Test run end-to-end pipeline with synthetic mock data
    results = run_pipeline(
        radius_deg=2.0,
        tolerance_days=10000.0,  # Wide tolerance for mock verification
        anomaly_threshold=0.60,
        use_mock=True,
    )
    print("\nSample Output Results:")
    print(results[["source_id", "ra", "dec", "dist_pc", "delay_days", "anomaly_score", "alert_triggered"]].head())
