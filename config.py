"""
Configuration parameters for the SETI Ellipsoid Detector.
"""

from datetime import datetime, timezone
import os
from dotenv import load_dotenv

# Automatically load environment variables from .env file if present
load_dotenv()

# --- Physical & Astronomical Constants ---
PARSEC_TO_LIGHT_YEAR: float = 3.261563777
DAYS_PER_YEAR: float = 365.2425  # Mean Julian year in days

# --- Search & Detection Defaults ---
DEFAULT_TOLERANCE_DAYS: float = 30.0  # Search shell thickness (+/- days around exact surface)
DEFAULT_MAX_MAGNITUDE: float = 16.0   # Default Gaia G magnitude threshold

# --- Historic Supernovae Anchors ---
HISTORIC_SUPERNOVAE = {
    "SN1987A": {
        "name": "Supernova 1987A (LMC)",
        "ra_deg": 83.8667,
        "dec_deg": -69.2697,
        "distance_pc": 51200.0,
        "epoch": datetime(1987, 2, 23, 10, 38, 0, tzinfo=timezone.utc),
    },
    "SN1572": {
        "name": "Tycho's Supernova (SN 1572)",
        "ra_deg": 0.4225,
        "dec_deg": 64.1408,
        "distance_pc": 2500.0,
        "epoch": datetime(1572, 11, 6, 0, 0, 0, tzinfo=timezone.utc),
    },
    "SN1604": {
        "name": "Kepler's Supernova (SN 1604)",
        "ra_deg": 257.5492,
        "dec_deg": -21.4858,
        "distance_pc": 6000.0,
        "epoch": datetime(1604, 10, 9, 0, 0, 0, tzinfo=timezone.utc),
    },
    "SN1054": {
        "name": "Crab Supernova (SN 1054)",
        "ra_deg": 83.6331,
        "dec_deg": 22.0145,
        "distance_pc": 2000.0,
        "epoch": datetime(1054, 7, 4, 0, 0, 0, tzinfo=timezone.utc),
    },
}

# Default anchor aliases
SN1987A_RA_DEG: float = HISTORIC_SUPERNOVAE["SN1987A"]["ra_deg"]
SN1987A_DEC_DEG: float = HISTORIC_SUPERNOVAE["SN1987A"]["dec_deg"]
SN1987A_DISTANCE_PC: float = HISTORIC_SUPERNOVAE["SN1987A"]["distance_pc"]
SN1987A_EPOCH: datetime = HISTORIC_SUPERNOVAE["SN1987A"]["epoch"]
