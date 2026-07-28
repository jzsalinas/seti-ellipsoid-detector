# 🌌 Mid-Infrared Excess & Dyson Swarm Technosignature Model

## 1. Executive Summary & Physics Overview

A primary observational technosignature for advanced ETI civilizations (Kardashev Scale Type II / II+) is the collection and utilization of stellar energy via circumstellar artificial megastructures, commonly known as **Dyson Spheres or Dyson Swarms**.

According to the laws of thermodynamics, any artificial structure capturing stellar energy must ultimately re-radiate waste heat into the interstellar medium at an equilibrium radiation temperature $T_{\text{equilibrium}} \sim 100 - 300 \text{ K}$.

By **Wien's Displacement Law**, peak thermal emission for waste heat at $100 - 300 \text{ K}$ falls squarely in the mid-infrared spectrum ($10 - 30 \ \mu\text{m}$):

$$\lambda_{\text{peak}} = \frac{2898 \ \mu\text{m} \cdot \text{K}}{T} \implies \lambda_{\text{peak}} \approx 10 \text{ to } 29 \ \mu\text{m}$$

This matches the sensitivity bands of the **WISE / AllWISE Space Telescope**:
- **W1:** $3.4 \ \mu\text{m}$ (Stellar Photosphere)
- **W2:** $4.6 \ \mu\text{m}$ (Stellar Photosphere)
- **W3:** $12.0 \ \mu\text{m}$ (Warm Dust / Waste Heat $T \sim 250 \text{ K}$)
- **W4:** $22.0 \ \mu\text{m}$ (Cool Dust / Waste Heat $T \sim 130 \text{ K}$)

---

## 2. Mathematical Formalism & Excess Calculation

Normal main-sequence stars follow a Rayleigh-Jeans blackbody slope in mid-IR where photospheric colors satisfy:

$$(W1 - W2)_{\text{star}} \approx 0, \quad (W3 - W4)_{\text{star}} \approx 0$$

An active **Dyson Swarm** surrounding a target star on the active SETI Ellipsoid shell adds a thermal blackbody component $\mathcal{F}_{\text{waste}}(\lambda)$ to the unattenuated stellar flux $\mathcal{F}_{\text{star}}(\lambda)$:

$$\mathcal{F}_{\text{total}}(\lambda) = \mathcal{F}_{\text{star}}(\lambda) + \gamma \cdot \mathcal{B}(\lambda, T_{\text{waste}})$$

Where $\gamma$ is the covering factor ($0 < \gamma \le 1$).

### Infrared Excess Metric ($\Delta E_{W3-W4}$)

$$\text{Excess}_{W3-W4} = (W3 - W4)_{\text{observed}} - \text{Expected}_{W3-W4}(W1 - W2)$$

Candidate stars meeting both criteria are tagged as **Dyson Swarm Technosignature Candidates**:
1. $\text{Excess}_{W3-W4} \ge 1.0 \text{ mag}$
2. $(W1 - W4) \ge 2.5 \text{ mag}$

---

## 3. Integration with SETI Ellipsoid Geometric Filtering

Combining mid-IR excess filtering with 3D SETI Ellipsoid geometric cross-matching isolates stars that are **simultaneously**:
1. Positioned on the active light-delay shell of a galactic event ($t_{\text{elapsed}} = \frac{d_1 + d_2 - d_0}{c}$).
2. Exhibiting anomalous thermal waste-heat emission consistent with active industrial megastructures.

This two-pronged strategy drastically reduces false positives from dusty young stellar objects (YSOs) or asymptotic giant branch (AGB) stars.
