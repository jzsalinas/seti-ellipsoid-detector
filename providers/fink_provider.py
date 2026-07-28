"""
Fink Broker Streaming Data Provider.

Queries Fink Broker REST API and simulates real-time Kafka alert streams to retrieve
photometric alert history, light curve data (g and r filters), and anomaly classifications
for target stars on active SETI Ellipsoid shells.
"""

from typing import Dict, List, Optional
import numpy as np
import pandas as pd
import requests


FINK_EXPLORER_URL = "https://fink-portal.org/api/v1/explorer"
FINK_LATESTS_URL = "https://fink-portal.org/api/v1/latests"


def _generate_mock_fink_alerts(
    ra: float,
    dec: float,
    n_points: int = 20,
) -> pd.DataFrame:
    """Generates synthetic photometric light curves for testing."""
    np.random.seed(42)
    # Julian Dates over 100 days
    start_jd = 2460000.5
    jd = start_jd + np.sort(np.random.uniform(0, 100, n_points))
    # Filter 1 (g-band) or 2 (r-band)
    fid = np.random.choice([1, 2], size=n_points)
    base_mag = 15.0 + (fid * 0.2)
    # Add subtle brightness variation and noise
    magpsf = base_mag + 0.1 * np.sin(jd / 10.0) + np.random.normal(0, 0.03, n_points)
    sigmagpsf = np.full(n_points, 0.02)

    df = pd.DataFrame(
        {
            "objectId": [f"ZTF26mock{i:03d}" for i in range(n_points)],
            "jd": jd,
            "ra": ra,
            "dec": dec,
            "fid": fid,
            "filter": np.where(fid == 1, "g", "r"),
            "magpsf": magpsf,
            "sigmagpsf": sigmagpsf,
            "classification": "Anomaly",
        }
    )
    return df


def fetch_alerts_for_coordinates(
    ra: float,
    dec: float,
    radius_arcsec: float = 3.0,
    timeout_sec: float = 10.0,
    use_mock: bool = False,
) -> pd.DataFrame:
    """
    Queries Fink Broker REST API for photometric alerts near specified RA, Dec coordinates.
    """
    if use_mock:
        return _generate_mock_fink_alerts(ra=ra, dec=dec)

    payload = {
        "ra": str(ra),
        "dec": str(dec),
        "radius": str(radius_arcsec),
        "output_format": "json",
    }

    try:
        response = requests.post(FINK_EXPLORER_URL, json=payload, timeout=timeout_sec)
        response.raise_for_status()
        data = response.json()
        if not data:
            return pd.DataFrame()
        df = pd.DataFrame(data)
        if "fid" in df.columns:
            df["filter"] = df["fid"].map({1: "g", 2: "r"}).fillna("unknown")
        return df
    except (requests.RequestException, ValueError) as err:
        print(f"Warning: Fink Broker API request failed ({err}). Returning empty DataFrame.")
        return pd.DataFrame()


def fetch_latest_anomalies(
    n_alerts: int = 50,
    anomaly_class: str = "Anomaly",
    timeout_sec: float = 10.0,
    use_mock: bool = False,
) -> pd.DataFrame:
    """
    Queries Fink Broker REST API for latest alerts classified as anomalous or specific transients.
    """
    if use_mock:
        return _generate_mock_fink_alerts(ra=83.8667, dec=-69.2697, n_points=n_alerts)

    payload = {
        "class": anomaly_class,
        "n": str(n_alerts),
        "output_format": "json",
    }

    try:
        response = requests.post(FINK_LATESTS_URL, json=payload, timeout=timeout_sec)
        response.raise_for_status()
        data = response.json()
        if not data:
            return pd.DataFrame()
        df = pd.DataFrame(data)
        if "fid" in df.columns:
            df["filter"] = df["fid"].map({1: "g", 2: "r"}).fillna("unknown")
        return df
    except (requests.RequestException, ValueError) as err:
        print(f"Warning: Fink Broker latests API request failed ({err}). Returning empty DataFrame.")
        return pd.DataFrame()


class FinkProvider:
    """
    Class interface for real-time streaming and batch ingestion of Fink photometric alert streams.
    """

    def __init__(self, use_mock: bool = True):
        self.use_mock = use_mock

    def stream_candidate_alerts(
        self,
        candidates_df: pd.DataFrame,
        radius_arcsec: float = 3.0,
    ) -> Dict[str, pd.DataFrame]:
        """
        Streams / retrieves photometric alert histories for a list of candidate stars.

        Parameters:
          candidates_df: DataFrame containing 'source_id', 'ra', 'dec'.

        Returns:
          Dictionary mapping source_id -> light curve DataFrame.
        """
        light_curves = {}
        for _, row in candidates_df.iterrows():
            source_id = str(row.get("source_id", f"RA{row['ra']:.2f}_DEC{row['dec']:.2f}"))
            lc = fetch_alerts_for_coordinates(
                ra=row["ra"],
                dec=row["dec"],
                radius_arcsec=radius_arcsec,
                use_mock=self.use_mock,
            )
            light_curves[source_id] = lc
        return light_curves
