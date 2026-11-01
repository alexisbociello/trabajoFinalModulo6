# Plan de supervisión y recuperación — Horizonte v1

Fecha real: 2026-11-01. Flujo consolidado: pipeline 1.0.0, contrato/diccionario v1, política v2 para fecha simulada 2026-10-19. Los ensayos fueron ejecutados por Codex; no se atribuye revisión humana ni autorización comercial a las comprobaciones del agente.

## Flujo y responsabilidades

Fuente protegida → verificación de integridad y esquema → validación por registro → selección de una única política por fecha de ejecución → cálculo decimal → publicación conjunta de tres productos en destino nuevo → contraste de conteos, importes, porcentaje, estado y pruebas → aceptación del responsable del trabajo.

El ejecutor técnico registra hechos y detiene ante incumplimientos. El responsable del trabajo autoriza nuevas ejecuciones y acepta resultados. El responsable de la fuente aclara el significado de datos o IDs conflictivos; el responsable del contrato autoriza cambios de esquema; el responsable de política valida su vigencia. Son funciones, no personas designadas: los nombres del equipo siguen pendientes. En el caso académico, una duda normativa puede escalarse al docente. El agente no puede asumir estas decisiones por cuenta propia.

## Indicadores por ejecución

| Indicador | Referencia del caso completo | Comprobación / respuesta |
|---|---|---|
| Integridad de fuente | SHA-256 inicial conservado | Comparar antes y después; si difiere, detener y revisar versión |
| Esquema y campos | 6 columnas exactas, orden contractual | Comparar antes de calcular; detener si difiere |
| Filas | 16 = 13 válidas + 3 excluidas | Conciliar y revisar decisiones por origen; no contar motivos como filas |
| Exclusiones | 14 duplicado del 5; 15 cantidad negativa; 16 precio vacío | Preservar valores y motivos; no imputar |
| Unidades | 91 | Contraste por categoría y total |
| Ventas / costos / margen | 5720 / 4210 / 1510 UM | Razón de sumas; precisión decimal sin redondeos intermedios |
| Porcentaje | 1510/5720 × 100 = 26,40% mostrado | Comparar umbral sin redondear; no promediar porcentajes |
| Política / fecha | v2, umbral 30%, 2026-10-19 | Fecha de ejecución; cobertura única; no extender v1 |
| Estado global | ALERTA con v2; SIN ALERTA con v1 | Cambio de clasificación sin cambio de ventas |
| Pruebas | P1–P8 y tres detenciones con evidencia | Revisar observado, código de retorno y destinos |
| Ejecución | Código 0 y tres productos coherentes | Un destino antiguo no demuestra éxito actual |
| Entorno | Python/Docker identificados | Comparar negocio y calidad; registrar metadatos por separado |

Los valores anteriores son referencias para este CSV completo, no reglas universales para aceptar entradas nuevas. Un archivo de prueba con dos filas tiene sus propios conteos esperados.

## Detenciones: causa, evidencia y reanudación

| Detención | Causa demostrada y evidencia | Condición para reanudar | Función que autoriza |
|---|---|---|---|
| Esquema incompatible | La copia contiene precio en lugar de precio_unitario. `06_Pruebas/01_Entradas/esquema_incompatible.csv` y `06_Pruebas/02_Resultados/Detencion_esquema/` | Fuente conforme o nueva versión explícita de contrato y código revisado; no renombrar por intuición | Responsable de fuente y contrato; responsable del trabajo acepta nueva ejecución |
| ID conflictivo | V001 aparece con cantidad 10 y 11; no son duplicados exactos. `06_Pruebas/01_Entradas/id_conflictivo.csv` y `06_Pruebas/02_Resultados/Detencion_ID_conflictivo/` | Aclaración del responsable de fuente y nueva entrada autorizada; el agente no decide qué venta conservar | Responsable de fuente; responsable del trabajo autoriza reejecución |
| Política faltante | Carpeta de prueba solo contiene v1 hasta 2026-10-18; fecha pedida 2026-10-19. `06_Pruebas/01_Entradas/politicas_sin_v2/` y `06_Pruebas/02_Resultados/Detencion_politica_faltante/` | Una política válida y única que cubra la fecha; no extender vigencia ni seleccionar la más reciente por defecto | Responsable de política; responsable del trabajo autoriza reejecución |

Las tres detenciones originales tienen retorno no exitoso y no crearon la carpeta de productos. Se preservan archivos defectuosos y mensajes. Estas causas se observan en los archivos; no se atribuyen a una hipótesis de IA, a un fallo del modelo ni a un problema comercial inexistente.

## Caso sin filas válidas

P8 contiene originales 15 y 16 con orígenes locales 1 y 2. Resultado: 2 leídas, 0 válidas, 2 excluidas; importes monetarios suman 0, porcentaje null y NO EVALUABLE. Es una ejecución técnicamente exitosa con información insuficiente para evaluar margen, no una detención contractual ni una alerta por 0%. No completar valores ni presentar conclusiones comerciales. Su revisión puede requerir nueva fuente autorizada, no alterar la copia original.

## Procedimiento de recuperación

1. Registrar problema observado, comando, retorno, evidencia y destino que no se publicó; identificar como anteriores las salidas previas.
2. Conservar fuente original, copias defectuosas y todos los resultados anteriores.
3. Obtener datos/contrato/política válidos del responsable correspondiente. Si cambia una regla o código, conservar versión previa y justificar el cambio mínimo.
4. Verificar huellas, encabezado, clave y cobertura de política antes de publicar productos.
5. Ejecutar con fecha explícita en un destino nuevo y registrar entorno, versión, comando y consola.
6. Repetir la prueba afectada y comprobaciones pertinentes. Ante corrección real de código, repetir además las ocho pruebas base, como exige la consigna; no modificar criterios esperados para ocultar un fallo.
7. Comparar decisiones e importes, confirmar original intacto y registrar aceptación del responsable. Sin esa decisión no inventar una aprobación humana.

## Ensayos efectivamente ejecutados

Se ejecutó `python3 04_Trabajo/07_Supervision_y_recuperacion/verificar_operacion.py`. Se comprobaron las tres detenciones previas y luego se ensayaron tres reanudaciones usando el maestro válido conservado y las políticas completas. Esto demuestra recuperación con sustitución explícita por una fuente conocida; no resuelve automáticamente los archivos defectuosos ni decide entre IDs reales conflictivos.

Las tres reanudaciones dieron código 0 y sus tres productos coinciden byte a byte con la ejecución v2 de referencia. Se confirmó P8. Se verificaron 54 archivos de evidencias anteriores sin cambios y el original intacto. Código y reglas sin cambios; no se inventó corrección ni se afirmó repetir la matriz completa en esta etapa.

Auditoría y comandos: `05_Ejecuciones/04_Recuperacion/20261101T221547185846Z/auditoria_operacion.json` y subcarpetas de ese mismo intento. Cada repetición usa una marca UTC nueva.

## Límites y cierre

Clasificación informativa; no modificar precios ni enviar mensajes. Fuente sin clientes, causas ni series adicionales. Roles sucesivos en un mismo agente no garantizan independencia. E1–E4 tienen productos y pruebas; el informe final, anexos de participación, README global de reproducción y ZIP final siguen pendientes. Los nombres de responsables deben completarse para el cierre documental; no impiden ejecutar estos ensayos autorizados.

## Actualización de cierre - 2026-11-01

Se generaron informe PDF, anexos, README global e inventario/ZIP técnico. La matriz completa se repitió en copia nueva satisfactoriamente; evidencia en 07_Evidencias/03_Consola_y_versiones/validacion_cierre. Identidad y reflexión propia siguen pendientes. Las menciones anteriores a tareas pendientes describen el estado al generar este plan.
