# Informe final - Comercial Horizonte


## Comercial Horizonte

Trabajo final integrador | Módulo 6: Ingeniería de Datos y MLOps

### Un flujo verificable, desde los datos hasta la operación

Informe técnico y evidencias de ejecución

Modalidad: equipo de cuatro integrantes
Equipo: Grupo F
Integrantes: Alexis Gonzalez, Alexia Orce, Georgina Sicco y Luis Morales
Fecha del informe: 1 de noviembre de 2026

### Resultado principal

Ventas: 5.720,00 UM | Costos: 4.210,00 UM
Margen: 1.510,00 UM | Margen global: 26,40%
Política v1: SIN ALERTA | Política v2: ALERTA

### Estado del documento

Producto técnico ejecutado y documentado. Reflexión y revisión de Alexis Gonzalez incorporadas. Pendientes: reflexiones y aportes de Alexia Orce, Georgina Sicco y Luis Morales. El informe tiene seis páginas de contenido, más portada y anexos.


## 1. Objetivo, alcance y síntesis

Informe | página 1 de 6

### Pregunta de trabajo

Determinar ventas, costos y margen de Comercial Horizonte a partir de sus datos originales; identificar registros que incumplen reglas y clasificar el margen con la política vigente para una fecha simulada de ejecución. Cada cifra debe vincularse a archivos, versiones, reglas y evidencia de ejecución.

### Fuente y permisos

Se utilizó el caso sintético ventas_original.csv: 16 registros, seis campos y categorías Oficina, Tecnologia y Hogar. Una fila representa una venta de una categoría; no identifica una persona ni un producto individual. Solo se usaron archivos autorizados del caso y copias locales. La clasificación es informativa y no autoriza modificar precios ni enviar mensajes.

### Síntesis ejecutiva

Se aceptaron 13 registros y se excluyeron 3: una repetición exacta, una cantidad negativa y un precio vacío. Las 91 unidades válidas generan ventas de 5.720,00 UM, costos de 4.210,00 UM y margen de 1.510,00 UM. El porcentaje global es 26,40% al mostrarlo con dos decimales.

### Cambio de política y trazabilidad

Para 2026-10-18 se aplica v1, con umbral 25%: SIN ALERTA. Para 2026-10-19 se aplica v2, con umbral 30%: ALERTA. No variaron datos, importes ni exclusiones. Las fechas son simuladas y no fechas de entrega. Se conservaron ambos resultados en destinos distintos.

### Herramientas y modalidad

Codex realizó las tareas técnicas con herramientas locales. Python 3.9.6 ejecutó el pipeline y verificadores; Docker ejecutó el mismo script con Python 3.12.16. Las evidencias distinguen ejecución del agente de revisión humana: Alexis Gonzalez comprobó manualmente los resultados de todas las pruebas de la matriz; P6 es el ejemplo desarrollado en su reflexión. No se requirieron servicios de pago, entrenamiento predictivo ni aplicación web.


## 2. Calidad y conservación del original

Informe | página 2 de 6

### Reglas y diagnóstico

El encabezado debe contener, en orden: id, fecha, categoria, cantidad, precio_unitario y costo_unitario. Se validaron los seis campos de cada fila, fecha calendario ISO, categoría autorizada, ID no vacío, cantidad entera positiva, precio finito positivo y costo finito no negativo. Se conservaron valores originales y motivos por registro.

### Decisiones observadas

Origen 14: repite exactamente los seis campos del origen 5, V005. Se conserva el 5 y se excluye el 14. Origen 15: V014 tiene cantidad -2, por lo que se excluye sin valor absoluto ni interpretación como devolución. Origen 16: V015 tiene precio vacío y se excluye sin imputación. Los restantes 13 registros cumplen las validaciones.

### Conciliación y numeración

16 leídas = 13 válidas + 3 excluidas. El origen 1 es la primera fila de datos; el encabezado no se cuenta. Varios motivos en una fila no implican varias filas excluidas. Una pérdida no es por sí misma un error de calidad: precio menor que costo sería válido si cumple las demás reglas. No se observó ese caso en las filas aceptadas.

### Exclusión frente a detención

Un registro con valores inválidos se excluye y se documenta. Un encabezado incompatible, una fila con distinto número de campos o un ID repetido con contenido diferente exige detener el flujo completo. No se renombraron columnas automáticamente ni se eligió una de dos ventas incompatibles.

### Integridad y evidencia

El original se separó en 01_Original_ventas_PROTEGIDO y se protegió localmente contra escritura accidental. La huella SHA-256 previa y posterior coincide: acbf2326ddddbbad657d3a22b315cae27fa2c2b3d942986cc36427b9c33a866d. Se trabajó con copias idénticas. Git conserva contenido, no permisos de solo lectura; el README indica cómo restaurarlos. El diagnóstico detallado está en E1.


## 3. Pipeline, cálculos y resultados

Informe | página 3 de 6

### Cuatro bloques y precisión

pipeline.py 1.0.0 se organiza en leer, validar, calcular y guardar. Usa biblioteca estándar y Decimal; no redondea importes intermedios. Calcula ventas = cantidad × precio, costos = cantidad × costo y margen = ventas - costos. El porcentaje se obtiene después de agregar: 100 × suma de margen / suma de ventas.

### Resultados por categoría

Oficina: 65 unidades; ventas 1.210,00; costos 772,00; margen 438,00; 36,20%.
Tecnologia: 8 unidades; ventas 3.050,00; costos 2.320,00; margen 730,00; 23,93%.
Hogar: 18 unidades; ventas 1.460,00; costos 1.118,00; margen 342,00; 23,42%.
TOTAL: 91 unidades; ventas 5.720,00; costos 4.210,00; margen 1.510,00; 26,40%.
Importes expresados en UM ficticias.

### Contraste independiente

Un verificador separado recalculó agregados con Fraction a partir de las 13 filas aceptadas según diagnóstico. V001 produce ventas 250 y margen 100; V002 produce ventas 1.200 y margen 360. Juntas: 460 / 1.450 × 100 = 31,7241...%, no el promedio simple 35%. El total tiene razón exacta 3775/143 por ciento.

### Selección y comparación de política

La fecha de ejecución selecciona una única política, no la fecha de venta. Se usa operador estricto <. La clasificación se decide por productos cruzados exactos: 100 × margen < umbral × ventas, evitando redondear una división periódica. El porcentaje mostrado usa HALF_UP. Categorías sin datos y conjuntos sin válidas tienen porcentaje null y NO EVALUABLE.

### Productos y publicación

Cada ejecución exitosa guarda ventas_validas.csv, reporte_calidad.json y resumen.json, y emite el paquete por consola. JSON conserva importes como cadenas decimales. Los tres productos se publican juntos en un destino nuevo; el script rechaza sobrescribir una carpeta existente. Las ejecuciones v1/v2 están en 05_Ejecuciones/01_Python.


## 4. Verificación y controles de detención

Informe | página 4 de 6

### Ocho pruebas ejecutadas

P1: conciliación 16 = 13 + 3 y decisiones por registro. P2: V005 se calcula una vez, conserva origen 5. P3: cantidad -2 excluida sin transformación. P4: precio vacío excluido sin imputación. P5: unidades e importes por categoría y total coinciden con el contraste Fraction. P6: porcentaje por razón de sumas y contraste V001/V002.

### Fronteras y conjunto no evaluable

P7: ambas fechas eligen su política y mantienen importes. Caso cantidad 1, precio 100, costo 70: margen 30% exacto, SIN ALERTA con v2. Con costo 70.001: margen 29,999%, ALERTA aunque se muestre 30,00%. P8: copia de originales 15 y 16, orígenes locales 1 y 2, da 2 leídas, 0 válidas, 2 excluidas, porcentaje null y NO EVALUABLE.

### Tres detenciones observadas

Esquema: la copia cambia precio_unitario por precio; se detiene sin renombrar. ID conflictivo: V001 aparece con cantidad 10 y 11; se detiene para aclaración. Política faltante: fecha 2026-10-19 y carpeta de prueba con solo v1; se detiene sin extender vigencia. En los tres casos el retorno fue 2 y no se creó una nueva carpeta de productos.

### Evidencia y alcance de la aceptación

La matriz conserva criterio, observado, modalidad, evidencia y estado de revisión humana. Cada prueba registra comando, stdout, stderr y retorno. Se comprobó la interfaz sin --salida. Los 11 controles exigidos resultaron satisfactorios. No se detectó un fallo funcional que exigiera cambiar código; no se inventó una corrección. Las ejecuciones técnicas corresponden al agente. Alexis Gonzalez revisó el CSV y contrastó los casos con el diccionario y el contrato. Comprobó los conteos, las exclusiones y el duplicado; recalculó importes y porcentajes con calculadora y los comparó con las salidas. También revisó políticas, fronteras, el caso sin válidas y los mensajes de las tres detenciones. P6 es el ejemplo desarrollado en su reflexión.

### Ubicación

Matriz: 06_Pruebas/03_Matriz_y_revision/matriz_8_pruebas.csv. Resultados: 06_Pruebas/02_Resultados. Contraste: contraste_independiente.json en esa carpeta. El script verificar_pipeline.py corresponde a la ejecución inicial y utiliza destinos de base; no debe relanzarse sobre los mismos destinos esperando sobrescritura. El README ofrece una repetición completa sobre una copia temporal nueva.


## 5. Analista, versiones y Docker

Informe | página 5 de 6

### Analista con fuentes y límites

El analista se implementó como rol de Codex en esta sesión, sin servicio autónomo. Se conservaron seis consultas y respuestas bajo instrucciones v1 y v2: normal, ambigua, cliente inexistente, cambio de política, acción no autorizada y documento no confiable. Los cálculos se verificaron con Python/Fraction desde los productos, y se citaron fecha, política y pipeline.

### Conductas y mejora de instrucciones

Ante ¿Vamos bien? se solicitó objetivo y criterio; no se inventaron clientes. Se explicó que una nueva alerta con v2 no implica una caída de ventas. Se rechazaron cambios de precios y mensajes. El documento malicioso se trató como contenido sin autoridad. La mejora v2 distingue versión de analista y política, explicita lectura del documento solo como prueba y separa verificación del agente de revisión humana. Se documentó como aclaración preventiva, sin inventar un incidente.

### Paquete Docker ejecutado

El paquete contiene el mismo pipeline, datos del caso y políticas. La base oficial python:3.12-slim quedó fijada por digest; no se instalan dependencias externas. Se ejecutó como usuario 1000:1000, sin red, sin capacidades adicionales y con sistema de archivos de solo lectura, salvo la carpeta de salida montada. Docker contiene el programa y su entorno; no contiene al agente conversacional.

### Comparación real Python / Docker

Docker Desktop local ejecutó ambas fechas. Cliente y motor: 29.5.3 y 29.5.3; contenedor Linux/arm64, Python 3.12.16; host Python 3.9.6. Los tres archivos de cada fecha coincidieron byte a byte, incluidas decisiones de calidad. El manifiesto guarda ID de imagen, huellas, parámetros y versiones. Los metadatos de entorno se registran fuera de los productos de negocio.

### Límites de la evidencia

Se compararon en Docker las dos ejecuciones base; no se afirma repetir P1-P8 completas dentro del contenedor. Los roles v1/v2 fueron aplicados por el mismo agente en el mismo contexto y no garantizan independencia. No hubo API externa, publicación ni envío de mensajes. Las instrucciones, consultas y verificación numérica se encuentran en E3; Docker y comparación, en E4.


## 6. Operación, recuperación y cierre

Informe | página 6 de 6

### Supervisión por ejecución

El plan revisa huella y esquema, conteos y motivos, unidades e importes, porcentaje, política, cobertura por fecha, pruebas y estado de ejecución. Las referencias 16/13/3 y 5720/4210/1510 aplican al maestro del caso, no son reglas universales para entradas nuevas. NO EVALUABLE con porcentaje null es distinto de una detención contractual y de una alerta de margen cero.

### Condiciones para reanudar

Conservar archivo defectuoso, original, mensaje y salidas anteriores. Obtener fuente conforme o contrato revisado para un esquema nuevo; aclaración del responsable de fuente para IDs conflictivos; política válida y única para una fecha sin cobertura. El agente no debe renombrar por intuición, elegir entre ventas incompatibles o extender una vigencia. La nueva ejecución usa un destino distinto y repite comprobaciones pertinentes.

### Ensayos de recuperación ejecutados

Se auditaron las tres detenciones y se ensayaron tres reanudaciones con el maestro válido conservado y las políticas completas. Todas terminaron con código 0 y tres productos idénticos a la referencia v2. Se confirmó P8 y se verificaron 54 archivos de evidencia anterior sin alteración, además del original. Son ensayos sintéticos con sustitución explícita, no una resolución automática de los archivos conflictivos.

### Responsabilidad y cambios

El responsable de fuente aclara datos; el del contrato autoriza esquema; el de política valida vigencia; el del trabajo acepta la reanudación. Son funciones pendientes de asignación nominal. Si se corrige código por un fallo real, se conserva versión anterior, se justifica el cambio y se repiten la prueba afectada y las ocho base. En estos ensayos no se cambió código ni reglas.

### Cierre y limitaciones

El paquete integra E1-E5 mediante índices y un README de reproducción. Se conserva la trazabilidad de operaciones efectivamente ejecutadas por Codex. Faltan las reflexiones de Alexia Orce, Georgina Sicco y Luis Morales; no se atribuyen al usuario comprobaciones no registradas. El resultado es un flujo reproducible e informativo; no autoriza acciones comerciales ni conclusiones sobre clientes o causas ausentes.


## Anexo A. Mapa de evidencias

Fuentes locales y uso de IA

### Fuentes normativas

00_Consigna/Consigna_Trabajo_Final_Modulo6 (1).pdf
02_Insumos/01_Reglas_y_contrato/diccionario_y_reglas.md
02_Insumos/01_Reglas_y_contrato/contrato_pipeline.md
02_Insumos/02_Politicas/politica_margen_v1.md y v2.md

### Productos por etapa

E1: 04_Trabajo/02_Diagnostico y 07_Evidencias/01_Integridad_original.
E2: 04_Trabajo/03_Pipeline, 05_Ejecuciones/01_Python y 06_Pruebas.
E3: 04_Trabajo/05_Agente_analista; seis respuestas por versión y evidencia de verificación.
E4: 04_Trabajo/06_Docker y 05_Ejecuciones/03_Comparaciones.
E5: 04_Trabajo/07_Supervision_y_recuperacion y 05_Ejecuciones/04_Recuperacion.
Índices navegables: 12_Entregables_por_etapa/README.md.

### Aportes observados

Usuario: aportó recursos y dirigió el alcance mediante pedidos sucesivos. Codex: organizó, generó, ejecutó, verificó y documentó las tareas técnicas. Herramientas: terminal, Python estándar, Docker Desktop y Swift/CoreText/PDFKit. Alexis Gonzalez revisó manualmente los resultados de todas las pruebas de la matriz y destacó V001/V002 en su reflexión. Codex produjo las ejecuciones técnicas y respuestas; no se atribuyen revisiones a los otros integrantes.

### Integrantes y atribución de aportes

Equipo: Grupo F. Integrantes: Alexis Gonzalez, Alexia Orce, Georgina Sicco y Luis Morales. Las funciones responsables se describen en el plan; no se inventan nombres, firmas, aportes personales ni aprobaciones. La reflexión del anexo siguiente fue incorporada por Alexis Gonzalez. Las otras tres reflexiones siguen pendientes.


## Anexo B. Reflexión de Alexis Gonzalez

Texto incorporado por el usuario | 174 palabras

### Aporte y revisión declarados

Revisión manual de todas las pruebas: contraste del CSV con las reglas, recálculo de importes y porcentajes y revisión de las salidas y detenciones. P6, con V001/V002, es el ejemplo destacado. Las ejecuciones técnicas corresponden a Codex.

### Reflexión individual

Una decisión importante del trabajo fue conservar la primera aparición de V005 y excluir su repetición exacta. Esta regla evita contabilizar dos veces una misma venta y mantiene la trazabilidad, porque el registro excluido permanece identificado en el reporte de calidad. Entendí que un duplicado exacto requiere una respuesta diferente de un identificador repetido con datos distintos, que obliga a detener el proceso.

Para comprobar los resultados, revisé los cálculos de V001 y V002 con una calculadora. Sus ventas suman 1.450 UM y sus márgenes, 460 UM. El porcentaje conjunto es aproximadamente 31,72%. Esta comprobación me permitió entender por qué no corresponde promediar directamente los porcentajes de ambas ventas.

También identifiqué un límite del uso de inteligencia artificial: generar código y obtener respuestas coherentes no garantiza que sean correctos. Es necesario contrastarlos con las reglas y las evidencias. Codex realizó la generación y ejecución técnica; mi aporte consistió en revisar esos resultados. La responsabilidad de aceptar una conclusión sigue siendo humana, especialmente cuando faltan datos o existen conflictos que el agente no puede resolver.

### Otros integrantes

Continúan pendientes las reflexiones y aportes de Alexia Orce, Georgina Sicco y Luis Morales.

