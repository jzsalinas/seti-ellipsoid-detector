"""
Pulsed Optical Technosignature & Laser Emission Engine.

Evaluates high-resolution optical spectra (APF / Lick Observatory Levy Spectrograph),
calculates monochromatic emission line widths (Angstroms), peak-to-continuum flux contrast ratios,
and identifies artificial pulsed laser technosignatures on active SETI Ellipsoid stars.
"""

from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd


# Wavelength range for APF Levy Spectrograph (in Angstroms)
APF_WAVELENGTH_RANGE_ANGSTROM = (3740.0, 9700.0)

# Default thresholds for artificial pulsed optical laser technosignatures
DEFAULT_MAX_LINEWIDTH_ANGSTROM: float = 0.05   # Maximum line width in Angstroms (ultra-monochromatic)
DEFAULT_MIN_PEAK_RATIO: float = 5.0             # Minimum peak-to-continuum flux ratio
DEFAULT_MIN_PULSE_SIGMA: float = 8.0            # Minimum statistical significance in std deviations


def evaluate_optical_technosignatures(
    df: pd.DataFrame,
    max_linewidth_angstrom: float = DEFAULT_MAX_LINEWIDTH_ANGSTROM,
    min_peak_ratio: float = DEFAULT_MIN_PEAK_RATIO,
    min_pulse_sigma: float = DEFAULT_MIN_PULSE_SIGMA,
) -> pd.DataFrame:
    """
    Evaluates optical spectra for monochromatic emission spikes, high contrast ratio, and significance
    characteristic of artificial pulsed optical laser technosignatures.

    Parameters:
      df: DataFrame containing 'peak_wavelength_a', 'linewidth_a', 'peak_to_continuum_ratio', 'pulse_sigma'.

    Returns:
      DataFrame with added columns:
        - 'is_monochromatic': Boolean mask for linewidth <= max_linewidth_angstrom.
        - 'is_high_contrast': Boolean mask for peak_to_continuum_ratio >= min_peak_ratio.
        - 'is_optical_candidate': Boolean mask for candidate optical laser technosignatures.
        - 'optical_technosignature_score': Normalized significance score.
    """
    df_out = df.copy()

    lw = df_out["linewidth_a"]
    ratio = df_out["peak_to_continuum_ratio"]
    sigma = df_out["pulse_sigma"]

    is_monochromatic = lw <= max_linewidth_angstrom
    is_high_contrast = ratio >= min_peak_ratio
    is_significant = sigma >= min_pulse_sigma

    is_optical_candidate = is_monochromatic & is_high_contrast & is_significant

    # Score calculation: weighted by peak contrast and narrowness
    score = np.where(
        is_optical_candidate,
        (ratio / min_peak_ratio) * (sigma / min_pulse_sigma) * (max_linewidth_angstrom / np.maximum(0.001, lw)),
        0.0,
    )

    df_out["is_monochromatic"] = is_monochromatic
    df_out["is_high_contrast"] = is_high_contrast
    df_out["is_optical_candidate"] = is_optical_candidate
    df_out["optical_technosignature_score"] = score

    return df_out.sort_values(by="optical_technosignature_score", ascending=False)
