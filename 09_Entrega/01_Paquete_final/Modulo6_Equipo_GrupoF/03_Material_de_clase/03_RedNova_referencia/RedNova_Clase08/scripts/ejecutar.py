#!/usr/bin/env python3
"""Ejecutar RedNova con rutas delimitadas; solo usa la biblioteca estandar."""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
IMAGE = 'rednova-clase08:1.0'


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def run(command, *, capture=True):
    return subprocess.run(command, cwd=ROOT, text=True, encoding='utf-8', errors='replace',
                          stdout=subprocess.PIPE if capture else None,
                          stderr=subprocess.STDOUT if capture else None, check=False)


def git_state():
    """Identidad del repositorio del caso, sin tomar un repositorio padre por error."""
    if not shutil.which('git'):
        return {'disponible': False, 'motivo': 'Git no esta instalado o no esta en PATH.'}
    located = run(['git', 'rev-parse', '--show-toplevel'])
    if located.returncode or Path(located.stdout.strip()).resolve() != ROOT.resolve():
        return {'disponible': False, 'motivo': 'Esta carpeta no tiene su propio repositorio Git. Ejecute git init aqui.'}
    head = run(['git', 'rev-parse', '--verify', 'HEAD'])
    status = run(['git', 'status', '--porcelain=v1', '--untracked-files=normal'])
    branch = run(['git', 'branch', '--show-current'])
    return {'disponible': True, 'commit': head.stdout.strip() if head.returncode == 0 else None,
            'rama': branch.stdout.strip(), 'estado_corto': status.stdout,
            'arbol_limpio': status.returncode == 0 and not status.stdout.strip()}


def docker_ready():
    if not shutil.which('docker'):
        raise ValueError('Docker no esta instalado o no esta en PATH. Puede ejecutar la ruta local.')
    result = run(['docker', 'version', '--format', '{{json .}}'])
    if result.returncode:
        raise ValueError('El motor Docker no responde. Abra Docker Desktop y espere a que este listo.\n' + result.stdout)
    payload = json.loads(result.stdout)
    if not payload.get('Server'):
        raise ValueError('Hay cliente Docker, pero no hay servidor disponible.')
    server = payload['Server']
    if server.get('Os', 'linux') != 'linux':
        raise ValueError('Este paquete requiere contenedores Linux. Seleccionelos en Docker Desktop.')
    return payload


def image_metadata(image):
    result = run(['docker', 'image', 'inspect', image])
    if result.returncode:
        raise ValueError('No existe la imagen indicada. Ejecute primero: python scripts/ejecutar.py construir')
    item = json.loads(result.stdout)[0]
    return {
        'etiqueta_solicitada': image, 'id': item['Id'], 'repo_digests': item.get('RepoDigests', []),
        'arquitectura': item.get('Architecture'), 'os': item.get('Os'),
        'creada': item.get('Created'), 'usuario': item.get('Config', {}).get('User'),
        'codigo_sha256': (item.get('Config', {}).get('Labels') or {}).get('org.rednova.source_sha256'),
    }


def fingerprints():
    paths = []
    for folder in ['datos', 'config', 'src']:
        paths += [p for p in (ROOT / folder).rglob('*') if p.is_file()
                  and '__pycache__' not in p.parts and p.suffix != '.pyc']
    paths += [ROOT / 'requirements.lock']
    return {p.relative_to(ROOT).as_posix(): digest(p) for p in sorted(paths)}


def source_digest():
    source = {k: v for k, v in fingerprints().items() if k.startswith('src/')}
    return hashlib.sha256(json.dumps(source, sort_keys=True).encode('utf-8')).hexdigest()


def config_path(value):
    path = (ROOT / value).resolve()
    try:
        rel = path.relative_to((ROOT / 'config').resolve())
    except ValueError:
        raise ValueError('--config debe identificar un archivo dentro de config/.')
    if not path.is_file() or path.suffix != '.json':
        raise ValueError('No existe el archivo de configuracion JSON: ' + str(path))
    return path, rel.as_posix()


def build(image):
    versions = docker_ready()
    started = now()
    command = ['docker', 'build', '--build-arg', 'SOURCE_SHA256=' + source_digest(), '--tag', image, '.']
    print('Construyendo la imagen. La primera descarga puede necesitar varios minutos.', flush=True)
    result = run(command)
    stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    dest = ROOT / 'salidas' / ('construccion_' + stamp)
    dest.mkdir(parents=True, exist_ok=False)
    (dest / 'consola.txt').write_text(result.stdout, encoding='utf-8')
    payload = {'inicio_utc': started, 'fin_utc': now(), 'comando': command, 'git': git_state(),
               'codigo_salida': result.returncode, 'docker': versions,
               'dockerfile_sha256': digest(ROOT / 'Dockerfile'),
               'codigo_fuente_sha256': {k: v for k, v in fingerprints().items() if k.startswith('src/')}}
    if result.returncode == 0:
        payload['imagen'] = image_metadata(image)
        # Solo se registra la base si fue observada: un builder remoto puede no dejarla local.
        try:
            payload['base_observada_localmente'] = image_metadata('python:3.12-slim')
        except ValueError:
            payload['base_observada_localmente'] = None
    write_json(dest / 'construccion.json', payload)
    print(result.stdout)
    print('Evidencia:', dest.relative_to(ROOT))
    if result.returncode:
        print('La construccion fallo; no se ha acreditado una imagen nueva.', file=sys.stderr)
    return result.returncode


def execute(args):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}', args.nombre):
        raise ValueError('--nombre: use 1 a 64 letras ASCII, numeros, guion o guion bajo.')
    cfg, cfg_rel = config_path(args.config)
    target = ROOT / 'salidas' / args.nombre
    if target.exists():
        raise ValueError('Esa corrida ya existe. Use otro --nombre para conservar la evidencia anterior.')
    before = fingerprints()
    metadata = {'modo': args.accion, 'inicio_utc': now(), 'configuracion': 'config/' + cfg_rel,
                'python_lanzador': platform.python_version(), 'entradas_sha256': before, 'git_inicio': git_state()}
    if args.accion == 'docker':
        metadata['docker'] = docker_ready()
        image = image_metadata(args.imagen)
        metadata['imagen'] = image
        if image.get('codigo_sha256') != source_digest():
            raise ValueError('La imagen no corresponde al codigo actual. Vuelva a ejecutar construir.')
        # UID del anfitrion Linux evita crear archivos ajenos. Desktop comparte mediante su VM.
        if sys.platform.startswith('linux'):
            uid, gid = os.getuid(), os.getgid()
            if uid == 0:
                raise ValueError('Ejecute la actividad con su cuenta habitual sin root.')
            container_user = f'{uid}:{gid}'
        else:
            container_user = '10001:10001'
        target.mkdir(parents=True, exist_ok=False)
        # Cada ejecucion recibe su propia carpeta de salida; otras corridas no se montan.
        command = ['docker', 'run', '--rm', '--network', 'none', '--read-only',
                   '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges:true',
                   '--user', container_user,
                   '--mount', f'type=bind,source={ROOT / "datos"},target=/datos,readonly',
                   '--mount', f'type=bind,source={ROOT / "config"},target=/config,readonly',
                   '--mount', f'type=bind,source={target},target=/salida',
                   image['id'], '--datos', '/datos', '--config', '/config/' + cfg_rel,
                   '--salida', '/salida/resultados']
        metadata['usuario_contenedor'] = container_user
    else:
        target.mkdir(parents=True, exist_ok=False)
        if args.accion == 'mlops':
            command = [sys.executable, '-B', '-m', 'src.entrenar', '--datos', str(ROOT / 'datos'),
                       '--salida', str(target / 'resultados')]
            metadata['configuracion'] = 'entrenamiento_temporal_definido_en_src.entrenar'
        else:
            command = [sys.executable, '-B', '-m', 'src.pipeline', '--datos', str(ROOT / 'datos'),
                       '--config', str(cfg), '--salida', str(target / 'resultados')]
    metadata['comando'] = command
    print('Ejecutando:', args.accion, '| corrida:', args.nombre, flush=True)
    result = run(command)
    print(result.stdout)
    metadata['fin_utc'] = now()
    metadata['git_fin'] = git_state()
    metadata['codigo_salida'] = result.returncode
    after = fingerprints()
    metadata['entradas_sin_cambios'] = before == after
    metadata['archivos_modificados'] = sorted(k for k in before.keys() | after.keys() if before.get(k) != after.get(k))
    (target / 'consola.txt').write_text(result.stdout, encoding='utf-8')
    write_json(target / 'ejecucion.json', metadata)
    print('Evidencia:', target.relative_to(ROOT))
    if not metadata['entradas_sin_cambios']:
        print('ERROR: cambiaron entradas durante la ejecucion. Revisar ejecucion.json.', file=sys.stderr)
        return 2
    if result.returncode:
        print('La corrida no termino correctamente. Revise consola.txt y los diagnosticos; use otro nombre al corregir.', file=sys.stderr)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='accion', required=True)
    sub.add_parser('comprobar', help='Comprueba Python y el motor Docker, sin ejecutar el pipeline.')
    b = sub.add_parser('construir', help='Construye la imagen y conserva evidencia real.')
    b.add_argument('--imagen', default=IMAGE)
    for mode in ['local', 'docker', 'mlops']:
        p = sub.add_parser(mode, help='Ejecuta una corrida nueva y conserva su evidencia.')
        p.add_argument('--nombre', required=True)
        p.add_argument('--config', default='config/ejecucion.json')
        p.add_argument('--imagen', default=IMAGE)
    args = parser.parse_args()
    if sys.version_info < (3, 11):
        parser.error('Se requiere Python 3.11 o posterior.')
    try:
        if args.accion == 'comprobar':
            print('Python:', platform.python_version(), '|', sys.executable)
            print('Carpeta del proyecto:', ROOT)
            git_version = run(['git', '--version']) if shutil.which('git') else None
            print(git_version.stdout.strip() if git_version else 'Git: no disponible; revisar GUIA_GIT.md.')
            versions = docker_ready()
            print('Docker cliente:', versions['Client']['Version'])
            print('Docker servidor:', versions['Server']['Version'])
            print('Listo para construir y ejecutar. Este control no ejecuta el pipeline.')
            return 0
        if args.accion == 'construir':
            return build(args.imagen)
        return execute(args)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print('ERROR:', exc, file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
