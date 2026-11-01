# Prompts breves para dirigir al agente

Ejecutar desde la copia del proyecto. La clase entrega el programa completo: el agente no tiene que reinventarlo.

## Leer y explicar

Lee README_INICIO.md y CONTRATO_DATOS.md. Explica el problema RedNova, el grano y clave de cada fuente y las etapas del pipeline. Usa solo archivos del proyecto. No modifiques datos ni reglas. Hazme tres preguntas para comprobar mi comprensión.

## Aprender y registrar Git

Lee GUIA_GIT.md y explícame carpeta, repositorio, preparación y commit con mis archivos. Ayúdame a crear el repositorio local, configurar una identidad didáctica y registrar la base. Antes de add comprueba la carpeta y .gitignore. Muéstrame el resultado de status y log y pregúntame qué significa. No publiques ni subas nada.

## Ejecutar la base

Ejecuta el comando de la guía para local_v1 con las herramientas disponibles. Conserva la consola y los archivos reales. Abre informe.md, calidad.json y resumen.json. Distingue 543 líneas históricas de 3 líneas al cierre. Comprueba el cálculo manual de A100. Si falla, explica el diagnóstico sin fabricar una salida.

## Revisar MLOps

Lee pronosticos.csv, reposicion.csv y manifiesto.json. Explica M0, emisión, corte, versión y por qué las 140 unidades se consideran demanda residual en este conjunto sintético. Justifica el tránsito elegible y el estado REVISAR. No interpretes las métricas del libro como métricas de esta corrida.

## Repetir con Docker

Lee Dockerfile, .dockerignore y GUIA_DOCKER.md. Explica qué entra en imagen, qué se monta y dónde se escribe. Si el motor está disponible, usa el ejecutor del paquete para construir, correr docker_v1 y comparar contra local_v1. Si no puedes ejecutar, registra el pendiente y continúa con una repetición local. No presentes Python local como Docker.

## Comparar políticas

Ayúdame a añadir mi equipo al campo proposito de config/escenario_v2.json conservando su explicación. Revisa conmigo el diff, registra ese cambio como segundo commit y ejecuta escenario_v2 con su configuración. Las dos políticas ya están provistas: no atribuyas su creación al alumno. Contrasta pronóstico, inventario, tránsito, margen y propuesta frente a local_v1. Explica por qué 70 pasa a 90. Señala que es contrafactual y no un nuevo cierre operativo de julio.

## Cerrar la entrega

Ayúdame a crear entrega/ y copiar allí PLANTILLA_ENTREGA.md como RESPUESTAS.md. Completemos esa copia a partir de archivos reales y conservemos la plantilla original. Pregúntame las explicaciones personales; no las inventes. Reúne las corridas existentes con scripts/entregar.py y comunica los pendientes sin atribuirme ejecuciones que solo observé.
