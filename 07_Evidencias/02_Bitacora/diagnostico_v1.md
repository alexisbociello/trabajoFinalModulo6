# Bitácora — diagnóstico v1

- Fecha real UTC: 2026-10-31T15:17:16.677424+00:00.
- Objetivo: diagnosticar las 16 filas de Comercial Horizonte según diccionario y contrato v1.
- Ejecutor: Codex, herramienta de terminal, Python 3.9.6.
- Comando ejecutado: `python3 04_Trabajo/02_Diagnostico/ejecutar_diagnostico.py`.
- Entrada: `04_Trabajo/01_Copias_de_datos/ventas_trabajo.csv`, idéntica al original protegido.
- Productos: `04_Trabajo/02_Diagnostico/diagnostico.md`, `evidencia_diagnostico.json` y script reproducible en esa misma carpeta.
- Resultado observado: 16 leídas, 13 válidas, 3 excluidas (orígenes 14, 15 y 16).
- Detalle: origen 14 duplicado del 5; origen 15 cantidad -2; origen 16 precio vacío.
- Original: SHA-256 antes/después idéntico al registro inicial; no alterado.
- Verificación adicional del agente: correspondencia exacta de las tres exclusiones y referencia al origen 5 confirmadas mediante aserciones.
- Consola: `07_Evidencias/03_Consola_y_versiones/diagnostico_v1_consola.json`.
- Revisión humana: pendiente. Los ejemplos del diagnóstico fueron preparados por el agente; no constituyen comprobación manual del estudiante.
- Siguiente paso: revisión humana del diagnóstico y generación del pipeline de cuatro bloques. Las pruebas completas y la evaluación de políticas siguen pendientes.
