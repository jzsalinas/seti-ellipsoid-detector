"""
Gaia DR3 Data Provider.

Queries ESA Gaia DR3 via astroquery using ADQL to retrieve astrometric data
and calculate stellar distances in parsecs. Includes mock support for offline testing.
"""

from typing import Optional
import numpy as np
import pandas as pd

from config import DEFAULT_MAX_MAGNITUDE


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
    # Parallax between 0.5 mas (2000 pc) and 20 mas (50 pc)
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

    Args:
        ra_center: Target Right Ascension in degrees.
        dec_center: Target Declination in degrees.
        radius_deg: Search cone radius in degrees.
        max_magnitude: Maximum G-band magnitude threshold (faintest stars to include).
        row_limit: Maximum number of rows to return from ADQL query.
        use_mock: If True, returns mock data for offline testing without querying ESA servers.

    Returns:
        pandas.DataFrame with columns:
        ['source_id', 'ra', 'dec', 'parallax', 'dist_pc', 'pmra', 'pmdec', 'phot_g_mean_mag']
    """
    if use_mock:
        return _generate_mock_gaia_data(
            ra_center=ra_center,
            dec_center=dec_center,
            radius_deg=radius_deg,
            row_limit=min(row_limit, 50),
        )

    try:
        from astroquery.gaia import Gaia
    except ImportError as err:
        raise ImportError(
            "astroquery is required for Gaia queries. Install via pip install astroquery."
        ) from err

    adql_query = f"""
    SELECT TOP {row_limit}
        source_id, ra, dec, parallax, pmra, pmdec, phot_g_mean_mag
    FROM gaiadr3.gaia_source
    WHERE 1=CONTAINS(
        POINT('ICRS', ra, dec),
        CIRCLE('ICRS', {ra_center}, {dec_center}, {radius_deg})
    )
      AND parallax > 0.1
      AND parallax_over_error > 5
      AND phot_g_mean_mag <= {max_magnitude}
    ORDER BY phot_g_mean_mag ASC
    """

    job = Gaia.launch_job_async(adql_query)
    results_table = job.get_results()
    df = results_table.to_pandas()

    if df.empty:
        df["dist_pc"] = []
        return df

    # Convert parallax (mas) to distance in parsecs (pc)
    df["dist_pc"] = 1000.0 / df["parallax"]

    return df[
        ["source_id", "ra", "dec", "parallax", "dist_pc", "pmra", "pmdec", "phot_g_mean_mag"]
    ]
