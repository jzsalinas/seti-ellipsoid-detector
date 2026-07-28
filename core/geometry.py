"""
SETI Ellipsoid 3D Geometric Engine.

Calculates 3D spatial geometry and light travel time delays for stars relative to
supernova and discrete cosmic anchors (pulsar glitches, magnetar giant flares)
to determine single-shell and multi-anchor intersection candidates.
"""

from datetime import datetime, timezone
from typing import Dict, List, Tuple, Union
import numpy as np
import pandas as pd

from config import (
    SN1987A_RA_DEG,
    SN1987A_DEC_DEG,
    SN1987A_DISTANCE_PC,
    SN1987A_EPOCH,
    PARSEC_TO_LIGHT_YEAR,
    DAYS_PER_YEAR,
    DEFAULT_TOLERANCE_DAYS,
)
from core.anchor import CosmicAnchor


def spherical_to_cartesian(
    ra_deg: Union[float, np.ndarray, pd.Series],
    dec_deg: Union[float, np.ndarray, pd.Series],
    dist_pc: Union[float, np.ndarray, pd.Series],
) -> Tuple[
    Union[float, np.ndarray, pd.Series],
    Union[float, np.ndarray, pd.Series],
    Union[float, np.ndarray, pd.Series],
]:
    """
    Converts spherical coordinates (RA, Dec in degrees, distance in parsecs)
    to 3D Cartesian coordinates (x, y, z) in parsecs (ICRS frame).
    """
    ra_rad = np.radians(ra_deg)
    dec_rad = np.radians(dec_deg)

    x = dist_pc * np.cos(dec_rad) * np.cos(ra_rad)
    y = dist_pc * np.cos(dec_rad) * np.sin(ra_rad)
    z = dist_pc * np.sin(dec_rad)

    return x, y, z


def _parse_datetime(date_val: Union[str, datetime]) -> datetime:
    """Parses string or datetime object into UTC datetime."""
    if isinstance(date_val, str):
        dt = datetime.fromisoformat(date_val)
    elif isinstance(date_val, datetime):
        dt = date_val
    else:
        raise ValueError(f"Invalid date format: {date_val}")

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def calculate_ellipsoid_delay(
    ra_deg: Union[float, np.ndarray, pd.Series],
    dec_deg: Union[float, np.ndarray, pd.Series],
    dist_pc: Union[float, np.ndarray, pd.Series],
    current_date: Union[str, datetime],
    sn_ra: float = SN1987A_RA_DEG,
    sn_dec: float = SN1987A_DEC_DEG,
    sn_dist_pc: float = SN1987A_DISTANCE_PC,
    sn_epoch: datetime = SN1987A_EPOCH,
) -> Union[float, np.ndarray, pd.Series]:
    """
    Calculates the deviation in days between the observation time and the exact time
    the supernova ellipsoid light shell reaches the star's position.
    """
    # 3D Position of Anchor
    xe, ye, ze = spherical_to_cartesian(sn_ra, sn_dec, sn_dist_pc)

    # 3D Position of Target Star(s)
    xs, ys, zs = spherical_to_cartesian(ra_deg, dec_deg, dist_pc)

    # Distances
    d0 = sn_dist_pc
    d1 = dist_pc
    d2 = np.sqrt((xs - xe) ** 2 + (ys - ye) ** 2 + (zs - ze) ** 2)

    # Geometric path length difference in parsecs -> converted to light-years
    path_diff_pc = d1 + d2 - d0
    geometric_delay_ly = path_diff_pc * PARSEC_TO_LIGHT_YEAR

    # Elapsed time from SN light arrival to current_date
    obs_dt = _parse_datetime(current_date)
    epoch_dt = _parse_datetime(sn_epoch)

    elapsed_seconds = (obs_dt - epoch_dt).total_seconds()
    elapsed_days = elapsed_seconds / 86400.0
    elapsed_years = elapsed_days / DAYS_PER_YEAR

    # Deviation from current observation date in days
    delay_years = geometric_delay_ly - elapsed_years
    delay_days = delay_years * DAYS_PER_YEAR

    return delay_days


def is_in_ellipsoid_shell(
    ra_deg: Union[float, np.ndarray, pd.Series],
    dec_deg: Union[float, np.ndarray, pd.Series],
    dist_pc: Union[float, np.ndarray, pd.Series],
    current_date: Union[str, datetime],
    tolerance_days: float = DEFAULT_TOLERANCE_DAYS,
    sn_ra: float = SN1987A_RA_DEG,
    sn_dec: float = SN1987A_DEC_DEG,
    sn_dist_pc: float = SN1987A_DISTANCE_PC,
    sn_epoch: datetime = SN1987A_EPOCH,
) -> Tuple[Union[bool, np.ndarray, pd.Series], Union[float, np.ndarray, pd.Series]]:
    """
    Determines if star(s) are inside the active SETI Ellipsoid shell within tolerance_days.
    """
    delay_days = calculate_ellipsoid_delay(
        ra_deg=ra_deg,
        dec_deg=dec_deg,
        dist_pc=dist_pc,
        current_date=current_date,
        sn_ra=sn_ra,
        sn_dec=sn_dec,
        sn_dist_pc=sn_dist_pc,
        sn_epoch=sn_epoch,
    )

    is_inside = np.abs(delay_days) <= tolerance_days
    return is_inside, delay_days


def calculate_multi_anchor_delays(
    ra_deg: Union[float, np.ndarray, pd.Series],
    dec_deg: Union[float, np.ndarray, pd.Series],
    dist_pc: Union[float, np.ndarray, pd.Series],
    current_date: Union[str, datetime],
    anchors: List[CosmicAnchor],
) -> pd.DataFrame:
    """
    Calculates ellipsoid light travel delays for a list of CosmicAnchors.

    Returns a Pandas DataFrame where each column corresponds to an anchor's delay in days.
    """
    delays_dict = {}
    for anchor in anchors:
        col_name = f"delay_{anchor.id}"
        delays_dict[col_name] = calculate_ellipsoid_delay(
            ra_deg=ra_deg,
            dec_deg=dec_deg,
            dist_pc=dist_pc,
            current_date=current_date,
            sn_ra=anchor.ra_deg,
            sn_dec=anchor.dec_deg,
            sn_dist_pc=anchor.distance_pc,
            sn_epoch=anchor.epoch,
        )
    return pd.DataFrame(delays_dict)


def calculate_multi_anchor_rms_delay(
    delays_df: pd.DataFrame,
) -> Union[float, np.ndarray, pd.Series]:
    """
    Computes the Root Mean Square (RMS) deviation across N anchor delays.

    Formula:
      RMS_Delay = sqrt( (1 / N) * sum( delay_i^2 ) )
    """
    squared_sums = (delays_df ** 2).sum(axis=1)
    n_anchors = delays_df.shape[1]
    if n_anchors == 0:
        return np.zeros(len(delays_df))
    return np.sqrt(squared_sums / float(n_anchors))


def find_multi_anchor_intersections(
    df: pd.DataFrame,
    current_date: Union[str, datetime],
    anchors: List[CosmicAnchor],
    tolerance_days: float = DEFAULT_TOLERANCE_DAYS,
    min_anchors_hit: int = 2,
    max_rms_days: Optional[float] = None,
) -> pd.DataFrame:
    """
    Filters and scores target stars from a DataFrame that intersect multiple cosmic anchors.

    Parameters:
      df: DataFrame containing stellar coordinates ('ra', 'dec', and 'dist_pc' or 'distance_gspphot').
      current_date: Observation epoch for calculation.
      anchors: List of CosmicAnchor objects.
      tolerance_days: Maximum absolute delay (in days) to consider a star on an anchor's shell.
      min_anchors_hit: Minimum number of anchors a star must intersect simultaneously.
      max_rms_days: Optional maximum threshold for overall multi-anchor RMS delay.

    Returns:
      DataFrame containing candidate stars with calculated delay columns, 'anchors_hit_count',
      and 'rms_delay_days', filtered according to criteria.
    """
    df_out = df.copy()

    # Normalize distance column name
    if "dist_pc" in df_out.columns:
        dist_series = df_out["dist_pc"]
    elif "distance_gspphot" in df_out.columns:
        dist_series = df_out["distance_gspphot"]
    elif "distance_pc" in df_out.columns:
        dist_series = df_out["distance_pc"]
    else:
        raise ValueError("DataFrame must contain 'dist_pc', 'distance_gspphot', or 'distance_pc'")

    ra_series = df_out["ra"] if "ra" in df_out.columns else df_out["ra_deg"]
    dec_series = df_out["dec"] if "dec" in df_out.columns else df_out["dec_deg"]

    # Calculate delays for all anchors
    delays_df = calculate_multi_anchor_delays(
        ra_deg=ra_series,
        dec_deg=dec_series,
        dist_pc=dist_series,
        current_date=current_date,
        anchors=anchors,
    )

    # Count how many anchor shells each star falls inside
    hits_matrix = np.abs(delays_df) <= tolerance_days
    anchors_hit_count = hits_matrix.sum(axis=1)

    # Calculate RMS delay across all anchors
    rms_delay_days = calculate_multi_anchor_rms_delay(delays_df)

    # Attach columns
    for col in delays_df.columns:
        df_out[col] = delays_df[col]

    df_out["anchors_hit_count"] = anchors_hit_count
    df_out["rms_delay_days"] = rms_delay_days

    # Filter criteria
    mask = df_out["anchors_hit_count"] >= min_anchors_hit
    if max_rms_days is not None:
        mask = mask & (df_out["rms_delay_days"] <= max_rms_days)

    return df_out[mask].sort_values(by=["anchors_hit_count", "rms_delay_days"], ascending=[False, True])
