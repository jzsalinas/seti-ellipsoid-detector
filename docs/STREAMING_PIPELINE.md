# ⚡ Fink Broker Real-Time Streaming & Photometric Anomaly Monitoring (Layer 3)

## 1. Executive Summary & System Architecture

Layer 3 of the **SETI Ellipsoid Detector** pipeline establishes continuous real-time photometric alert stream processing via the **Fink Broker** (ingesting ZTF and Vera C. Rubin Observatory LSST alert streams).

When candidate stars on active SETI Ellipsoid light-delay shells enter observation windows, their transient optical light curves ($g$ and $r$ passbands) are processed in real-time by our unsupervised `IsolationForest` anomaly engine.

```text
 ┌────────────────────────────────────────────────────────┐
 │ Layer 1: 3D SETI Ellipsoid & Alien Latency Filtering   │
 └───────────────────────────┬────────────────────────────┘
                             │ Active Shell Candidates
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │ Layer 2: AllWISE Mid-IR Excess (Dyson Swarm Search)    │
 └───────────────────────────┬────────────────────────────┘
                             │ Candidate Targets
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │ Layer 3: Fink Broker Alert Ingestion & Light Curve ML  │
 │ - Photometric extraction (g, r passbands)             │
 │ - Feature vector calculation (variance, skew, color)   │
 │ - IsolationForest Anomaly Scoring                     │
 └───────────────────────────┬────────────────────────────┘
                             │ Triggered Anomalies
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │ Layer 4: Publication & Telegram Alert Dispatcher       │
 └────────────────────────────────────────────────────────┘
```

---

## 2. Fink Broker Ingestion Methods

1. **REST Explorer Endpoint (`/api/v1/explorer`):** Cone searches around RA, Dec coordinates for historical and active alerts.
2. **REST Latests Endpoint (`/api/v1/latests`):** Ingests real-time alert streams filtered by classification labels (`Anomaly`, `Supernova`, `Microlensing`, `Unknown`).
3. **Kafka Live Topic Consumer (`FinkProvider`):** Batch polling and continuous streaming of target light curves.

---

## 3. Light Curve Feature Extraction Vector

For each stream light curve, our `AnomalyEvaluator` extracts a 5-dimensional feature vector $\vec{\mathcal{F}}$:

1. **Photometric Variance ($\sigma_{\text{mag}}^2$):** Overall variability in optical brightness.
2. **Peak-to-Peak Range ($\Delta m = m_{\text{max}} - m_{\text{min}}$):** Maximum flux excursion.
3. **Light Curve Skewness ($\gamma_1$):** Asymmetry of brightness bursts.
4. **Optical Color Index ($(g - r)$):** Mean chromaticity across ZTF filters.
5. **Fit Residual Variance ($\chi_{\text{fit}}^2$):** Deviation from standard astrophysical stellar variability models.

---

## 4. Real-Time Anomaly Scoring & Alert Triggering

The feature vector is evaluated by `IsolationForest`:

$$\text{Anomaly Score}(S) \in [0, 1]$$

Where scores exceeding the threshold ($\text{Score} \ge \text{Threshold}$) trigger high-priority alerts dispatched directly to Telegram channels and exported as CSV candidates.
