"""
Unit Tests for ETI Reaction Latency Profiles & Shell Thickness Conversions.
"""

import pytest
from core.anchor import (
    AlienLatencyProfile,
    get_latency_tolerance_days,
    latency_days_to_shell_thickness_pc,
)


def test_alien_latency_profile_values():
    assert AlienLatencyProfile.AUTOMATED_BEACON.value == 60.0
    assert AlienLatencyProfile.BUREAUCRATIC.value == 730.0
    assert AlienLatencyProfile.GENERATIONAL.value == 1825.0


def test_get_latency_tolerance_days():
    # From Enum
    assert get_latency_tolerance_days(AlienLatencyProfile.AUTOMATED_BEACON) == 60.0
    # From string
    assert get_latency_tolerance_days("bureaucratic") == 730.0
    assert get_latency_tolerance_days("GENERATIONAL") == 1825.0
    # From numeric string or float
    assert get_latency_tolerance_days("90.0") == 90.0
    assert get_latency_tolerance_days(45.0) == 45.0

    with pytest.raises(ValueError):
        get_latency_tolerance_days("unknown_profile")


def test_latency_days_to_shell_thickness_pc():
    # 365.2425 days = 1 year = 1 / 3.261563777 parsec ~ 0.3066 pc
    thickness_1yr = latency_days_to_shell_thickness_pc(365.2425)
    assert pytest.approx(thickness_1yr, 0.001) == 0.3066

    # Automated beacon (60 days)
    thickness_60d = latency_days_to_shell_thickness_pc(60.0)
    assert pytest.approx(thickness_60d, 0.001) == 0.0504

    # Bureaucratic (730 days ~ 2 years)
    thickness_730d = latency_days_to_shell_thickness_pc(730.0)
    assert pytest.approx(thickness_730d, 0.001) == 0.6128
