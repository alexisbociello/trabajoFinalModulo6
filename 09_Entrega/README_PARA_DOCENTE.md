# Comercial Horizonte - Grupo F

Integrantes: Alexis Gonzalez, Alexia Orce, Georgina Sicco y Luis Morales.

## Orden sugerido de revisión

1. [Informe PDF](08_Informe/03_PDF_final/Informe_Final_Modulo6_GrupoF.pdf): seis páginas de contenido, portada y anexos.
2. [Índice E1–E5](10_Entregables_por_etapa/README.md): acceso a los productos de cada etapa.
3. [Matriz P1–P8 y tres detenciones](06_Pruebas/03_Matriz_y_revision/matriz_8_pruebas.csv): resultado observado y ruta a la evidencia.
4. [Agente analista](04_Trabajo/05_Agente_analista/ficha_agente_analista.md): instrucciones v1/v2, seis respuestas por versión y comprobaciones.
5. [Docker real y comparación](04_Trabajo/06_Docker/README.md): entorno observado, comandos y equivalencia con Python.
6. [Plan de supervisión y recuperación](04_Trabajo/07_Supervision_y_recuperacion/plan_supervision_y_recuperacion.md).

## Resultado

16 leídas = 13 válidas + 3 excluidas. 91 unidades. Ventas: 5720 UM; costos: 4210 UM; margen: 1510 UM; margen porcentual mostrado: 26.40%. Política v1, 2026-10-18: SIN ALERTA. Política v2, 2026-10-19: ALERTA. Las fechas son simuladas. Las ejecuciones y verificaciones técnicas fueron realizadas por Codex con herramientas; Alexis Gonzalez comprobó manualmente los resultados de todas las pruebas de la matriz; P6 es el ejemplo desarrollado en su reflexión.

## Reproducción

Desde esta carpeta, requiere Python 3.9 o posterior y biblioteca estándar:

```sh
python3 04_Trabajo/03_Pipeline/pipeline.py --entrada 01_Original_ventas_PROTEGIDO/ventas_original.csv --politicas 02_Insumos/02_Politicas --fecha-ejecucion 2026-10-19
```

Sin --salida, emite JSON y no escribe productos. Para guardar, agregar `--salida 05_Ejecuciones/reproduccion_nueva` con un destino que no exista. Para v1, usar fecha 2026-10-18 y destino distinto. Cada éxito genera ventas_validas.csv, reporte_calidad.json y resumen.json. Error contractual: retorno 2 sin nuevos productos.

Repetir P1–P8 y tres detenciones sin sobrescribir evidencia:

```sh
python3 06_Pruebas/reproducir_pruebas_en_copia.py
```

Resultado esperado: 11 controles aprobados, más comprobación de interfaz por consola e integridad. Crea una copia temporal nueva e informa su ubicación.

Con motor Docker iniciado:

```sh
python3 04_Trabajo/06_Docker/ejecutar_y_comparar.py
```

Construye y ejecuta ambas políticas sin red; compara los tres productos con Python. La primera construcción puede descargar la base oficial. El contenedor contiene el pipeline y su entorno, no el analista conversacional.

Auditar detenciones y ensayar recuperación:

```sh
python3 04_Trabajo/07_Supervision_y_recuperacion/verificar_operacion.py
```

## Integridad

```sh
shasum -a 256 -c SHA256SUMS.txt
shasum -a 256 -c 07_Evidencias/01_Integridad_original/ventas_original.sha256
```

El inventario está en MANIFIESTO_ENTREGA.json. El original se conserva sin editar; si el extractor no respeta permisos, se puede restaurar la protección local con `chmod 444 01_Original_ventas_PROTEGIDO/ventas_original.csv` y `chmod 555 01_Original_ventas_PROTEGIDO`.

## Participación del equipo y evidencias

Alexis Gonzalez revisó manualmente todas las pruebas de la matriz, contrastó el CSV con las reglas y recalculó importes y porcentajes. Alexia Orce ejecutó v1/v2 desde Visual Studio Code y comprobó el cambio de alerta con importes constantes. Georgina Sicco declara la ejecución del pipeline y pruebas, el recálculo con calculadora de V001/V002 y la comparación de resúmenes. Luis Morales reflexiona sobre el trabajo E1-E5, la reproducibilidad y los criterios de aceptación; su texto no identifica una ejecución individual específica.

El trabajo manual se refleja en contrastar reglas, recalcular cifras y explicar resultados. Las evidencias conservan comandos, salidas, errores, versiones, huellas y comparaciones: permiten seguir cada conclusión hasta su comprobación. Las ejecuciones históricas de Codex y las revisiones declaradas por integrantes se distinguen sin atribuir autorías no documentadas.

Las cuatro reflexiones están incorporadas al PDF y en [los anexos individuales](08_Informe/02_Anexos_y_reflexiones/participacion_y_uso_IA.md).

Se conservaron salidas, errores, comandos y versiones necesarios para evaluar. Se excluyeron libros, diapositivas, RedNova, plantillas vacías, temporales y versiones obsoletas. Las copias de código/datos dentro del paquete Docker son necesarias para reproducirlo.
