FROM python:3.12-slim@sha256:aa943ce411423c7582288f18707ff66eddcbaeb510502d747a72aeb34f30d159
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY pipeline.py /app/pipeline.py
COPY datos/ventas_original.csv /app/datos/ventas_original.csv
COPY politicas/politica_margen_v1.md politicas/politica_margen_v2.md /app/politicas/
USER 1000:1000
ENTRYPOINT ["python", "/app/pipeline.py"]
