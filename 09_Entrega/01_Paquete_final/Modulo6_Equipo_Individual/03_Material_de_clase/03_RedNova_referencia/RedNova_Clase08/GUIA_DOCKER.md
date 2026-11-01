# Docker desde cero en esta práctica

## Cuatro ideas antes de escribir comandos

1. **Dockerfile = receta.** Es un archivo de texto que indica el entorno y el programa que se prepararán.
2. **Imagen = paquete preparado.** `construir` lee la receta y crea una imagen con Python y el código. Construir no ejecuta el cálculo de ventas.
3. **Contenedor = una ejecución.** `docker` inicia una ejecución de esa imagen, calcula y termina. Cada nueva corrida usa un nombre nuevo.
4. **Montaje = carpeta accesible desde el contenedor.** `/datos` es cómo el contenedor ve `datos/` en la computadora. No hay que crear una carpeta `/datos` en el disco. `readonly` permite leer esas entradas, mientras que la carpeta de salida sí admite escritura.

Docker Desktop es la aplicación que mantiene el motor disponible. Escribimos las órdenes en la terminal de la computadora desde `RedNova_Clase08`, no en un chat ni dentro de Docker Desktop. En esta actividad Python local inicia el ejecutor; el cálculo de la modalidad Docker lo realiza Python dentro del contenedor.

## Primer recorrido, una línea por vez

Instale y compruebe las herramientas siguiendo `PREPARACION_ANTES_DE_CLASE.md`. En Windows cambie `python3` por el comando Python que verificó.

```text
docker version
python3 scripts/ejecutar.py construir
python3 scripts/ejecutar.py docker --nombre docker_v1
python3 scripts/comparar.py salidas/local_v1 salidas/docker_v1 --salida salidas/comparacion_local_docker.json
```

- `docker version`: deben responder Client y Server.
- `construir`: espere el fin de la descarga/construcción; se guarda `salidas/construccion_FECHA/construccion.json`. Debe tener código de salida 0 e ID real de imagen.
- `docker --nombre docker_v1`: debe terminar con código 0; abra `salidas/docker_v1/resultados/informe.md`. El nombre `docker_v1` es la carpeta de evidencia, no el nombre de la imagen.
- `comparar`: requiere que primero haya ejecutado `local_v1` con la misma base. Deben aparecer `reproducibilidad_comprobada: true` y `contraste_local_docker: true`. Haga esta comparación **antes** de editar la configuración del escenario v2.

El ejecutor (`scripts/ejecutar.py`) es un programa corto que prepara rutas y argumentos. No oculta la orden utilizada: abra `comando` en `ejecucion.json` para leer el `docker run` real. Así no necesitamos escribir montajes largos distintos para Windows y Mac.

Al finalizar, el contenedor desaparece por `--rm`, pero la imagen continúa disponible y los resultados permanecen en la carpeta montada. No hay un sitio web que abrir: este programa procesa archivos y termina. Docker no guarda automáticamente el historial de cambios; para eso usamos Git.

## Si el motor sigue sin responder

Conserve el mensaje y declare Docker pendiente, o registre la demostración docente observada. Para ensayar la comparación sin contenedores, después de `local_v1` y antes de editar el escenario v2:

```text
python3 scripts/ejecutar.py local --nombre local_repetida
python3 scripts/comparar.py salidas/local_v1 salidas/local_repetida --salida salidas/comparacion_local_local.json
```

La coincidencia puede ser verdadera, pero `contraste_local_docker` será `false`, porque ambas corridas son locales. En la entrega use `local_repetida` en lugar de una carpeta `docker_v1` que no se haya ejecutado. No reutilice el nombre de una corrida fallida.

## Qué empaqueta la imagen

El `Dockerfile` parte de la imagen oficial `python:3.12-slim`, crea `/app` y copia únicamente el código `src/` y la declaración de dependencias. No copia los datos ni las políticas. El cálculo recibe esos archivos en el momento de ejecutar.

| Instrucción | Significado en el caso |
|---|---|
| `FROM python:3.12-slim` | Entorno Python oficial; su etiqueta puede cambiar con el tiempo. |
| `ARG SOURCE_SHA256` y `LABEL` | Registran la huella del código que el ejecutor realmente calculó al construir. |
| `WORKDIR /app` | Carpeta desde la que se ejecuta el programa. |
| `ENV ...` | Evita escritura de bytecode y normaliza opciones del intérprete. |
| `COPY --chmod=644 requirements.lock ...` | Conserva la declaración de que no hay paquetes externos. |
| `COPY --chmod=755 src/ ...` | Incluye el código y permite que el usuario del contenedor lea los archivos y recorra las carpetas; no copia fuentes de negocio ni cambia permisos del anfitrión. |
| `USER 10001:10001` | Ejecuta con identificadores sin privilegios de administrador. |
| `ENTRYPOINT ...` | Inicia el módulo `src.pipeline`. |
| `CMD ...` | Proporciona rutas predeterminadas de entradas y salidas. |

`.dockerignore` utiliza una lista permitida. El contexto de construcción contiene solo Dockerfile, `.dockerignore`, requirements y código. `datos/`, `config/`, documentos y corridas quedan fuera de la imagen.

## Cómo se ejecuta

El ejecutor construye un comando `docker run` y lo conserva literalmente en `ejecucion.json`. Utiliza una lista de argumentos del sistema, sin concatenar comandos de shell; así las rutas con espacios funcionan en PowerShell y macOS/Linux.

| Opción | Propósito |
|---|---|
| `--rm` | Elimina el contenedor al terminar; la salida permanece en el montaje. |
| `--network none` | El pipeline no tiene conectividad externa. |
| `--read-only` | La raíz del contenedor no permite escritura. |
| `--cap-drop ALL` | Retira las capacidades Linux adicionales. |
| `--security-opt no-new-privileges:true` | Impide adquirir nuevos privilegios. |
| Montaje `datos/` → `/datos`, `readonly` | Lectura de las fuentes. |
| Montaje `config/` → `/config`, `readonly` | Lectura de la configuración y políticas. |
| Montaje `salidas/NOMBRE` → `/salida` | Única carpeta persistente habilitada para escritura. |

Cada contenedor recibe únicamente la carpeta de su corrida. Las corridas anteriores no se montan. El programa crea `/salida/resultados`, que debe ser una carpeta nueva. No se publican puertos, se montan carpetas personales ni se entrega el socket Docker al contenedor.

En Linux el ejecutor utiliza el UID/GID de la cuenta que lo inicia para que los archivos de salida pertenezcan a esa cuenta; rechaza ejecutar la actividad como root. En Docker Desktop para macOS/Windows utiliza `10001:10001`. Si falla el acceso a un montaje, revise la carpeta compartida y los permisos de la cuenta. No solucione el problema con `chmod 777` o privilegios de administrador.

El montaje de solo lectura protege contra cambios desde el contenedor; no anonimiza el contenido. Estas opciones reducen accesos del proceso; no constituyen una garantía de aislamiento absoluto.

## Construcción, etiqueta, ID y digest

```text
python3 scripts/ejecutar.py construir
```

El ejecutor registra el comando y su salida en `salidas/construccion_FECHA/`. Si la construcción termina correctamente, inspecciona la imagen y conserva su ID, arquitectura, usuario y `RepoDigests` realmente observados. Una imagen construida localmente puede tener `RepoDigests: []`; esa ausencia no es un error y no se completa inventando una referencia.

La etiqueta `rednova-clase08:1.0` es un nombre mutable. Al ejecutar, el programa consulta esa etiqueta y usa el **ID observado** para iniciar el contenedor. Además exige que la huella del código registrada en la imagen coincida con el código actual del paquete. Si cambió `src/`, debe volver a construir.

La base también usa una etiqueta mutable. Una construcción posterior puede incorporar otra revisión de Python o del sistema base. El paquete permite reproducir el cálculo y conserva el entorno observado; no promete reconstrucción binaria idéntica a partir de una etiqueta. Para archivar exactamente una imagen ya construida, puede conservarse con `docker image save` usando su ID real y cargarse con `docker image load`; no es requisito de esta práctica.

La descarga inicial de la base requiere conectividad. `--network none` se aplica a la **ejecución**, no a la adquisición de esa base.

## Estado de verificación del paquete

La revisión del 27/10/2026 ejecutó realmente la construcción y el pipeline Docker en macOS con Apple silicon. Los seis productos de negocio coincidieron con la corrida Python local. Se corrigió un fallo de permisos del código dentro de la imagen mediante `COPY --chmod`; no fue necesario ampliar permisos del anfitrión. La comprobación docente se conserva por separado. En esta edición cada equipo genera y conserva sus propias evidencias.

Esto acredita ese entorno y esas entradas. Cada equipo debe comprobar su instalación, generar sus propias corridas y registrar su modalidad. No se ha realizado una prueba nativa en Windows ni Linux durante esta revisión.

## Qué cuenta como evidencia

- `construccion.json` acredita una construcción solo si su código de salida es cero y tiene un ID observado.
- `ejecucion.json` distingue `local`, `docker` y `mlops`, conserva el código de salida y verifica que las entradas no cambiaron.
- `consola.txt` conserva mensajes y errores reales.
- `resultados/manifiesto.json` describe la corrida del pipeline.
- `git_inicio` y `git_fin` en la corrida registran el commit y el estado del repositorio observado.
- `comparacion_local_docker.json` contrasta los productos concretos, no una captura de comandos.

El comparador exige coincidencia de `calidad.json`, `ventas_diarias.csv`, `pronosticos.csv`, `reposicion.csv`, `resumen.json` e `informe.md`. Compara además las huellas del código y las entradas, y la configuración elegida. Los metadatos que identifican el entorno y la hora se conservan aparte.

## Problemas frecuentes

| Mensaje o situación | Qué hacer |
|---|---|
| `python` no se reconoce | Probar `python3` (macOS/Linux) o `py -3` (Windows). Verificar Python 3.11+. |
| Cliente instalado, servidor no disponible | Abrir Docker Desktop y esperar a que el motor esté listo. |
| No existe la imagen | Ejecutar `construir`. |
| La imagen no corresponde al código actual | Reconstruir después de cambiar `src/`. |
| Corrida ya existe | Elegir un nombre nuevo y conservar la anterior. |
| Fallo en validaciones de datos | Leer el diagnóstico. No cambiar datos originales para forzar éxito. |
| Comparación falsa | Revisar las filas del informe: puede haber diferencias de datos, código o política. |
| Sin Docker durante la clase | Ejecutar lo local y registrar la demostración docente o la etapa pendiente. |

## Documentación oficial consultada

- [Dockerfile: COPY, USER y ENTRYPOINT](https://docs.docker.com/reference/dockerfile/).
- [Ejecución de contenedores y usuario](https://docs.docker.com/engine/containers/run/).
- [Montajes de carpetas y opción readonly](https://docs.docker.com/engine/storage/bind-mounts/).
- [Referencia de docker container run](https://docs.docker.com/reference/cli/docker/container/run/).

Consulta: 27/10/2026. No se requiere estudiar toda la referencia para completar la actividad.
