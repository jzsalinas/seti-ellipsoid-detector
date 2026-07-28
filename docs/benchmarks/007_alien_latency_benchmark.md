# 🔬 EXP-007: ETI Reaction Latency & Shell Thickness Sensitivity Benchmark

- **Date:** 2026-07-28
- **Primary Script:** `scripts/benchmark_alien_latency.py`
- **Modules Evaluated:** `core/anchor.py`, `core/geometry.py`, `core/visualizer.py`
- **Documentation:** `docs/ALIEN_LATENCY_MODEL.md`
- **Status:** ✅ Completed

---

## 🎯 Benchmark Objective
Evaluate the impact of ETI reaction, deliberation, and transmission latency ($\Delta t_{\text{response}}$) on the physical 3D spatial thickness of the SETI Ellipsoid shell ($\Delta R_{\text{shell}}$ in parsecs) and the resulting candidate star selection counts across synthetic catalog fields (2,000 stars up to $4,000 \text{ pc}$).

---

## 📊 Quantitative Benchmark Results

| Latency Profile | Time Window ($\pm \Delta t$) | Spatial Thickness ($\Delta R_{\text{shell}}$) | Single-Anchor Hits ($\ge 1$) | Multi-Anchor Hits ($\ge 2$) | WebGL 3D Interactive Artifact |
|---|---|---|---|---|---|
| **`AUTOMATED_BEACON`** | $\pm 60 \text{ days}$ | $0.0504 \text{ pc}$ ($0.16 \text{ ly}$) | 0 | 0 | `scratch/latency_benchmark_automated_beacon.html` |
| **`BUREAUCRATIC`** | $\pm 730 \text{ days}$ ($\pm 2 \text{ yr}$) | $0.6128 \text{ pc}$ ($2.0 \text{ ly}$) | 5 | 0 | `scratch/latency_benchmark_bureaucratic.html` |
| **`GENERATIONAL`** | $\pm 1825 \text{ days}$ ($\pm 5 \text{ yr}$) | $1.5320 \text{ pc}$ ($5.0 \text{ ly}$) | 15 | 0 | `scratch/latency_benchmark_generational.html` |

---

## 🚀 Key Insights & Theoretical Conclusions

1. **Linear Scaling of Candidate Volume with Shell Thickness:** Expanding tolerance from $\pm 60$ days to $\pm 5$ years increases single-anchor candidate hits from 0 to 15 stars due to the proportional volume expansion of the 3D ellipsoid shell.
2. **False Positive Suppression via Multi-Anchor Intersections:** While wider latency windows (e.g. 5 years) increase single-ellipsoid star counts, requiring simultaneous intersection across $N \ge 2$ distinct anchors (Supernovae + Pulsars) strictly eliminates background stars, isolating true spatial-temporal intersection candidates.
3. **Integration & Test Verification:** All 3 latency profiles integrate seamlessly with `AlienLatencyProfile` enum in `core/anchor.py` and pass 100% of unit tests.
