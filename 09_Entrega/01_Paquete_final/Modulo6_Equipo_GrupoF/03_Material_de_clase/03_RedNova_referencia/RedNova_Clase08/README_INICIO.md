# RedNova — práctica de Ingeniería de Datos y MLOps

**Edición para estudiantes · Clase 08 · Miércoles 28/10/2026.** Comience por `PREPARACION_ANTES_DE_CLASE.md` y siga la guía PDF en `material/Clase_08_Miercoles_Docker_del_Pipeline.pdf`. Complete una copia de la plantilla de entrega con sus propias respuestas.

Este paquete implementa una porción pequeña del caso de la clase 07. Todos los datos son sintéticos: una sucursal (S03), tres productos y un histórico de enero a junio de 2025. Las fechas de negocio son simuladas. El paquete está completo; no necesita recuperar trabajos de clases anteriores.

**Objetivo:** convertir archivos de origen en resultados comprobables, evaluar un modelo candidato, conservar versiones y ejecutar el mismo cálculo dentro de Docker.

## 1. Preparación antes de la clase

Lea primero `PREPARACION_ANTES_DE_CLASE.md`: explica instalación, terminal y carpeta paso a paso. La sesión de 90 minutos supone las herramientas ya preparadas.

1. Descomprima el ZIP en una carpeta de trabajo. No ejecute dentro del ZIP.
2. Abra una terminal en la carpeta `RedNova_Clase08`, donde están `Dockerfile` y este documento.
3. Use Python 3.11 o posterior y Git. En macOS/Linux se escribe `python3`; en Windows pruebe `py -3` o `python`.
4. Para la etapa Docker, abra Docker Desktop. No se requieren cuentas de nube, API, contraseñas ni paquetes de Python adicionales.

Los comandos siguientes usan `python3`. En Windows sustitúyalo por `py -3` o `python`, según lo comprobado. Ejecute una línea por vez en la terminal desde `RedNova_Clase08`, no en Prism ni en el chat.

```text
python3 scripts/ejecutar.py comprobar
```

Si Python funciona pero el motor Docker no responde, puede avanzar con las etapas locales. Una ejecución Python no acredita una ejecución Docker. Para esa etapa, abra Docker Desktop o registre explícitamente la demostración observada del docente.

## 2. Git: registrar la base

Lea `GUIA_GIT.md`, que explica cada término y comando. Git conserva versiones locales; no se requiere GitHub.

```text
git init
git config user.name "Equipo01"
git config user.email "equipo01@example.invalid"
git status
git add .
git diff --cached --stat
git commit -m "Base RedNova para clase 08"
git log --oneline -3
git status
```

La identidad es ficticia y local. Revise que se registra únicamente el proyecto. Debe quedar un commit y árbol limpio. El `.gitignore` suministrado separa resultados y material de lectura del código, configuraciones y datos sintéticos que sí versionamos. Guardar un archivo, hacer un commit y ejecutar Python son acciones distintas.

## 3. Ingeniería de Datos: ejecutar y revisar

```text
python3 scripts/ejecutar.py local --nombre local_v1
```

Abra `salidas/local_v1/resultados/`. Lea primero `informe.md` y `resumen.json`. Revise después `calidad.json`, `ventas_diarias.csv`, `pronosticos.csv` y `reposicion.csv`.

El programa valida contratos, integra fuentes sin multiplicar ventas, aplica costos por fecha, calcula un pronóstico M0 de siete días y produce una propuesta de reposición. Los originales permanecen en `datos/`; las salidas van a otra carpeta.

Para el cierre de S03 del 30/06/2025 debe poder reconstruir estas cifras:

| Producto | Unidades | Venta neta | Costo | Margen |
|---|---:|---:|---:|---:|
| A100 | 20 | 900 | 600 | 300 |
| B200 | 5 | 1000 | 750 | 250 |
| C300 | 2 | 1000 | 800 | 200 |
| **Total** | **27** | **2900** | **2150** | **750** |

El margen global es `750 / 2900 × 100 = 25,86 %`. El descuento de A100 es **100 UM por línea**, no un porcentaje ni 100 por unidad. El histórico completo contiene otras fechas; no confunda su total acumulado con este cierre diario.

## 4. MLOps: leer la evidencia; entrenamiento como ampliación

Durante la clase, revise primero el pronóstico M0, su corte, su versión y el manifiesto. El entrenamiento M1 es una ampliación para después de la práctica o una demostración breve del docente si hay tiempo:

```text
python3 scripts/ejecutar.py mlops --nombre mlops_v1
```

Revise los archivos generados en `salidas/mlops_v1/resultados/`: `modelo_m1.json`, `metricas.json`, `predicciones_evaluacion.csv`, `particiones.csv`, `manifiesto.json` y `decision_modelo.md`. El entrenamiento usa pasado, la validación permite comparar y la prueba final queda separada por fecha. Las ventanas objetivo de siete días no deben cruzar las fronteras de las particiones.

M0 es la referencia simple que utiliza la suma de los últimos siete días completos. M1 es un candidato didáctico de regresión lineal. Su existencia no significa que deba adoptarse: compare errores, compruebe qué información estaba disponible y explique la decisión. Este ejercicio no modifica automáticamente el modelo aprobado de reposición, que sigue siendo M0.

Las métricas de esta ejecución corresponden a los datos sintéticos incluidos. Los cuatro ejemplos numéricos del libro son ejercicios independientes; no son resultados de entrenamiento de este paquete.

## 5. Reproducibilidad: construir y ejecutar Docker

La primera construcción puede descargar la imagen oficial de Python y necesita Internet. La ejecución posterior del pipeline usa `--network none`.

```text
python3 scripts/ejecutar.py construir
python3 scripts/ejecutar.py docker --nombre docker_v1
python3 scripts/comparar.py salidas/local_v1 salidas/docker_v1 --salida salidas/comparacion_local_docker.json
```

`reproducibilidad_comprobada: true` y `contraste_local_docker: true` deben aparecer en esta comparación. El primer campo exige ejecuciones exitosas, entradas intactas, misma configuración y coincidencia de los archivos de negocio. Si aparece `false`, revise las diferencias; no declare equivalencia.

Los manifiestos pueden diferir en hora real, ruta, sistema operativo y versión de Python. Esas diferencias se conservan, pero no se usan para exigir igualdad byte por byte de metadatos de ejecución.

### Si Docker no funciona en su equipo

Antes de editar la configuración de la etapa 6, repita localmente y compare:

```text
python3 scripts/ejecutar.py local --nombre local_repetida
python3 scripts/comparar.py salidas/local_v1 salidas/local_repetida --salida salidas/comparacion_local_local.json
```

Puede dar `reproducibilidad_comprobada: true`, pero `contraste_local_docker: false`: se compararon dos ejecuciones locales. Registre Docker como pendiente o como demostración docente observada, según corresponda. Esta alternativa permite continuar la actividad.

## 6. Versiones: documentar y comparar una política provista

Las políticas v1 y v2 ya vienen en el paquete. Abra `config/escenario_v2.json`, añada ` Equipo01.` al final del valor `proposito` (dentro de las comillas, conservando la explicación existente) y guarde. Esta anotación identifica el trabajo del equipo; no cambia la fórmula. Siga `GUIA_GIT.md`:

```text
git diff -- config/escenario_v2.json
git add config/escenario_v2.json
git diff --cached -- config/escenario_v2.json
git commit -m "Documenta escenario v2: seguridad de 2 a 3 dias"
git log --oneline -3
git status

python3 scripts/ejecutar.py local --nombre escenario_v2 --config config/escenario_v2.json
```

Compare `reposicion.csv` de `local_v1` con el de `escenario_v2`. Es un **escenario contrafactual**: mantiene las entradas y aumenta los días de seguridad de dos a tres. No representa un cierre real del día siguiente ni una nueva demanda observada. Ventas y márgenes no deberían cambiar por este cambio de política. Las propuestas esperadas pasan de (70, 0, 8) a (90, 0, 10) para A100, B200 y C300. El historial debe mostrar los dos commits.

La política v1 corresponde a decisiones hasta el 30/06/2025; v2 rige desde el 01/07/2025. El escenario alternativo queda marcado como tal para que el cambio aislado no se confunda con una aplicación operativa fuera de vigencia.

## 7. Evidencia y entrega

Cada ejecución del ejecutor crea una carpeta nueva:

- `resultados/`: los productos del programa.
- `ejecucion.json`: comando, modo real, código de salida, hashes de entradas, entorno observado y estado/commit Git al inicio y al final.
- `consola.txt`: salida real de la ejecución.

Un nombre de corrida existente se rechaza. Para repetir, use otro nombre, por ejemplo `local_v1_repeticion`. No borre una corrida para ocultar un fallo.

Cree la carpeta `entrega/` con el explorador. Copie allí `PLANTILLA_ENTREGA.md` como `RESPUESTAS.md` y complete sus respuestas. Guarde allí también observaciones propias antes de generar el ZIP. No edite los registros automáticos.

```text
python3 scripts/entregar.py --nombre Equipo01 --corridas local_v1 docker_v1 escenario_v2
```

Si Docker quedó pendiente y realizó la repetición local, use esta alternativa:

```text
python3 scripts/entregar.py --nombre Equipo01 --corridas local_v1 local_repetida escenario_v2
```

Use solo nombres de corridas existentes y terminadas; registre aparte cualquier intento fallido que también decida incluir. Para volver a generar una entrega, elija otro nombre, por ejemplo `Equipo01_revision2`: un ZIP existente no se sobrescribe.

Si completó la ampliación M1, agregue `mlops_v1` a la lista de corridas. Se crea `entregas/Equipo01.zip`. El comando no envía ni publica archivos. Incluye los registros de construcción Docker, la comparación y `evidencia_git/estado.json` e `historial.txt`. La carpeta `.git` permanece en su computadora; el ZIP guarda evidencia del historial, no un repositorio completo restaurable. Si una etapa fue demostración docente, registre quién la ejecutó y qué verificó usted; no la atribuya a su equipo.

## Archivos que conviene reconocer

| Ruta | Función |
|---|---|
| `datos/` | Fuentes sintéticas conservadas. |
| `config/ejecucion.json` | Corte, fecha y política del caso principal. |
| `config/escenario_v2.json` | Cambio controlado de política. |
| `src/` | Código que valida, integra, pronostica y calcula. |
| `tests/` | Pruebas del programa y sus bloqueos. |
| `Dockerfile` | Define el programa y entorno de la imagen. |
| `.dockerignore` | Excluye datos, salidas y archivos ajenos del contexto. |
| `requirements.lock` | Declara que no hay dependencias externas. |
| `CONTRATO_DATOS.md` | Columnas, claves, unidades y reglas. |
| `PREPARACION_ANTES_DE_CLASE.md` | Instalación, terminal y verificación previas. |
| `GUIA_GIT.md`, `.gitignore` | Versiones paso a paso y exclusiones de Git. |
| `GUIA_DOCKER.md` | Explicación de imagen, montajes, permisos y evidencia. |
| `salidas/` | Corridas nuevas y registros de construcción. |

**Alcance:** se producen propuestas revisables, no pedidos a proveedores. Los datos sintéticos sirven para aprender y probar el flujo; no prueban desempeño de un sistema comercial real.
