# Comercial Horizonte: diccionario y reglas, versión 1
Caso sintético único; importes en UM ficticias. Las fechas del CSV y de las políticas son simulaciones, NO fechas del calendario del curso. Hay 16 registros de datos, sin contar el encabezado. Registro 1 = primera fila de datos = línea física 2 del CSV. El original nunca se edita.

## Columnas exactas y en este orden
| Columna | Significado | Regla |
|---|---|---|
| id | Identificador de una venta | Texto no vacío; primera aparición es referencia |
| fecha | Fecha ficticia de esa venta | Fecha real del calendario en formato ISO AAAA-MM-DD |
| categoria | Grupo del artículo | Oficina, Tecnologia o Hogar, sin inferir categorías nuevas |
| cantidad | Unidades vendidas | Entero positivo, sin valor absoluto ni redondeo |
| precio_unitario | Ingreso por unidad, UM | Decimal finito estrictamente mayor que 0 |
| costo_unitario | Costo por unidad, UM | Decimal finito mayor o igual que 0 |

Cada fila describe una venta de una categoría. No es una persona ni un producto individual. `id` es la clave esperada. No agregar nombres de clientes, descuentos, devoluciones o causas no suministradas. No hay devoluciones en este caso: una cantidad negativa es inválida según el contrato.

## Decisiones autorizadas
1. Encabezado distinto, columna faltante/adicional, fila con distinto número de campos o ID repetido con datos diferentes: DETENER, no generar resultados nuevos, pedir revisión humana. No renombrar automáticamente ni decidir cuál de dos ventas incompatibles conservar.
2. Duplicado exacto (los seis campos idénticos): conservar primera aparición, excluir posterior, anotar referencia a registro original. El registro 14 repite exactamente el 5.
3. Cantidad no entera o no positiva, precio vacío/no positivo/no numérico, costo negativo/no numérico, cualquier número no finito, fecha inválida, ID vacío o categoría no autorizada: excluir e informar cada motivo. No imputar.
4. Una venta con costo mayor que precio puede ser válida: el margen negativo NO es un error de calidad automáticamente.
5. Separar `ventas_validas` e incidencias. Cada incidencia contiene número del registro de origen, ID, valores originales, motivo y decisión. Conservar evidencia de exclusión; no destruir filas.

## Cálculo y precisión
Ventas = cantidad × precio; costos = cantidad × costo; margen = ventas − costos. Agregar importes por categoría y total. Margen global (%) = 100 × suma(margen) / suma(ventas), NO promedio de porcentajes. Usar Decimal; no redondear importes intermedios. Mostrar importes y porcentajes con dos decimales, redondeo HALF_UP solo al presentar. Comparar umbral antes de mostrar.

Cero filas válidas o ventas totales cero: estado NO EVALUABLE, margen porcentual `null`, nunca 0. No confundir el margen monetario de un conjunto vacío (suma 0) con un porcentaje definido. El criterio se aplica después de validar entradas y elegir una política válida.