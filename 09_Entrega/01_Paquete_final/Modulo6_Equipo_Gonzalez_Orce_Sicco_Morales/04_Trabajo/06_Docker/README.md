# Docker — Comercial Horizonte

## Resultado real

Se construyó y ejecutó este paquete en Docker Desktop local para ambas fechas simuladas. Los tres productos de cada ejecución coinciden byte a byte con Python: ventas_validas.csv, reporte_calidad.json y resumen.json. También coinciden las decisiones de calidad. Original intacto, comprobado mediante SHA-256.

- Motor Docker: 29.5.3; cliente: 29.5.3.
- Python local: 3.9.6; contenedor: Python 3.12.16.
- Contenedor: linux/arm64.
- ID real de imagen: `sha256:8fb7032885bdce8f97c350604168f40ece6cd401da1450024565c0040359e6de`.
- Base oficial fijada mediante digest: `FROM python:3.12-slim@sha256:aa943ce411423c7582288f18707ff66eddcbaeb510502d747a72aeb34f30d159`.
- Ejecutor real: Codex mediante herramientas en este equipo. No es ejecución docente observada.

## Contenido

Dockerfile, pipeline.py (idéntico al script de E2), datos/ventas_original.csv (copia idéntica al original protegido), políticas v1/v2 y .dockerignore. Sin paquetes externos de Python. Docker contiene el pipeline y su entorno; el analista conversacional se usa fuera del contenedor.

## Reproducir automáticamente

Desde la raíz del proyecto:

```sh
python3 04_Trabajo/06_Docker/ejecutar_y_comparar.py
```

Requiere Docker instalado y motor iniciado. La primera construcción puede descargar la imagen oficial; ejecuciones sin red (`--network none`). El procedimiento verifica hashes de código, datos y políticas; construye, captura versiones y comandos, ejecuta ambas fechas, compara los tres productos con las salidas locales y comprueba integridad del original. Cada repetición crea un destino nuevo por marca UTC. No elimina imágenes o contenedores ajenos.

## Construcción y ejecución manual

Desde la raíz:

```sh
docker build --tag horizonte-modulo6:1.0.0 04_Trabajo/06_Docker
mkdir -p 05_Ejecuciones/02_Docker/manual_v1
docker run --rm --network none --read-only --cap-drop ALL --security-opt no-new-privileges --mount "type=bind,src=$(pwd)/05_Ejecuciones/02_Docker/manual_v1,dst=/salidas" horizonte-modulo6:1.0.0 --entrada /app/datos/ventas_original.csv --politicas /app/politicas --fecha-ejecucion 2026-10-18 --salida /salidas/productos
```

Para v2 usar un directorio nuevo y fecha 2026-10-19. El destino productos no debe existir. La imagen ejecuta como usuario 1000:1000; en otros sistemas el directorio montado debe permitir escritura a ese usuario. Solo se monta la carpeta de salida, no el original ni carpetas personales. Los datos se leen desde la imagen.

## Evidencia

Comparación: `05_Ejecuciones/03_Comparaciones/python_docker_20261101T221330250205Z.json`. Logs, comandos y códigos de salida: `07_Evidencias/03_Consola_y_versiones/docker/20261101T221330250205Z`. Cada ejecución se realizó por ID de imagen para identificar exactamente lo ejecutado. Las huellas del paquete y los destinos están en el manifiesto.

Difieren sistema y Python entre host y contenedor; esos metadatos están en el manifiesto, fuera de los tres productos de negocio. Los tres productos no incluyen metadatos variables del sistema y son idénticos. El script no fue modificado para obtener esta igualdad. Esta etapa compara las dos ejecuciones base; P1–P8 y las detenciones se habían probado con Python, no se afirma haber repetido toda la matriz dentro de Docker.
