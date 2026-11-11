# Reflexión individual - Georgina Sicco
Al repartir las tareas, mi parte fue ejecutar el pipeline y las pruebas, y revisar los resultados. Recalcular V001 y V002 me ayudó a entender por qué el margen global se obtiene dividiendo el margen total por las ventas totales: las operaciones tienen montos distintos, así que promediar sus porcentajes les daría el mismo peso.

Con calculadora comprobé V001: 10×25=250 en ventas, 10×15=150 en costos por lo que obtengo 100 de margen. Para V002: 2×600=1.200 en ventas, 2×420=840 en costos lo que me da 360 de margen. Juntas, suman 1.450 en ventas y 460 de margen (31,72%). Luego comparé los resúmenes v1 y v2: ambos muestran 5.720 en ventas, 4.210 en costos y 1.510 de margen (26,40%); cambia el umbral, de 25% a 30%, y el estado, de "SIN ALERTA" a "ALERTA".

Mi aporte fue correr el pipeline y las pruebas, recalcular esas filas y comparar los resúmenes; no escribí el código base. Algo importante a destacar: Una alerta indica que el resultado cruza una regla definida, pero por sí sola no explica la causa ni demuestra que las ventas hayan bajado, por esto siempre es interesante la revisión humana de la política para poner el resultado en contexto.
