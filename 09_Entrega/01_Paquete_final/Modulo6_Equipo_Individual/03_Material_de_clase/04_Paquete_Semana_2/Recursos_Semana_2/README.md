# Recursos para las clases 3 y 4 — Semana 2

Estos archivos acompañan el libro y las clases de **Python con agentes y pipelines**, del Módulo 6: Ingeniería de Datos y MLOps.

## Archivos del caso

En la raíz de esta carpeta se incluyen:

- `ventas_original.csv`: datos originales del caso. Conservar sin modificar.
- `diccionario_y_reglas.md`: significado de los campos y reglas de validación.
- `contrato_pipeline.md`: especificación del proceso y de sus salidas.
- `politica_margen_v1.md` y `politica_margen_v2.md`: políticas de margen y sus vigencias.
- `matriz_8_pruebas.csv`: registro de las pruebas P1–P8.
- `plantilla_bitacora.md`: registro de prompts, ejecuciones, evidencias y revisión humana.
- `plantilla_entrega.md`: organización de la entrega.
- `roles_agentes.md`: roles de trabajo de los agentes.

Leer las reglas y el contrato antes de generar el script. La política se selecciona por la **fecha simulada de ejecución**, no por la fecha de la venta. Conservar los resultados de cada ejecución en una carpeta nueva.

## Datos pequeños de prueba

Los cuatro CSV de `Pruebas/` reproducen los ejemplos de la guía y el libro como archivos independientes. No deben agregarse a `ventas_original.csv`.

| Archivo | Prueba y fecha simulada | Resultado esperado |
|---|---|---|
| `Pruebas/frontera_30.csv` | P7; `2026-10-19` (v2) | Margen del 30 %: **SIN ALERTA**, porque la igualdad no activa la alerta. |
| `Pruebas/redondeo_29999.csv` | P7; `2026-10-19` (v2) | Porcentaje sin redondear 29,999 %: **ALERTA**, aunque se muestre 30,00 %. |
| `Pruebas/sin_validas.csv` | P8; `2026-10-18` (v1) | Dos registros leídos, cero válidos y dos excluidos; sumas cero, porcentaje `null` y estado **NO EVALUABLE**. |
| `Pruebas/esquema_incompatible.csv` | D1; `2026-10-18` (v1) | Detención por encabezado incompatible; no renombrar automáticamente la columna `precio`. |

En `sin_validas.csv`, el registro local 1 corresponde al registro original 15 y el registro local 2 al original 16. Ambos se conservan sin cambios.

P7 se registra en la matriz existente. D1 es una demostración docente y se registra en la bitácora; no agrega una prueba P9. Los resultados de la tabla son expectativas para contrastar: no acreditan una ejecución.

## Trabajo que se realiza en clase

`pipeline.py` se genera, revisa y ejecuta durante la práctica. Sus tres productos —`ventas_validas.csv`, `reporte_calidad.json` y `resumen.json`— también se crean durante la práctica, por lo que no forman parte de este paquete de entradas.

Los CSV están codificados en UTF-8, sin BOM, con coma como separador y punto decimal. Se conserva el campo vacío de precio de `sin_validas.csv` para poder comprobar la validación.
