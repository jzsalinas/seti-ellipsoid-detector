"""
Cosmic Anchor Data Models, Definitions, and Alien Latency Profiles.

Defines the structure for historic supernovae, pulsar glitches, magnetar giant flares,
binary pulsar periastron passages, and ETI reaction latency profiles used as temporal
light-delay anchors in the SETI Ellipsoid Detector.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Union


class AnchorType(Enum):
    SUPERNOVA = "Supernova"
    PULSAR_GLITCH = "Pulsar_Glitch"
    MAGNETAR_FLARE = "Magnetar_Flare"
    BINARY_PERIASTRON = "Binary_Periastron"


class AlienLatencyProfile(Enum):
    """
    Alien ETI Response Latency Profiles.

    - AUTOMATED_BEACON: Autonomous AI detection and automated beacon (~60 days / 0.16 yr / ~0.05 pc).
    - BUREAUCRATIC: Political deliberation, scientific verification, allocation (~730 days / 2 yr / ~0.61 pc).
    - GENERATIONAL: Prolonged active transmission beacon (~1825 days / 5 yr / ~1.53 pc).
    """
    AUTOMATED_BEACON = 60.0
    BUREAUCRATIC = 730.0
    GENERATIONAL = 1825.0


def get_latency_tolerance_days(profile: Union[AlienLatencyProfile, str, float]) -> float:
    """
    Returns search shell tolerance window in days for a given profile or float value.
    """
    if isinstance(profile, AlienLatencyProfile):
        return profile.value
    elif isinstance(profile, str):
        key = profile.upper()
        if hasattr(AlienLatencyProfile, key):
            return AlienLatencyProfile[key].value
        try:
            return float(profile)
        except ValueError:
            raise ValueError(f"Unknown AlienLatencyProfile profile: {profile}")
    elif isinstance(profile, (int, float)):
        return float(profile)
    else:
        raise TypeError(f"Invalid latency profile type: {type(profile)}")


def latency_days_to_shell_thickness_pc(tolerance_days: float) -> float:
    """
    Converts time tolerance in days to physical 3D ellipsoid shell thickness in parsecs.
    """
    years = tolerance_days / 365.2425
    return years / 3.261563777


@dataclass(frozen=True)
class CosmicAnchor:
    """
    Represents a discrete astronomical event anchor for SETI ellipsoid geometric calculations.
    """
    id: str
    name: str
    ra_deg: float
    dec_deg: float
    distance_pc: float
    epoch: datetime
    anchor_type: AnchorType

    def __post_init__(self):
        if self.epoch.tzinfo is None:
            # Enforce UTC timezone if naive
            object.__setattr__(self, 'epoch', self.epoch.replace(tzinfo=timezone.utc))


# --- Standard Historic Supernovae Anchors ---
SN_1987A = CosmicAnchor(
    id="SN1987A",
    name="Supernova 1987A (LMC)",
    ra_deg=83.8667,
    dec_deg=-69.2697,
    distance_pc=51200.0,
    epoch=datetime(1987, 2, 23, 10, 38, 0, tzinfo=timezone.utc),
    anchor_type=AnchorType.SUPERNOVA,
)

SN_1572 = CosmicAnchor(
    id="SN1572",
    name="Tycho's Supernova (SN 1572)",
    ra_deg=0.4225,
    dec_deg=64.1408,
    distance_pc=2500.0,
    epoch=datetime(1572, 11, 6, 0, 0, 0, tzinfo=timezone.utc),
    anchor_type=AnchorType.SUPERNOVA,
)

SN_1604 = CosmicAnchor(
    id="SN1604",
    name="Kepler's Supernova (SN 1604)",
    ra_deg=257.5492,
    dec_deg=-21.4858,
    distance_pc=6000.0,
    epoch=datetime(1604, 10, 9, 0, 0, 0, tzinfo=timezone.utc),
    anchor_type=AnchorType.SUPERNOVA,
)

SN_1054 = CosmicAnchor(
    id="SN1054",
    name="Crab Supernova (SN 1054)",
    ra_deg=83.6331,
    dec_deg=22.0145,
    distance_pc=2000.0,
    epoch=datetime(1054, 7, 4, 0, 0, 0, tzinfo=timezone.utc),
    anchor_type=AnchorType.SUPERNOVA,
)

# --- Standard Pulsar Glitches & High-Energy Discrete Flares ---
VELA_GLITCH_1969 = CosmicAnchor(
    id="VELA_GLITCH_1969",
    name="Vela Pulsar Historic Glitch (PSR B0833-45)",
    ra_deg=128.836,
    dec_deg=-45.176,
    distance_pc=287.0,
    epoch=datetime(1969, 3, 1, 0, 0, 0, tzinfo=timezone.utc),
    anchor_type=AnchorType.PULSAR_GLITCH,
)

CRAB_GLITCH_2017 = CosmicAnchor(
    id="CRAB_GLITCH_2017",
    name="Crab Pulsar Major Glitch (PSR B0531+21)",
    ra_deg=83.6331,
    dec_deg=22.0145,
    distance_pc=2000.0,
    epoch=datetime(2017, 11, 8, 0, 0, 0, tzinfo=timezone.utc),
    anchor_type=AnchorType.PULSAR_GLITCH,
)

SGR_1806_2004 = CosmicAnchor(
    id="SGR1806_FLARE_2004",
    name="Magnetar SGR 1806-20 Giant Flare",
    ra_deg=272.137,
    dec_deg=-20.409,
    distance_pc=8700.0,
    epoch=datetime(2004, 12, 27, 21, 36, 16, tzinfo=timezone.utc),
    anchor_type=AnchorType.MAGNETAR_FLARE,
)

PSR_J0737_3039 = CosmicAnchor(
    id="PSR_J0737_3039",
    name="Double Pulsar Periastron (PSR J0737-3039A/B)",
    ra_deg=114.425,
    dec_deg=-30.665,
    distance_pc=1150.0,
    epoch=datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
    anchor_type=AnchorType.BINARY_PERIASTRON,
)

# Registry dictionary of default anchors
DEFAULT_COSMIC_ANCHORS: Dict[str, CosmicAnchor] = {
    SN_1987A.id: SN_1987A,
    SN_1572.id: SN_1572,
    SN_1604.id: SN_1604,
    SN_1054.id: SN_1054,
    VELA_GLITCH_1969.id: VELA_GLITCH_1969,
    CRAB_GLITCH_2017.id: CRAB_GLITCH_2017,
    SGR_1806_2004.id: SGR_1806_2004,
    PSR_J0737_3039.id: PSR_J0737_3039,
}
