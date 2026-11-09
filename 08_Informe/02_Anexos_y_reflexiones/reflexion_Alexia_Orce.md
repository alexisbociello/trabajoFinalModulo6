# Reflexión individual - Alexia Orce

Para mi revisión decidí ejecutar el programa con dos fechas simuladas y mantener el mismo archivo de ventas. Quería ver qué pasaba con la alerta cuando cambiaba el umbral de la política y los datos de entrada seguían siendo los mismos.

Ejecuté el programa desde la terminal de Visual Studio Code. Usé Codex como guía para preparar los comandos, interpretar las salidas y redactar esta reflexión. En ambas ejecuciones observé ventas de 5.720 UM, costos de 4.210 UM y un margen de 1.510 UM, equivalente al 26,40 %. Con la política v1, que alerta por debajo del 25 %, el total quedó «SIN ALERTA». Con la política v2, que alerta por debajo del 30 %, el mismo total quedó en «ALERTA».

Mi aporte concreto fue realizar las dos ejecuciones y revisar el resultado global. La comparación me permitió entender por qué conviene mirar qué política se aplicó antes de interpretar una alerta como señal de que empeoraron las ventas. Mi comprobación se limita a estas dos ejecuciones con los datos del caso. Para evaluar cómo responde el programa ante otros datos o justo en el umbral, se necesitan pruebas adicionales.
