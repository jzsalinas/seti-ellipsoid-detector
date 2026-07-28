"""
Unit tests for core/visualizer.py.
"""

import os
import pandas as pd
import pytest

from core.visualizer import generate_interactive_3d_ellipsoid, generate_multi_supernovae_3d_map
from providers.gaia_provider import get_candidate_stars


def test_interactive_3d_visualization():
    df_stars = get_candidate_stars(83.8667, -69.2697, radius_deg=1.0, use_mock=True)

    out_path = os.path.abspath("scratch/test_viz_3d.html")
    res_path = generate_interactive_3d_ellipsoid(
        stars_df=df_stars,
        output_html=out_path,
    )

    assert os.path.exists(res_path)
    assert res_path.endswith(".html")
    assert os.path.getsize(res_path) > 1000  # Non-empty HTML


def test_multi_supernovae_3d_map():
    df_stars = get_candidate_stars(83.8667, -69.2697, radius_deg=1.0, use_mock=True)

    out_path = os.path.abspath("scratch/test_multi_map_3d.html")
    res_path = generate_multi_supernovae_3d_map(
        stars_df=df_stars,
        output_html=out_path,
    )

    assert os.path.exists(res_path)
    assert res_path.endswith(".html")
    assert os.path.getsize(res_path) > 1000
