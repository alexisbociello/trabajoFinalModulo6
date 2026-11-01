# Bitácora E4 — Docker

Fecha real: 2026-11-01. Ejecutor: Codex mediante terminal y Docker Desktop local.
Solicitud: «podes avanzar con el siguiente paso doker».

Se preparó paquete autónomo de Horizonte con copias verificadas del script y entradas. Se construyó imagen oficial de Python con base fijada por digest y se ejecutó sin red, como usuario sin privilegios y con sistema de archivos de solo lectura salvo salida montada.

Comando orquestador ejecutado: `python3 04_Trabajo/06_Docker/ejecutar_y_comparar.py`.
Resultado: dos ejecuciones exitosas para 2026-10-18/v1 y 2026-10-19/v2. Seis comparaciones de archivos idénticas byte a byte; original intacto. Python local 3.9.6 frente a Python 3.12.16. Código sin cambios.

Evidencia: `05_Ejecuciones/03_Comparaciones/python_docker_20261101T221330250205Z.json` y `07_Evidencias/03_Consola_y_versiones/docker/20261101T221330250205Z`. Allí figuran comandos, consola, versión, ID de imagen, huellas y parámetros. No hubo fallos funcionales ni se inventaron correcciones. El acceso inicial al socket requirió autorización de herramienta, tras lo cual el motor respondió y todas las operaciones se completaron.

La ejecución fue real en este equipo; no se atribuye revisión humana o ejecución docente. La comparación comprende los casos base de ambas políticas. Pendiente E5: consolidar plan de supervisión, detención y recuperación y documentación final.
