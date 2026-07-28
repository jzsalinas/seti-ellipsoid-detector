# 📻 Narrow-Band Radio Technosignatures & Doppler Drift Model

## 1. Executive Summary & Physics Overview

Radio technosignature searches (pioneered by Project Ozma and scaled by **Breakthrough Listen**) search for artificial narrow-band radio signals emitted by extraterrestrial transmitters.

Natural astrophysical radio processes (synchrotron emission, thermal bremsstrahlung, interstellar masers) emit over wide frequency bands ($\Delta \nu > \text{kHz} \text{ to } \text{MHz}$).

In contrast, point-to-point radio transmissions engineered by advanced ETI civilizations concentrate power into **ultra-narrow bandwidths** ($\Delta \nu \le 5 \text{ Hz}$) to optimize Signal-to-Noise Ratio ($\text{SNR}$) across interstellar distances:

$$\text{SNR} \propto \frac{P_{\text{transmitter}}}{\sqrt{\Delta \nu \cdot T_{\text{system}}}}$$

---

## 2. Linear Doppler Drift Rate Mechanics ($\dot{\nu}_{\text{drift}}$)

Because both the transmitting planet (host exoplanet) and receiving planet (Earth) undergo rotational and orbital acceleration, any non-ecliptic narrow-band radio signal exhibits a deterministic **line-of-sight Doppler drift rate** $\dot{\nu}_{\text{drift}}$ in Hz/s:

$$\dot{\nu}_{\text{drift}} = \frac{d\nu}{dt} = -\frac{\nu_0}{c} \cdot a_{\parallel}$$

Where:
- $\nu_0$: Carrier frequency ($\text{MHz}$).
- $a_{\parallel}$: Net line-of-sight acceleration vector ($\text{m/s}^2$) resulting from planetary rotation ($a_{\text{rot}} \approx 0.034 \text{ m/s}^2$ for Earth) and orbital revolution ($a_{\text{orb}} \approx 0.0059 \text{ m/s}^2$).
- $c$: Speed of light ($299,792,458 \text{ m/s}$).

### Plausible Doppler Drift Bounds

For typical Earth-sized exoplanets orbiting G/K/M dwarf stars:

$$0.01 \text{ Hz/s} \le |\dot{\nu}_{\text{drift}}| \le 4.00 \text{ Hz/s}$$

Signals exhibiting exact zero drift ($\dot{\nu} \approx 0.00 \text{ Hz/s}$) are flagged as **Radio Frequency Interference (RFI)** originating from terrestrial ground transmitters.

---

## 3. Breakthrough Listen Receiver Bands

| Band Name | Frequency Range ($\text{GHz}$) | Primary Astronomical / SETI Targets |
|---|---|---|
| **`L_band`** | $1.10 - 1.90 \text{ GHz}$ | Neutral Hydrogen 21 cm Line ($1.4204 \text{ GHz}$) / "Water Hole" ($1.42 - 1.66 \text{ GHz}$) |
| **`S_band`** | $1.80 - 2.80 \text{ GHz}$ | Deep Space Network (DSN) S-band uplink frequencies |
| **`C_band`** | $3.95 - 8.00 \text{ GHz}$ | Interstellar scintillation minimum windows |
| **`X_band`** | $7.80 - 11.20 \text{ GHz}$ | High-frequency interstellar communication windows |

---

## 4. Integration with SETI Ellipsoid Pipeline (Layer 4)

Cross-matching candidate stars crossing active SETI Ellipsoid light-delay shells with Breakthrough Listen GBT / Parkes radio archives isolates targets meeting **4 simultaneous criteria**:

1. Geometric positioning on active 3D SETI Ellipsoid light shell.
2. Mid-infrared waste-heat excess (Layer 2 Dyson Swarms).
3. Optical light curve variability (Layer 3 Fink stream).
4. Narrow-band ($\Delta \nu \le 5 \text{ Hz}$) drifting ($\dot{\nu} \sim \text{Hz/s}$) radio emission ($\text{SNR} \ge 10$).
