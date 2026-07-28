# 🛰️ SETI Ellipsoid Detector — Agent Guidelines & Memory

Este archivo contiene las directivas operativas, la arquitectura del sistema, las reglas de estilo y la hoja de ruta para **todos los agentes de Inteligencia Artificial que trabajen en este repositorio**.

---

## 🎯 Visión del Proyecto y Filosofía

- **Nombre:** SETI Ellipsoid Detector
- **Licencia:** MIT (Open Source, totalmente documentado).
- **Idioma de Comunicación con el Usuario:** Español (tono colega, profesional, preciso y colaborativo).
- **Concepto Científico Central:** Estrategia geométrica del Elipsoide de SETI para sincronización temporal de tecnoseñales basada en eventos galácticos descollantes (Foco 1: Tierra, Foco 2: Supernovas Históricas como SN 1987A, SN 1572 Tycho, SN 1604 Kepler, SN 1054 Crab).
- **Ecuación Fundamental del Retardo:**
  $$\Delta t = \frac{d_1 + d_2 - d_0}{c}$$

---

## 🛠️ Directivas Operativas para Agentes

### 1. Principios de Código y Rendimiento
- **Vectorización Obligatoria:** Toda la geometría 3D y evaluación del elipsoide en `core/geometry.py` DEBE mantenerse 100% vectorizada utilizando `NumPy` y `Pandas` (evitar bucles `for` en DataFrames).
- **Consultas TAP a Gaia DR3:** Usar SIEMPRE rangos de cajas delimitadoras en ADQL (`ra BETWEEN min AND max AND dec BETWEEN min AND max`) en [providers/gaia_provider.py](file:///home/jzsalinas/Documents/antigravity/seti-ellipsoid-detector/providers/gaia_provider.py) para aprovechar índices espaciales y evitar timeouts TAP (ejecución $< 0.5\text{s}$).

### 2. Estándares de Visualización 3D WebGL ([core/visualizer.py](file:///home/jzsalinas/Documents/antigravity/seti-ellipsoid-detector/core/visualizer.py))
- **Estilo Estético:** Dark Theme (`plotly_dark`), fondo `#111`, `aspectmode='data'` para preservar proporciones espaciales 1:1 en parsecs.
- **La Tierra (Origen):** Esfera dorada brillante (`#ffd700`) en $(0,0,0)$.
- **Supernova (Foco 2):** Esfera brillante cian-blanca (`#e0f7fa` con borde `#00e5ff`).
- **Malla 3D del Elipsoide:** Malla translúcida cian que se expande/contrae dinámicamente según la época del slider temporal.
- **Estrellas Activas:** Representadas por puntos estelares verdes (`#00e676`) + **Anillo de Latitud proyectado EXACTAMENTE SOBRE LA MALLA 3D DEL ELIPSOIDE** ($R_{\text{superficie}}$) + Vector de proyección radial punteado (cian) desde la estrella a la superficie.

### 3. Registro de Experimentos y Documentación
- Cada vez que se desarrolle un nuevo script de prueba o benchmark en `scripts/`, se debe registrar un reporte en `docs/benchmarks/XXX_nombre.md` y actualizar la tabla principal en [docs/EXPERIMENTS.md](file:///home/jzsalinas/Documents/antigravity/seti-ellipsoid-detector/docs/EXPERIMENTS.md).
- Mantener siempre la suite de tests en `tests/` pasando al 100% mediante `./venv/bin/pytest -v`.

---

## 📂 Mapa del Código y Componentes

```text
seti-ellipsoid-detector/
├── config.py                 # Constantes (SN 1987A, Tycho, Kepler, Crab)
├── core/
│   ├── geometry.py           # Conversiones 3D Cartesianas y geometría de retardo
│   ├── anomaly_engine.py     # IsolationForest y extracción de características
│   └── visualizer.py         # Visualizador 3D WebGL (individual y mapa multiancla)
├── providers/
│   ├── gaia_provider.py      # Proveedor ADQL de Gaia DR3 (pyvo)
│   └── fink_provider.py      # Consumidor de alertas ZTF/Rubin (Fink REST API)
├── notifier/
│   └── telegram_bot.py       # Generador de gráficos oscuros y alertas Telegram
├── pipeline.py               # Orquestador end-to-end
├── scripts/                  # Herramientas CLI (visualizadores 3D, benchmarks)
│   ├── visualize_ellipsoid_3d.py
│   ├── visualize_multi_ellipsoids_3d.py
│   ├── test_live_gaia.py
│   ├── test_multianchor.py
│   ├── benchmark_performance.py
│   ├── benchmark_anomaly.py
│   └── record_experiment.py
├── docs/                     # Registro de Experimentos (EXP-001 a EXP-005)
└── tests/                    # Suite de 15 tests unitarios e integración
```

---

## 🗺️ Hoja de Ruta (Roadmap para Próximos Chats)

### ✅ Fases Completadas (Fases 1 a 5)
1. Engine geométrico 3D y tests unitarios.
2. Ingesta indexada de Gaia DR3.
3. Ingesta de curvas de luz de Fink Broker.
4. Motor no supervisado de detección de anomalías (`IsolationForest`).
5. Notificador Telegram y Pipeline orquestador.
6. Visualizador 3D interactivo con slider de época y mapa multiancla 3D.
7. Bitácora de experimentos `EXP-001` a `EXP-005` y documentación MIT.

### 🚀 Próxima Fase (Fase 6 — Próximo Chat)
1. **Red de Anclas Secundarias (Púlsares & Repetidores):**
   - Incorporar catálogos de púlsares de milisegundos (ATNF Pulsar Catalogue) y repetidores periódicos de radio/ópticos como anclas temporales secundarias.
   - Extender el visualizador 3D multiancla para superponer redes de elipsoides cruzados de púlsares + supernovas.
2. **Streaming & Ingesta Continua:**
   - Optimización de canalizaciones en tiempo real con Fink Broker para monitoreo continuo de fotometría anómala en la superficie del elipsoide.
