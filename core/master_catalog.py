"""
SETI Ellipsoid Candidate Master Catalog Generator & 5-Layer Synthesizer.

Aggregates 3D light-delay geometry (Layer 1), AllWISE mid-IR excess (Layer 2),
Fink photometric alert stream ML anomalies (Layer 3), Breakthrough Listen narrowband radio drift (Layer 4),
and APF optical laser pulses (Layer 5) into a unified public priority catalog for SETI observatories.
"""

from enum import Enum
import json
import os
from typing import Dict, List, Optional, Union
import numpy as np
import pandas as pd

from core.anchor import CosmicAnchor, AlienLatencyProfile, get_latency_tolerance_days
from providers.pulsar_provider import PulsarProvider
from providers.wise_provider import WISEProvider
from providers.fink_provider import FinkProvider
from providers.breakthrough_provider import BreakthroughListenProvider
from providers.apf_provider import APFProvider
from core.geometry import find_multi_anchor_intersections
from core.infrared_engine import evaluate_dyson_swarm_excess
from core.anomaly_engine import AnomalyEvaluator
from core.radio_engine import evaluate_radio_technosignatures
from core.optical_engine import evaluate_optical_technosignatures


class PriorityTier(Enum):
    CRITICAL_TARGET = "CRITICAL_TARGET"   # Priority Score >= 75
    HIGH_PRIORITY = "HIGH_PRIORITY"       # Priority Score >= 50
    MEDIUM_PRIORITY = "MEDIUM_PRIORITY"   # Priority Score >= 25
    SHELL_MONITOR = "SHELL_MONITOR"       # Priority Score < 25


def calculate_composite_priority_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates composite SETI Priority Score (0.0 to 100.0) combining all 5 evaluation layers.

    Weights:
      - Layer 1 (Geometry & Multi-Anchor Hits): 20%
      - Layer 2 (Mid-IR Waste Heat Excess): 20%
      - Layer 3 (Optical Light Curve Anomaly): 20%
      - Layer 4 (Narrowband Radio Technosignature): 20%
      - Layer 5 (Pulsed Monochromatic Laser): 20%
    """
    df_out = df.copy()

    # Layer 1 score (based on anchors_hit_count and RMS delay)
    hits = df_out.get("anchors_hit_count", pd.Series(np.ones(len(df_out))))
    l1_score = np.clip(hits * 10.0, 0.0, 20.0)

    # Layer 2 score (mid-IR excess)
    ir_score = df_out.get("ir_excess_score", pd.Series(np.zeros(len(df_out))))
    l2_score = np.clip(ir_score * 15.0, 0.0, 20.0)

    # Layer 3 score (Fink light curve anomaly score)
    anom_score = df_out.get("anomaly_score", pd.Series(np.zeros(len(df_out))))
    l3_score = np.clip(anom_score * 20.0, 0.0, 20.0)

    # Layer 4 score (Radio technosignature score)
    radio_score = df_out.get("radio_technosignature_score", pd.Series(np.zeros(len(df_out))))
    l4_score = np.clip(radio_score * 0.8, 0.0, 20.0)

    # Layer 5 score (Optical laser score)
    opt_score = df_out.get("optical_technosignature_score", pd.Series(np.zeros(len(df_out))))
    l5_score = np.clip(opt_score * 1.5, 0.0, 20.0)

    composite_score = l1_score + l2_score + l3_score + l4_score + l5_score

    # Assign Priority Tiers
    tiers = []
    for s in composite_score:
        if s >= 75.0:
            tiers.append(PriorityTier.CRITICAL_TARGET.value)
        elif s >= 50.0:
            tiers.append(PriorityTier.HIGH_PRIORITY.value)
        elif s >= 25.0:
            tiers.append(PriorityTier.MEDIUM_PRIORITY.value)
        else:
            tiers.append(PriorityTier.SHELL_MONITOR.value)

    df_out["l1_score"] = l1_score
    df_out["l2_score"] = l2_score
    df_out["l3_score"] = l3_score
    df_out["l4_score"] = l4_score
    df_out["l5_score"] = l5_score
    df_out["priority_score"] = composite_score
    df_out["priority_tier"] = tiers

    return df_out.sort_values(by="priority_score", ascending=False)


class MasterCatalogGenerator:
    """
    Synthesizes multi-layer SETI evaluations into a unified Candidate Master Catalog.
    """

    def __init__(
        self,
        anchors: Optional[List[CosmicAnchor]] = None,
        latency_profile: AlienLatencyProfile = AlienLatencyProfile.BUREAUCRATIC,
        use_mock: bool = True,
    ):
        provider = PulsarProvider()
        self.anchors = anchors if anchors else provider.list_anchors()
        self.tolerance_days = get_latency_tolerance_days(latency_profile)
        self.use_mock = use_mock

        self.wise_provider = WISEProvider(use_mock=use_mock)
        self.fink_provider = FinkProvider(use_mock=use_mock)
        self.radio_provider = BreakthroughListenProvider(use_mock=use_mock)
        self.apf_provider = APFProvider(use_mock=use_mock)
        self.anomaly_evaluator = AnomalyEvaluator()

    def build_catalog(
        self,
        stars_df: pd.DataFrame,
        current_date: str = "2026-07-28T00:00:00",
        inject_synthetic_signals: bool = True,
    ) -> pd.DataFrame:
        """
        Executes end-to-end 5-layer synthesis pipeline and generates ranked Master Catalog.
        """
        if stars_df.empty:
            return pd.DataFrame()

        # Layer 1: Geometry & Multi-Anchor Intersection
        l1_df = find_multi_anchor_intersections(
            df=stars_df,
            current_date=current_date,
            anchors=self.anchors,
            tolerance_days=self.tolerance_days,
            min_anchors_hit=1,
        )
        if l1_df.empty:
            return pd.DataFrame()

        # Layer 2: AllWISE Mid-IR Excess
        wise_df = self.wise_provider.get_wise_photometry(l1_df, inject_dyson_candidates=inject_synthetic_signals)
        l2_df = evaluate_dyson_swarm_excess(wise_df)

        # Layer 3: Fink Broker ML Anomaly Scores
        fink_streams = self.fink_provider.stream_candidate_alerts(l2_df)
        anom_scores = []
        for _, r in l2_df.iterrows():
            sid = str(r["source_id"])
            lc = fink_streams.get(sid, pd.DataFrame())
            feats = self.anomaly_evaluator.extract_features(lc)
            anom_scores.append(self.anomaly_evaluator.compute_anomaly_score(feats))
        l2_df["anomaly_score"] = anom_scores

        # Layer 4: Breakthrough Listen Radio Technosignatures
        radio_df = self.radio_provider.get_radio_observations(l2_df, inject_technosignatures=inject_synthetic_signals)
        l4_df = evaluate_radio_technosignatures(radio_df)

        # Layer 5: APF Pulsed Optical Lasers
        optical_df = self.apf_provider.get_optical_spectra(l4_df, inject_laser_pulses=inject_synthetic_signals)
        l5_df = evaluate_optical_technosignatures(optical_df)

        # Composite Synthesis
        master_df = calculate_composite_priority_score(l5_df)
        return master_df

    def export_catalog(
        self,
        master_df: pd.DataFrame,
        csv_path: str = "scratch/seti_ellipsoid_master_catalog.csv",
        json_path: str = "scratch/seti_ellipsoid_master_catalog.json",
    ) -> Tuple[str, str]:
        """
        Exports the master catalog to standardized CSV and JSON artifact files.
        """
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        master_df.to_csv(csv_path, index=False)

        # Build JSON metadata export
        catalog_dict = {
            "metadata": {
                "generated_at": "2026-07-28T00:00:00Z",
                "total_candidates": len(master_df),
                "critical_targets": int((master_df["priority_tier"] == PriorityTier.CRITICAL_TARGET.value).sum()),
                "high_priority_targets": int((master_df["priority_tier"] == PriorityTier.HIGH_PRIORITY.value).sum()),
            },
            "candidates": master_df.to_dict(orient="records"),
        }

        with open(json_path, "w") as f:
            json.dump(catalog_dict, f, indent=2, default=str)

        return os.path.abspath(csv_path), os.path.abspath(json_path)
