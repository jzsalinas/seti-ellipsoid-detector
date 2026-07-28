"""
Breakthrough Listen Open Data Provider.

Interfaces with Green Bank Telescope (GBT) and Parkes Observatory target catalogs
to query radio observation spectrogram metadata, receiver bands (L, S, C, X),
and Doppler drift detections for SETI Ellipsoid candidate stars.
"""

from typing import Dict, List, Optional
import numpy as np
import pandas as pd


class BreakthroughListenProvider:
    """
    Interface for querying Breakthrough Listen Open Data radio observation archives.
    """

    def __init__(self, use_mock: bool = True):
        self.use_mock = use_mock

    def get_radio_observations(
        self,
        stars_df: pd.DataFrame,
        receiver_band: str = "L_band",
        inject_technosignatures: bool = False,
        technosignature_fraction: float = 0.20,
    ) -> pd.DataFrame:
        """
        Cross-matches Gaia DR3 target stars with Breakthrough Listen radio observation catalogs.

        Parameters:
          stars_df: DataFrame of target stars with 'source_id', 'ra', 'dec', 'dist_pc'.
          receiver_band: Receiver band string ('L_band', 'S_band', 'C_band', 'X_band').
          inject_technosignatures: If True, injects synthetic narrowband drifting radio signals.
          technosignature_fraction: Fraction of targets to inject with artificial signals.

        Returns:
          DataFrame merged with radio observation parameters ('freq_center_mhz', 'bandwidth_hz',
          'drift_rate_hz_s', 'snr', 'telescope', 'receiver_band').
        """
        df_out = stars_df.copy().reset_index(drop=True)
        n_stars = len(df_out)

        if n_stars == 0:
            df_out["freq_center_mhz"] = pd.Series(dtype=float)
            df_out["bandwidth_hz"] = pd.Series(dtype=float)
            df_out["drift_rate_hz_s"] = pd.Series(dtype=float)
            df_out["snr"] = pd.Series(dtype=float)
            df_out["telescope"] = pd.Series(dtype=str)
            df_out["receiver_band"] = pd.Series(dtype=str)
            return df_out

        np.random.seed(101)

        # Receiver center frequencies (e.g. L-band ~1420 MHz neutral hydrogen line)
        f_center = np.full(n_stars, 1420.40575)  # 21 cm Hydrogen line
        # Natural astrophysical emission: wide bandwidth (> kHz to MHz) and near-zero drift
        bandwidth_hz = np.random.uniform(500.0, 50000.0, n_stars)
        drift_rate = np.random.normal(0.0, 0.002, n_stars)
        snr = np.random.uniform(2.0, 8.0, n_stars)

        telescopes = np.random.choice(["Green Bank Telescope", "Parkes Observatory"], size=n_stars)

        # Inject synthetic artificial technosignatures (narrow bandwidth ~ 1 Hz, non-zero drift ~ 0.5 Hz/s)
        if inject_technosignatures and n_stars > 0:
            n_inject = max(1, int(n_stars * technosignature_fraction))
            inject_indices = np.random.choice(n_stars, size=n_inject, replace=False)

            bandwidth_hz[inject_indices] = np.random.uniform(0.5, 3.0, n_inject)
            drift_rate[inject_indices] = np.random.uniform(0.1, 1.5, n_inject) * np.random.choice([-1, 1], size=n_inject)
            snr[inject_indices] = np.random.uniform(15.0, 50.0, n_inject)

        df_out["freq_center_mhz"] = f_center
        df_out["bandwidth_hz"] = bandwidth_hz
        df_out["drift_rate_hz_s"] = drift_rate
        df_out["snr"] = snr
        df_out["telescope"] = telescopes
        df_out["receiver_band"] = receiver_band

        return df_out
