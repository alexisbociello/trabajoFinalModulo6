# Preparación para el miércoles 28 de octubre

La actividad dura 90 minutos **con las herramientas instaladas previamente**. Se puede trabajar en equipos con una computadora preparada. No hace falta saber programar ni tener cuenta de GitHub. Reserve tiempo antes de clase para descargar e instalar: Docker puede requerir reinicio o ayuda técnica.

## Qué es cada herramienta

- **Editor:** permite leer y guardar archivos de texto. Puede usar VS Code o el editor que ya utilice. Los `.md` son textos; los `.json` contienen valores y reglas; los `.py` son programas. No editar el JSON con Word.
- **Terminal:** ventana donde escribimos una instrucción y pulsamos Enter. En Windows usaremos PowerShell; en macOS, Terminal. El comando actúa desde una carpeta actual.
- **Python:** ejecuta el programa local y los pequeños ejecutores de la guía.
- **Git:** conserva versiones elegidas de los archivos en esta computadora.
- **Docker Desktop:** mantiene funcionando el motor que construye imágenes y ejecuta contenedores. Tener solo el comando `docker` instalado no prueba que el motor funcione.
- **Prism/PDF:** contiene el material de estudio. Los comandos de Git, Python y Docker van en la terminal de la computadora, no en el documento LaTeX, el chat ni un intérprete con el símbolo `>>>`.

## 1. Instalar si falta

Use los sitios oficiales y la opción correspondiente a su sistema:

1. [Python](https://www.python.org/downloads/): versión 3.11 o posterior. En Windows habilite la opción de añadir Python a PATH si el instalador la ofrece. Cierre y abra de nuevo la terminal tras instalar.
2. [Git](https://git-scm.com/install/): en Windows, Git for Windows. En macOS, `git --version` puede ofrecer las herramientas de línea de comandos de Apple; complete esa instalación antes del encuentro.
3. [Docker Desktop](https://docs.docker.com/get-started/get-docker/): elija Windows o Mac; para Mac distinga Apple silicon e Intel. En Windows revise los requisitos de virtualización/WSL 2 del instalador oficial y use contenedores Linux. En un equipo institucional, pida ayuda si faltan permisos o requisitos. Abra Docker Desktop y espere a que el motor esté listo.

No se requiere cuenta de nube para esta actividad. Si una instalación no se completa, avise antes de clase y trabaje con una computadora preparada. No dedique los 90 minutos a resolver infraestructura.

## 2. Extraer y abrir la carpeta correcta

1. Extraiga el ZIP: Windows, clic derecho → **Extraer todo**; macOS, doble clic.
2. Entre a `RedNova_Clase08`. Debe ver `README_INICIO.md`, `Dockerfile`, `datos`, `config`, `src` y `scripts`. A veces la extracción crea una carpeta exterior adicional: entre hasta ver esos archivos.
3. Windows: en esa carpeta, clic derecho → **Abrir en Terminal** (PowerShell). Alternativa: escriba `powershell` en la barra de direcciones del Explorador y Enter.
4. macOS: abra Terminal, escriba `cd ` (incluya el espacio), arrastre desde Finder la carpeta `RedNova_Clase08` a la ventana y pulse Enter. Si ya abrió la carpeta en un editor con terminal integrada, use esa terminal.
5. Compruebe `pwd` y luego `ls` (ambos funcionan en PowerShell y macOS). Deben mostrar la ruta y los archivos anteriores. `cd` cambia de carpeta; `pwd` muestra dónde está; `ls` muestra su contenido. Si copia una ruta manualmente use comillas dobles cuando haya espacios.

## 3. Verificar antes de ejecutar

Escriba una línea por vez. No copie símbolos de invitación como `$`, `PS>` ni `>>>`.

```text
git --version
docker version
```

Git debe mostrar una versión. Docker debe mostrar **Client y Server**. Si aparece Client pero un error de conexión, abra Docker Desktop y espere; instalar el cliente no basta.

Para Python, en macOS/Linux:

```text
python3 --version
python3 scripts/ejecutar.py comprobar
```

En Windows pruebe:

```text
py -3 --version
py -3 scripts/ejecutar.py comprobar
```

Si Windows reconoce `python` en lugar de `py -3`, use `python`. **Toda la guía usa `python3`: en Windows sustituya ese comienzo por `py -3` o `python`, según lo que verificó.** No cambie el resto del comando. No hay que instalar bibliotecas externas de Python.

## 4. Preparar Docker con tiempo

```text
python3 scripts/ejecutar.py construir
```

La primera vez puede descargar la imagen oficial de Python y necesita Internet. Espere a que termine y lea si terminó correctamente. Esta construcción no ejecuta todavía las ventas. En clase se podrá repetir la construcción; Docker reutiliza capas cuando corresponde.

Si el motor no funciona, puede hacer Git y el cálculo local. Docker quedará **pendiente** o **observado en el equipo docente**, según lo que realmente ocurra. Una ejecución local no se presenta como Docker.

## Lista de llegada

- [ ] ZIP extraído y carpeta correcta abierta.
- [ ] Git muestra versión.
- [ ] Python 3.11+ funciona y sé qué comando usar.
- [ ] Docker Desktop abierto; `docker version` muestra Server.
- [ ] Imagen construida o dificultad avisada al docente.
- [ ] Puedo abrir y guardar un archivo de texto sin cambiar su extensión.
