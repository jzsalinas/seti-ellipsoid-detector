# 🛰️ SETI Ellipsoid Detector

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests: Pytest](https://img.shields.io/badge/tests-pytest-green.svg)](https://docs.pytest.org/)

An open-source, modular Python framework to detect candidate technosignatures and anomalous stellar transients active on the **SETI Ellipsoid shell** around historical supernova events (such as **SN 1987A**, **SN 1572 Tycho**, **SN 1604 Kepler**, and **SN 1054 Crab**).

---

## 🌌 The SETI Ellipsoid Concept

The **SETI Ellipsoid** is a geometric strategy for Search for Extraterrestrial Intelligence (SETI) observations. It assumes that an extraterrestrial civilization observing a prominent galactic event (such as Supernova 1987A) might emit synchronized signals or optical/radio beacons towards Earth.

```
                   [ Supernova (SN 1987A) ] (E)
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

The arrival time difference $\Delta t$ between the direct supernova light reaching Earth and a signal emitted by target star $S$ upon seeing the supernova is:

$$\Delta t = \frac{d_1 + d_2 - d_0}{c}$$

Stars currently crossing the active ellipsoid surface satisfy:

$$d_1 + d_2 - d_0 = c \cdot (t_{\text{obs}} - t_{\text{SN}})$$

---

## ✨ Key Features

- **📐 3D Geometric Engine (`core/geometry.py`):** Calculates 3D ICRS Cartesian positions, light travel delays, and active shell crossings. Fully vectorized for processing large DataFrames (`NumPy` & `Pandas`).
- **🌐 Interactive 3D WebGL Visualizer (`core/visualizer.py`):** Generates dark-themed interactive 3D WebGL HTML plots rendering Earth, Supernova foci, target stars, and the active 3D SETI Ellipsoid shell in real-time.
- **🌌 Gaia DR3 Provider (`providers/gaia_provider.py`):** Queries ESA Gaia DR3 astrometric data using ADQL via `pyvo`, automatically calculating stellar distances from parallax.
- **⚡ Fink Broker Ingestion (`providers/fink_provider.py`):** Ingests real-time photometric alert histories ($g$ and $r$ optical filters) from ZTF / Vera C. Rubin Observatory alerts via Fink REST API.
- **🤖 Unsupervised Anomaly Engine (`core/anomaly_engine.py`):** Computes light curve feature vectors (magnitude variance, peak-to-peak range, skewness, $(g-r)$ color index, fit residuals) and scores anomalies using `IsolationForest` (`scikit-learn`).
- **📊 Dark-Mode Plotter & Telegram Notifier (`notifier/telegram_bot.py`):** Generates publication-quality dark-mode light curve plots and dispatches alerts directly to Telegram channels.

---

## 🏗️ Project Architecture

```text
seti-ellipsoid-detector/
├── config.py                 # Global constants (SN 1987A, Tycho, Kepler, Crab, search parameters)
├── core/
│   ├── __init__.py
│   ├── geometry.py           # 3D spatial geometry & light travel delay calculations
│   ├── anomaly_engine.py     # Feature extraction & IsolationForest anomaly scoring
│   └── visualizer.py         # Plotly WebGL interactive 3D ellipsoid renderer
├── providers/
│   ├── __init__.py
│   ├── gaia_provider.py      # ADQL queries to ESA Gaia DR3 via pyvo
│   └── fink_provider.py      # Fink Broker REST API consumer (ZTF / Rubin alerts)
├── notifier/
│   ├── __init__.py
│   └── telegram_bot.py       # Light curve plotting & Telegram alert dispatcher
├── pipeline.py               # Main end-to-end orchestrator script
├── requirements.txt          # Project dependencies
├── LICENSE                   # MIT License
├── docs/                     # Experiment Registry & Benchmark Reports
│   ├── EXPERIMENTS.md
│   └── benchmarks/
├── scripts/                  # Command-line tools & benchmarks
│   ├── visualize_ellipsoid_3d.py
│   ├── test_live_gaia.py
│   ├── test_multianchor.py
│   ├── benchmark_performance.py
│   ├── benchmark_anomaly.py
│   └── record_experiment.py
└── tests/                    # Unit & integration test suite (14 tests)
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

### 2. Interactive 3D Ellipsoid Visualization

Generate an interactive 3D WebGL plot in your browser:

```bash
python scripts/visualize_ellipsoid_3d.py --sn SN1572
```

Open the generated file `scratch/seti_ellipsoid_SN1572_3d.html` in any web browser to rotate, zoom, and inspect stars on the 3D SETI Ellipsoid surface!

### 3. Running the Pipeline

```python
from pipeline import run_pipeline

results = run_pipeline(
    ra_center=83.8667,
    dec_center=-69.2697,
    radius_deg=1.0,
    tolerance_days=30.0,
    anomaly_threshold=0.85,
    use_mock=False,
)

print(results.head())
```

---

## 🧪 Running Unit Tests

Execute the full test suite (14 passing unit & integration tests):

```bash
pytest -v
```

---

## 📄 License

This project is open-source software licensed under the **[MIT License](LICENSE)**.
