# Git desde cero: dos versiones explicables

Git registra versiones que **usted decide guardar**. Guardar un archivo en el editor cambia el archivo; `git commit` registra una versión en el historial. Git funciona localmente: esta práctica no usa GitHub, cuentas, `push` ni servidores remotos; tampoco requiere crear ramas adicionales.

## Vocabulario con nuestro proyecto

| Concepto | Significado |
|---|---|
| Carpeta de trabajo | Archivos que estamos viendo y editando en `RedNova_Clase08`. |
| Repositorio | Esa carpeta junto a la carpeta oculta `.git`, donde Git guarda el historial. |
| Área de preparación | Selección de cambios que formarán el próximo commit; `git add` los prepara. |
| Commit | Versión registrada con un mensaje y un identificador. No se crea en cada guardado. |
| Hash de commit | Identificador que devuelve Git; será distinto en cada equipo. No copiar el hash de otro. |
| `.gitignore` | Lista de archivos que no queremos incorporar al seguimiento de Git. No borra esos archivos. |

Flujo: **editar y guardar → revisar diferencias → preparar con add → registrar con commit → consultar log**.

## 1. Registrar el punto de partida (8–23 minutos)

En la terminal, desde la carpeta que contiene `Dockerfile`, ejecute:

```text
git --version
git init
git config user.name "Equipo01"
git config user.email "equipo01@example.invalid"
git status
git add .
git diff --cached --stat
git commit -m "Base RedNova para clase 08"
git log --oneline -3
git status
```

Sustituya Equipo01 por su equipo. El correo es un identificador **ficticio para este ejercicio local**; no se envía correo ni se crea una cuenta. La configuración se aplica a este repositorio porque no usamos `--global`. Si su repositorio ya tiene una identidad que desea conservar, no necesita reemplazarla.

Qué hace cada línea:

1. `git init` inicia el historial de esta carpeta; no descarga nada. La rama inicial puede llamarse main o master: no importa para esta práctica.
2. `git config` indica quién firma los commits locales. Git no verifica que una identidad sea real.
3. `git status` muestra cambios sin registrar. Al comienzo verá archivos sin seguimiento.
4. `git add .` prepara todos los archivos no ignorados de esta carpeta y sus subcarpetas. El punto significa «desde aquí». Por eso debe comprobar antes que está en `RedNova_Clase08`.
5. `git diff --cached --stat` resume lo que va a registrar. No continúe si ve archivos personales ajenos a la práctica.
6. `git commit -m ...` registra la base. Las comillas mantienen el mensaje unido y `-m` evita abrir otro editor.
7. `git log --oneline -3` muestra hasta tres commits; ahora debe mostrar uno. Si abre un visor, la tecla `q` permite salir.
8. `git status` debe indicar árbol limpio, por ejemplo `nothing to commit, working tree clean`.

El paquete incluye `.gitignore`: excluye salidas, entregas, documentos de lectura y temporales. **Código, configuración y estos datos sintéticos pequeños sí se registran**. Para datos reales, grandes o reservados habría que diseñar otra estrategia. `.dockerignore` tiene otra función: limita lo que se envía a la construcción de la imagen; no controla Git.

## 2. Ejecutar sin confundir guardado y ejecución

Siga la guía para `local_v1` y `docker_v1`. Un commit no ejecuta Python ni Docker. Los ejecutores registran el commit y el estado de Git observados, además de las huellas de archivos. Las corridas se conservan en `salidas/`, fuera de Git, y se incorporan al ZIP final mediante el ejecutor de entrega.

```text
git status
```

Después de ejecutar, debe seguir limpio si no editó archivos seguidos. Un árbol limpio no significa «no hay salidas»: significa «no hay cambios pendientes ni archivos nuevos sin seguimiento, salvo los ignorados».

## 3. Registrar una segunda versión (68–82 minutos)

El paquete **ya trae** la política v1 (seguridad de 2 días), la v2 (3 días) y la configuración que selecciona cada una. El alumno documentará el escenario y lo ejecutará; no afirmará haber creado esas políticas.

1. Abra `config/escenario_v2.json` en el editor.
2. Localice la línea `"proposito": "..."`. Conserve el texto y agregue ` Equipo01.` dentro de las comillas finales del valor. Es una anotación, no un cambio de cálculo.
3. Guarde. No quite comillas, comas ni llaves, y conserve la extensión `.json`.
4. Revise y registre:

```text
git diff -- config/escenario_v2.json
git status
git add config/escenario_v2.json
git diff --cached -- config/escenario_v2.json
git commit -m "Documenta escenario v2: seguridad de 2 a 3 dias"
git log --oneline -3
git status
python3 scripts/ejecutar.py local --nombre escenario_v2 --config config/escenario_v2.json
```

En el diff, `-` muestra el texto anterior y `+` el nuevo. No escriba esos signos en el archivo. Antes de `add`, `git diff` muestra el cambio guardado; después, `git diff --cached` muestra el cambio preparado. Tras el commit, el historial debe tener **dos commits** y el árbol quedar limpio. El cambio de propósito altera la huella del archivo de configuración, pero no la fórmula ni los datos.

La corrida v2 selecciona la política ya suministrada de tres días: A100 pasa de 70 a 90, C300 de 8 a 10, B200 sigue en 0. Ventas, costos y márgenes se mantienen. La prueba es contrafactual: no es una observación del día siguiente.

Opcional: para leer qué cambia entre las políticas provistas:

```text
git diff --no-index -- config/politica_reposicion.json config/politica_reposicion_v2.json
```

`--no-index` compara dos archivos, incluso sin historial. Un código de salida 1 significa que encontró diferencias; no es un fallo. Cambian también identificador y vigencia para describir v2. El supuesto de demanda y la entrada histórica se mantienen.

## 4. Evidencia y errores frecuentes

La entrega conserva una instantánea del historial y del estado de Git; la carpeta oculta `.git` permanece en su computadora. El ZIP de entrega no equivale a una copia íntegra del repositorio con historial restaurable.

| Situación | Cómo continuar |
|---|---|
| `git` no se reconoce | Complete la instalación y abra una terminal nueva. |
| `not a git repository` | Verifique `pwd`/`ls`; ejecute `git init` únicamente en la carpeta de la práctica. |
| `Author identity unknown` | Ejecute las dos líneas `git config` anteriores y repita el commit. |
| `nothing to commit` al segundo commit | Compruebe que guardó el cambio en `proposito` y preparó ese archivo. No fabrique otro cambio para esconder el problema. |
| Diff vacío tras `git add` | Use `git diff --cached`; el cambio ya pasó al área de preparación. |
| Aviso LF/CRLF | Es un aviso sobre finales de línea entre sistemas; normalmente no impide continuar. No cambie ajustes globales por este aviso. |
| Se abrió un visor de historial | Pulse `q` para volver a la terminal. |
| JSON inválido tras editar | Revise comillas y comas con el docente; no sustituya los resultados calculados. |

Para explicar al cierre: ¿qué diferencia hay entre guardar, hacer `add`, hacer `commit` y ejecutar el programa? ¿Qué identifica el commit y qué identifican las huellas de datos?

Referencia: [tutorial oficial de Git](https://git-scm.com/docs/gittutorial). Consulta: 27/10/2026.
