"""
Unit tests for core/geometry.py.
"""

from datetime import datetime, timezone, timedelta
import numpy as np
import pandas as pd
import pytest

from config import (
    SN1987A_RA_DEG,
    SN1987A_DEC_DEG,
    SN1987A_DISTANCE_PC,
    SN1987A_EPOCH,
    PARSEC_TO_LIGHT_YEAR,
    DAYS_PER_YEAR,
)
from core.geometry import (
    spherical_to_cartesian,
    calculate_ellipsoid_delay,
    is_in_ellipsoid_shell,
)


def test_spherical_to_cartesian_basic():
    # RA = 0, Dec = 0, dist = 100
    x, y, z = spherical_to_cartesian(0.0, 0.0, 100.0)
    assert pytest.approx(x, abs=1e-5) == 100.0
    assert pytest.approx(y, abs=1e-5) == 0.0
    assert pytest.approx(z, abs=1e-5) == 0.0

    # Dec = 90 (North pole)
    x, y, z = spherical_to_cartesian(45.0, 90.0, 50.0)
    assert pytest.approx(x, abs=1e-5) == 0.0
    assert pytest.approx(y, abs=1e-5) == 0.0
    assert pytest.approx(z, abs=1e-5) == 50.0


def test_exact_ellipsoid_point():
    """
    Construct a synthetic star along the line of sight to SN 1987A.
    If the star is closer to Earth than SN 1987A by 10 light years (in path difference),
    then 10 years after SN 1987A epoch, its delay should be ~ 0 days.
    """
    sn_epoch = SN1987A_EPOCH
    # 10 light-years in parsecs
    delay_ly = 10.0
    delay_pc = delay_ly / PARSEC_TO_LIGHT_YEAR

    # Star directly along SN line of sight at d1 = (d0 - delay_pc / 2)
    # Since SN is at d0, star at S along line of sight has d2 = d0 - d1 = delay_pc / 2
    # d1 + d2 - d0 = d1 + (d0 - d1) - d0 = 0? Wait!
    # For a star directly on the line of sight between Earth and SN:
    # d1 + d2 = d0, so d1 + d2 - d0 = 0.
    # For a star behind SN along line of sight: d1 = d0 + delta, d2 = delta => d1 + d2 - d0 = 2 delta.

    # Let's test a star behind Earth in opposite direction:
    # SN at (RA, Dec, d0), Star at (-SN_RA, -SN_Dec, d1).
    # Or simply compute d1, d2 explicitly:
    d0 = SN1987A_DISTANCE_PC
    # Place star such that d1 = 100 pc, d2 = 51150 pc (d1 + d2 - d0 = 50 pc)
    # 50 pc = 50 * 3.261563777 = 163.07818885 light years.
    # Current date = epoch + 163.07818885 years.
    path_diff_pc = 15.0  # parsecs
    path_diff_ly = path_diff_pc * PARSEC_TO_LIGHT_YEAR

    # Observation date exactly path_diff_ly years after SN epoch
    target_date = sn_epoch + timedelta(days=path_diff_ly * DAYS_PER_YEAR)

    # Let's create a star at (RA, Dec, dist) that yields path_diff_pc
    # Place star at origin offset
    # d0 = 51200, d1 = 100. If star is at opposite RA/Dec to SN:
    # d2 = d0 + d1 = 51300 pc.
    # d1 + d2 - d0 = 100 + 51300 - 51200 = 200 pc = 200 * PARSEC_TO_LIGHT_YEAR ly.
    # Let's test calculate_ellipsoid_delay with exact arithmetic
    opposite_ra = (SN1987A_RA_DEG + 180.0) % 360.0
    opposite_dec = -SN1987A_DEC_DEG
    d1 = 100.0

    expected_ly = (d1 + (d0 + d1) - d0) * PARSEC_TO_LIGHT_YEAR  # 200 * ly
    date_at_shell = sn_epoch + timedelta(days=expected_ly * DAYS_PER_YEAR)

    delay = calculate_ellipsoid_delay(opposite_ra, opposite_dec, d1, current_date=date_at_shell)
    assert abs(delay) < 1.0  # Within 1 day tolerance


def test_is_in_ellipsoid_shell_scalar():
    current_date = "2026-07-28T00:00:00"

    # Test star
    ra = 83.8667
    dec = -69.2697
    dist = 5000.0

    is_inside, delay_days = is_in_ellipsoid_shell(
        ra_deg=ra,
        dec_deg=dec,
        dist_pc=dist,
        current_date=current_date,
        tolerance_days=30.0,
    )

    assert isinstance(is_inside, (bool, np.bool_))
    assert isinstance(delay_days, (float, np.floating))


def test_vectorized_dataframe_input():
    df = pd.DataFrame(
        {
            "ra": [83.8667, 120.0, 200.0],
            "dec": [-69.2697, 10.0, -45.0],
            "dist_pc": [100.0, 250.0, 500.0],
        }
    )

    current_date = datetime(2026, 1, 1, tzinfo=timezone.utc)

    is_inside, delay_days = is_in_ellipsoid_shell(
        ra_deg=df["ra"],
        dec_deg=df["dec"],
        dist_pc=df["dist_pc"],
        current_date=current_date,
        tolerance_days=30.0,
    )

    assert len(is_inside) == 3
    assert len(delay_days) == 3
    assert isinstance(is_inside, pd.Series) or isinstance(is_inside, np.ndarray)


def test_custom_sn_distance():
    custom_dist = 50000.0  # 50 kpc
    current_date = datetime(2026, 1, 1, tzinfo=timezone.utc)

    delay_default = calculate_ellipsoid_delay(100.0, 20.0, 300.0, current_date=current_date)
    delay_custom = calculate_ellipsoid_delay(
        100.0, 20.0, 300.0, current_date=current_date, sn_dist_pc=custom_dist
    )

    assert delay_default != delay_custom
