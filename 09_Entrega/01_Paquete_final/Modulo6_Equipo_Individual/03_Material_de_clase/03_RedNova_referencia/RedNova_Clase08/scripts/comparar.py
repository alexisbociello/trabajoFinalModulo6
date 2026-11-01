#!/usr/bin/env python3
"""Compara dos corridas reales con las mismas entradas y salidas de negocio."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS = ['calidad.json', 'ventas_diarias.csv', 'pronosticos.csv',
            'reposicion.csv', 'resumen.json', 'informe.md']


def read_json(p):
    return json.loads(p.read_text(encoding='utf-8'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('primera', help='Carpeta de corrida, por ejemplo salidas/local_v1')
    parser.add_argument('segunda', help='Carpeta de corrida, por ejemplo salidas/docker_v1')
    parser.add_argument('--salida', help='JSON nuevo dentro de salidas/. Si se omite solo muestra el resultado.')
    args = parser.parse_args()
    try:
        runs = [(ROOT / name).resolve() for name in (args.primera, args.segunda)]
        for p in runs:
            p.relative_to(ROOT / 'salidas')
        if runs[0] == runs[1]:
            raise ValueError('Seleccione dos carpetas de corrida distintas.')
        metadata = [read_json(p / 'ejecucion.json') for p in runs]
        valid = all(m.get('codigo_salida') == 0 and m.get('entradas_sin_cambios') is True for m in metadata)
        files = []
        for name in PRODUCTS:
            paths = [p / 'resultados' / name for p in runs]
            present = all(p.is_file() for p in paths)
            hashes = [hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None for p in paths]
            # Hash igual equivale aqui a bytes iguales; no se confunde igualdad de totales con de archivos.
            files.append({'archivo': name, 'presente_en_ambas': present,
                          'coincide': present and hashes[0] == hashes[1],
                          'sha256_primera': hashes[0], 'sha256_segunda': hashes[1]})
        same_inputs = metadata[0]['entradas_sha256'] == metadata[1]['entradas_sha256']
        same_config = metadata[0]['configuracion'] == metadata[1]['configuracion']
        accepted = valid and same_inputs and same_config and all(f['coincide'] for f in files)
        report = {'corridas': [str(p.relative_to(ROOT)) for p in runs],
                  'modos_observados': [m.get('modo') for m in metadata],
                  'contraste_local_docker': accepted and {m.get('modo') for m in metadata} == {'local', 'docker'},
                  'ejecuciones_exitosas_y_entradas_intactas': valid,
                  'mismas_huellas_entradas_codigo_config': same_inputs,
                  'misma_configuracion_seleccionada': same_config,
                  'archivos': files, 'reproducibilidad_comprobada': accepted,
                  'excluidos_del_contraste_de_negocio': ['manifiesto.json', 'ejecucion.json', 'consola.txt'],
                  'nota': 'Tiempos, rutas y versiones del entorno pueden diferir. Si se comparan politicas distintas, las diferencias son el experimento; esta prueba no las declara equivalentes.'}
        print(json.dumps(report, ensure_ascii=False, indent=2))
        if args.salida:
            out = (ROOT / args.salida).resolve()
            out.relative_to(ROOT / 'salidas')
            out.parent.mkdir(parents=True, exist_ok=True)
            with out.open('x', encoding='utf-8') as handle:
                json.dump(report, handle, ensure_ascii=False, indent=2)
                handle.write('\n')
        return 0 if accepted else 1
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print('ERROR: no se pudo comprobar equivalencia:', exc, file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
