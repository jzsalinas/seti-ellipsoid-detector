# EXP-003: Evaluación Multiancla de Supernovas Históricas

- **Fecha de Ejecución:** 2026-07-28 16:45 UTC
- **Versión del Código / Commit:** `d707051`
- **Script Utilizado:** `scripts/test_multianchor.py`
- **Objetivo:** Comparar la geometría del elipsoide y el cruce de cáscaras activas alrededor de 4 eventos ancla de supernovas históricas (SN 1987A, SN 1572 Tycho, SN 1604 Kepler, SN 1054 Cangrejo).

---

## ⚙️ Configuración y Parámetros

- **Supernovas Evaluadas:**
  1. **SN 1987A:** RA $83,8667^\circ$, Dec $-69,2697^\circ$, Dist $51.200\text{ pc}$, Época: `1987-02-23`
  2. **SN 1572 (Tycho):** RA $0,4225^\circ$, Dec $+64,1408^\circ$, Dist $2.500\text{ pc}$, Época: `1572-11-06`
  3. **SN 1604 (Kepler):** RA $257,5492^\circ$, Dec $-21,4858^\circ$, Dist $6.000\text{ pc}$, Época: `1604-10-09`
  4. **SN 1054 (Crab):** RA $83,6331^\circ$, Dec $+22,0145^\circ$, Dist $2.000\text{ pc}$, Época: `1054-07-04`
- **Radio de Cono Gaia:** $2,0^\circ$ alrededor de cada supernovas.
- **Ventana de Tolerancia:** $\pm 1 \text{ año}$ ($\pm 365,25 \text{ días}$).

---

## 📊 Resultados Obtenidos

| Ancla ID | Nombre de Supernova | Época Original | Estrellas Evaluadas | Estrellas en Cáscara Activa (±1 año) | Mínimo Retardo Absoluto (días) |
|---|---|---|---|---|---|
| **SN1987A** | Supernova 1987A (LMC) | 1987-02-23 | 500 | 0 | 12.055,4 días (~33 años) |
| **SN1572** | Supernova de Tycho (SN 1572) | 1572-11-06 | 500 | 0 | 9.958,8 días (~27 años) |
| **SN1604** | Supernova de Kepler (SN 1604) | 1604-10-09 | 500 | 0 | 146.061,9 días (~400 años) |
| **SN1054** | Nebulosa del Cangrejo (SN 1054) | 1054-07-04 | 500 | 0 | 27.192,6 días (~74 años) |

---

## 💡 Conclusiones

1. **Tycho (SN 1572):** La estrella más cercana a la cáscara del elipsoide de Tycho tiene un desvío de sólo 9.958 días (~27 años), estando muy próxima al cruce en escala galáctica.
2. **Escala Temporal vs Distancia:** Supernovas más antiguas y cercanas a la Vía Láctea (como SN 1572 a 2.500 pc y SN 1054 a 2.000 pc) presentan frentes de onda más amplios y distribuciones geométricas ideales para rastreos en todo el cielo.
