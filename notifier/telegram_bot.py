"""
Telegram Bot Notifier & Light Curve Plotting.

Generates dark-mode high-contrast matplotlib light curve charts for anomalous candidates
and dispatches Telegram alerts.
"""

from typing import Optional
import os
import matplotlib.pyplot as plt
import pandas as pd
import requests


def generate_lightcurve_plot(
    star_id: str,
    lightcurve_df: pd.DataFrame,
    anomaly_score: float,
    output_path: Optional[str] = None,
) -> str:
    """
    Generates a publication-quality dark-mode light curve plot for a candidate star.

    Args:
        star_id: Identifier of the candidate star (Gaia or Fink object ID).
        lightcurve_df: DataFrame containing lightcurve columns ['jd', 'magpsf', 'filter'].
        anomaly_score: Calculated anomaly score between 0.0 and 1.0.
        output_path: Path to save PNG image. If None, saves to 'scratch/star_id_lc.png'.

    Returns:
        Absolute filepath to the generated plot image.
    """
    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(9, 5), dpi=150)

    if not lightcurve_df.empty and "magpsf" in lightcurve_df.columns:
        # Plot g-band
        df_g = lightcurve_df[lightcurve_df["filter"] == "g"]
        if not df_g.empty:
            ax.errorbar(
                df_g["jd"] - 2400000.5,
                df_g["magpsf"],
                yerr=df_g.get("sigmagpsf", 0.02),
                fmt="o",
                color="#00e676",
                label="Filter g",
                alpha=0.85,
                capsize=3,
            )

        # Plot r-band
        df_r = lightcurve_df[lightcurve_df["filter"] == "r"]
        if not df_r.empty:
            ax.errorbar(
                df_r["jd"] - 2400000.5,
                df_r["magpsf"],
                yerr=df_r.get("sigmagpsf", 0.02),
                fmt="s",
                color="#ff1744",
                label="Filter r",
                alpha=0.85,
                capsize=3,
            )

    ax.invert_yaxis()  # Standard astronomical convention: fainter magnitude is down
    ax.set_xlabel("Modified Julian Date (MJD)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Apparent Magnitude (mag)", fontsize=11, fontweight="bold")
    ax.set_title(
        f"SETI Candidate: {star_id} | Anomaly Score: {anomaly_score:.3f}",
        fontsize=13,
        fontweight="bold",
        pad=12,
        color="#00e5ff",
    )
    ax.grid(True, linestyle="--", alpha=0.3)
    ax.legend(loc="best", framealpha=0.8)

    plt.tight_layout()

    if output_path is None:
        os.makedirs("scratch", exist_ok=True)
        output_path = os.path.abspath(f"scratch/lc_{star_id}.png")

    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    return output_path


def send_alert(
    star_id: str,
    anomaly_score: float,
    lightcurve_df: pd.DataFrame,
    ra: float = 0.0,
    dec: float = 0.0,
    bot_token: Optional[str] = None,
    chat_id: Optional[str] = None,
) -> bool:
    """
    Dispatches a Telegram alert with the light curve plot and candidate metadata.
    If bot_token or chat_id are missing, saves the plot image locally and logs notification.
    """
    plot_path = generate_lightcurve_plot(star_id, lightcurve_df, anomaly_score)

    caption = (
        f"🚨 <b>SETI Ellipsoid Anomaly Detection</b> 🚨\n\n"
        f"<b>Star ID:</b> {star_id}\n"
        f"<b>Coordinates:</b> RA {ra:.4f}°, Dec {dec:.4f}°\n"
        f"<b>Anomaly Score:</b> <code>{anomaly_score:.4f}</code>\n"
        f"<b>Observations:</b> {len(lightcurve_df)} points\n\n"
        f"<i>Candidate is active on the SN 1987A Ellipsoid shell.</i>"
    )

    token = bot_token or os.environ.get("TELEGRAM_BOT_TOKEN")
    cid = chat_id or os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not cid:
        print(f"[Notifier] Local Alert generated for {star_id} (Score: {anomaly_score:.3f}). Plot saved to: {plot_path}")
        return True

    url = f"https://api.telegram.org/bot{token}/sendPhoto"

    try:
        with open(plot_path, "rb") as img_file:
            payload = {
                "chat_id": cid,
                "caption": caption,
                "parse_mode": "HTML",
            }
            files = {"photo": img_file}
            res = requests.post(url, data=payload, files=files, timeout=15.0)
            if not res.ok:
                print(f"[Notifier] Telegram API Error ({res.status_code}): {res.text}")
                return False
            print(f"[Notifier] Telegram alert successfully sent to chat {cid} for {star_id}.")
            return True
    except Exception as err:
        print(f"[Notifier] Failed to send Telegram alert: {err}")
        return False
