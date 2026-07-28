"""
Fink Broker Data Provider.

Queries Fink Broker REST API to retrieve real-time photometric alert history,
light curve data (g and r filters), and anomaly classifications.
"""

from typing import Optional
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

    Args:
        ra: Right Ascension in degrees.
        dec: Declination in degrees.
        radius_arcsec: Cone search radius in arcseconds.
        timeout_sec: Request timeout in seconds.
        use_mock: If True, returns mock light curve data for offline testing.

    Returns:
        pandas.DataFrame containing alert photometry history.
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
        # Fallback empty dataframe on request failure
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

    Args:
        n_alerts: Number of alerts to retrieve.
        anomaly_class: Classification label ('Anomaly', 'Supernova', 'Microlensing', etc.)
        timeout_sec: Request timeout in seconds.
        use_mock: If True, returns mock data for testing.
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
