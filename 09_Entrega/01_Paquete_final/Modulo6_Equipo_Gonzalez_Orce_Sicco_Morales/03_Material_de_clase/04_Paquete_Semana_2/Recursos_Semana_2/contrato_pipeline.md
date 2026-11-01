# Contrato del pipeline, versión 1
## Objetivo
Diagnosticar calidad y calcular ventas, costos y margen de Comercial Horizonte sin alterar el original. Los números se calculan con herramientas, no se adivinan en una respuesta de texto.

## Entradas autorizadas
`ventas_original.csv`, `diccionario_y_reglas.md`, este contrato, `politica_margen_v1.md`, `politica_margen_v2.md` y una fecha simulada de ejecución explícita. No leer otras carpetas, conectores ni información personal. Cada política declara versión, desde, hasta, umbral y operador; la fecha de venta no selecciona la política.

## Cuatro bloques
1. LEER: verificar columnas exactas y cantidad de campos, enumerar registros desde 1 sin el encabezado.
2. VALIDAR: aplicar diccionario, preservar primera aparición exacta, detener ante ID conflictivo o esquema nuevo. No imputar ni corregir a ciegas.
3. CALCULAR: Decimal, razón de sumas, categorías y total; seleccionar política por fecha explícita, comparar sin redondear. Fecha ausente, previa a vigencia, política faltante, solapada o mal formada: detener y pedir aclaración.
4. GUARDAR: nuevos archivos en carpeta de salida separada; original solo lectura. No sobrescribir entradas ni usar carpetas personales. Emitir también JSON por consola para ejecución autocontenida.

## Productos
- `pipeline.py`: script generado por el agente, explicado y revisado.
- `ventas_validas.csv`: columnas originales más registro_origen, ventas, costos, margen; mantiene orden original de registros aceptados.
- `reporte_calidad.json`: registros leídos/válidos/excluidos e incidencias con origen, valores, motivo y decisión.
- `resumen.json`: agregados por categoría y total (unidades, ventas, costos, margen, margen_pct y margen_pct_mostrado), estado de alerta, archivo y versión de política, fecha simulada de ejecución.
- Bitácora y matriz de pruebas: archivos/versiones, plan, comandos realmente ejecutados, herramientas, salidas observadas, revisión y nueva versión.

## Interfaz de referencia para revisión, no memorización
`python pipeline.py --entrada ventas_original.csv --politicas politicas --fecha-ejecucion 2026-10-18 --salida resultados_v1`
Sin `--salida`, imprimir el paquete JSON en consola sin escribir resultados. Si se detiene por error, salida no exitosa y mensaje de revisión; no presentar una salida vieja como actual. JSON representa Decimal con cadenas exactas; `margen_pct_mostrado` es solo presentación. Solo el porcentaje no definido se representa con null.

## Aceptación
Ejecutar las ocho pruebas de `matriz_8_pruebas.csv`, más controles de esquema, ID conflictivo y política faltante. No aceptar un script porque el agente diga que es correcto. El docente dispone de referencia separada; el estudiante primero solicita generación propia. No hay API, secretos, entrenamiento predictivo ni dependencia externa obligatoria.