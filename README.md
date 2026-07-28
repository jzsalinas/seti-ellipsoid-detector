# 🛰️ SETI Ellipsoid Detector

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests: Pytest](https://img.shields.io/badge/tests-pytest-green.svg)](https://docs.pytest.org/)

An open-source, modular Python framework to detect candidate technosignatures and anomalous stellar transients active on the **SETI Ellipsoid shell** around historical supernova events (such as **SN 1987A**, **SN 1572 Tycho**, **SN 1604 Kepler**, **SN 1054 Crab**) and discrete cosmic anchors (**Pulsar Glitches**, **Magnetar Giant Flares**, and **Binary Pulsar Periastrons**).

---

## 🌌 The SETI Ellipsoid Concept & Multi-Anchor Geometry

The **SETI Ellipsoid** is a geometric strategy for Search for Extraterrestrial Intelligence (SETI) observations. It assumes that an extraterrestrial civilization observing a prominent galactic event (such as Supernova 1987A or a Pulsar Glitch) might emit synchronized signals towards Earth.

```text
                   [ Cosmic Anchor / Supernova / Glitch ] (E)
                                  /        \
                                 /          \  d2
                                /            \
                            d0 /              v
                              /         [ Target Star ] (S)
                             /               /
                            v               /  d1
                     [ Earth / Observer ] <-/
                            (O)
```

The arrival time difference $\Delta t$ between the direct event light reaching Earth and a signal emitted by target star $S$ upon seeing the event is:

$$\Delta t = \frac{d_1 + d_2 - d_0}{c}$$

### 👽 ETI Reaction Latency & Spatial Shell Thickness

Recognizing that ETI observers incur detection, deliberation, and transmission latencies, the search window tolerance $\Delta t_{\text{tolerance}}$ defines a 3D spatial shell thickness $\Delta R_{\text{shell}}$ centered on the exact geometric surface:

$$\Delta R_{\text{shell}} (\text{pc}) = \frac{\Delta t_{\text{tolerance}} (\text{years})}{3.261563777}$$

Standardized profiles in `core.anchor.AlienLatencyProfile`:
- **`AUTOMATED_BEACON`**: $\pm 60 \text{ days}$ ($\sim 0.16 \text{ yr} \approx 0.05 \text{ pc}$ shell thickness).
- **`BUREAUCRATIC`**: $\pm 730 \text{ days}$ ($\sim 2.0 \text{ yr} \approx 0.61 \text{ pc}$ shell thickness).
- **`GENERATIONAL`**: $\pm 1825 \text{ days}$ ($\pm 5.0 \text{ yr} \approx 1.53 \text{ pc}$ shell thickness).

Read the complete theoretical physics documentation in **[docs/ALIEN_LATENCY_MODEL.md](docs/ALIEN_LATENCY_MODEL.md)**.

---

## ✨ Key Features

- **📐 3D Geometric Engine (`core/geometry.py`):** Calculates 3D ICRS Cartesian positions, single-shell light travel delays, multi-anchor intersection scoring (RMS Delay), and active shell crossings. Fully vectorized for processing large DataFrames (`NumPy` & `Pandas`).
- **⚡ Discrete Cosmic Anchors (`core/anchor.py` & `providers/pulsar_provider.py`):** Supports discrete temporal markers including Supernovae, Pulsar Glitches (Vela, Crab), Magnetar Giant Flares (SGR 1806-20), and Binary Pulsar Periastron passages.
- **🌐 Interactive 3D WebGL Visualizer (`core/visualizer.py`):** Generates dark-themed interactive 3D WebGL HTML plots rendering Earth, anchor foci, target stars, translucent 3D ellipsoid surfaces, and multi-anchor intersection candidates in real-time.
- **🌌 Gaia DR3 Provider (`providers/gaia_provider.py`):** Queries ESA Gaia DR3 astrometric data using ADQL via `pyvo`, automatically calculating stellar distances from parallax.
- **⚡ Fink Broker Ingestion (`providers/fink_provider.py`):** Ingests real-time photometric alert histories ($g$ and $r$ optical filters) from ZTF / Vera C. Rubin Observatory alerts via Fink REST API.
- **🤖 Unsupervised Anomaly Engine (`core/anomaly_engine.py`):** Computes light curve feature vectors (magnitude variance, peak-to-peak range, skewness, $(g-r)$ color index, fit residuals) and scores anomalies using `IsolationForest` (`scikit-learn`).
- **📊 Dark-Mode Plotter & Telegram Notifier (`notifier/telegram_bot.py`):** Generates publication-quality dark-mode light curve plots and dispatches alerts directly to Telegram channels.

---

## 🏗️ Project Architecture

```text
seti-ellipsoid-detector/
├── config.py                 # Global constants (anchors, physical parameters)
├── core/
│   ├── __init__.py
│   ├── anchor.py             # CosmicAnchor dataclass, AnchorType, & AlienLatencyProfile
│   ├── geometry.py           # 3D spatial geometry, light delays, & multi-anchor RMS scoring
│   ├── anomaly_engine.py     # Feature extraction & IsolationForest anomaly scoring
│   └── visualizer.py         # Plotly WebGL interactive 3D map & multi-anchor intersection renderer
├── providers/
│   ├── __init__.py
│   ├── gaia_provider.py      # ADQL queries to ESA Gaia DR3 via pyvo
│   ├── fink_provider.py      # Fink Broker REST API consumer (ZTF / Rubin alerts)
│   └── pulsar_provider.py    # Cosmic anchors catalog provider (Pulsars, Glitches, Flares)
├── notifier/
│   ├── __init__.py
│   └── telegram_bot.py       # Light curve plotting & Telegram alert dispatcher
├── pipeline.py               # Main end-to-end orchestrator script
├── requirements.txt          # Project dependencies
├── LICENSE                   # MIT License
├── docs/                     # Documentation & Experiment Registry
│   ├── ALIEN_LATENCY_MODEL.md
│   ├── EXPERIMENTS.md
│   └── benchmarks/
├── scripts/                  # Command-line tools & benchmarks
│   ├── visualize_ellipsoid_3d.py
│   ├── visualize_multi_ellipsoids_3d.py
│   ├── visualize_multi_anchors_3d.py
│   ├── benchmark_performance.py
│   ├── benchmark_anomaly.py
│   └── record_experiment.py
└── tests/                    # Unit & integration test suite (20+ tests)
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

### 2. Interactive 3D Multi-Anchor Map (Supernovae + Pulsars)

Render historical supernovae and pulsar glitch ellipsoids simultaneously in 3D WebGL:

```bash
python scripts/visualize_multi_anchors_3d.py --tolerance 365 --min-hits 2
```

Open `scratch/multi_anchor_intersection_3d.html` in your browser to inspect the superposed 3D ellipsoids!

---

## 🧪 Running Unit Tests

Execute the full test suite (20+ passing unit & integration tests):

```bash
pytest -v
```

---

## 📄 License

This project is open-source software licensed under the **[MIT License](LICENSE)**.
