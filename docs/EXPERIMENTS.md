# 🔬 Bitácora Histórica de Experimentos y Pruebas

Registro histórico centralizado de pruebas de campo, experimentos en vivo y benchmarks de rendimiento para el proyecto **SETI Ellipsoid Detector**.

---

## 📜 Índice de Experimentos Registrados

| ID | Fecha (UTC) | Commit | Título / Campaña | Estado | Reporte Detallado |
|---|---|---|---|---|---|
| **EXP-001** | 2026-07-28 16:46 | `d707051` | Benchmark de Rendimiento 3D y Escalabilidad Masiva (5M estrellas) | ✅ Completado | [001_3d_performance_benchmark.md](benchmarks/001_3d_performance_benchmark.md) |
| **EXP-002** | 2026-07-28 16:45 | `d707051` | Prueba Real de Campo: Consulta ADQL Indexada a Gaia DR3 | ✅ Completado | [002_live_gaia_field_test.md](benchmarks/002_live_gaia_field_test.md) |
| **EXP-003** | 2026-07-28 16:45 | `d707051` | Evaluación Multiancla de Supernovas Históricas (1987A, 1572, 1604, 1054) | ✅ Completado | [003_multi_anchor_supernovae.md](benchmarks/003_multi_anchor_supernovae.md) |
| **EXP-004** | 2026-07-28 16:47 | `d707051` | Benchmark de Inyección de Tecnoseñales & Evaluador IsolationForest | ✅ Completado | [004_technosignature_anomaly_benchmark.md](benchmarks/004_technosignature_anomaly_benchmark.md) |
| **EXP-005** | 2026-07-28 18:04 | `4f450b9` | Mapa 3D Multiancla y Superposición de Elipsoides Galácticos | ✅ Completado | [005_multi_supernovae_3d_map.md](benchmarks/005_multi_supernovae_3d_map.md) |
| **EXP-006** | 2026-07-28 18:43 | `phase-6` | Red de Anclas Secundarias (Púlsares & Magnetares) e Intersección Multiancla | ✅ Completado | [006_multi_anchor_intersection.md](benchmarks/006_multi_anchor_intersection.md) |
| **EXP-007** | 2026-07-28 19:07 | `phase-6` | ETI Reaction Latency & Shell Thickness Sensitivity Benchmark | ✅ Completed | [007_alien_latency_benchmark.md](benchmarks/007_alien_latency_benchmark.md) |

---

## 🛠️ Cómo Registrar un Nuevo Experimento

Para ejecutar y registrar automáticamente una nueva prueba en la bitácora:

```bash
python scripts/record_experiment.py --title "Nombre del Experimento" --script "scripts/mi_script.py"
```
