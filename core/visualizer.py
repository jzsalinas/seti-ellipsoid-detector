"""
Interactive 3D SETI Ellipsoid & Stellar Catalog Visualizer.

Generates dark-theme WebGL 3D interactive visualizations (Plotly HTML) rendering
Earth, Supernova foci, target stars, and the active 3D SETI Ellipsoid shell.
"""

from typing import Optional, Dict, Any
import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from config import (
    SN1987A_RA_DEG,
    SN1987A_DEC_DEG,
    SN1987A_DISTANCE_PC,
    SN1987A_EPOCH,
    PARSEC_TO_LIGHT_YEAR,
    DAYS_PER_YEAR,
)
from core.geometry import spherical_to_cartesian, _parse_datetime


def _create_ellipsoid_mesh(
    xe: float, ye: float, ze: float, d0: float, delta_t_years: float, n_points: int = 40
):
    """
    Constructs 3D mesh grid coordinates (X, Y, Z) for an ellipsoid with foci at (0,0,0) and (xe, ye, ze).
    """
    # Major and minor axes in parsecs
    path_diff_ly = delta_t_years
    path_diff_pc = path_diff_ly / PARSEC_TO_LIGHT_YEAR

    a = (d0 + path_diff_pc) / 2.0  # Semi-major axis
    c_foci = d0 / 2.0               # Focal distance
    b = np.sqrt(max(a ** 2 - c_foci ** 2, 1e-3))  # Semi-minor axis

    # Parametric sphere
    u = np.linspace(0, 2 * np.pi, n_points)
    v = np.linspace(0, np.pi, n_points)
    U, V = np.meshgrid(u, v)

    # Standard unrotated ellipsoid centered at origin
    x_std = a * np.sin(V) * np.cos(U)
    y_std = b * np.sin(V) * np.sin(U)
    z_std = b * np.cos(V)

    # Rotation matrix to align X-axis with SN vector (xe, ye, ze)
    sn_vec = np.array([xe, ye, ze])
    norm_sn = np.linalg.norm(sn_vec)
    if norm_sn == 0:
        v_target = np.array([1.0, 0.0, 0.0])
    else:
        v_target = sn_vec / norm_sn

    v_src = np.array([1.0, 0.0, 0.0])
    v_axis = np.cross(v_src, v_target)
    sin_angle = np.linalg.norm(v_axis)
    cos_angle = np.dot(v_src, v_target)

    if sin_angle < 1e-6:
        R = np.eye(3) if cos_angle > 0 else -np.eye(3)
    else:
        v_axis = v_axis / sin_angle
        K = np.array(
            [
                [0, -v_axis[2], v_axis[1]],
                [v_axis[2], 0, -v_axis[0]],
                [-v_axis[1], v_axis[0], 0],
            ]
        )
        R = np.eye(3) + K * sin_angle + np.dot(K, K) * (1 - cos_angle)

    # Center of ellipsoid is midpoint between Earth (0,0,0) and Supernova (xe, ye, ze)
    center = sn_vec / 2.0

    # Apply rotation and translation
    pts = np.stack([x_std.flatten(), y_std.flatten(), z_std.flatten()], axis=0)
    pts_rot = np.dot(R, pts)

    X = pts_rot[0, :].reshape(n_points, n_points) + center[0]
    Y = pts_rot[1, :].reshape(n_points, n_points) + center[1]
    Z = pts_rot[2, :].reshape(n_points, n_points) + center[2]

    return X, Y, Z


def generate_interactive_3d_ellipsoid(
    stars_df: pd.DataFrame,
    sn_ra: float = SN1987A_RA_DEG,
    sn_dec: float = SN1987A_DEC_DEG,
    sn_dist_pc: float = SN1987A_DISTANCE_PC,
    sn_epoch: Any = SN1987A_EPOCH,
    sn_name: str = "SN 1987A",
    current_date: Any = "2026-07-28T00:00:00",
    output_html: Optional[str] = None,
) -> str:
    """
    Generates an interactive Plotly 3D WebGL HTML visualization.
    Renders Earth, Supernova focus, target stars, and the active 3D SETI Ellipsoid shell.
    """
    # Parse dates & compute elapsed time in years
    obs_dt = _parse_datetime(current_date)
    epoch_dt = _parse_datetime(sn_epoch)
    elapsed_years = (obs_dt - epoch_dt).total_seconds() / (86400.0 * DAYS_PER_YEAR)

    # Cartesian 3D coordinates for Supernova
    xe, ye, ze = spherical_to_cartesian(sn_ra, sn_dec, sn_dist_pc)

    # Compute target stars 3D coordinates
    xs, ys, zs = spherical_to_cartesian(stars_df["ra"], stars_df["dec"], stars_df["dist_pc"])

    fig = go.Figure()

    # 1. Earth at origin (0,0,0)
    fig.add_trace(
        go.Scatter3d(
            x=[0],
            y=[0],
            z=[0],
            mode="markers+text",
            marker=dict(size=10, color="#ffd700", symbol="circle"),
            text=["🌍 Earth (Observer)"],
            textposition="top center",
            name="Earth (0,0,0)",
        )
    )

    # 2. Supernova focus
    fig.add_trace(
        go.Scatter3d(
            x=[xe],
            y=[ye],
            z=[ze],
            mode="markers+text",
            marker=dict(size=12, color="#ff1744", symbol="diamond"),
            text=[f"💥 {sn_name}"],
            textposition="top center",
            name=f"{sn_name} (d={sn_dist_pc:.0f} pc)",
        )
    )

    # 3. SETI Ellipsoid Translucent 3D Surface Mesh
    try:
        X_mesh, Y_mesh, Z_mesh = _create_ellipsoid_mesh(xe, ye, ze, sn_dist_pc, elapsed_years)
        fig.add_trace(
            go.Surface(
                x=X_mesh,
                y=Y_mesh,
                z=Z_mesh,
                colorscale=[[0, "rgba(0, 229, 255, 0.25)"], [1, "rgba(0, 229, 255, 0.25)"]],
                showscale=False,
                name="SETI Ellipsoid Shell",
                hoverinfo="name",
                opacity=0.35,
            )
        )
    except Exception as err:
        print(f"Warning: Could not render ellipsoid mesh surface: {err}")

    # 4. Target Stars Scatter3d color-coded by delay_days
    delays = stars_df.get("delay_days", np.zeros(len(stars_df)))
    hover_texts = [
        f"<b>Star ID:</b> {row.get('source_id', 'N/A')}<br>"
        f"<b>RA:</b> {row['ra']:.4f}° | <b>Dec:</b> {row['dec']:.4f}°<br>"
        f"<b>Distance:</b> {row['dist_pc']:.1f} pc<br>"
        f"<b>G mag:</b> {row.get('phot_g_mean_mag', 0.0):.2f}<br>"
        f"<b>Ellipsoid Delay:</b> {row.get('delay_days', 0.0):+.1f} days"
        for _, row in stars_df.iterrows()
    ]

    fig.add_trace(
        go.Scatter3d(
            x=xs,
            y=ys,
            z=zs,
            mode="markers",
            marker=dict(
                size=5,
                color=delays,
                colorscale="Viridis",
                colorbar=dict(title="Delay (days)"),
                opacity=0.85,
            ),
            text=hover_texts,
            hoverinfo="text",
            name="Gaia DR3 Stars",
        )
    )

    # Dark template layout
    fig.update_layout(
        template="plotly_dark",
        title=dict(
            text=f"🌌 SETI Ellipsoid 3D Interactive Visualization | {sn_name} ({obs_dt.strftime('%Y-%m-%d')})",
            font=dict(size=16, color="#00e5ff"),
        ),
        scene=dict(
            xaxis=dict(title="X (parsecs)", backgroundcolor="#111", gridcolor="#333"),
            yaxis=dict(title="Y (parsecs)", backgroundcolor="#111", gridcolor="#333"),
            zaxis=dict(title="Z (parsecs)", backgroundcolor="#111", gridcolor="#333"),
            aspectmode="data",
        ),
        margin=dict(l=0, r=0, b=0, t=40),
    )

    if output_html is None:
        os.makedirs("scratch", exist_ok=True)
        output_html = os.path.abspath(f"scratch/seti_ellipsoid_{sn_name.replace(' ', '_')}_3d.html")

    fig.write_html(output_html, include_plotlyjs="cdn")
    print(f"✅ Interactive 3D visualization generated: {output_html}")
    return output_html
