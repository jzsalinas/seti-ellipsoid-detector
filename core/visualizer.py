"""
Interactive 3D SETI Ellipsoid & Stellar Catalog Visualizer.

Generates dark-theme WebGL 3D interactive visualizations (Plotly HTML) rendering
Earth, Supernova foci, target stars, line of sight, and the active 3D SETI Ellipsoid shell.
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
from core.geometry import spherical_to_cartesian, calculate_ellipsoid_delay, _parse_datetime


def _create_ellipsoid_mesh(
    xe: float, ye: float, ze: float, d0: float, delta_t_years: float, n_points: int = 50
):
    """
    Constructs 3D mesh grid coordinates (X, Y, Z) for an ellipsoid with foci at (0,0,0) [Earth] and (xe, ye, ze) [Supernova].
    """
    path_diff_ly = delta_t_years
    path_diff_pc = path_diff_ly / PARSEC_TO_LIGHT_YEAR

    a = (d0 + path_diff_pc) / 2.0  # Semi-major axis
    c_foci = d0 / 2.0               # Focal distance (half distance between Earth and SN)
    b = np.sqrt(max(a ** 2 - c_foci ** 2, 1.0))  # Semi-minor axis

    # Parametric sphere mesh
    u = np.linspace(0, 2 * np.pi, n_points)
    v = np.linspace(0, np.pi, n_points)
    U, V = np.meshgrid(u, v)

    # Standard unrotated ellipsoid with major axis along X
    x_std = a * np.sin(V) * np.cos(U)
    y_std = b * np.sin(V) * np.sin(U)
    z_std = b * np.cos(V)

    # Rotation matrix R mapping (1,0,0) to normalized Supernova direction vector
    sn_vec = np.array([xe, ye, ze])
    norm_sn = np.linalg.norm(sn_vec)
    v_target = sn_vec / norm_sn if norm_sn > 0 else np.array([1.0, 0.0, 0.0])

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
    Renders Earth, Supernova focus, line of sight, target stars, and the active 3D SETI Ellipsoid shell.
    Includes enhanced camera controls (Pan, Zoom, Orbit, Resetting center).
    """
    stars_df = stars_df.copy()

    # Parse dates & compute elapsed time in years
    obs_dt = _parse_datetime(current_date)
    epoch_dt = _parse_datetime(sn_epoch)
    elapsed_years = (obs_dt - epoch_dt).total_seconds() / (86400.0 * DAYS_PER_YEAR)

    # Automatically compute exact delay in days for all stars
    delay_days = calculate_ellipsoid_delay(
        ra_deg=stars_df["ra"],
        dec_deg=stars_df["dec"],
        dist_pc=stars_df["dist_pc"],
        current_date=current_date,
        sn_ra=sn_ra,
        sn_dec=sn_dec,
        sn_dist_pc=sn_dist_pc,
        sn_epoch=sn_epoch,
    )
    stars_df["delay_days"] = delay_days

    xe, ye, ze = spherical_to_cartesian(sn_ra, sn_dec, sn_dist_pc)
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
            name="Earth (Focus 1)",
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
            name=f"{sn_name} (Focus 2, d={sn_dist_pc:.0f} pc)",
        )
    )

    # 3. Dashed line of sight Earth -> Supernova
    fig.add_trace(
        go.Scatter3d(
            x=[0, xe],
            y=[0, ye],
            z=[0, ze],
            mode="lines",
            line=dict(color="#ff9100", width=3, dash="dash"),
            name="Line of Sight (Focal Axis)",
        )
    )

    # 4. Translucent 3D Ellipsoid Surface Mesh
    try:
        X_mesh, Y_mesh, Z_mesh = _create_ellipsoid_mesh(xe, ye, ze, sn_dist_pc, elapsed_years)
        fig.add_trace(
            go.Surface(
                x=X_mesh,
                y=Y_mesh,
                z=Z_mesh,
                colorscale=[[0, "rgba(0, 229, 255, 0.22)"], [1, "rgba(0, 229, 255, 0.22)"]],
                showscale=False,
                name=f"SETI Ellipsoid Shell ({elapsed_years:.1f} yr)",
                hoverinfo="name",
                opacity=0.30,
            )
        )
    except Exception as err:
        print(f"Warning: Could not render ellipsoid mesh surface: {err}")

    # 5. Target Stars Scatter3d color-coded by ellipsoid status
    shell_mask = np.abs(delay_days) <= 365.0
    past_mask = delay_days < -365.0
    future_mask = delay_days > 365.0

    for mask, color, label_name, symbol in [
        (past_mask, "#7c4dff", "Past Shell (Foreground / Light Passed)", "circle"),
        (shell_mask, "#00e676", "ACTIVE SETI SHELL (On Surface ±1yr)", "diamond"),
        (future_mask, "#ff5252", "Future Shell (Background / Not Arrived)", "circle"),
    ]:
        if not np.any(mask):
            continue

        df_sub = stars_df[mask]
        sub_hover = [
            f"<b>Star ID:</b> {row.get('source_id', 'N/A')}<br>"
            f"<b>RA:</b> {row['ra']:.4f}° | <b>Dec:</b> {row['dec']:.4f}°<br>"
            f"<b>Distance:</b> {row['dist_pc']:.1f} pc<br>"
            f"<b>G mag:</b> {row.get('phot_g_mean_mag', 0.0):.2f}<br>"
            f"<b>Ellipsoid Delay:</b> {row.get('delay_days', 0.0):+.1f} days"
            for _, row in df_sub.iterrows()
        ]

        fig.add_trace(
            go.Scatter3d(
                x=xs[mask],
                y=ys[mask],
                z=zs[mask],
                mode="markers",
                marker=dict(
                    size=8 if label_name.startswith("ACTIVE") else 4,
                    color=color,
                    symbol=symbol,
                    opacity=0.9,
                ),
                text=sub_hover,
                hoverinfo="text",
                name=f"{label_name} ({sum(mask)})",
            )
        )

    fig.update_layout(
        template="plotly_dark",
        title=dict(
            text=f"🌌 SETI Ellipsoid 3D Interactive Model | {sn_name} (Elapsed: {elapsed_years:.1f} yrs)",
            font=dict(size=16, color="#00e5ff"),
        ),
        scene=dict(
            xaxis=dict(title="X (parsecs)", backgroundcolor="#111", gridcolor="#333"),
            yaxis=dict(title="Y (parsecs)", backgroundcolor="#111", gridcolor="#333"),
            zaxis=dict(title="Z (parsecs)", backgroundcolor="#111", gridcolor="#333"),
            aspectmode="data",
            camera=dict(
                up=dict(x=0, y=0, z=1),
                eye=dict(x=1.25, y=1.25, z=1.25),
            ),
        ),
        dragmode="turntable",
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(0,0,0,0.7)",
            bordercolor="rgba(0,229,255,0.4)",
            borderwidth=1,
        ),
        margin=dict(l=0, r=0, b=0, t=40),
    )

    if output_html is None:
        os.makedirs("scratch", exist_ok=True)
        output_html = os.path.abspath(f"scratch/seti_ellipsoid_{sn_name.replace(' ', '_')}_3d.html")

    fig.write_html(
        output_html,
        include_plotlyjs="cdn",
        config={
            "scrollZoom": True,
            "displayModeBar": True,
            "displaylogo": False,
            "modeBarButtonsToAdd": [
                "pan3d",
                "orbit3d",
                "table3d",
                "resetCameraDefault3d",
                "resetCameraLastSave3d",
            ],
        },
    )
    print(f"✅ Interactive 3D visualization generated: {output_html}")
    return output_html
