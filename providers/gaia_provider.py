"""
Gaia DR3 Data Provider.

Queries ESA Gaia DR3 via pyvo using indexed ADQL to retrieve astrometric data
and calculate stellar distances in parsecs. Includes mirror fallback and mock support.
"""

from typing import Optional
import numpy as np
import pandas as pd

from config import DEFAULT_MAX_MAGNITUDE

TAP_MIRRORS = [
    ("https://gea.esac.esa.int/tap-server/tap", "gaiadr3.gaia_source"),
    ("https://gaia.aip.de/tap", "gaiadr3.gaia_source"),
    ("https://dc.g-vo.org/tap", "gaia.dr3_source"),
]


def _generate_mock_gaia_data(
    ra_center: float,
    dec_center: float,
    radius_deg: float,
    row_limit: int = 50,
) -> pd.DataFrame:
    """Generates synthetic Gaia candidates around center coordinates for testing."""
    np.random.seed(42)
    ra = ra_center + np.random.uniform(-radius_deg, radius_deg, row_limit)
    dec = dec_center + np.random.uniform(-radius_deg, radius_deg, row_limit)
    parallax = np.random.uniform(0.5, 20.0, row_limit)
    dist_pc = 1000.0 / parallax
    phot_g_mean_mag = np.random.uniform(8.0, 15.5, row_limit)
    source_id = np.arange(1000000, 1000000 + row_limit, dtype=np.int64)

    df = pd.DataFrame(
        {
            "source_id": source_id,
            "ra": ra,
            "dec": dec,
            "parallax": parallax,
            "dist_pc": dist_pc,
            "pmra": np.random.uniform(-5.0, 5.0, row_limit),
            "pmdec": np.random.uniform(-5.0, 5.0, row_limit),
            "phot_g_mean_mag": phot_g_mean_mag,
        }
    )
    return df


def get_candidate_stars(
    ra_center: float,
    dec_center: float,
    radius_deg: float,
    max_magnitude: float = DEFAULT_MAX_MAGNITUDE,
    row_limit: int = 500,
    use_mock: bool = False,
) -> pd.DataFrame:
    """
    Retrieves stellar candidates from Gaia DR3 around target spherical coordinates.
    Uses indexed RA/Dec bounding box for instant TAP query execution.
    """
    if use_mock:
        return _generate_mock_gaia_data(
            ra_center=ra_center,
            dec_center=dec_center,
            radius_deg=radius_deg,
            row_limit=min(row_limit, 50),
        )

    # Compute bounding box using RA/Dec indexing for maximum TAP query speed
    cos_dec = max(np.abs(np.cos(np.radians(dec_center))), 0.1)
    ra_min = (ra_center - radius_deg / cos_dec) % 360.0
    ra_max = (ra_center + radius_deg / cos_dec) % 360.0
    dec_min = max(dec_center - radius_deg, -90.0)
    dec_max = min(dec_center + radius_deg, 90.0)

    import pyvo as vo

    last_error = None
    for tap_url, table_name in TAP_MIRRORS:
        try:
            if ra_min < ra_max:
                ra_clause = f"ra BETWEEN {ra_min:.6f} AND {ra_max:.6f}"
            else:
                ra_clause = f"(ra >= {ra_min:.6f} OR ra <= {ra_max:.6f})"

            adql_query = f"""
            SELECT TOP {row_limit}
                source_id, ra, dec, parallax, pmra, pmdec, phot_g_mean_mag
            FROM {table_name}
            WHERE {ra_clause}
              AND dec BETWEEN {dec_min:.6f} AND {dec_max:.6f}
              AND parallax > 0.1
              AND parallax_over_error > 3
              AND phot_g_mean_mag <= {max_magnitude}
            ORDER BY phot_g_mean_mag ASC
            """

            service = vo.dal.TAPService(tap_url)
            results = service.search(adql_query)
            df = results.to_table().to_pandas()

            if df.empty:
                df["dist_pc"] = []
                return df

            df["parallax"] = df["parallax"].astype(float)
            df["dist_pc"] = 1000.0 / df["parallax"]

            cols = ["source_id", "ra", "dec", "parallax", "dist_pc", "pmra", "pmdec", "phot_g_mean_mag"]
            for col in cols:
                if col not in df.columns:
                    df[col] = 0.0

            return df[cols]
        except Exception as err:
            last_error = err
            print(f"Warning: TAP Query to {tap_url} failed ({err}). Trying next mirror...")

    raise RuntimeError(f"All Gaia DR3 TAP mirrors failed. Last error: {last_error}")
