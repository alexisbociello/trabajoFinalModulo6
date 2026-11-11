# Comercial Horizonte - Trabajo final Módulo 6

Fecha de cierre técnico: 1 de noviembre de 2026. Modalidad: equipo de cuatro integrantes. Equipo: Grupo F. Integrantes: Alexis Gonzalez, Alexia Orce, Georgina Sicco y Luis Morales. Las fechas 2026-10-18 y 2026-10-19 son simuladas y no fechas de entrega.

## Empezar por aquí

- [Informe PDF](08_Informe/03_PDF_final/Informe_Final_Modulo6_GrupoF.pdf): seis páginas de contenido más portada y cinco anexos.
- [Informe editable](08_Informe/01_Borradores/informe_final_editable.md).
- [Entregables separados E1–E5](10_Entregables_por_etapa/README.md).
- [Participación y uso de IA](08_Informe/02_Anexos_y_reflexiones/participacion_y_uso_IA.md).

## Estado y alcance

Diagnóstico, pipeline, ejecuciones v1/v2, P1–P8, tres detenciones, analista v1/v2, Docker y tres ensayos de recuperación están ejecutados y documentados. El informe, anexos, guía e inventario integran la entrega técnica. Las cuatro reflexiones están integradas en el informe final. La participación distingue generación técnica con IA, revisiones manuales y aportes declarados.

Codex ejecutó las tareas técnicas con herramientas locales. Las revisiones manuales y los aportes declarados por el equipo están registrados en participación y en las cuatro reflexiones. El usuario indicó que no requiere defensa; no se preparó una presentación adicional.

## Resultados esperados

16 registros leídos = 13 válidos + 3 excluidos. Excluidos: origen 14 duplicado del 5, origen 15 cantidad negativa y origen 16 precio vacío. 91 unidades; ventas 5720 UM, costos 4210 UM, margen 1510 UM, margen porcentual 26.40 al presentar. Con política v1 (25%) el total es SIN ALERTA; con v2 (30%) es ALERTA. No cambian datos ni importes. Son reglas de referencia para este maestro, no para cualquier archivo futuro.

## Requisitos y protección del original

Python 3.9 o posterior, biblioteca estándar. Para E4: Docker con motor iniciado; construcción inicial puede requerir descarga de la imagen oficial. No se necesitan API, credenciales, nube ni paquetes Python externos. Las ejecuciones observadas usaron Python local 3.9.6 y Docker con Python 3.12.16.

Desde la raíz de la carpeta extraída:

```sh
shasum -a 256 -c 07_Evidencias/01_Integridad_original/ventas_original.sha256
chmod 444 01_Original_ventas_PROTEGIDO/ventas_original.csv
chmod 555 01_Original_ventas_PROTEGIDO
```

Los permisos protegen contra escritura accidental y son reversibles por el propietario. Git y algunos extractores no conservan permisos; la huella verifica el contenido.

## Reproducir el pipeline sin escribir archivos

```sh
python3 04_Trabajo/03_Pipeline/pipeline.py --entrada 01_Original_ventas_PROTEGIDO/ventas_original.csv --politicas 02_Insumos/02_Politicas --fecha-ejecucion 2026-10-19
```

Emite JSON por consola. Para guardar los tres productos usar un destino que todavía no exista:

```sh
python3 04_Trabajo/03_Pipeline/pipeline.py --entrada 01_Original_ventas_PROTEGIDO/ventas_original.csv --politicas 02_Insumos/02_Politicas --fecha-ejecucion 2026-10-19 --salida 05_Ejecuciones/01_Python/reproduccion_v2_nueva
```

Para v1, cambiar a fecha 2026-10-18 y un destino propio nuevo. No usar una carpeta existente: el script se detiene para preservar resultados anteriores. Los productos son ventas_validas.csv, reporte_calidad.json y resumen.json. Error contractual: retorno 2 y mensaje por stderr, sin productos nuevos. La consola conserva JSON completo incluso cuando se guardan archivos.

## Repetir las ocho pruebas y las tres detenciones

```sh
python3 06_Pruebas/reproducir_pruebas_en_copia.py
```

Crea una copia temporal nueva, copia solo código y entradas necesarias, ejecuta las pruebas y muestra dónde guardó matriz, resultados y consola. También admite `--destino` con una carpeta todavía inexistente. No sobrescribe evidencias del proyecto. Resultado esperado: 11 controles aprobados, además de interfaz sin --salida e integridad. El verificador original `verificar_pipeline.py` conserva sus destinos iniciales; usar este envoltorio para repetir con seguridad.

P7: 30% exacto SIN ALERTA; 29.999% ALERTA aunque se muestre 30.00. P8: dos filas, ninguna válida, porcentaje null y NO EVALUABLE. Detenciones: esquema cambiado, mismo ID con datos distintos y política faltante.

## Reproducir analista, Docker y operación

- Analista: [guía E3](04_Trabajo/05_Agente_analista/README.md). Las instrucciones y respuestas están guardadas. `python3 04_Trabajo/05_Agente_analista/verificar_fuentes.py` verifica números; no invoca un modelo ni regenera respuestas conversacionales.
- Docker real: `python3 04_Trabajo/06_Docker/ejecutar_y_comparar.py`. Construye la imagen, ejecuta v1/v2 sin red y compara con Python. Cada intento tiene marca UTC nueva. [Guía del paquete](04_Trabajo/06_Docker/README.md). Los logs históricos pueden contener rutas absolutas del equipo original; los scripts actuales calculan la raíz automáticamente.
- Recuperación: `python3 04_Trabajo/07_Supervision_y_recuperacion/verificar_operacion.py`. Genera tres ensayos en destinos nuevos, audita detenciones previas y conservación de evidencias. [Plan operativo](04_Trabajo/07_Supervision_y_recuperacion/plan_supervision_y_recuperacion.md).

El paquete Docker incluye copia exacta del mismo pipeline y entradas; ante cambios futuros, actualizar esas copias explícitamente. El verificador de Docker rechaza discrepancias de hashes antes de construir. Docker contiene el programa y su entorno, no el agente de conversación.

## Evidencias y versiones

`07_Evidencias` conserva huellas, bitácoras y comandos. `05_Ejecuciones/03_Comparaciones` contiene versiones Docker/Python, ID real de imagen y huellas del paquete. `05_Ejecuciones/04_Recuperacion` conserva auditoría y reanudaciones. `06_Pruebas/03_Matriz_y_revision` contiene observado y modalidad; las plantillas originales permanecen en `02_Insumos`.

Los productos Docker de ambas fechas coinciden byte a byte con Python. Los metadatos distintos de entorno están en manifiestos separados. No se afirma haber repetido P1–P8 completas dentro de Docker.

## Inventario y cierre

Dentro del ZIP final, `MANIFIESTO_ENTREGA.json` identifica los archivos y `SHA256SUMS.txt` permite comprobarlos con `shasum -a 256 -c SHA256SUMS.txt`. Ambos se generan al empaquetar. El inventario no se incluye a sí mismo para evitar referencias circulares.

El ZIP abre bajo una sola carpeta Modulo6_Equipo_GrupoF. Incluye los productos y evidencias evaluables de Horizonte; excluye material de clase y RedNova. Se excluyen .git, .DS_Store, temporales y el propio ZIP. Las cuatro reflexiones y sus aportes están integrados.

## Cierre de entrega - 11 de noviembre de 2026

Alexis Gonzalez revisó manualmente todas las pruebas de la matriz, contrastó el CSV con las reglas y recalculó importes y porcentajes. Alexia Orce ejecutó v1/v2 desde Visual Studio Code y comprobó el cambio de alerta con importes constantes. Georgina Sicco declara la ejecución del pipeline y pruebas, el recálculo con calculadora de V001/V002 y la comparación de resúmenes. Luis Morales reflexiona sobre el trabajo E1-E5, la reproducibilidad y los criterios de aceptación; su texto no identifica una ejecución individual específica.

El trabajo manual se refleja en contrastar reglas, recalcular cifras y explicar resultados. Las evidencias conservan comandos, salidas, errores, versiones, huellas y comparaciones: permiten seguir cada conclusión hasta su comprobación. Las ejecuciones históricas de Codex y las revisiones declaradas por integrantes se distinguen sin atribuir autorías no documentadas.

Entrega final: `09_Entrega/01_ZIP/Modulo6_Equipo_GrupoF.zip`.

## Organización y reconstrucción de la entrega

Carpetas 00-03: consigna, original protegido, insumos y material de consulta. Carpetas 04-07: trabajo técnico, ejecuciones, pruebas y evidencias. Carpeta 08: informe y reflexiones. Carpeta 09: empaquetador, validación y ZIP final. Carpeta 10: índices por etapa.

Para regenerar el PDF: `swift 08_Informe/01_Borradores/fuentes_pdf/generar_informe.swift`. Revisar las imágenes de `tmp/pdfs` y eliminarlas al terminar. Para reconstruir el ZIP: `python3 09_Entrega/empaquetar.py`. La fuente del README incluido en el ZIP es `09_Entrega/README_PARA_DOCENTE.md`.
