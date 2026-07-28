"""
Anomaly Engine Benchmark & Technosignature Injection Test.

Generates 1,000 synthetic stellar light curves, injecting 50 anomalous technosignature signals:
1. Deep erratic dips (Tabby's star style artificial transits).
2. Periodic high-intensity optical beacon pulses.
3. Rapid color fluctuations (g - r).

Evaluates Precision, Recall, F1-Score, and ROC-AUC of the IsolationForest model.
"""

from typing import Tuple, List, Dict
import os
import sys
import numpy as np
import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.anomaly_engine import AnomalyEvaluator


def generate_benchmark_dataset(
    n_normal: int = 950,
    n_anomalous: int = 50,
) -> Tuple[List[pd.DataFrame], np.ndarray]:
    """Generates synthetic light curve dataset with ground truth anomaly labels."""
    np.random.seed(42)
    lightcurves = []
    labels = []  # 0 for normal, 1 for anomaly

    # 1. Normal Stars (stable photometry with minor Gaussian noise)
    for i in range(n_normal):
        n_pts = np.random.randint(15, 40)
        jd = 2460000.5 + np.sort(np.random.uniform(0, 150, n_pts))
        fid = np.random.choice([1, 2], size=n_pts)
        base_mag = 14.0 + (fid * 0.1)
        magpsf = base_mag + np.random.normal(0, 0.02, n_pts)

        df = pd.DataFrame(
            {
                "jd": jd,
                "fid": fid,
                "filter": np.where(fid == 1, "g", "r"),
                "magpsf": magpsf,
            }
        )
        lightcurves.append(df)
        labels.append(0)

    # 2. Anomalous Stars (Technosignatures & Transients)
    for i in range(n_anomalous):
        n_pts = np.random.randint(20, 50)
        jd = 2460000.5 + np.sort(np.random.uniform(0, 150, n_pts))
        fid = np.random.choice([1, 2], size=n_pts)
        base_mag = 14.0 + (fid * 0.1)
        magpsf = base_mag + np.random.normal(0, 0.03, n_pts)

        anomaly_type = i % 3
        if anomaly_type == 0:
            # Type A: Tabby's star deep erratic dip (up to 2 magnitudes drop)
            dip_mask = (jd > 2460050.0) & (jd < 2460070.0)
            magpsf[dip_mask] += np.random.uniform(0.8, 2.5, np.sum(dip_mask))
        elif anomaly_type == 1:
            # Type B: High-intensity optical pulse / beacon spikes
            spike_idx = np.random.choice(n_pts, size=min(3, n_pts), replace=False)
            magpsf[spike_idx] -= np.random.uniform(1.2, 3.0, len(spike_idx))
        else:
            # Type C: Extreme color variation (g - r)
            g_mask = fid == 1
            magpsf[g_mask] += np.random.uniform(0.5, 1.5, np.sum(g_mask))

        df = pd.DataFrame(
            {
                "jd": jd,
                "fid": fid,
                "filter": np.where(fid == 1, "g", "r"),
                "magpsf": magpsf,
            }
        )
        lightcurves.append(df)
        labels.append(1)

    return lightcurves, np.array(labels)


def main():
    print("=== ANOMALY EVALUATOR BENCHMARK & TECHNOSIGNATURE TEST ===")
    print("Generating dataset: 950 Normal Stars vs 50 Injected Anomalies...")

    lightcurves, y_true = generate_benchmark_dataset(n_normal=950, n_anomalous=50)

    evaluator = AnomalyEvaluator(contamination=0.05)

    # Fit evaluator on feature matrix
    feature_list = [evaluator.extract_features(df) for df in lightcurves]
    feature_df = pd.DataFrame(feature_list)

    evaluator.fit(feature_df)

    # Compute anomaly scores
    y_scores = np.array([evaluator.compute_anomaly_score(feats) for feats in feature_list])

    # Threshold classification at score >= 0.65
    threshold = 0.65
    y_pred = (y_scores >= threshold).astype(int)

    # Metrics
    prec = precision_score(y_true, y_pred)
    rec = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    roc_auc = roc_auc_score(y_true, y_scores)

    print(f"\n=== MODEL BENCHMARK METRICS (Threshold = {threshold}) ===")
    print(f"Total Evaluated Stars: {len(y_true)}")
    print(f"True Anomalies: {sum(y_true)} | Predicted Anomalies: {sum(y_pred)}")
    print(f"Precision: {prec * 100:.2f}%")
    print(f"Recall:    {rec * 100:.2f}%")
    print(f"F1-Score:  {f1:.4f}")
    print(f"ROC-AUC:   {roc_auc:.4f}")

    # Display Top 5 Highest Scored Anomalies
    df_results = pd.DataFrame(
        {
            "Star Index": np.arange(len(y_true)),
            "Ground Truth": y_true,
            "Anomaly Score": y_scores,
            "Predicted": y_pred,
        }
    )

    top_anomalies = df_results.sort_values(by="Anomaly Score", ascending=False).head(10)
    print("\n=== TOP 10 HIGHEST SCORED CANDIDATES ===")
    print(top_anomalies.to_string(index=False))


if __name__ == "__main__":
    main()
