# EXP-002: Prueba Real de Campo sobre el Archivo ESA Gaia DR3

- **Fecha de Ejecución:** 2026-07-28 16:45 UTC
- **Versión del Código / Commit:** `d707051`
- **Script Utilizado:** `scripts/test_live_gaia.py`
- **Objetivo:** Consultar en vivo el archivo astronómico de la ESA Gaia DR3 vía ADQL indexado en un cono de 1.5° alrededor de SN 1987A y calcular el retardo geométrico del elipsoide para estrellas reales.

---

## ⚙️ Configuración y Parámetros

- **Evento Ancla:** Supernova 1987A (RA: $83.8667^\circ$, Dec: $-69.2697^\circ$, Distancia: $51.200\text{ pc}$)
- **Época Ancla:** `1987-02-23T10:38:00 UTC`
- **Radio de Búsqueda:** $1,5^\circ$ (Bounding box indexada por RA/Dec)
- **Criterio de Selección:** `parallax > 0.1 mas`, `parallax_over_error > 3`, `phot_g_mean_mag <= 16.0`

---

## 📊 Resultados Obtenidos

- **Estrellas Reales Obtenidas:** 500 estrellas de Gaia DR3.
- **Rango de Distancias:** $26,4\text{ pc}$ a $6.692,8\text{ pc}$ (Mediana: $513,2\text{ pc}$).
- **Tiempo de Respuesta TAP Query:** $< 1,0 \text{ segundo}$.

### Top 5 Estrellas Más Cercanas a la Superficie del Elipsoide Hoy

| Gaia Source ID | RA (deg) | Dec (deg) | Distancia (pc) | Magnitud G | Retardo (días) |
|---|---|---|---|---|---|
| `4657161578842924032` | 85.8866° | -70.3996° | 6.692,8 pc | 11.90 | -11.940,1 días |
| `4651910040767673344` | 80.8066° | -70.5988° | 4.235,3 pc | 11.84 | -11.998,3 días |
| `4657361694264276992` | 87.5609° | -70.3036° | 3.589,3 pc | 10.90 | -12.511,9 días |
| `4657383237823397888` | 87.1676° | -70.0539° | 4.724,4 pc | 11.30 | -12.577,4 días |
| `4657395259417192448` | 87.7572° | -70.0227° | 3.282,9 pc | 10.51 | -12.874,9 días |

---

## 💡 Conclusiones

1. **Optimización TAP ADQL:** La incorporación de cláusulas de rango `RA BETWEEN ... AND DEC BETWEEN ...` optimiza el uso de índices espaciales en la base de datos de la ESA, reduciendo el tiempo de consulta de timeouts de 30s a respuestas inmediatas en sub-segundos.
2. **Interpretación Astrofísica:** Las estrellas observadas en el primer plano galáctico (entre 300 pc y 6000 pc) fueron atravesadas por la luz de SN 1987A hace aproximadamente 32 años (retardos de $\sim -11.900$ días). Para encontrar estrellas activas hoy en la cáscara de 39.4 años de SN 1987A, se deben evaluar estrellas dentro del volumen muy cercano ($\sim 20$ años luz de la Tierra) o estrellas en el plano posterior profundo de la Gran Nube de Magallanes.
