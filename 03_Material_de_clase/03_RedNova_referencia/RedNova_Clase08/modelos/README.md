# Modelos y evidencia

M0 es la referencia inicial: suma las ventas observadas en los siete días completos anteriores a la emisión, sin quiebres declarados. No tiene parámetros aprendidos ni necesita un archivo binario.

El candidato M1 se entrena mediante el módulo `src.entrenar`; su artefacto JSON y sus métricas se guardan en la carpeta de salida elegida para esa ejecución. Guardar parámetros permite repetir la inferencia y revisar qué versión se utilizó.

La comparación usa datos sintéticos y particiones temporales. La generación del artefacto no implica aprobación para uso operativo ni demuestra superioridad en datos reales. La política inicial mantiene M0 como referencia aprobada para el ejercicio; M1 conserva el estado de candidato hasta revisión humana.

No se incluye un modelo externo descargado ni se requiere cuenta, API o conexión a Internet para entrenar con los archivos suministrados.
