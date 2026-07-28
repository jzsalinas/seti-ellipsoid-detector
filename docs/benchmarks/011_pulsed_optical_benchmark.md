# 🔬 EXP-011: APF / Lick Observatory Pulsed Optical Technosignature Benchmark

- **Date:** 2026-07-28
- **Primary Script:** `scripts/benchmark_pulsed_optical.py`
- **Modules Evaluated:** `core/optical_engine.py`, `providers/apf_provider.py`
- **Documentation:** `docs/OPTICAL_TECHNOSIGNATURE_MODEL.md`
- **Status:** ✅ Completed

---

## 🎯 Benchmark Objective
Evaluate Layer 5 high-resolution optical spectrograph cross-matching (Automated Planet Finder - APF Levy Spectrograph at Lick Observatory, $374 - 970 \text{ nm}$ at $R \approx 100,000$) for target stars crossing active SETI Ellipsoid light shells to identify monochromatic ($\Delta \lambda \le 0.05 \text{ \AA}$), high-contrast ($\mathcal{F}_{\text{peak}} / \mathcal{F}_{\text{continuum}} \ge 5.0$) optical laser emission pulses ($\lambda = 532 \text{ nm}$ or $1064 \text{ nm}$).

---

## 📊 Quantitative Pipeline Results

- **Synthetic Catalog Size:** 500 stars (dist $\le 1,500 \text{ pc}$)
- **Active Shell Candidates (±730 days / Bureaucratic Latency):** 6 target stars crossing active SETI Ellipsoid light shells
- **APF Levy Spectrograph Archives Cross-Matched:** 6/6 stars matched with high-resolution spectra
- **Optical Laser Technosignature Candidates Detected:** 3 target stars meeting ultra-narrow monochromatic linewidth and peak contrast thresholds

### Optical Laser Candidate Evaluation Summary

| Source ID | Dist (pc) | Monochromatic Peak Wavelength ($\lambda$) | Linewidth ($\Delta \lambda$) | Peak-to-Continuum Ratio | Significance ($\sigma$) | Optical Technosignature Candidate | Score |
|---|---|---|---|---|---|---|---|
| `GAIA_DR3_6000315` | 99.0 | $5320.0 \text{ \AA}$ ($532 \text{ nm}$) | **0.0166 \AA** | **13.13** | **14.0 $\sigma$** | 🔦 **Optical Laser** | **13.81** |
| `GAIA_DR3_6000236` | 278.7 | $5320.0 \text{ \AA}$ ($532 \text{ nm}$) | **0.0242 \AA** | **14.96** | **14.7 $\sigma$** | 🔦 **Optical Laser** | **11.33** |
| `GAIA_DR3_6000073` | 80.2 | $5320.0 \text{ \AA}$ ($532 \text{ nm}$) | **0.0281 \AA** | **17.65** | **12.9 $\sigma$** | 🔦 **Optical Laser** | **10.15** |
| `GAIA_DR3_6000037` | 336.5 | $4790.9 \text{ \AA}$ | 2.3049 \AA | 1.69 | 1.8 $\sigma$ | False (Stellar Line) | 0.00 |

---

## 🚀 Key Technical Insights

1. **Monochromatic Spectral Line Resolution:** High-resolution spectrographs ($R \approx 100,000$) resolve narrow artificial laser emissions ($\Delta \lambda < 0.05 \text{ \AA}$) from thermal Doppler-broadened stellar absorption lines ($\Delta \lambda > 0.5 \text{ \AA}$).
2. **5-Layer Multilayer Convergence:** Combining 3D light-delay geometry, mid-IR Dyson waste heat, optical alert stream anomalies, narrowband radio drift, and pulsed optical spectroscopy isolates ultra-high confidence technosignature targets.
3. **Artifact Export:** Results export cleanly to CSV artifacts (`scratch/pulsed_optical_candidates_exp011.csv`).
