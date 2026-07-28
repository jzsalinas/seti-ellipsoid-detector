"""
SETI Ellipsoid 3D Geometric Engine.

Calculates 3D spatial geometry and light travel time delays for stars relative to
a supernova event (by default SN 1987A) to determine if target stars lie on the
active SETI Ellipsoid surface shell.
"""

from datetime import datetime, timezone
from typing import Tuple, Union
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

    Formula:
      d0 = Earth-to-Supernova distance
      d1 = Earth-to-Star distance
      d2 = Supernova-to-Star distance
      Geometric delay (light years) = d1 + d2 - d0
      Elapsed time since SN signal reached Earth (years) = (current_date - sn_epoch) / 365.2425 days
      Delay (days) = (Geometric delay - Elapsed time) * 365.2425

    Positive delay_days: Light shell has not reached star yet (in the future).
    Negative delay_days: Light shell passed star in the past.
    Near zero: Star is currently inside the ellipsoid shell.
    """
    # 3D Position of Supernova
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

    Returns:
      (is_inside, delay_days)
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
