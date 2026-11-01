# Pipeline Horizonte v1.0.0

## Uso

Desde la raíz del proyecto, requiere Python 3.9 o posterior y solo biblioteca estándar:

```sh
python3 04_Trabajo/03_Pipeline/pipeline.py --entrada 01_Original_ventas_PROTEGIDO/ventas_original.csv --politicas 02_Insumos/02_Politicas --fecha-ejecucion 2026-10-18 --salida 05_Ejecuciones/01_Python/2026-10-18_v1/ejecucion_02
```

Para v2 usar fecha 2026-10-19 y un destino propio nuevo. Nunca reutilizar una carpeta de salida existente. Sin `--salida`, el paquete completo se imprime como JSON sin guardar productos. Las fechas son simuladas, no fechas de entrega.

## Los cuatro bloques

1. Leer: comprueba encabezado y seis campos, conserva orden y huella SHA-256.
2. Validar: examina cada campo, conserva primer duplicado exacto y registra todos los motivos. Un ID con contenido distinto detiene el flujo.
3. Calcular: elige una única política por fecha de ejecución. Calcula importes con Decimal y razón de sumas. Para decidir alerta usa productos cruzados: `100*margen < umbral*ventas`, evitando redondear una división periódica. El porcentaje de salida puede ser una expansión decimal finita de una razón periódica; la clasificación no depende de esa aproximación. HALF_UP únicamente para presentación del porcentaje. Los importes del CSV/JSON se conservan como cadenas decimales exactas.
4. Guardar: genera los tres productos en un temporal y publica la carpeta completa; rechaza destinos existentes y preserva entradas. JSON también por consola. Error: mensaje por stderr y código 2.

Los agregados incluyen todas las categorías permitidas y total. Categoría vacía: porcentaje null y NO EVALUABLE. Se registra versión, fecha, política y huella de entrada.

## Verificación ejecutada

`python3 06_Pruebas/verificar_pipeline.py` ejecutó P1–P8 y tres detenciones. El verificador ya dejó productos en destinos nuevos; para repetir hay que modificar los destinos o identificar un nuevo intento, sin borrar evidencias anteriores.

Resultados: 16 leídas = 13 válidas + 3 excluidas; 91 unidades; ventas 5720; costos 4210; margen 1510; margen porcentual mostrado 26.40. v1 SIN ALERTA y v2 ALERTA. P7: 30% SIN ALERTA; 29.999% ALERTA aun mostrando 30.00. P8: dos excluidas, porcentaje null y NO EVALUABLE.

Contraste independiente con Fraction (no importa funciones del pipeline), por categoría y total. V001/V002: ventas 1450, margen 460, porcentaje 460/1450×100; el promedio simple 35% es incorrecto.

Evidencias: `06_Pruebas/02_Resultados`, matriz en `06_Pruebas/03_Matriz_y_revision`, productos reales en `05_Ejecuciones/01_Python/.../ejecucion_01`. Cada ejecución conserva comando, código de retorno, stdout y stderr. La integridad del original se verificó al terminar.

## Revisión del agente y límites

Revisión contra contrato: esquema y conflictos detienen; exclusiones rastreables; sin imputación; política por ejecución; precisión decimal; comparación estricta; conjunto vacío; tres productos; rechazo a sobrescritura; interfaz por consola. No se observaron fallos en las pruebas ejecutadas, por lo que no se inventó una corrección.

Las ejecuciones y verificaciones fueron realizadas por Codex con herramientas. La revisión humana no está registrada. Docker y las seis consultas del analista quedan para sus etapas correspondientes. No se requiere confirmación de comprensión para continuar el trabajo autorizado.
