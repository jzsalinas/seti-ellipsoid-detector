# 🔬 EXP-010: Breakthrough Listen Open Data Radio Technosignature & Doppler Drift Benchmark

- **Date:** 2026-07-28
- **Primary Script:** `scripts/benchmark_breakthrough_listen.py`
- **Modules Evaluated:** `core/radio_engine.py`, `providers/breakthrough_provider.py`
- **Documentation:** `docs/RADIO_TECHNOSIGNATURE_MODEL.md`
- **Status:** ✅ Completed

---

## 🎯 Benchmark Objective
Evaluate Layer 4 high-resolution radio observation cross-matching (Breakthrough Listen GBT / Parkes Observatory $L, S, C, X$ bands) for target stars crossing active SETI Ellipsoid light shells to identify narrow-band ($\Delta \nu \le 5 \text{ Hz}$) drifting ($\dot{\nu} \sim \text{Hz/s}$) radio technosignatures.

---

## 📊 Quantitative Pipeline Results

- **Synthetic Catalog Size:** 500 stars (dist $\le 2,000 \text{ pc}$)
- **Active Shell Candidates (±730 days / Bureaucratic Latency):** 4 target stars crossing active SETI Ellipsoid light shells
- **Breakthrough Listen Radio Archives Cross-Matched:** 4/4 stars matched with $L$-band ($1.42 \text{ GHz}$) observations
- **Radio Technosignature Candidates Detected:** 1 target star (`GAIA_DR3_5000150`) meeting narrow bandwidth, Doppler drift, and SNR thresholds

### Radio Candidate Evaluation Summary

| Source ID | Dist (pc) | Telescope Observatory | Bandwidth ($\Delta \nu$) | Drift Rate ($\dot{\nu}_{\text{drift}}$) | SNR | Technosignature Candidate | Technosignature Score |
|---|---|---|---|---|---|---|---|
| `GAIA_DR3_5000150` | 1345.2 | Green Bank Telescope | **0.71 Hz** | **0.94 Hz/s** | **36.4** | 📻 **Radio Candidate** | **25.68** |
| `GAIA_DR3_5000401` | 77.5 | Parkes Observatory | 26.06 kHz | 0.001 Hz/s | 6.3 | False (Natural Emission) | 0.00 |
| `GAIA_DR3_5000318` | 190.4 | Parkes Observatory | 28.75 kHz | 0.001 Hz/s | 3.1 | False (Natural Emission) | 0.00 |
| `GAIA_DR3_5000340` | 504.4 | Parkes Observatory | 1.91 kHz | 0.001 Hz/s | 5.3 | False (Natural Emission) | 0.00 |

---

## 🚀 Key Technical Insights

1. **RFI and Natural Emission Discrimination:** Wideband natural emissions ($\Delta \nu > 1 \text{ kHz}$) and static zero-drift signals ($\dot{\nu} \approx 0$) are cleanly filtered out, isolating narrow-band drifting signals characteristic of non-terrestrial artificial transmitters.
2. **Doppler Acceleration Physics:** Incorporating Doppler drift rate calculations ($\dot{\nu} = -\nu_0 \frac{a_{\parallel}}{c}$) accounts for planetary rotation and exoplanetary orbital motion.
3. **Artifact Export:** Candidate radio detections export to structured CSV artifacts (`scratch/radio_technosignature_candidates_exp010.csv`).
