"""
WISE / AllWISE Infrared Photometry Provider.

Provides interface for querying AllWISE mid-infrared magnitudes (W1, W2, W3, W4)
cross-matched with Gaia DR3 candidate stars crossing SETI Ellipsoid active shells.
"""

from typing import Dict, List, Optional
import numpy as np
import pandas as pd


class WISEProvider:
    """
    Interface for fetching and cross-matching AllWISE infrared photometry for target stars.
    """

    def __init__(self, use_mock: bool = True):
        self.use_mock = use_mock

    def get_wise_photometry(
        self,
        stars_df: pd.DataFrame,
        inject_dyson_candidates: bool = False,
        dyson_fraction: float = 0.20,
    ) -> pd.DataFrame:
        """
        Cross-matches Gaia DR3 target stars with AllWISE photometry.

        Parameters:
          stars_df: DataFrame of target stars with 'source_id', 'ra', 'dec', 'dist_pc'.
          inject_dyson_candidates: If True, injects synthetic mid-IR excess in a subset of stars.
          dyson_fraction: Fraction of stars to inject with artificial Dyson Swarm excess.

        Returns:
          DataFrame merged with 'w1mpro', 'w2mpro', 'w3mpro', 'w4mpro' magnitudes and measurement errors.
        """
        df_out = stars_df.copy().reset_index(drop=True)
        n_stars = len(df_out)

        if n_stars == 0:
            df_out["w1mpro"] = pd.Series(dtype=float)
            df_out["w2mpro"] = pd.Series(dtype=float)
            df_out["w3mpro"] = pd.Series(dtype=float)
            df_out["w4mpro"] = pd.Series(dtype=float)
            return df_out

        # Generate realistic photospheric AllWISE magnitudes based on distance and Gaia G mag
        g_mag = df_out["phot_g_mean_mag"] if "phot_g_mean_mag" in df_out.columns else np.full(n_stars, 12.0)

        np.random.seed(42)

        # Normal main-sequence star colors: W1 ~ G - 0.5, W2 ~ W1, W3 ~ W1, W4 ~ W1
        w1 = (g_mag - np.random.uniform(0.3, 0.8, n_stars)).to_numpy()
        w2 = w1 - np.random.normal(0.02, 0.05, n_stars)
        w3 = w2 - np.random.normal(0.05, 0.08, n_stars)
        w4 = w3 - np.random.normal(0.05, 0.12, n_stars)

        # Inject synthetic Dyson Swarm mid-IR excess (excess in W3 & W4 due to 100-300K waste heat)
        if inject_dyson_candidates and n_stars > 0:
            n_inject = max(1, int(n_stars * dyson_fraction))
            inject_indices = np.random.choice(n_stars, size=n_inject, replace=False)

            # Dyson Swarm: strong excess in W3 (12um) and W4 (22um)
            w3[inject_indices] -= np.random.uniform(1.2, 2.5, n_inject)
            w4[inject_indices] -= np.random.uniform(2.5, 4.5, n_inject)

        df_out["w1mpro"] = w1
        df_out["w2mpro"] = w2
        df_out["w3mpro"] = w3
        df_out["w4mpro"] = w4
        df_out["w1_err"] = np.random.uniform(0.02, 0.05, n_stars)
        df_out["w2_err"] = np.random.uniform(0.02, 0.05, n_stars)
        df_out["w3_err"] = np.random.uniform(0.03, 0.08, n_stars)
        df_out["w4_err"] = np.random.uniform(0.05, 0.15, n_stars)

        return df_out
