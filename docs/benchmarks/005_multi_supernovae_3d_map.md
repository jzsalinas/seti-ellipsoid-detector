# EXP-005: Mapa 3D Multiancla y Superposición de Elipsoides Galácticos

- **Fecha de Ejecución:** 2026-07-28 18:04 UTC
- **Versión del Código / Commit:** `4f450b9`
- **Script Utilizado:** `scripts/visualize_multi_ellipsoids_3d.py`
- **Objetivo:** Superponer en una sola escena WebGL 3D interactiva los elipsoides de SETI de las 4 supernovas históricas (SN 1987A, SN 1572 Tycho, SN 1604 Kepler y SN 1054 Cangrejo) junto con sus catálogos estelares de Gaia DR3.

---

## ⚙️ Configuración y Parámetros

- **Supernovas Representadas:**
  1. 💥 **SN 1987A (LMC):** Distancia $51.200\text{ pc}$ (Gran Nube de Magallanes). Malla 3D cian.
  2. 💥 **SN 1572 (Tycho):** Distancia $2.500\text{ pc}$ (Casiopea). Malla 3D magenta.
  3. 💥 **SN 1604 (Kepler):** Distancia $6.000\text{ pc}$ (Ofiuco). Malla 3D ámbar/dorada.
  4. 💥 **SN 1054 (Crab):** Distancia $2.000\text{ pc}$ (Tauro). Malla 3D verde esmeralda.
- **Catálogo Cargado:** 800 estrellas reales de Gaia DR3.

---

## 📊 Resultados Obtenidos y Hallazgos Visuales

1. **Escala Galáctica de SN 1987A:** El mapa 3D reveló visualmente la enorme diferencia de escala entre las supernovas galácticas locales (Tycho a 2.500 pc, Crab a 2.000 pc y Kepler a 6.000 pc) y SN 1987A (a 51.200 pc en la Gran Nube de Magallanes), cuya aguja de proyección se extiende fuera del plano de la Vía Láctea.
2. **Red de Intersección de Elipsoides:** Las supernovas intra-galácticas (Tycho, Kepler y Crab) forman una red de intersección de cáscaras elípticas concentradas alrededor del sistema solar $\text{O}(0,0,0)$, ofreciendo una cobertura de sincronización temporal ideal para el monitoreo de tecnoseñales en estrellas cercanas.

---

## 💡 Conclusiones y Próximos Pasos

- **Conclusión:** El monitoreo multiancla simultáneo es la única estrategia viable dada la estrecha ventana temporal de sincronización de eventos individuales.
- **Próxima Fase:** Incorporar catálogos de púlsares de milisegundos y repetidores periódicos de radio/ópticos como anclas adicionales de tiempo e interpolación espacial.
