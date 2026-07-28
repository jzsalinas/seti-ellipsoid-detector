"""
Live Fink Broker Ingestion & Anomaly Scoring Test.

Queries real-time transient alerts from Fink Broker REST API, extracts photometric light curves,
evaluates anomaly scores via IsolationForest, and generates plots.
"""

import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from providers.fink_provider import fetch_latest_anomalies, fetch_alerts_for_coordinates
from core.anomaly_engine import AnomalyEvaluator
from notifier.telegram_bot import generate_lightcurve_plot


def main():
    print("=== LIVE FINK BROKER INGESTION & ANOMALY EVALUATION ===")
    print("Querying latest anomalous alerts from Fink Broker REST API...\n")

    try:
        df_latests = fetch_latest_anomalies(n_alerts=15, anomaly_class="Anomaly", use_mock=False)

        if df_latests.empty:
            print("Fink API returned no latest alerts for 'Anomaly' class. Trying fallback 'Supernova'...")
            df_latests = fetch_latest_anomalies(n_alerts=15, anomaly_class="Supernova", use_mock=False)

        if df_latests.empty:
            print("Fink API returned empty response. Running with mock data for demonstration.")
            df_latests = fetch_latest_anomalies(n_alerts=15, use_mock=True)

        print(f"✅ Ingested {len(df_latests)} live alerts from Fink Broker.")
        print(f"Alert columns: {list(df_latests.columns)[:10]}\n")

        evaluator = AnomalyEvaluator()
        scored_objects = []

        # Process each unique object
        object_col = "objectId" if "objectId" in df_latests.columns else df_latests.columns[0]
        unique_objects = df_latests[object_col].unique()[:5]

        for obj_id in unique_objects:
            obj_df = df_latests[df_latests[object_col] == obj_id].copy()

            features = evaluator.extract_features(obj_df)
            score = evaluator.compute_anomaly_score(features)

            plot_path = generate_lightcurve_plot(
                star_id=str(obj_id),
                lightcurve_df=obj_df,
                anomaly_score=score,
            )

            scored_objects.append(
                {
                    "objectId": obj_id,
                    "n_points": len(obj_df),
                    "mag_std": round(features["mag_std"], 3),
                    "mag_range": round(features["mag_range"], 3),
                    "color_g_r": round(features["color_g_r"], 3),
                    "Anomaly Score": round(score, 4),
                    "Plot Path": plot_path,
                }
            )

        df_summary = pd.DataFrame(scored_objects)
        print("=== EVALUATED TRANSIENTS SUMMARY ===")
        print(df_summary[["objectId", "n_points", "mag_std", "mag_range", "Anomaly Score"]].to_string(index=False))
        print(f"\nPlots saved to scratch/ directory.")

    except Exception as err:
        print(f"❌ Fink test error: {err}")


if __name__ == "__main__":
    main()
