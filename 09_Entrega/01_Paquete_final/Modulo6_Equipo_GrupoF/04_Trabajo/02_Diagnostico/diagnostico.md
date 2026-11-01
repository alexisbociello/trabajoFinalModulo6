# Diagnóstico de calidad — Comercial Horizonte, v1

Una fila representa una venta de una categoría; no identifica personas ni productos individuales. Fuente: CSV sintético del caso. Clave esperada: `id`. Columnas exactas y orden: `id, fecha, categoria, cantidad, precio_unitario, costo_unitario`.

Tipos: ID y categoría como texto; fecha calendario ISO; cantidad entera positiva; precio decimal finito positivo; costo decimal finito no negativo. Categorías permitidas: Oficina, Tecnologia y Hogar. Se aplicó el diccionario v1 y el contrato v1, identificados por huella en la evidencia adjunta.

## Procedimiento y resultado

Ejecución real por Codex con Python, sobre una copia idéntica al original. Se comprobaron encabezado, seis campos por fila, clave, duplicados, fechas, categorías y números. Origen 1 corresponde a la primera fila de datos (línea física 2). No se corrigieron ni imputaron valores.

**Conciliación: 16 leídas = 13 válidas + 3 excluidas.** Cada fila excluida se cuenta una sola vez. No se detectaron cambios de esquema ni IDs conflictivos que requieran detener este diagnóstico. La política y los cálculos de negocio se verificarán en el pipeline posterior.

| Origen | ID | Fecha | Categoría | Cantidad | Precio | Costo | Decisión | Regla / motivo |
|---|---|---|---|---|---|---|---|---|
| 1 | V001 | 2026-10-05 | Oficina | 10 | 25 | 15 | ACEPTAR | Cumple todas las validaciones del diccionario v1 |
| 2 | V002 | 2026-10-05 | Tecnologia | 2 | 600 | 420 | ACEPTAR | Cumple todas las validaciones del diccionario v1 |
| 3 | V003 | 2026-10-06 | Hogar | 5 | 80 | 56 | ACEPTAR | Cumple todas las validaciones del diccionario v1 |
| 4 | V004 | 2026-10-06 | Oficina | 20 | 12 | 8 | ACEPTAR | Cumple todas las validaciones del diccionario v1 |
| 5 | V005 | 2026-10-07 | Tecnologia | 3 | 150 | 120 | ACEPTAR | Cumple todas las validaciones del diccionario v1 |
| 6 | V006 | 2026-10-07 | Hogar | 4 | 100 | 85 | ACEPTAR | Cumple todas las validaciones del diccionario v1 |
| 7 | V007 | 2026-10-08 | Oficina | 8 | 30 | 18 | ACEPTAR | Cumple todas las validaciones del diccionario v1 |
| 8 | V008 | 2026-10-08 | Tecnologia | 1 | 900 | 720 | ACEPTAR | Cumple todas las validaciones del diccionario v1 |
| 9 | V009 | 2026-10-09 | Hogar | 6 | 50 | 35 | ACEPTAR | Cumple todas las validaciones del diccionario v1 |
| 10 | V010 | 2026-10-09 | Oficina | 15 | 20 | 14 | ACEPTAR | Cumple todas las validaciones del diccionario v1 |
| 11 | V011 | 2026-10-12 | Tecnologia | 2 | 250 | 200 | ACEPTAR | Cumple todas las validaciones del diccionario v1 |
| 12 | V012 | 2026-10-12 | Hogar | 3 | 120 | 96 | ACEPTAR | Cumple todas las validaciones del diccionario v1 |
| 13 | V013 | 2026-10-13 | Oficina | 12 | 15 | 9 | ACEPTAR | Cumple todas las validaciones del diccionario v1 |
| 14 | V005 | 2026-10-07 | Tecnologia | 3 | 150 | 120 | EXCLUIR | Duplicado exacto: conservar primera aparición (regla 2); origen de referencia: 5 |
| 15 | V014 | 2026-10-13 | Hogar | -2 | 75 | 50 | EXCLUIR | cantidad: debe ser entero positivo (regla 3) |
| 16 | V015 | 2026-10-14 | Oficina | 7 | (vacío) | 11 | EXCLUIR | precio_unitario: vacío o no numérico (regla 3) |

## Tres contrastes para revisión humana

1. **V005, orígenes 5 y 14:** los seis valores son idénticos: `V005,2026-10-07,Tecnologia,3,150,120`. Se acepta el origen 5 y se excluye el 14. Para explicar el efecto: 3 × 150 = 450 de ventas; 3 × 120 = 360 de costos; margen 90, contabilizados una sola vez. Es una comprobación preparada por el agente, pendiente de contraste humano.
2. **Origen 15, V014:** cantidad original `-2`; incumple entero positivo. Se excluye; no se aplica valor absoluto ni se supone una devolución.
3. **Origen 16, V015:** precio original vacío; incumple precio numérico positivo. Se excluye sin imputación; cantidad 7 y costo 11 no permiten inferir el precio.

Una pérdida puede ser válida si los demás campos cumplen las reglas: precio menor que costo no es por sí solo una exclusión. No se encontró ese caso en las 13 filas aceptadas.

## Integridad y trazabilidad

La huella SHA-256 del original se comprobó antes y después, contra el registro inicial y contra la copia de trabajo. El original conserva su contenido. Las huellas, versión Python, comando, valores originales y decisiones están en `evidencia_diagnostico.json`. El script reproducible es `ejecutar_diagnostico.py`; no es el pipeline final ni prueba las ocho condiciones completas.

## Uso de IA y pendiente humano

Pedido que originó esta ejecución: «eso lo puedes realizar tu? que informacion o decision extra de mi parte necesitas?», referido al diagnóstico de calidad previamente propuesto. Codex leyó las reglas, generó el verificador, lo ejecutó y documentó resultados. No se atribuye esta ejecución ni un cálculo manual al estudiante.

Pendiente: el estudiante debe contrastar los tres casos, confirmar la conciliación y registrar su revisión propia en la bitácora. No se aprobaron P1–P8 ni controles de detención con esta sola ejecución. No se necesita una nueva regla de negocio para resolver estas filas.
