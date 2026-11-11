# Analista Horizonte — E3

Este agente está implementado como instrucciones de rol para Codex, con fuentes verificadas; no requiere una aplicación ni un proceso autónomo. Para usarlo, aplicar `v2/instrucciones.md`, indicar consulta y fecha simulada y aportar los archivos autorizados de la ejecución correspondiente. No confundir versión de instrucciones con versión de política.

Ver la ficha, matriz de seis consultas y respuestas v1/v2. Las consultas de prueba se tomaron de la ficha suministrada y fueron respondidas por Codex en esta sesión. Las verificaciones con Python fueron efectivamente ejecutadas; las respuestas fueron generadas por Codex. Posteriormente Luis Manuel Morales registró su revisión en los controles E3-C1 a E3-C6 de la matriz aportada; la matriz de consultas enlaza ese registro.

Reproducir la verificación desde la raíz: `python3 04_Trabajo/05_Agente_analista/verificar_fuentes.py`. Este comando recalcula evidencia numérica; no reejecuta un modelo conversacional ni genera respuestas nuevas. Para repetir las pruebas conversacionales hay que presentar los seis pedidos al rol y conservar sus nuevas respuestas.
