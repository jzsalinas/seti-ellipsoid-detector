"""
Core engine modules for SETI Ellipsoid Detector.
"""

from .geometry import (
    spherical_to_cartesian,
    calculate_ellipsoid_delay,
    is_in_ellipsoid_shell,
)
from .anomaly_engine import AnomalyEvaluator

__all__ = [
    "spherical_to_cartesian",
    "calculate_ellipsoid_delay",
    "is_in_ellipsoid_shell",
    "AnomalyEvaluator",
]
