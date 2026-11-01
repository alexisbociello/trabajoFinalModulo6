# Imagen oficial. La etiqueta es mutable; el ejecutor registra el ID observado.
FROM python:3.12-slim
ARG SOURCE_SHA256=sin_registrar
LABEL org.rednova.source_sha256=$SOURCE_SHA256
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=0
# Permisos explicitos dentro de la imagen: el ZIP puede extraerse con archivos privados.
# Sin pip: el proyecto utiliza exclusivamente la biblioteca estandar.
COPY --chmod=644 requirements.lock /app/requirements.lock
COPY --chmod=755 src/ /app/src/
USER 10001:10001
ENTRYPOINT ["python", "-m", "src.pipeline"]
CMD ["--datos", "/datos", "--config", "/config/ejecucion.json", "--salida", "/salida/resultados"]
