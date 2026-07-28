# 📜 SETI Ellipsoid Candidate Master Catalog Specification

## 1. Executive Summary & Multilayer Pipeline Overview

The **SETI Ellipsoid Candidate Master Catalog** synthesizes multi-wavelength astronomical observations and mathematical models into a public priority list of target stars for observational SETI campaigns.

It aggregates 5 distinct observational layers into a unified **SETI Priority Score** ($\text{Score} \in [0.0, 100.0]$):

```text
 ┌────────────────────────────────────────────────────────┐
 │ Layer 1: 3D Light-Delay & Alien Latency Geometry       │ (20% Weight)
 ├────────────────────────────────────────────────────────┤
 │ Layer 2: AllWISE Mid-IR Excess (Dyson Swarm Waste Heat)│ (20% Weight)
 ├────────────────────────────────────────────────────────┤
 │ Layer 3: Fink Broker Optical Alerts (IsolationForest) │ (20% Weight)
 ├────────────────────────────────────────────────────────┤
 │ Layer 4: Breakthrough Listen Radio (Doppler Drift)     │ (20% Weight)
 ├────────────────────────────────────────────────────────┤
 │ Layer 5: APF Pulsed Monochromatic Laser Emission       │ (20% Weight)
 └───────────────────────────┬────────────────────────────┘
                             │ Composite Priority Score (0-100)
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │ Priority Tiers: CRITICAL | HIGH | MEDIUM | SHELL_MONITOR│
 └────────────────────────────────────────────────────────┘
```

---

## 2. Composite SETI Priority Score Formula

$$\text{PriorityScore} = S_{\text{L1}} + S_{\text{L2}} + S_{\text{L3}} + S_{\text{L4}} + S_{\text{L5}}$$

Where each layer contributes up to 20 points ($20\%$ weight):

| Layer | Subsystem / Parameter Evaluated | Layer Score Calculation |
|---|---|---|
| **Layer 1** | 3D Geometry & Multi-Anchor Hits | $S_{\text{L1}} = \min(20.0, \text{Hits}_{\text{anchors}} \cdot 10.0)$ |
| **Layer 2** | AllWISE Mid-IR Excess ($\Delta(W3-W4)$) | $S_{\text{L2}} = \min(20.0, \text{Score}_{\text{IR}} \cdot 15.0)$ |
| **Layer 3** | Fink Optical Light Curve ML Anomaly | $S_{\text{L3}} = \min(20.0, \text{Score}_{\text{IsolationForest}} \cdot 20.0)$ |
| **Layer 4** | Breakthrough Listen Radio Drift ($\dot{\nu}$) | $S_{\text{L4}} = \min(20.0, \text{Score}_{\text{Radio}} \cdot 0.8)$ |
| **Layer 5** | APF Optical Laser Pulse ($\Delta \lambda \le 0.05 \text{ \AA}$) | $S_{\text{L5}} = \min(20.0, \text{Score}_{\text{Optical}} \cdot 1.5)$ |

---

## 3. Standardized Observational Priority Tiers

| Priority Tier | Score Range | Actionable Observational Recommendation |
|---|---|---|
| 🚨 **`CRITICAL_TARGET`** | $\ge 75.0$ | High-priority immediate observation across GBT, VLA, and Keck/APF. |
| ⭐ **`HIGH_PRIORITY`** | $50.0 - 74.9$ | Targeted spectroscopic and photometric follow-up. |
| 🔍 **`MEDIUM_PRIORITY`** | $25.0 - 49.9$ | Secondary target monitoring during sky surveys. |
| 🛰️ **`SHELL_MONITOR`** | $< 25.0$ | Background shell target tracking. |

---

## 4. Master Catalog Data Schema (CSV / JSON)

| Column Name | Data Type | Description |
|---|---|---|
| `source_id` | String | Gaia DR3 Unique Source Identifier |
| `ra`, `dec` | Float | ICRS Right Ascension and Declination in degrees |
| `dist_pc` | Float | Stellar distance from Earth in parsecs |
| `anchors_hit_count` | Integer | Number of cosmic anchor shells intersected simultaneously |
| `rms_delay_days` | Float | RMS delay deviation across intersected anchors |
| `excess_w3_w4` | Float | Mid-IR color excess in magnitudes ($W3 - W4$) |
| `is_dyson_candidate` | Boolean | True if target exhibits Dyson Swarm waste-heat excess |
| `anomaly_score` | Float | IsolationForest optical light curve anomaly score |
| `bandwidth_hz` | Float | Radio signal bandwidth in Hz |
| `drift_rate_hz_s` | Float | Line-of-sight Doppler drift rate in Hz/s |
| `is_radio_candidate` | Boolean | True if target exhibits narrow-band drifting radio emission |
| `linewidth_a` | Float | Optical emission linewidth in Angstroms |
| `is_optical_candidate` | Boolean | True if target exhibits monochromatic pulsed laser emission |
| `priority_score` | Float | Composite SETI Priority Score ($0.0 - 100.0$) |
| `priority_tier` | String | Standardized Observational Priority Tier |
