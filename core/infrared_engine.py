"""
Infrared Excess Detection & Dyson Swarm Technosignature Engine.

Calculates mid-infrared colors (W1, W2, W3, W4 at 3.4, 4.6, 12, 22 um), evaluates expected
stellar blackbody continuum, and identifies infrared excess candidates indicative of ETI waste-heat
megastructures (Dyson Swarms / Spheres) on active SETI Ellipsoid stars.
"""

from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd


# Standard AllWISE wavelength definitions (in micrometers)
WISE_WAVELENGTHS_UM = {
    "w1": 3.4,
    "w2": 4.6,
    "w3": 12.0,
    "w4": 22.0,
}

# Thresholds for significant mid-infrared excess (Dyson Swarm candidate criteria)
DEFAULT_W3_W4_EXCESS_THRESHOLD: float = 1.0   # mag excess in (W3 - W4)
DEFAULT_W1_W4_EXCESS_THRESHOLD: float = 2.5   # mag excess in (W1 - W4)


def calculate_infrared_colors(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates standard WISE infrared color indices for a DataFrame containing W1, W2, W3, W4 magnitudes.

    Parameters:
      df: DataFrame containing 'w1mpro', 'w2mpro', 'w3mpro', 'w4mpro' (or 'w1', 'w2', 'w3', 'w4').

    Returns:
      DataFrame with added color columns: 'w1_w2', 'w2_w3', 'w3_w4', 'w1_w4'.
    """
    df_out = df.copy()

    w1 = df_out["w1mpro"] if "w1mpro" in df_out.columns else df_out["w1"]
    w2 = df_out["w2mpro"] if "w2mpro" in df_out.columns else df_out["w2"]
    w3 = df_out["w3mpro"] if "w3mpro" in df_out.columns else df_out["w3"]
    w4 = df_out["w4mpro"] if "w4mpro" in df_out.columns else df_out["w4"]

    df_out["w1_w2"] = w1 - w2
    df_out["w2_w3"] = w2 - w3
    df_out["w3_w4"] = w3 - w4
    df_out["w1_w4"] = w1 - w4

    return df_out


def estimate_expected_w3_w4_color(w1_w2: Union[float, np.ndarray, pd.Series]) -> Union[float, np.ndarray, pd.Series]:
    """
    Estimates expected photospheric baseline (W3 - W4) color for normal stars based on (W1 - W2).

    Normal main-sequence stars have Rayleigh-Jeans behavior in mid-IR where (W1 - W2) ~ 0 and (W3 - W4) ~ 0.
    """
    return 0.05 + 0.2 * np.maximum(0.0, w1_w2)


def evaluate_dyson_swarm_excess(
    df: pd.DataFrame,
    w3_w4_threshold: float = DEFAULT_W3_W4_EXCESS_THRESHOLD,
    w1_w4_threshold: float = DEFAULT_W1_W4_EXCESS_THRESHOLD,
) -> pd.DataFrame:
    """
    Evaluates infrared excess significance and tags candidate stars showing mid-IR excess
    characteristic of waste heat from circumstellar artificial megastructures (Dyson Swarms).

    Returns DataFrame with added columns:
      - 'expected_w3_w4': Expected stellar photospheric color.
      - 'excess_w3_w4': Observed minus expected (W3 - W4) excess in magnitudes.
      - 'is_dyson_candidate': Boolean mask for Dyson Swarm technosignature candidates.
      - 'ir_excess_score': Normalized excess score.
    """
    df_colored = calculate_infrared_colors(df)

    w1_w2 = df_colored["w1_w2"]
    w3_w4 = df_colored["w3_w4"]
    w1_w4 = df_colored["w1_w4"]

    expected_w3_w4 = estimate_expected_w3_w4_color(w1_w2)
    excess_w3_w4 = w3_w4 - expected_w3_w4

    # Candidate criteria: significant deviation in W3-W4 and W1-W4 from normal photosphere
    is_dyson_candidate = (excess_w3_w4 >= w3_w4_threshold) & (w1_w4 >= w1_w4_threshold)

    # Score scaling: normalized ratio over threshold
    ir_excess_score = np.maximum(0.0, excess_w3_w4 / w3_w4_threshold)

    df_colored["expected_w3_w4"] = expected_w3_w4
    df_colored["excess_w3_w4"] = excess_w3_w4
    df_colored["is_dyson_candidate"] = is_dyson_candidate
    df_colored["ir_excess_score"] = ir_excess_score

    return df_colored.sort_values(by="ir_excess_score", ascending=False)
