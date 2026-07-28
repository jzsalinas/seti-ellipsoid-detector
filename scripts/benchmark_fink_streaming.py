"""
Benchmark Script: Fink Broker Real-Time Alert Streaming & Anomaly Monitoring (EXP-009).

Simulates continuous streaming ingestion of Fink photometric alert light curves (g and r filters),
evaluates IsolationForest anomaly scores for active SETI Ellipsoid candidates, and dispatches alerts.
"""

import os
import sys
import numpy as np
import pandas as pd

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.anchor import AlienLatencyProfile
from providers.pulsar_provider import PulsarProvider
from providers.wise_provider import WISEProvider
from providers.fink_provider import FinkProvider
from core.geometry import find_multi_anchor_intersections
from core.infrared_engine import evaluate_dyson_swarm_excess
from core.anomaly_engine import AnomalyEvaluator


def generate_synthetic_gaia_catalog(n_stars: int = 500) -> pd.DataFrame:
    """Generates synthetic Gaia stars for streaming benchmark testing."""
    np.random.seed(303)
    ra = np.random.uniform(0, 360, n_stars)
    dec = np.random.uniform(-90, 90, n_stars)
    dist = np.random.uniform(50, 2500.0, n_stars)
    source_ids = [f"GAIA_DR3_{4000000 + i}" for i in range(n_stars)]

    return pd.DataFrame(
        {
            "source_id": source_ids,
            "ra": ra,
            "dec": dec,
            "dist_pc": dist,
            "phot_g_mean_mag": np.random.uniform(9.0, 15.5, n_stars),
        }
    )


def run_fink_streaming_benchmark():
    print("================================================================================")
    print("⚡ SETI Ellipsoid Detector: Fink Real-Time Streaming Benchmark (EXP-009)")
    print("================================================================================\n")

    provider = PulsarProvider()
    anchors = provider.list_anchors()

    print(f"🛰️ Loaded {len(anchors)} Cosmic Anchors:")
    for a in anchors:
        print(f"  - [{a.anchor_type.value:17s}] {a.id:20s}: {a.name}")

    print("\n🌟 Generating synthetic Gaia stellar catalog (500 stars up to 2,500 pc)...")
    stars_df = generate_synthetic_gaia_catalog(n_stars=500)

    obs_date = "2026-07-28T00:00:00"
    tolerance_days = AlienLatencyProfile.BUREAUCRATIC.value  # ±730 days (~2 years)

    print(f"\n🔍 [Layer 1] Filtering active SETI Ellipsoid candidates (Tolerance: ±{tolerance_days:.0f} days)...")
    ellipsoid_candidates = find_multi_anchor_intersections(
        df=stars_df,
        current_date=obs_date,
        anchors=anchors,
        tolerance_days=tolerance_days,
        min_anchors_hit=1,
    )
    print(f"✨ Found {len(ellipsoid_candidates)} stars currently crossing active ellipsoid shells.")

    print("\n🔭 [Layer 2] Querying AllWISE mid-IR photometry...")
    wise_provider = WISEProvider(use_mock=True)
    wise_df = wise_provider.get_wise_photometry(ellipsoid_candidates, inject_dyson_candidates=True, dyson_fraction=0.50)
    ir_evaluated_df = evaluate_dyson_swarm_excess(wise_df)

    print("\n⚡ [Layer 3] Streaming Fink Broker photometric alert light curves (g and r filters)...")
    fink_provider = FinkProvider(use_mock=True)
    fink_streams = fink_provider.stream_candidate_alerts(ir_evaluated_df)

    evaluator = AnomalyEvaluator()

    results = []
    print("\n🤖 Scoring photometric light curve anomaly vectors using IsolationForest:\n")
    print(f"{'Source ID':18s} | {'Dist (pc)':10s} | {'Dyson Candidate':16s} | {'Stream Alerts':14s} | {'Anomaly Score':13s}")
    print("-" * 80)

    for idx, row in ir_evaluated_df.iterrows():
        source_id = str(row["source_id"])
        dist_pc = float(row["dist_pc"])
        is_dyson = bool(row["is_dyson_candidate"])

        lc_df = fink_streams.get(source_id, pd.DataFrame())
        n_alerts = len(lc_df)

        features = evaluator.extract_features(lc_df)
        score = evaluator.compute_anomaly_score(features)

        print(f"{source_id:18s} | {dist_pc:10.1f} | {str(is_dyson):16s} | {n_alerts:14d} | {score:13.4f}")

        results.append(
            {
                "source_id": source_id,
                "dist_pc": dist_pc,
                "ra": row["ra"],
                "dec": row["dec"],
                "is_dyson_candidate": is_dyson,
                "excess_w3_w4": row["excess_w3_w4"],
                "stream_alert_count": n_alerts,
                "anomaly_score": score,
            }
        )

    results_df = pd.DataFrame(results).sort_values(by="anomaly_score", ascending=False)

    out_csv = os.path.abspath("scratch/fink_streaming_candidates_exp009.csv")
    results_df.to_csv(out_csv, index=False)
    print(f"\n✅ Streaming Benchmark Complete! Results exported to: {out_csv}")
    return results_df


if __name__ == "__main__":
    run_fink_streaming_benchmark()
