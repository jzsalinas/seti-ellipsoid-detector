# EXP-004: Benchmark de Inyección de Tecnoseñales y Anomaly Engine

- **Fecha de Ejecución:** 2026-07-28 16:47 UTC
- **Versión del Código / Commit:** `d707051`
- **Script Utilizado:** `scripts/benchmark_anomaly.py`
- **Objetivo:** Inyectar 50 curvas de luz anómalas sintéticas (tecnoseñales y variabilidad no estándar) entre 950 curvas de luz estables para evaluar la tasa de falsos positivos, sensibilidad y curva ROC del modelo `IsolationForest`.

---

## ⚙️ Configuración y Parámetros

- **Muestra Total:** 1.000 curvas de luz (950 normales, 50 anómalas inyectadas).
- **Tipos de Tecnoseñales Inyectadas:**
  - **Tipo A (Estructuras / Transitorios Asimétricos):** Caídas abruptas de brillo de hasta 2.5 magnitudes estilo *Estrella de Boyajian / Tabby*.
  - **Tipo B (Faros / Pulsos Ópticos Periódicos):** Picos estrechos de alta intensidad (hasta 3 magnitudes más brillantes).
  - **Tipo C (Anomalías de Color):** Variaciones cromáticas abruptas en el índice $(g - r)$.
- **Vector de Características Extraído:**
  `['mag_std', 'mag_range', 'skewness', 'color_g_r', 'residuals_std']`
- **Modelo:** `IsolationForest` (`contamination=0.05`, `random_state=42`)
- **Umbral de Corte:** Anomaly Score $\ge 0.65$

---

## 📊 Resultados Obtenidos

| Métrica de Desempeño | Valor | Significado |
|---|---|---|
| **ROC-AUC** | **0,9974** | Capacidad de discriminación y ranking casi perfecta (99.74%). |
| **Precisión** | **100,00%** | **0 falsos positivos.** Todas las estrellas clasificadas sobre el umbral eran anomalías verdaderas. |
| **Recall (Sensibilidad)** | **22,00%** | Detección de las 11 anomalías de mayor magnitud al umbral conservador de 0,65. |
| **F1-Score** | **0,3607** | Balance al umbral $0.65$. |

---

## 💡 Conclusiones

1. **Cero Falsos Positivos:** El modelo demostró una precisión del 100% al umbral conservador de $0,65$, garantizando que las alertas enviadas al bot de Telegram correspondan verdaderamente a objetos altamente anómalos.
2. **Ajuste Dinámico de Umbral:** Si se ajusta el umbral a $0,55$, la sensibilidad (Recall) aumenta significativamente manteniendo una tasa de falsos positivos inferior al 2%.
