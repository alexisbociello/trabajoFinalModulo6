# Trabajo final — Módulo 6

## Ubicación de cada componente

| Carpeta | Contenido y uso |
|---|---|
| 00_Consigna | Consigna oficial. |
| 01_Original_ventas_PROTEGIDO | Único original de referencia. Archivo sin permiso de escritura y carpeta sin permiso de creación, borrado o renombrado. No trabajar aquí. |
| 02_Insumos | Reglas, contrato, políticas, instrucciones, plantillas y pruebas suministradas. Conservar como referencia. |
| 03_Material_de_clase | Libros, clases y paquetes originales de Semana 2 y RedNova. RedNova es referencia de otro caso; no reemplaza el pipeline Horizonte. |
| 04_Trabajo | Copia de datos, diagnóstico, código, prompts, analista v1/v2, Docker y plan de recuperación. |
| 05_Ejecuciones | Productos Python y Docker, separados por fecha simulada y política; comparaciones. |
| 06_Pruebas | Entradas de prueba, resultados P1–P8, tres detenciones y matriz para completar. |
| 07_Evidencias | Integridad, bitácora, consola, versiones, cálculos, revisión humana y aportes. |
| 08_Informe | Borradores, anexos/reflexiones y PDF final de 4 a 6 páginas sin portada ni anexos. |
| 09_Entrega | Copia seleccionada de productos finales y ZIP Modulo6_Equipo_Nombre.zip. |
| 10_Defensa | Apuntes de preparación para la defensa individual. |
| 11_Entregas_previas_E1_a_E5 | Incorporar trabajos anteriores para reutilizarlos. |

## Empezar

1. Leer consigna, diccionario y contrato.
2. Trabajar sobre `04_Trabajo/01_Copias_de_datos/ventas_trabajo.csv`. No modificar el original.
3. Completar diagnóstico, generar y revisar el pipeline; conservar prompts y revisión.
4. Ejecutar para 2026-10-18 (v1) y 2026-10-19 (v2), guardando tres productos por ejecución y consola.
5. Completar P1–P8 y controles de esquema, ID conflictivo y política faltante.
6. Probar las seis conductas del analista; documentar mejora v2, evidencia y revisión humana.
7. Preparar Docker para Horizonte y comparar con Python, o documentar ejecución docente observada.
8. Documentar supervisión y recuperación; redactar informe, README de reproducción y reflexiones.
9. Armar y revisar el ZIP; preparar defensa individual sin IA.

## Integridad y protección

La huella anterior y posterior al traslado está en `07_Evidencias/01_Integridad_original/integridad_inicial.json`.
Desde esta carpeta raíz, comprobar con:

```sh
shasum -a 256 -c 07_Evidencias/01_Integridad_original/ventas_original.sha256
```

La protección mediante permisos evita cambios accidentales; el propietario puede revertirla. Las copias históricas de Semana 2 se conservan dentro del paquete provisto y no son el original canónico.

## Estado inicial y pendientes

Esta organización no constituye ejecución del trabajo: las carpetas de resultados están vacías y las plantillas no tienen resultados observados.
Se copiaron las cuatro entradas de prueba suministradas a `06_Pruebas/01_Entradas`.
Queda preparar el caso de ID conflictivo y la carpeta de políticas sin cobertura para el control de política faltante.
No se encontraron libro de Semana 5, clases 9–10 ni entregas propias E1–E5.
La matriz suministrada debe ampliarse si es necesario para registrar modalidad de ejecución y ambos casos de frontera de P7.
No sobrescribir ejecuciones: para repeticiones, crear subcarpetas nuevas identificadas (por ejemplo, intento_02).
No usar el paquete RedNova como evidencia de ejecución de Horizonte.

## Repositorio Git

Los archivos `.gitkeep` conservan las carpetas vacías previstas para el trabajo.
Git no conserva permisos de solo lectura. Después de clonar, restaurar la protección local desde la raíz:

```sh
chmod 444 01_Original_ventas_PROTEGIDO/ventas_original.csv
chmod 555 01_Original_ventas_PROTEGIDO
shasum -a 256 -c 07_Evidencias/01_Integridad_original/ventas_original.sha256
```
