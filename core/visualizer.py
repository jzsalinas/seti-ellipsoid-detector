"""
Interactive 3D SETI Ellipsoid & Stellar Catalog Visualizer.

Includes single-anchor visualization and multi-supernova 3D superposition maps rendering:
- Earth: Gold sphere focus at origin
- Multiple Supernova Anchors (SN 1987A, SN 1572 Tycho, SN 1604 Kepler, SN 1054 Crab)
- Superposed 3D Translucent Ellipsoid Surface Meshes
- Gaia DR3 Candidate Stars color-coded by active shell status across all supernovas
"""

from typing import Optional, Dict, Any, List, Tuple
import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from config import (
    SN1987A_RA_DEG,
    SN1987A_DEC_DEG,
    SN1987A_DISTANCE_PC,
    SN1987A_EPOCH,
    HISTORIC_SUPERNOVAE,
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
    c_foci = d0 / 2.0               # Focal distance
    b = np.sqrt(max(a ** 2 - c_foci ** 2, 1.0))  # Semi-minor axis

    u = np.linspace(0, 2 * np.pi, n_points)
    v = np.linspace(0, np.pi, n_points)
    U, V = np.meshgrid(u, v)

    x_std = a * np.sin(V) * np.cos(U)
    y_std = b * np.sin(V) * np.sin(U)
    z_std = b * np.cos(V)

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

    center = sn_vec / 2.0

    pts = np.stack([x_std.flatten(), y_std.flatten(), z_std.flatten()], axis=0)
    pts_rot = np.dot(R, pts)

    X = pts_rot[0, :].reshape(n_points, n_points) + center[0]
    Y = pts_rot[1, :].reshape(n_points, n_points) + center[1]
    Z = pts_rot[2, :].reshape(n_points, n_points) + center[2]

    return X, Y, Z


def _generate_surface_ring_and_projections(
    xe: float, ye: float, ze: float, d0: float, delta_t_years: float,
    xs_in: Any, ys_in: Any, zs_in: Any, n_pts: int = 50
) -> Tuple[List[float], List[float], List[float], List[float], List[float], List[float]]:
    """
    Generates 3D coordinates for rings projected EXACTLY ON THE SURFACE MESH of the ellipsoid,
    plus dotted projection vectors connecting stars to their surface projection points.
    """
    xs = np.asarray(xs_in, dtype=float)
    ys = np.asarray(ys_in, dtype=float)
    zs = np.asarray(zs_in, dtype=float)

    path_diff_pc = delta_t_years / PARSEC_TO_LIGHT_YEAR
    a = (d0 + path_diff_pc) / 2.0
    c_foci = d0 / 2.0
    b = np.sqrt(max(a ** 2 - c_foci ** 2, 1.0))

    sn_vec = np.array([xe, ye, ze], dtype=float)
    norm_sn = np.linalg.norm(sn_vec)
    v_axis = sn_vec / norm_sn if norm_sn > 0 else np.array([1.0, 0.0, 0.0])

    ring_xs, ring_ys, ring_zs = [], [], []
    vec_xs, vec_ys, vec_zs = [], [], []

    for i in range(len(xs)):
        s_vec = np.array([xs[i], ys[i], zs[i]], dtype=float)
        p_axial = np.dot(s_vec, v_axis)
        x_center = p_axial - (d0 / 2.0)

        if abs(x_center) >= a:
            r_surf = 2.0
        else:
            r_surf = b * np.sqrt(max(1.0 - (x_center / a) ** 2, 1e-4))

        c_ring = p_axial * v_axis
        radial_vec = s_vec - c_ring
        dist_radial = np.linalg.norm(radial_vec)

        if dist_radial < 1e-3:
            u1 = np.cross(v_axis, [0.0, 0.0, 1.0])
            if np.linalg.norm(u1) < 1e-3:
                u1 = np.cross(v_axis, [0.0, 1.0, 0.0])
            u1 = u1 / np.linalg.norm(u1)
        else:
            u1 = radial_vec / dist_radial

        u2 = np.cross(v_axis, u1)
        u2 = u2 / np.linalg.norm(u2)

        # Ring on surface mesh
        theta = np.linspace(0, 2 * np.pi, n_pts)
        r_pts = (
            c_ring[:, None]
            + r_surf * np.cos(theta)[None, :] * u1[:, None]
            + r_surf * np.sin(theta)[None, :] * u2[:, None]
        )

        ring_xs.extend(list(r_pts[0]) + [None])
        ring_ys.extend(list(r_pts[1]) + [None])
        ring_zs.extend(list(r_pts[2]) + [None])

        # Projection vector from star to nearest surface point
        s_proj = c_ring + r_surf * u1
        vec_xs.extend([s_vec[0], s_proj[0], None])
        vec_ys.extend([s_vec[1], s_proj[1], None])
        vec_zs.extend([s_vec[2], s_proj[2], None])

    return ring_xs, ring_ys, ring_zs, vec_xs, vec_ys, vec_zs


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
    Generates an interactive Plotly 3D WebGL HTML visualization for a single supernova anchor.
    """
    stars_df = stars_df.copy()

    obs_dt = _parse_datetime(current_date)
    epoch_dt = _parse_datetime(sn_epoch)
    elapsed_years_base = (obs_dt - epoch_dt).total_seconds() / (86400.0 * DAYS_PER_YEAR)
    current_year = obs_dt.year

    delay_days_base = calculate_ellipsoid_delay(
        ra_deg=stars_df["ra"],
        dec_deg=stars_df["dec"],
        dist_pc=stars_df["dist_pc"],
        current_date=current_date,
        sn_ra=sn_ra,
        sn_dec=sn_dec,
        sn_dist_pc=sn_dist_pc,
        sn_epoch=sn_epoch,
    )
    stars_df["delay_days"] = delay_days_base

    xe, ye, ze = spherical_to_cartesian(sn_ra, sn_dec, sn_dist_pc)
    xs, ys, zs = spherical_to_cartesian(stars_df["ra"], stars_df["dec"], stars_df["dist_pc"])
    xs_arr = np.asarray(xs)
    ys_arr = np.asarray(ys)
    zs_arr = np.asarray(zs)

    fig = go.Figure()

    # 0. Earth (Gold sphere)
    fig.add_trace(
        go.Scatter3d(
            x=[0],
            y=[0],
            z=[0],
            mode="markers+text",
            marker=dict(size=11, color="#ffd700", symbol="circle", line=dict(color="#ffffff", width=1)),
            text=["🌍 Earth (Observer)"],
            textposition="top center",
            name="Earth (Focus 1)",
        )
    )

    # 1. Supernova (Glowing Cyan-White sphere)
    fig.add_trace(
        go.Scatter3d(
            x=[xe],
            y=[ye],
            z=[ze],
            mode="markers+text",
            marker=dict(size=13, color="#e0f7fa", symbol="circle", line=dict(color="#00e5ff", width=3)),
            text=[f"💥 {sn_name}"],
            textposition="top center",
            name=f"{sn_name} (Focus 2, d={sn_dist_pc:.0f} pc)",
        )
    )

    # 2. Line of sight Earth -> Supernova
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

    time_steps = [
        (f"Present Day ({current_year}) [±1 yr]", 0.0, 365.25),
        (f"+10 Years ({current_year+10}) [±1 yr]", 10.0, 365.25),
        (f"+50 Years ({current_year+50}) [±5 yr]", 50.0, 1826.25),
        (f"+100 Years ({current_year+100}) [±10 yr]", 100.0, 3652.5),
        (f"+500 Years ({current_year+500}) [±50 yr]", 500.0, 18262.5),
        (f"+500 Years Wide ({current_year+500}) [±250 yr]", 500.0, 91310.6),
        (f"-50 Years ({current_year-50}) [±5 yr]", -50.0, 1826.25),
    ]

    base_trace_count = 3
    num_steps = len(time_steps)
    traces_per_step = 6

    for step_idx, (step_label, year_offset, tol_days) in enumerate(time_steps):
        target_elapsed_years = elapsed_years_base + year_offset
        target_delay_offset = year_offset * DAYS_PER_YEAR
        current_delays = delay_days_base - target_delay_offset

        default_visible = (step_idx == 0)

        try:
            X_mesh, Y_mesh, Z_mesh = _create_ellipsoid_mesh(xe, ye, ze, sn_dist_pc, target_elapsed_years)
            fig.add_trace(
                go.Surface(
                    x=X_mesh,
                    y=Y_mesh,
                    z=Z_mesh,
                    colorscale=[[0, "rgba(0, 229, 255, 0.22)"], [1, "rgba(0, 229, 255, 0.22)"]],
                    showscale=False,
                    name=f"Ellipsoid Shell ({target_elapsed_years:.1f} yr)",
                    hoverinfo="name",
                    opacity=0.30,
                    visible=default_visible,
                )
            )
        except Exception:
            fig.add_trace(go.Surface(x=[], y=[], z=[], visible=default_visible))

        shell_mask = np.abs(current_delays) <= tol_days
        past_mask = current_delays < -tol_days
        future_mask = current_delays > +tol_days

        df_past = stars_df[past_mask]
        past_hover = [
            f"<b>Star ID:</b> {row.get('source_id', 'N/A')}<br>"
            f"<b>Distance:</b> {row['dist_pc']:.1f} pc<br>"
            f"<b>Ellipsoid Delay:</b> {current_delays.iloc[i]:+.1f} days"
            for i, (_, row) in enumerate(df_past.iterrows())
        ] if len(df_past) > 0 else []

        fig.add_trace(
            go.Scatter3d(
                x=xs_arr[past_mask],
                y=ys_arr[past_mask],
                z=zs_arr[past_mask],
                mode="markers",
                marker=dict(size=4, color="#7c4dff", symbol="circle", opacity=0.7),
                text=past_hover,
                hoverinfo="text",
                name=f"Past Shell ({sum(past_mask)})",
                visible=default_visible,
            )
        )

        df_active = stars_df[shell_mask]
        active_hover = [
            f"<b>ACTIVE SETI CANDIDATE!</b><br>"
            f"<b>Star ID:</b> {row.get('source_id', 'N/A')}<br>"
            f"<b>RA:</b> {row['ra']:.4f}° | <b>Dec:</b> {row['dec']:.4f}°<br>"
            f"<b>Distance:</b> {row['dist_pc']:.1f} pc<br>"
            f"<b>Delay at Date:</b> {current_delays.iloc[i]:+.1f} days"
            for i, (_, row) in enumerate(df_active.iterrows())
        ] if len(df_active) > 0 else []

        fig.add_trace(
            go.Scatter3d(
                x=xs_arr[shell_mask],
                y=ys_arr[shell_mask],
                z=zs_arr[shell_mask],
                mode="markers",
                marker=dict(size=8, color="#00e676", symbol="circle", line=dict(color="#ffffff", width=1), opacity=1.0),
                text=active_hover,
                hoverinfo="text",
                name=f"ACTIVE SETI STARS ({sum(shell_mask)})",
                visible=default_visible,
            )
        )

        df_future = stars_df[future_mask]
        future_hover = [
            f"<b>Star ID:</b> {row.get('source_id', 'N/A')}<br>"
            f"<b>Distance:</b> {row['dist_pc']:.1f} pc<br>"
            f"<b>Ellipsoid Delay:</b> {current_delays.iloc[i]:+.1f} days"
            for i, (_, row) in enumerate(df_future.iterrows())
        ] if len(df_future) > 0 else []

        fig.add_trace(
            go.Scatter3d(
                x=xs_arr[future_mask],
                y=ys_arr[future_mask],
                z=zs_arr[future_mask],
                mode="markers",
                marker=dict(size=4, color="#ff5252", symbol="circle", opacity=0.7),
                text=future_hover,
                hoverinfo="text",
                name=f"Future Shell ({sum(future_mask)})",
                visible=default_visible,
            )
        )

        if np.any(shell_mask):
            rx, ry, rz, vx, vy, vz = _generate_surface_ring_and_projections(
                xe, ye, ze, sn_dist_pc, target_elapsed_years,
                xs_arr[shell_mask], ys_arr[shell_mask], zs_arr[shell_mask]
            )

            fig.add_trace(
                go.Scatter3d(
                    x=rx,
                    y=ry,
                    z=rz,
                    mode="lines",
                    line=dict(color="#00e676", width=4),
                    name=f"Surface Latitude Rings ({sum(shell_mask)})",
                    hoverinfo="name",
                    visible=default_visible,
                )
            )

            fig.add_trace(
                go.Scatter3d(
                    x=vx,
                    y=vy,
                    z=vz,
                    mode="lines",
                    line=dict(color="#00e5ff", width=2, dash="dot"),
                    name="Star Radial Projection Vectors",
                    hoverinfo="name",
                    visible=default_visible,
                )
            )
        else:
            fig.add_trace(go.Scatter3d(x=[], y=[], z=[], mode="lines", name="Surface Latitude Rings (0)", visible=default_visible))
            fig.add_trace(go.Scatter3d(x=[], y=[], z=[], mode="lines", name="Star Radial Projection Vectors", visible=default_visible))

    slider_steps = []

    for step_idx, (step_label, year_offset, tol_days) in enumerate(time_steps):
        visibility = [True] * base_trace_count

        for i in range(num_steps):
            is_active_step = (i == step_idx)
            visibility.extend([is_active_step] * traces_per_step)

        slider_steps.append(
            dict(
                method="update",
                label=step_label,
                args=[
                    {"visible": visibility},
                    {"title.text": f"🌌 SETI Ellipsoid 3D Dynamic Model | {sn_name} | Epoch: {step_label}"},
                ],
            )
        )

    sliders = [
        dict(
            active=0,
            currentvalue={"prefix": "⏱️ Time Evolution Epoch: ", "font": {"color": "#00e5ff", "size": 14}},
            pad={"t": 30, "b": 10},
            steps=slider_steps,
            bgcolor="#222",
            activebgcolor="#00e5ff",
            font={"color": "#fff"},
        )
    ]

    fig.update_layout(
        template="plotly_dark",
        title=dict(
            text=f"🌌 SETI Ellipsoid 3D Dynamic Model | {sn_name} | Epoch: Present Day ({current_year}) [±1 yr]",
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
        sliders=sliders,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(0,0,0,0.75)",
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
            ],
        },
    )
    print(f"✅ Interactive 3D visualization generated: {output_html}")
    return output_html


def generate_multi_supernovae_3d_map(
    stars_df: Optional[pd.DataFrame] = None,
    supernovae_dict: Dict[str, Any] = HISTORIC_SUPERNOVAE,
    current_date: Any = "2026-07-28T00:00:00",
    output_html: Optional[str] = None,
) -> str:
    """
    Generates a 3D Superposition Map rendering ALL historic supernova ellipsoids simultaneously around Earth.
    Allows toggling each Supernova Ellipsoid surface and inspecting candidates across the Galaxy.
    """
    obs_dt = _parse_datetime(current_date)
    current_year = obs_dt.year

    fig = go.Figure()

    # 1. Earth (Gold sphere at center)
    fig.add_trace(
        go.Scatter3d(
            x=[0],
            y=[0],
            z=[0],
            mode="markers+text",
            marker=dict(size=12, color="#ffd700", symbol="circle", line=dict(color="#ffffff", width=2)),
            text=["🌍 Earth (Observer)"],
            textposition="top center",
            name="Earth (Origin 0,0,0)",
        )
    )

    # Styling colors for each Supernova Anchor
    sn_styles = {
        "SN1987A": {"color": "#00e5ff", "mesh_color": "rgba(0, 229, 255, 0.22)"},
        "SN1572":  {"color": "#ff007f", "mesh_color": "rgba(255, 0, 127, 0.22)"},
        "SN1604":  {"color": "#ffab00", "mesh_color": "rgba(255, 171, 0, 0.22)"},
        "SN1054":  {"color": "#00e676", "mesh_color": "rgba(0, 230, 118, 0.22)"},
    }

    # Render each Supernova Focus & 3D Ellipsoid Mesh
    for sn_key, sn_info in supernovae_dict.items():
        name = sn_info["name"]
        ra = sn_info["ra_deg"]
        dec = sn_info["dec_deg"]
        d0 = sn_info["distance_pc"]
        epoch = sn_info["epoch"]

        style = sn_styles.get(sn_key, {"color": "#ffffff", "mesh_color": "rgba(255,255,255,0.2)"})

        xe, ye, ze = spherical_to_cartesian(ra, dec, d0)
        epoch_dt = _parse_datetime(epoch)
        elapsed_years = (obs_dt - epoch_dt).total_seconds() / (86400.0 * DAYS_PER_YEAR)

        # Supernova Focus Marker
        fig.add_trace(
            go.Scatter3d(
                x=[xe],
                y=[ye],
                z=[ze],
                mode="markers+text",
                marker=dict(size=13, color="#e0f7fa", symbol="circle", line=dict(color=style["color"], width=3)),
                text=[f"💥 {name}"],
                textposition="top center",
                name=f"{name} ({d0:.0f} pc)",
            )
        )

        # Focal line Earth -> Supernova
        fig.add_trace(
            go.Scatter3d(
                x=[0, xe],
                y=[0, ye],
                z=[0, ze],
                mode="lines",
                line=dict(color=style["color"], width=2, dash="dash"),
                name=f"Line of Sight: {sn_key}",
            )
        )

        # Translucent 3D Mesh
        try:
            X_mesh, Y_mesh, Z_mesh = _create_ellipsoid_mesh(xe, ye, ze, d0, elapsed_years, n_points=40)
            fig.add_trace(
                go.Surface(
                    x=X_mesh,
                    y=Y_mesh,
                    z=Z_mesh,
                    colorscale=[[0, style["mesh_color"]], [1, style["mesh_color"]]],
                    showscale=False,
                    name=f"Ellipsoid Mesh: {sn_key} ({elapsed_years:.0f} yr)",
                    hoverinfo="name",
                    opacity=0.25,
                )
            )
        except Exception as err:
            print(f"Warning: Could not render mesh for {sn_key}: {err}")

    # Render Candidate Stars if provided
    if stars_df is not None and not stars_df.empty:
        xs, ys, zs = spherical_to_cartesian(stars_df["ra"], stars_df["dec"], stars_df["dist_pc"])
        hover_texts = [
            f"<b>Star ID:</b> {row.get('source_id', 'N/A')}<br>"
            f"<b>RA:</b> {row['ra']:.4f}° | <b>Dec:</b> {row['dec']:.4f}°<br>"
            f"<b>Distance:</b> {row['dist_pc']:.1f} pc"
            for _, row in stars_df.iterrows()
        ]

        fig.add_trace(
            go.Scatter3d(
                x=xs,
                y=ys,
                z=zs,
                mode="markers",
                marker=dict(size=5, color="#ffffff", opacity=0.85),
                text=hover_texts,
                hoverinfo="text",
                name="Gaia DR3 Stars Catalog",
            )
        )

    fig.update_layout(
        template="plotly_dark",
        title=dict(
            text=f"🌌 Multi-Supernova SETI Ellipsoids Superposition 3D Map | ({current_year})",
            font=dict(size=16, color="#00e5ff"),
        ),
        scene=dict(
            xaxis=dict(title="X (parsecs)", backgroundcolor="#111", gridcolor="#333"),
            yaxis=dict(title="Y (parsecs)", backgroundcolor="#111", gridcolor="#333"),
            zaxis=dict(title="Z (parsecs)", backgroundcolor="#111", gridcolor="#333"),
            aspectmode="data",
            camera=dict(
                up=dict(x=0, y=0, z=1),
                eye=dict(x=1.5, y=1.5, z=1.2),
            ),
        ),
        dragmode="turntable",
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(0,0,0,0.8)",
            bordercolor="rgba(0,229,255,0.4)",
            borderwidth=1,
        ),
        margin=dict(l=0, r=0, b=0, t=40),
    )

    if output_html is None:
        os.makedirs("scratch", exist_ok=True)
        output_html = os.path.abspath("scratch/seti_multi_supernovae_3d_map.html")

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
            ],
        },
    )
    print(f"✅ Interactive Multi-Supernova 3D Map generated: {output_html}")
    return output_html
