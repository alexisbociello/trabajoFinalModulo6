# Guía rápida para el Grupo F

**Integrantes:** Alexis Gonzalez, Alexia Orce, Georgina Sicco y Luis Morales.

## 1. ¿De qué va el proyecto?

Trabajamos con **Comercial Horizonte**, una empresa ficticia con un archivo de 16 registros de ventas. El objetivo es convertir esos datos en resultados confiables usando reglas explícitas, Python y un agente de IA, y conservar evidencia de cómo se llegó a cada resultado.

El recorrido es:

**Datos originales → control de calidad → cálculos con Python → análisis con fuentes → reproducción en Docker → supervisión y recuperación.**

Un *pipeline* es el programa que realiza esos pasos de procesamiento de manera ordenada. Docker permite ejecutar ese programa en un entorno definido. El agente analista responde preguntas usando los archivos del caso y las instrucciones que delimitan su tarea.

## 2. ¿Qué se espera del trabajo?

Demostrar que podemos dirigir y supervisar el uso de IA: definir reglas, comprobar resultados, reconocer límites y justificar decisiones con evidencia. El código y los textos generados deben poder revisarse y reproducirse.

| Etapa | Qué demuestra | Dónde verlo |
|---|---|---|
| E1. Calidad | Detectar errores y preservar el archivo original | [Diagnóstico](04_Trabajo/02_Diagnostico/diagnostico.md) |
| E2. Pipeline y pruebas | Calcular correctamente y comprobar casos normales y especiales | [Matriz de pruebas](06_Pruebas/03_Matriz_y_revision/matriz_8_pruebas.csv) |
| E3. Agente analista | Responder con fuentes, pedir aclaraciones y respetar límites | [Guía del analista](04_Trabajo/05_Agente_analista/README.md) |
| E4. Docker y versiones | Obtener los mismos productos en otro entorno y registrar versiones | [Guía Docker](04_Trabajo/06_Docker/README.md) |
| E5. Supervisión y cierre | Saber cuándo detenerse, cómo reanudar y cómo documentar la entrega | [Plan operativo](04_Trabajo/07_Supervision_y_recuperacion/plan_supervision_y_recuperacion.md) |

## 3. Lo que todos tenemos que entender

- **Se leen 16 registros: 13 válidos y 3 excluidos.** Se excluyen la repetición exacta del registro 5 que aparece en el 14, una cantidad negativa y un precio vacío. El número de registro cuenta filas de datos, sin el encabezado.
- **Resultados:** 91 unidades; ventas de 5.720 UM; costos de 4.210 UM; margen de 1.510 UM; margen global de 26,40%. UM significa unidades monetarias ficticias.
- **Las fórmulas:** ventas = cantidad × precio; costos = cantidad × costo; margen = ventas − costos. El porcentaje global es margen total ÷ ventas totales × 100. No se promedian porcentajes de filas.
- **La política cambia la alerta.** Para la fecha simulada 18/10/2026, el umbral es 25% y el resultado es SIN ALERTA. Para el 19/10/2026, el umbral es 30% y da ALERTA. Las ventas y el margen son los mismos: cambió la regla. Esas fechas no son fechas de entrega.
- **El límite es estricto:** con umbral 30%, un margen de 30% exacto no genera alerta; 29,999% sí, aunque en pantalla aparezca 30,00% por redondeo.
- **Excluir una fila no es detener todo.** Una cantidad inválida se excluye y registra. Un esquema incompatible, un mismo ID con datos distintos o una política faltante obligan a detener el proceso y pedir revisión.
- **Sin filas válidas:** el porcentaje es `null` —no está definido— y el estado es NO EVALUABLE.
- **La IA tiene límites:** no puede inventar clientes, completar precios por intuición, cambiar políticas ni ejecutar acciones comerciales sin autorización.

## 4. ¿Qué está hecho y qué falta?

**Hecho:** diagnóstico, programa, ejecuciones con ambas políticas, ocho pruebas y tres detenciones, analista con dos versiones de instrucciones, ejecución real en Docker, comparación de resultados, ensayos de recuperación, informe y ZIP técnico.

**Participación registrada:** Codex generó y ejecutó el trabajo técnico. Alexis revisó manualmente los resultados de todas las pruebas de la matriz y completó su reflexión.

**Pendiente:** Alexia, Georgina y Luis deben revisar evidencia, informar su aporte concreto y completar su reflexión individual de **150–200 palabras**. Después hay que incorporar esos aportes al informe y regenerar el paquete final. Que exista un ZIP no significa que ya estén completos los pendientes personales.

## 5. Qué tiene que hacer cada uno y cómo

### Paso 1. Entender el conjunto

Leer esta guía y el [informe](08_Informe/03_PDF_final/Informe_Final_Modulo6_GrupoF.pdf). Si se necesita buscar o copiar texto, usar el [informe editable](08_Informe/01_Borradores/informe_final_editable.md).

Al terminar, cada uno debería poder explicar con sus palabras qué datos usamos, qué excluimos, cómo calculamos el margen y por qué cambia la alerta.

### Paso 2. Hacer una revisión propia

El siguiente es un **reparto sugerido para completar la revisión**, no una atribución de tareas ya realizadas. Pueden acordar otro reparto; cada uno debe conservar evidencia de lo que efectivamente haga.

| Integrante | Revisión sugerida | Cómo comprobarla |
|---|---|---|
| Alexia | Calidad de datos y exclusiones | Abrir el [CSV original](01_Original_ventas_PROTEGIDO/ventas_original.csv) en modo lectura y el diagnóstico. Contar 16 filas de datos; comparar registros 5 y 14; verificar cantidad negativa en el 15 y precio vacío en el 16. Contrastar con el [reporte de calidad](05_Ejecuciones/01_Python/2026-10-19_v2/ejecucion_01/reporte_calidad.json). |
| Georgina | Cálculos y cambio de política | Recalcular con calculadora V001 y V002 siguiendo la [guía aritmética](07_Evidencias/04_Calculos_independientes/calculo_V001_V002_para_revision.md). Comparar los resúmenes [v1](05_Ejecuciones/01_Python/2026-10-18_v1/ejecucion_01/resumen.json) y [v2](05_Ejecuciones/01_Python/2026-10-19_v2/ejecucion_01/resumen.json): mismos importes, distinto umbral y alerta. |
| Luis | Respuestas y límites del analista | Leer las respuestas v2 a [pregunta ambigua](04_Trabajo/05_Agente_analista/Consultas_y_respuestas/v2/02_ambiguedad.md), [dato inexistente](04_Trabajo/05_Agente_analista/Consultas_y_respuestas/v2/03_dato_inexistente.md), [acción no autorizada](04_Trabajo/05_Agente_analista/Consultas_y_respuestas/v2/05_accion_no_autorizada.md) y [documento no confiable](04_Trabajo/05_Agente_analista/Consultas_y_respuestas/v2/06_documento_no_confiable.md). Contrastarlas con las [instrucciones v2](04_Trabajo/05_Agente_analista/v2/instrucciones.md): comprobar que pide contexto, no inventa datos y respeta sus permisos. |

Para revisar no hace falta programar ni volver a ejecutar todo. Abrir un JSON como texto permite ver sus campos y resultados. Si se abre el CSV en una planilla, cerrarlo sin guardar cambios sobre el original.

### Paso 3. Registrar el aporte

Cada integrante debe completar este registro con lo que realmente hizo, incluso si encontró una duda o diferencia:

> **Nombre y fecha:** …  
> **Qué revisé:** …  
> **Archivos o casos consultados:** …  
> **Cómo lo comprobé:** …  
> **Resultado observado:** …  
> **Dudas o diferencias encontradas:** …

Incluirlo en el archivo personal, debajo de la reflexión. Una revisión debe describir una comprobación concreta: por ejemplo, comparar dos filas, recalcular un porcentaje o contrastar una respuesta con sus instrucciones. Si aparece una diferencia, registrar el valor esperado, el observado y el archivo; resolverla antes de cerrar la entrega.

### Paso 4. Escribir la reflexión individual

Cada uno completa su archivo:

- [Alexia Orce](08_Informe/02_Anexos_y_reflexiones/reflexion_Alexia_Orce_PENDIENTE.md).
- [Georgina Sicco](08_Informe/02_Anexos_y_reflexiones/reflexion_Georgina_Sicco_PENDIENTE.md).
- [Luis Morales](08_Informe/02_Anexos_y_reflexiones/reflexion_Luis_Morales_PENDIENTE.md).

Escribir **150–200 palabras propias** que expliquen:

1. Una decisión del proyecto que entendieron y por qué tiene sentido.
2. Una comprobación que realizaron: qué miraron, cómo la hicieron y qué obtuvieron.
3. Un límite o aprendizaje sobre el uso de IA y la responsabilidad humana.

Pueden usar la reflexión de Alexis como referencia de estructura. El contenido debe corresponder a la experiencia de cada uno. Diferenciar revisar resultados de haber generado o ejecutado el programa. Al completar el texto, reemplazar el estado “pendiente” por una descripción fiel del aporte realizado.

### Paso 5. Integrar y cerrar

El equipo debe designar a quien integre las tres reflexiones y los registros de revisión. Esa persona deberá:

1. Actualizar [participación y uso de IA](08_Informe/02_Anexos_y_reflexiones/participacion_y_uso_IA.md) y [pendientes](PENDIENTES_PERSONALES.md) con los aportes efectivamente recibidos.
2. Incorporar las reflexiones al informe editable, actualizar sus menciones de pendientes y regenerar el PDF; revisar que los textos estén completos y legibles.
3. Regenerar el ZIP desde la raíz del proyecto con `python3 09_Entrega/empaquetar.py` y revisar el resultado de la validación.
4. Abrir el ZIP actualizado y comprobar que contiene el informe y las reflexiones definitivas. La guía de entrega está en [09_Entrega/LEEME.md](09_Entrega/LEEME.md).

Editar siempre los archivos fuente del proyecto; después reconstruir el paquete. El archivo previsto para compartir con el docente es `09_Entrega/02_ZIP/Modulo6_Equipo_GrupoF.zip`.

## 6. Cuándo terminamos

- [ ] Todos pueden explicar el caso, los resultados y el cambio de alerta.
- [ ] Alexia, Georgina y Luis realizaron y registraron una revisión concreta.
- [ ] Las tres reflexiones tienen entre 150 y 200 palabras y reflejan experiencias reales.
- [ ] Las dudas o diferencias detectadas quedaron resueltas o explicitadas.
- [ ] Informe, participación y pendientes reflejan el estado final.
- [ ] El PDF y el ZIP fueron regenerados y revisados.

**Lo que cada compañero tiene que aportar ahora:** su reflexión de 150–200 palabras y el registro de su revisión, con archivos consultados, método y resultado observado.
