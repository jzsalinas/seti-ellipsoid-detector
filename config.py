"""
Configuration parameters for the SETI Ellipsoid Detector.
"""

from datetime import datetime, timezone

# --- SN 1987A Event Parameters ---
# Coordinates (ICRS Equatorial)
SN1987A_RA_DEG: float = 83.8667       # Right Ascension in degrees
SN1987A_DEC_DEG: float = -69.2697     # Declination in degrees

# Distance to SN 1987A in parsecs (Default ~ 51.2 kpc, configurable)
SN1987A_DISTANCE_PC: float = 51200.0

# Date when SN 1987A light first reached Earth (1987-02-23 10:38:00 UTC)
SN1987A_EPOCH: datetime = datetime(1987, 2, 23, 10, 38, 0, tzinfo=timezone.utc)

# --- Physical & Astronomical Constants ---
PARSEC_TO_LIGHT_YEAR: float = 3.261563777
DAYS_PER_YEAR: float = 365.2425  # Mean Julian year in days

# --- Search & Detection Defaults ---
DEFAULT_TOLERANCE_DAYS: float = 30.0  # Search shell thickness (+/- days around exact surface)
DEFAULT_MAX_MAGNITUDE: float = 16.0   # Default Gaia G magnitude threshold
