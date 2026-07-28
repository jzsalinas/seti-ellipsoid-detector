# 🔬 EXP-006: Red de Anclas Secundarias (Púlsares & Magnetares) e Intersección Multiancla

- **Fecha:** 2026-07-28
- **Script Principal:** `scripts/visualize_multi_anchors_3d.py`
- **Módulo de Anclas:** `core/anchor.py` & `providers/pulsar_provider.py`
- **Estado:** ✅ Completado

---

## 🎯 Objetivo del Experimento
Validar la incorporación de anclas temporales discretas no continuas (Pulsar Glitches, Magnetar Giant Flares, Binary Pulsar Periastron) junto con Supernovas históricas, y evaluar el algoritmo vectorizado de **intersección de elipsoides múltiples** (RMS Delay) en espacio 3D para colapsar el volumen de candidatos de búsqueda.

---

## 📊 Configuración de Anclas Evaluadas

| Anchor ID | Nombre Descriptivo | Tipo de Ancla | Época ($t_0$) | Distancia (pc) |
|---|---|---|---|---|
| `SN1987A` | Supernova 1987A (LMC) | Supernova | 1987-02-23 | 51,200 |
| `SN1572` | Tycho's Supernova (SN 1572) | Supernova | 1572-11-06 | 2,500 |
| `SN1604` | Kepler's Supernova (SN 1604) | Supernova | 1604-10-09 | 6,000 |
| `SN1054` | Crab Supernova (SN 1054) | Supernova | 1054-07-04 | 2,000 |
| `VELA_GLITCH_1969` | Vela Pulsar Historic Glitch | Pulsar Glitch | 1969-03-01 | 287 |
| `CRAB_GLITCH_2017` | Crab Pulsar Major Glitch | Pulsar Glitch | 2017-11-08 | 2,000 |
| `SGR1806_FLARE_2004` | Magnetar SGR 1806-20 Giant Flare | Magnetar Flare | 2004-12-27 | 8,700 |
| `PSR_J0737_3039` | Double Pulsar Periastron | Binary Periastron | 2023-01-01 | 1,150 |

---

## 🚀 Resultados y Conclusiones

1. **Abstracción `CosmicAnchor`:** Implementada exitosamente en `core/anchor.py` y gestionada a través de `PulsarProvider`, soportando fechas timezone-aware UTC.
2. **Cálculo de Desviación RMS Vectorizado:** La función `find_multi_anchor_intersections` computa de forma 100% vectorizada en NumPy/Pandas las matrices de retardo ($\text{delay}_i$) y la desviación cuadrática media (RMS Delay) para catálogos estelares de Gaia DR3.
3. **Visualización 3D WebGL:** Se generó exitosamente la mapa de superposición e intersección 3D (`scratch/multi_anchor_intersection_3d.html`), renderizando mallas de elipsoides translucidos, iconos de tipos de ancla y resaltado de candidatos intersección.
4. **Verificación de Tests:** 20/20 tests unitarios e integración pasando al 100% en `pytest`.
