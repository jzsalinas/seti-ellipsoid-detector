# 🛰️ SETI Ellipsoid Detector

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests: Pytest](https://img.shields.io/badge/tests-pytest-green.svg)](https://docs.pytest.org/)

An open-source, modular Python framework to detect candidate technosignatures and anomalous stellar transients active on the **SETI Ellipsoid shell** around historical supernova events (**SN 1987A**, **SN 1572 Tycho**, **SN 1604 Kepler**, **SN 1054 Crab**) and discrete cosmic anchors (**Pulsar Glitches**, **Magnetar Giant Flares**, and **Binary Pulsar Periastrons**).

---

## 🌌 The SETI Ellipsoid Concept & 5-Layer Multilayer Architecture

The **SETI Ellipsoid** is a geometric strategy for Search for Extraterrestrial Intelligence (SETI) observations. It assumes that an extraterrestrial civilization observing a prominent galactic event (such as Supernova 1987A or a Pulsar Glitch) might emit synchronized signals towards Earth.

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
 │ Public Master Catalog: CRITICAL | HIGH | MEDIUM | SHELL │
 └────────────────────────────────────────────────────────┘
```

The arrival time difference $\Delta t$ between direct event light reaching Earth and a signal emitted by target star $S$ upon seeing the event is:

$$\Delta t = \frac{d_1 + d_2 - d_0}{c}$$

### 👽 ETI Reaction Latency & Spatial Shell Thickness

Recognizing that ETI observers incur detection, deliberation, and transmission latencies, the search window tolerance $\Delta t_{\text{tolerance}}$ defines a 3D spatial shell thickness $\Delta R_{\text{shell}}$ centered on the exact geometric surface:

$$\Delta R_{\text{shell}} (\text{pc}) = \frac{\Delta t_{\text{tolerance}} (\text{years})}{3.261563777}$$

Standardized profiles in `core.anchor.AlienLatencyProfile`:
- **`AUTOMATED_BEACON`**: $\pm 60 \text{ days}$ ($\sim 0.16 \text{ yr} \approx 0.05 \text{ pc}$ shell thickness).
- **`BUREAUCRATIC`**: $\pm 730 \text{ days}$ ($\sim 2.0 \text{ yr} \approx 0.61 \text{ pc}$ shell thickness).
- **`GENERATIONAL`**: $\pm 1825 \text{ days}$ ($\pm 5.0 \text{ yr} \approx 1.53 \text{ pc}$ shell thickness).

Read the complete theoretical physics documentation in **[docs/ALIEN_LATENCY_MODEL.md](docs/ALIEN_LATENCY_MODEL.md)**, **[docs/INFRARED_EXCESS_MODEL.md](docs/INFRARED_EXCESS_MODEL.md)**, **[docs/STREAMING_PIPELINE.md](docs/STREAMING_PIPELINE.md)**, **[docs/RADIO_TECHNOSIGNATURE_MODEL.md](docs/RADIO_TECHNOSIGNATURE_MODEL.md)**, **[docs/OPTICAL_TECHNOSIGNATURE_MODEL.md](docs/OPTICAL_TECHNOSIGNATURE_MODEL.md)**, and **[docs/MASTER_CATALOG_SPECIFICATION.md](docs/MASTER_CATALOG_SPECIFICATION.md)**.

---

## ✨ Key Features

- **📐 3D Geometric Engine (`core/geometry.py`):** Calculates 3D ICRS Cartesian positions, single-shell light travel delays, multi-anchor intersection scoring (RMS Delay), and active shell crossings. Fully vectorized (`NumPy` & `Pandas`).
- **⚡ Discrete Cosmic Anchors (`core/anchor.py` & `providers/pulsar_provider.py`):** Supports discrete temporal markers including Supernovae, Pulsar Glitches (Vela, Crab), Magnetar Giant Flares (SGR 1806-20), and Binary Pulsar Periastron passages.
- **🛸 Mid-IR Excess Engine (`core/infrared_engine.py` & `providers/wise_provider.py`):** Evaluates $W3-W4$ and $W1-W4$ blackbody color excess to detect waste-heat radiation ($100-300 \text{ K}$) from circumstellar Dyson Swarms.
- **⚡ Real-Time Fink Stream Monitoring (`providers/fink_provider.py` & `core/anomaly_engine.py`):** Ingests real-time ZTF/Rubin optical alert streams and computes light curve feature vectors scored by `IsolationForest`.
- **📻 Breakthrough Listen Radio Engine (`core/radio_engine.py` & `providers/breakthrough_provider.py`):** Cross-matches GBT / Parkes radio archives ($L, S, C, X$ bands) for narrowband ($\Delta \nu \le 5 \text{ Hz}$) drifting ($\dot{\nu} \sim \text{Hz/s}$) signals.
- **🔦 APF Pulsed Optical Laser Engine (`core/optical_engine.py` & `providers/apf_provider.py`):** Evaluates high-resolution spectrograph data (APF Levy Spectrograph) for monochromatic laser pulses ($\Delta \lambda \le 0.05 \text{ \AA}$).
- **🌟 Master Catalog Synthesizer (`core/master_catalog.py`):** Synthesizes all 5 layers into a normalized SETI Priority Score ($0-100$) and exports public CSV/JSON datasets.

---

## 🏗️ Project Architecture

```text
seti-ellipsoid-detector/
├── config.py                 # Global constants & parameters
├── core/
│   ├── __init__.py
│   ├── anchor.py             # CosmicAnchor dataclass, AnchorType, & AlienLatencyProfile
│   ├── geometry.py           # 3D spatial geometry, light delays, & multi-anchor RMS scoring
│   ├── infrared_engine.py    # AllWISE mid-IR excess & Dyson Swarm candidate evaluator
│   ├── anomaly_engine.py     # Light curve feature extraction & IsolationForest anomaly scoring
│   ├── radio_engine.py       # Breakthrough Listen narrow-band radio drift evaluator
│   ├── optical_engine.py     # APF Levy spectrograph monochromatic laser pulse evaluator
│   ├── master_catalog.py     # 5-Layer Master Catalog synthesizer & priority scoring engine
│   └── visualizer.py         # Plotly WebGL interactive 3D map & multi-anchor intersection renderer
├── providers/
│   ├── __init__.py
│   ├── gaia_provider.py      # ADQL queries to ESA Gaia DR3 via pyvo
│   ├── fink_provider.py      # Fink Broker REST API & stream consumer (ZTF / Rubin alerts)
│   ├── pulsar_provider.py    # Cosmic anchors catalog provider (Pulsars, Glitches, Flares)
│   ├── wise_provider.py      # AllWISE mid-IR photometry provider
│   ├── breakthrough_provider.py # Breakthrough Listen GBT / Parkes radio catalog provider
│   └── apf_provider.py       # APF / Lick Observatory optical spectrograph provider
├── notifier/
│   ├── __init__.py
│   └── telegram_bot.py       # Light curve plotting & Telegram alert dispatcher
├── pipeline.py               # Main end-to-end orchestrator script
├── requirements.txt          # Project dependencies
├── LICENSE                   # MIT License
├── docs/                     # Documentation & Experiment Registry (EXP-001 to EXP-012)
│   ├── ALIEN_LATENCY_MODEL.md
│   ├── INFRARED_EXCESS_MODEL.md
│   ├── STREAMING_PIPELINE.md
│   ├── RADIO_TECHNOSIGNATURE_MODEL.md
│   ├── OPTICAL_TECHNOSIGNATURE_MODEL.md
│   ├── MASTER_CATALOG_SPECIFICATION.md
│   ├── EXPERIMENTS.md
│   └── benchmarks/
├── scripts/                  # Command-line tools & benchmarks
│   ├── visualize_ellipsoid_3d.py
│   ├── visualize_multi_ellipsoids_3d.py
│   ├── visualize_multi_anchors_3d.py
│   ├── benchmark_alien_latency.py
│   ├── benchmark_infrared_excess.py
│   ├── benchmark_fink_streaming.py
│   ├── benchmark_breakthrough_listen.py
│   ├── benchmark_pulsed_optical.py
│   └── build_master_catalog.py
└── tests/                    # Unit & integration test suite (35 passing tests)
```

---

## 🚀 Quick Start

### 1. Installation

```bash
git clone https://github.com/your-username/seti-ellipsoid-detector.git
cd seti-ellipsoid-detector

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Build Public Master Catalog

Build and export the 5-layer public SETI Ellipsoid Candidate Master Catalog:

```bash
python scripts/build_master_catalog.py --profile bureaucratic --n-stars 1000
```

Inspect `scratch/seti_ellipsoid_master_catalog.csv` and `scratch/seti_ellipsoid_master_catalog.json`!

---

## 🧪 Running Unit Tests

Execute the full test suite (35 passing unit & integration tests):

```bash
pytest -v
```

---

## 📄 License

This project is open-source software licensed under the **[MIT License](LICENSE)**.
