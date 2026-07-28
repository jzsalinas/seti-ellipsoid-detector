"""
Pulsar & High-Energy Transient Anchor Provider.

Manages catalogs of pulsar glitches, magnetar giant flares, and binary pulsar periastron events
as temporal anchors for multi-ellipsoid cross-matching.
"""

from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd

from core.anchor import CosmicAnchor, AnchorType, DEFAULT_COSMIC_ANCHORS


class PulsarProvider:
    """
    Interface for querying and managing discrete cosmic anchors (Pulsars, Glitches, Flares).
    """

    def __init__(self, catalog: Optional[Dict[str, CosmicAnchor]] = None):
        self._catalog: Dict[str, CosmicAnchor] = catalog.copy() if catalog else DEFAULT_COSMIC_ANCHORS.copy()

    def add_anchor(self, anchor: CosmicAnchor) -> None:
        """Registers a new custom CosmicAnchor into the catalog."""
        self._catalog[anchor.id] = anchor

    def get_anchor(self, anchor_id: str) -> Optional[CosmicAnchor]:
        """Retrieves an anchor by its unique ID."""
        return self._catalog.get(anchor_id)

    def list_anchors(
        self,
        anchor_types: Optional[List[AnchorType]] = None,
        max_distance_pc: Optional[float] = None,
    ) -> List[CosmicAnchor]:
        """
        Filters and returns a list of CosmicAnchors based on criteria.
        """
        results = list(self._catalog.values())

        if anchor_types:
            results = [a for a in results if a.anchor_type in anchor_types]

        if max_distance_pc is not None:
            results = [a for a in results if a.distance_pc <= max_distance_pc]

        return results

    def to_dataframe(self, anchor_types: Optional[List[AnchorType]] = None) -> pd.DataFrame:
        """
        Exports catalog anchors to a Pandas DataFrame for analysis.
        """
        anchors = self.list_anchors(anchor_types=anchor_types)
        data = []
        for a in anchors:
            data.append(
                {
                    "anchor_id": a.id,
                    "name": a.name,
                    "ra_deg": a.ra_deg,
                    "dec_deg": a.dec_deg,
                    "distance_pc": a.distance_pc,
                    "epoch": a.epoch,
                    "anchor_type": a.anchor_type.value,
                }
            )
        return pd.DataFrame(data)
