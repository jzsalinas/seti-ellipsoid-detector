"""
Radio Technosignature & Doppler Drift Rate Engine.

Evaluates high-resolution radio spectral data (Breakthrough Listen GBT / Parkes observations),
calculates Doppler drift rates (Hz/s) caused by planetary/orbital motion, narrowband signal widths (Hz),
and identifies artificial radio technosignature candidates on active SETI Ellipsoid stars.
"""

from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd


# Breakthrough Listen receiver band frequency ranges (in GHz)
BREAKTHROUGH_RECEIVER_BANDS = {
    "L_band": (1.10, 1.90),    # 1.10 - 1.90 GHz (Green Bank Telescope / Parkes)
    "S_band": (1.80, 2.80),    # 1.80 - 2.80 GHz
    "C_band": (3.95, 8.00),    # 3.95 - 8.00 GHz
    "X_band": (7.80, 11.20),   # 7.80 - 11.20 GHz
}

# Standard thresholds for artificial narrow-band radio technosignatures
DEFAULT_MAX_BANDWIDTH_HZ: float = 5.0       # Maximum narrow-band signal width in Hz (natural is > kHz)
DEFAULT_MIN_DRIFT_RATE_HZ_S: float = 0.01   # Minimum non-zero Doppler drift rate in Hz/s
DEFAULT_MAX_DRIFT_RATE_HZ_S: float = 4.00   # Maximum plausible planetary Doppler drift rate in Hz/s
DEFAULT_MIN_SNR: float = 10.0               # Minimum Signal-to-Noise Ratio


def calculate_doppler_drift_rate(
    f0_mhz: Union[float, np.ndarray, pd.Series],
    accel_m_s2: Union[float, np.ndarray, pd.Series],
) -> Union[float, np.ndarray, pd.Series]:
    """
    Calculates line-of-sight Doppler drift rate in Hz/s resulting from planetary or orbital acceleration.

    Formula:
      drift_rate (Hz/s) = - (f0 * 1e6 Hz) * (accel / c)
    """
    c_m_s = 299792458.0  # Speed of light in m/s
    f0_hz = f0_mhz * 1e6
    return -f0_hz * (accel_m_s2 / c_m_s)


def evaluate_radio_technosignatures(
    df: pd.DataFrame,
    max_bandwidth_hz: float = DEFAULT_MAX_BANDWIDTH_HZ,
    min_drift_rate: float = DEFAULT_MIN_DRIFT_RATE_HZ_S,
    max_drift_rate: float = DEFAULT_MAX_DRIFT_RATE_HZ_S,
    min_snr: float = DEFAULT_MIN_SNR,
) -> pd.DataFrame:
    """
    Evaluates radio signals for narrowband width, Doppler drift, and SNR characteristic of artificial technosignatures.

    Parameters:
      df: DataFrame containing 'freq_center_mhz', 'bandwidth_hz', 'drift_rate_hz_s', 'snr'.

    Returns:
      DataFrame with added columns:
        - 'is_narrowband': Boolean mask for signal width <= max_bandwidth_hz.
        - 'is_drifting': Boolean mask for non-zero Doppler drift within plausible bounds.
        - 'is_radio_candidate': Boolean mask for candidate artificial radio technosignatures.
        - 'radio_technosignature_score': Normalized significance score.
    """
    df_out = df.copy()

    bw = df_out["bandwidth_hz"]
    drift = np.abs(df_out["drift_rate_hz_s"])
    snr = df_out["snr"]

    is_narrowband = bw <= max_bandwidth_hz
    is_drifting = (drift >= min_drift_rate) & (drift <= max_drift_rate)
    is_high_snr = snr >= min_snr

    is_radio_candidate = is_narrowband & is_drifting & is_high_snr

    # Score calculation: SNR weighted by narrowness and non-zero drift significance
    score = np.where(
        is_radio_candidate,
        (snr / min_snr) * (max_bandwidth_hz / np.maximum(0.1, bw)),
        0.0,
    )

    df_out["is_narrowband"] = is_narrowband
    df_out["is_drifting"] = is_drifting
    df_out["is_radio_candidate"] = is_radio_candidate
    df_out["radio_technosignature_score"] = score

    return df_out.sort_values(by="radio_technosignature_score", ascending=False)
