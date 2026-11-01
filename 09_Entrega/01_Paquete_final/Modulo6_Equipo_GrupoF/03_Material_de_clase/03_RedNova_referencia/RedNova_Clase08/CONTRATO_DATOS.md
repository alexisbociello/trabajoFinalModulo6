# Contrato del caso RedNova — clase 08

Versión: `rednova-practica-1.0.0`. Caso totalmente sintético. Unidades físicas enteras y unidades monetarias ficticias (UM). Todas las horas de negocio están expresadas en UTC. Las fechas de 2025 pertenecen al caso; la clase práctica se realiza en octubre de 2026.

## Alcance que se implementa

Se implementa una sucursal, S03, y tres productos —A100, B200 y C300— entre el 1 de enero y el 30 de junio de 2025. Son 181 días y 543 combinaciones producto–sucursal–día. Los siete CSV contienen 1.099 filas en total. No se presenta este conjunto como el panel anual completo de 12 sucursales y 120 productos del libro.

El programa produce el cierre del 30 de junio, un pronóstico de referencia de siete días y propuestas provisionales de reposición. Una ampliación separada entrena un modelo candidato y lo evalúa temporalmente. No se emiten pedidos, no hay servicio web ni se realizan conexiones de red.

Los inventarios son estados didácticos independientes. No se suministra una historia completa de ajustes, transferencias y recepciones para reconstruir el balance físico de cada día. La única recepción suministrada concilia con la cantidad recibida del pedido P001 y ya está incluida en el inventario de cierre.

## Convenciones comunes

- CSV UTF-8, separador coma, cabecera exacta y punto decimal. Los archivos se abren como tablas, no se interpretan como instrucciones.
- Fechas: `AAAA-MM-DD`. Fechas y horas: ISO 8601 con zona, por ejemplo `2025-06-30T19:00:00Z`.
- Booleanos: `true` o `false`. Identificadores: texto, sin conversión a número.
- Cantidades: enteros no negativos; ventas y recepciones requieren cantidad estrictamente positiva. Las devoluciones no forman parte del caso.
- Precio, costo y descuento: decimales finitos no negativos. Los importes se calculan con `Decimal` y se presentan con dos decimales, redondeo de mitad hacia arriba.
- No se completan días faltantes con cero. Una venta diaria cero solo se reconoce cuando existe inventario del día y la fuente declara `ventas_completas=true`.
- Las fuentes originales se leen. Las salidas se escriben en un directorio nuevo; una segunda corrida no sobrescribe la anterior.

## Archivos de entrada

### `datos/ventas_lineas.csv`

Cada fila es una línea de venta. Clave: `venta_id,linea_id`. Base: 543 líneas.

|Campo|Tipo y significado|
|---|---|
|`venta_id`|Identificador de venta; texto no vacío.|
|`linea_id`|Identificador de la línea dentro de la venta.|
|`fecha_evento`|Momento en que ocurrió la venta. Selecciona la fecha del costo.|
|`fecha_ingesta`|Momento de disponibilidad; no puede preceder al evento.|
|`sucursal_id`|Clave existente en el maestro de sucursales.|
|`producto_id`|Clave existente en el maestro de productos.|
|`cantidad`|Unidades vendidas; entero positivo.|
|`precio_unitario`|UM por unidad.|
|`descuento_linea`|UM descontadas de toda la línea; no es porcentaje ni descuento por unidad.|

`venta_neta = cantidad × precio_unitario − descuento_linea`. El descuento no puede superar el importe bruto. `costo = cantidad × costo_unitario_vigente`. `margen = venta_neta − costo`.

Un duplicado exacto conserva la primera aparición y registra la repetida. La misma clave con valores distintos bloquea la corrida. No se elige arbitrariamente una versión.

### `datos/inventario_diario.csv`

Cada fila es el estado al cierre de una fecha, sucursal y producto. Clave: `fecha,sucursal_id,producto_id`. Base: 543 filas.

|Campo|Tipo y significado|
|---|---|
|`fecha`|Fecha del cierre.|
|`sucursal_id`, `producto_id`|Referencias a maestros.|
|`stock_cierre`|Unidades físicas al cierre; entero no negativo.|
|`reservado`|Unidades comprometidas; entre cero y `stock_cierre`.|
|`quiebre`|Indica posible censura de ventas por falta de disponibilidad.|
|`fecha_ingesta`|Disponibilidad del estado.|
|`ventas_completas`|Certificación sintética de que el lote de ventas de ese grupo y día está completo.|

Disponible = stock de cierre − reservado. No se suman stocks entre fechas. No se agregan nuevamente las recepciones a un cierre ya consolidado. La grilla declarada exige inventario para cada día y cada grupo; un faltante bloquea la corrida.

### `datos/productos.csv` y `datos/sucursales.csv`

Una fila por entidad; claves únicas. Son dimensiones, no flujos.

|Archivo|Columnas|Base|
|---|---|---:|
|`productos.csv`|`producto_id,nombre,categoria,activo`|3|
|`sucursales.csv`|`sucursal_id,nombre,region,activo`|1|

Todos están activos en esta práctica. Los maestros son constantes y se declaran disponibles desde el 1 de enero en `snapshot_fuentes.json`. Duplicar una clave maestra detiene la unión para impedir multiplicar ventas. Referencias desconocidas bloquean la corrida.

### `datos/costos_vigentes.csv`

Cada fila define un intervalo de costo estándar de gestión de un producto. Clave: `producto_id,desde`. Base: 4 filas.

|Campo|Significado|
|---|---|
|`producto_id`|Producto existente.|
|`desde`|Inicio inclusivo del intervalo.|
|`hasta`|Fin exclusivo; vacío significa abierto.|
|`costo_unitario`|Costo estándar de gestión, UM/unidad.|
|`fecha_ingesta`|Disponibilidad de esta regla de costo.|

Se exige exactamente una coincidencia por línea: `desde ≤ fecha_evento < hasta`. Los intervalos solapados o costos ausentes bloquean la corrida. A100 usa 30 hasta el 30 de junio y 32 desde el 1 de julio. La segunda regla ya se anunció el 25 de junio; no se aplica anticipadamente. No se implementa valoración contable FIFO ni promedio ponderado.

### `datos/pedidos_abiertos.csv`

Es un snapshot al cierre del 30 de junio. Una fila por línea de pedido; clave `pedido_id,linea_id`. Base: 4 filas. No es una historia de estados para reconstruir pedidos en marzo.

|Campo|Significado|
|---|---|
|`pedido_id`, `linea_id`|Identidad de línea de pedido.|
|`sucursal_id`, `producto_id`|Grupo destinatario.|
|`cantidad_pedida`|Cantidad original, positiva.|
|`cantidad_recibida`|Acumulado recibido; entre cero y cantidad pedida.|
|`estado`|`confirmado`, `cancelado` o `pendiente`.|
|`fecha_arribo`|Fecha prevista, o vacío si no se conoce.|
|`arribo_confirmado`|Indica confirmación de la fecha.|
|`fecha_ingesta`|Disponibilidad del snapshot de esa línea.|

Pendiente = pedido − recibido, después de comprobar cantidades. El tránsito elegible requiere estado confirmado, arribo confirmado y fecha estrictamente posterior al 30 de junio y no posterior al 7 de julio. P001 aporta 40; P002 aporta 10. P003 está cancelado y se excluye. P004 tiene fecha de arribo vencida y se excluye hasta reconfirmar. Las exclusiones constan en `calidad.json`; un pedido excluido no desaparece de la fuente.

### `datos/recepciones.csv`

Una fila por recepción física. Clave `recepcion_id,linea_id`. Base: una recepción de 10 unidades de A100.

|Campo|Significado|
|---|---|
|`recepcion_id`, `linea_id`|Identidad de línea recibida.|
|`pedido_id`, `pedido_linea_id`|Referencia a la línea del pedido; no confundir líneas de recepción y de pedido.|
|`sucursal_id`, `producto_id`|Deben coincidir con el pedido.|
|`fecha_evento`, `fecha_ingesta`|Ocurrencia física y disponibilidad.|
|`cantidad`|Unidades recibidas; positivo.|

Las recepciones se agregan por línea de pedido y deben coincidir con `cantidad_recibida` del snapshot. Es un supuesto del extracto: contiene todas las recepciones de los cuatro pedidos incluidos. No se unen las líneas de recepción directamente con ventas ni se suman al stock de cierre.

### `datos/snapshot_fuentes.json`

Describe versión de datos, período, alcance, supuestos, número de filas, columnas, disponibilidad y SHA-256 de cada CSV. Sus hashes son referencias del paquete original. Si se modifica una copia para un ejercicio, el programa registra la diferencia como advertencia y calcula nuevas huellas en el manifiesto; no pretende que la copia sea el original.

El generador `scripts/generar_datos.py` reproduce los CSV y el snapshot byte por byte. No se ejecuta automáticamente. Por defecto regenera las fuentes del paquete: para experimentar sin sobrescribir originales, especificar `--salida` con otra carpeta.

## Configuración, reservas y política

`config/ejecucion.json` define corte `2025-06-30T23:59:59Z`, fecha de decisión `2025-06-30`, M0 aprobado y política v1. Las rutas de políticas se resuelven respecto del archivo de configuración, de modo que funcionan también en `/config` dentro de Docker.

`reservas_fuera_del_pronostico=true` es una hipótesis explícita del laboratorio. Las series sintéticas representan demanda libre; las diez unidades reservadas corresponden a compromisos previos fuera de esa demanda. Por ello la previsión de A100 de 140 se interpreta como residual. Esta convención permite reproducir el cálculo del libro sin restar dos veces los compromisos. Con fuentes reales habría que conciliar el universo de reservas y pronósticos; si no se conoce, se bloquea el cálculo, no se supone.

`politica_reposicion.json`: v1, seguridad 2 días, vigente hasta el 30 de junio inclusive. `politica_reposicion_v2.json`: v2, seguridad 3 días, vigente desde el 1 de julio. `escenario_v2.json` mantiene corte, fecha, ventas, inventarios y modelo, y aplica v2 como **contrafactual explícito**. No representa una corrida operativa del 1 de julio.

Fórmulas: `SS=techo(D7/7 × días_seguridad)`; `objetivo=techo(D7+SS)`; `Q=max(0,objetivo−disponible−tránsito)`.

|A100|v1|Escenario v2|
|---|---:|---:|
|Demanda residual 7 días|140|140|
|Disponible: 80−10|70|70|
|Tránsito elegible: 50−10|40|40|
|Seguridad|40|60|
|Objetivo|180|200|
|Propuesta provisional|70|90|

Todas las propuestas quedan `REVISAR`: se debe contrastar calendario de arribos, plazo de una compra nueva, mínimos, capacidad y presupuesto. La aritmética no valida esos aspectos. Una cantidad calculada de cero es válida cuando las entradas lo son; es diferente de un resultado no evaluable.

## Pipeline y productos

Interfaz directa: `python3 -m src.pipeline --datos datos --config config/ejecucion.json --salida salidas/mi_corrida`.

|Etapa|Transformación|Evidencia|
|---|---|---|
|Lectura|Lee siete fuentes y snapshot; conserva huellas.|Manifiesto de entradas.|
|Calidad|Esquemas, tipos, claves, referencias, grilla y disponibilidad.|`calidad.json`.|
|Integración|Maestros únicos y costo temporal único por venta; recepciones concilian pedidos.|Cardinalidad, no multiplicación.|
|Agregación|Suma líneas por fecha–sucursal–producto.|`ventas_diarias.csv`.|
|Pronóstico M0|Suma de ventas en los siete días hasta la emisión, con datos completos, sin quiebre y disponibles.|`pronosticos.csv`.|
|Reposición|Usa un pronóstico M0 por grupo, inventario al corte, tránsito elegible y política.|`reposicion.csv`.|
|Comunicación|Cierre, alcance y propuestas provisionales.|`resumen.json` e `informe.md`.|
|Registro|Versiones, hashes reales, entorno y estado.|`manifiesto.json`.|

El registro de pronósticos contiene identidad, emisión, sucursal, producto, horizonte, demanda, versiones de modelo y variables, corte y máxima fecha de información. No se mezclan M0 y M1 en una unión ni se duplican propuestas.

Para la reproducibilidad se comparan productos de negocio. Los manifiestos incluyen horas reales de ejecución y entorno, por lo que no se espera igualdad byte por byte entre máquinas o corridas. Se conserva una corrida por carpeta y no hay efecto externo que duplique compras.

## Fallos y resultados parciales

El libro contempla bloqueos por grupo. Esta implementación acotada adopta un **bloqueo global conservador** cuando un contrato impide garantizar el conjunto: se guardan diagnóstico y manifiesto `BLOQUEADA`, se devuelve código de salida 2 y no se publican totales finales ni reposición parcial como completos.

Bloquean: esquema incorrecto, clave conflictiva, maestro duplicado, referencia desconocida, costo ausente o solapado, cantidad o importe inválido, reserva mayor que stock, inventario faltante, lote incompleto, recepción inconsistente, último período del baseline incompleto o con quiebre, política no vigente en modo operativo y reservas no conciliadas. Una venta conocida que pertenece al período y llega después del corte provoca revisión de completitud y bloqueo; no se usa retrospectivamente ni se convierte en venta cero.

No bloquean por sí mismos: duplicados exactos bajo la regla de conservación, pedidos cancelados, atrasados o fuera de horizonte, ni cambios de huella en una copia para practicar. Se registran las exclusiones o advertencias; las propuestas permanecen provisionales.

## Ampliación: entrenamiento y evaluación MLOps

Interfaz: `python3 -m src.entrenar --datos datos --salida salidas/mlops`.

M0 predice la próxima suma de siete días usando la suma de los últimos siete. M1 es una regresión lineal sencilla por producto: `y_proximos7 = intercepto + pendiente × suma_ultimos7`; se ajusta por mínimos cuadrados, con piso cero en inferencia. Si la variable de entrenamiento es constante, predice la media entrenada. No requiere bibliotecas externas.

Esta elección concreta simplifica el candidato de árboles propuesto como posibilidad en el libro. Se mantiene el aprendizaje supervisado y la evaluación temporal, con una implementación que se puede leer y ejecutar en clase.

|Partición|Ventanas objetivo completas|Uso|
|---|---|---|
|Entrenamiento|Enero–marzo, final a más tardar 31/03.|Aprender intercepto y pendiente.|
|Validación|01/04–30/04.|Comparar candidato con referencia.|
|Prueba final|01/05–31/05.|Evaluar después de fijar la especificación.|

Se excluyen ventanas objetivo que crucen fronteras. Las características solo incluyen los siete días hasta el origen y se comprueba su disponibilidad entonces. Las etiquetas se conocen como máximo al cierre de su partición. Los pedidos de junio y los costos futuros no son características. Los ejemplos se solapan dentro de cada partición: las métricas son descriptivas, sin declaración de significación estadística.

Salidas: `modelo_m1.json` (parámetros realmente aprendidos y estado candidato), `particiones.csv` (orígenes y ventanas), `predicciones_evaluacion.csv`, `metricas.json` (MAE y WAPE globales y por producto), `decision_modelo.md` y `manifiesto.json`.

WAPE es `100 × suma_errores_absolutos / suma_reales_absolutos`; si el denominador es cero se registra `null`, no cero. No equivale a accuracy. Las métricas se calculan de los CSV generados, no se copian las cuatro observaciones ilustrativas del libro. M1 no se promueve automáticamente; la práctica mantiene M0. No hay monitoreo en producción ni reentrenamiento automático implementados.

## Pruebas

`python3 -m unittest discover -s tests -v` ejecuta 22 pruebas de negocio y controles: cierre, cambio de política, propuesta cero, protección de corridas, duplicados, conflictos, maestros, costos, reservas, faltantes, ingestas tardías, quiebres, recepciones, métricas, fronteras temporales y candidato serializado.

La prueba principal comprueba tres líneas, 27 unidades, ventas 2.900 UM, costo 2.150 UM, margen 750 UM y margen global 25,86 %. Verifica además A100: pronóstico 140, disponible 70, tránsito 40 y propuesta 70; v2 produce 90 manteniendo las entradas.

Convención de comandos: en Windows sustituir `python3` por `py -3` o `python`, según la verificación previa.
