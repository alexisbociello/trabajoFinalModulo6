#!/usr/bin/env python3
"""Reune codigo, datos y corridas indicadas en un ZIP local; no envia nada."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import sys
import zipfile
import subprocess

from ejecutar import git_state

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--nombre', required=True, help='Identificador del equipo, sin espacios.')
    parser.add_argument('--corridas', nargs='+', required=True, help='Nombres de las carpetas de salidas/.')
    args = parser.parse_args()
    try:
        for name in [args.nombre] + args.corridas:
            if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}', name):
                raise ValueError('Use nombres de hasta 64 letras ASCII, numeros, guion o guion bajo.')
        files = set()
        for name in args.corridas:
            path = ROOT / 'salidas' / name
            if not path.is_dir():
                raise ValueError('No existe la corrida ' + name)
            if not (path / 'ejecucion.json').is_file():
                raise ValueError('Falta evidencia de ejecucion en ' + name)
            files.update(p for p in path.rglob('*') if p.is_file())
        for directory in ['src', 'datos', 'config', 'scripts', 'tests', 'entrega']:
            files.update(p for p in (ROOT / directory).rglob('*') if p.is_file()
                         and '__pycache__' not in p.parts and p.suffix != '.pyc')
        for name in ['Dockerfile', '.dockerignore', '.gitignore', 'requirements.lock', 'README_INICIO.md',
                     'GUIA_DOCKER.md', 'GUIA_GIT.md', 'CONTRATO_DATOS.md', 'PLANTILLA_ENTREGA.md',
                     'CONSIGNA_ETAPAS.md', 'PROMPTS_PARA_LA_PRACTICA.md', 'PREPARACION_ANTES_DE_CLASE.md']:
            path = ROOT / name
            if path.is_file():
                files.add(path)
        # Conservar tambien construcciones, incluidas las fallidas, sin confundirlas con corridas.
        for build_dir in (ROOT / 'salidas').glob('construccion_*'):
            if build_dir.is_dir():
                files.update(p for p in build_dir.rglob('*') if p.is_file())
        # Comparaciones explicitas guardadas en la raiz de salidas/.
        files.update((ROOT / 'salidas').glob('comparacion*.json'))
        dest = ROOT / 'entregas' / (args.nombre + '.zip')
        dest.parent.mkdir(exist_ok=True)
        # Validar antes de crear el ZIP para no dejar una entrega parcial por un enlace.
        for path in files:
            if path.is_symlink():
                raise ValueError('No se admiten enlaces simbolicos en una entrega.')
        git = git_state()
        history = ''
        if git['disponible'] and git.get('commit'):
            observed = subprocess.run(['git', '--no-pager', 'log', '--oneline', '--decorate', '--all'],
                                      cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace', check=False)
            history = observed.stdout
            git['historial_codigo_salida'] = observed.returncode
        # No se copia .git: puede contener configuracion local y referencias ajenas al ejercicio.
        with zipfile.ZipFile(dest, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(files):
                archive.write(path, arcname=Path(args.nombre) / path.relative_to(ROOT))
            archive.writestr(args.nombre + '/evidencia_git/estado.json',
                             json.dumps(git, ensure_ascii=False, indent=2) + '\n')
            archive.writestr(args.nombre + '/evidencia_git/historial.txt', history or 'No hay commits verificables. Revisar estado.json.\n')
        print('ZIP creado:', dest.relative_to(ROOT))
        print('Incluye', len(files) + 2, 'archivos. Revise que la plantilla de entrega este completa.')
        return 0
    except (OSError, ValueError) as exc:
        print('ERROR:', exc, file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
