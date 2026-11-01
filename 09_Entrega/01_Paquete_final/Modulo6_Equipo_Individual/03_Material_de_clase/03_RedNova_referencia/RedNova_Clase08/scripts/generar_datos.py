#!/usr/bin/env python3
"""Regenera exclusivamente las fuentes didácticas sintéticas de RedNova.

No necesita dependencias, red ni semillas aleatorias. No se ejecuta durante el
pipeline normal. Sobrescribe los siete CSV y su manifiesto en --salida.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import date, timedelta
from pathlib import Path

SCHEMAS = {
    'ventas_lineas.csv': ['venta_id', 'linea_id', 'fecha_evento', 'fecha_ingesta', 'sucursal_id', 'producto_id', 'cantidad', 'precio_unitario', 'descuento_linea'],
    'inventario_diario.csv': ['fecha', 'sucursal_id', 'producto_id', 'stock_cierre', 'reservado', 'quiebre', 'fecha_ingesta', 'ventas_completas'],
    'productos.csv': ['producto_id', 'nombre', 'categoria', 'activo'],
    'sucursales.csv': ['sucursal_id', 'nombre', 'region', 'activo'],
    'costos_vigentes.csv': ['producto_id', 'desde', 'hasta', 'costo_unitario', 'fecha_ingesta'],
    'pedidos_abiertos.csv': ['pedido_id', 'linea_id', 'sucursal_id', 'producto_id', 'cantidad_pedida', 'cantidad_recibida', 'estado', 'fecha_arribo', 'arribo_confirmado', 'fecha_ingesta'],
    'recepciones.csv': ['recepcion_id', 'linea_id', 'pedido_id', 'pedido_linea_id', 'sucursal_id', 'producto_id', 'fecha_evento', 'fecha_ingesta', 'cantidad'],
}


def generate(destination: Path) -> dict:
    destination.mkdir(parents=True, exist_ok=True)
    rows = {name: [] for name in SCHEMAS}
    start, end = date(2025, 1, 1), date(2025, 6, 30)
    day = start
    while day <= end:
        day_index = (day - start).days
        ds = day.isoformat()
        if day >= date(2025, 6, 24):
            quantities = {'A100': 20, 'B200': 5, 'C300': 2}
        else:
            quantities = {
                'A100': 10 + day_index // 30 + (day.weekday() % 3),
                'B200': 4 + day_index // 60 + (day.weekday() % 2),
                'C300': 2 + day_index // 90 + (1 if day.weekday() == 5 else 0),
            }
        for p, price in [('A100', 50), ('B200', 200), ('C300', 500)]:
            rows['ventas_lineas.csv'].append([
                f'V{day.strftime("%Y%m%d")}{p}', '1', ds + 'T18:00:00Z',
                ds + 'T19:00:00Z', 'S03', p, quantities[p], price,
                100 if day == end and p == 'A100' else 0,
            ])
            stock = {'A100': 200, 'B200': 100, 'C300': 40}[p]
            reserved = 0
            if day == end:
                stock = {'A100': 80, 'B200': 50, 'C300': 10}[p]
                reserved = 10 if p == 'A100' else 0
            rows['inventario_diario.csv'].append([
                ds, 'S03', p, stock, reserved, 'false', ds + 'T23:00:00Z', 'true'
            ])
        day += timedelta(days=1)

    rows['productos.csv'] = [
        ['A100', 'Resma de papel', 'Oficina', 'true'],
        ['B200', 'Lámpara de mesa', 'Hogar', 'true'],
        ['C300', 'Teclado', 'Tecnologia', 'true'],
    ]
    rows['sucursales.csv'] = [['S03', 'Sucursal Centro', 'Centro', 'true']]
    rows['costos_vigentes.csv'] = [
        ['A100', '2025-01-01', '2025-07-01', '30', '2025-01-01T00:00:00Z'],
        ['A100', '2025-07-01', '', '32', '2025-06-25T00:00:00Z'],
        ['B200', '2025-01-01', '', '150', '2025-01-01T00:00:00Z'],
        ['C300', '2025-01-01', '', '400', '2025-01-01T00:00:00Z'],
    ]
    rows['pedidos_abiertos.csv'] = [
        ['P001', '1', 'S03', 'A100', 50, 10, 'confirmado', '2025-07-02', 'true', '2025-06-30T23:10:00Z'],
        ['P002', '1', 'S03', 'B200', 10, 0, 'confirmado', '2025-07-04', 'true', '2025-06-30T23:10:00Z'],
        ['P003', '1', 'S03', 'C300', 5, 0, 'cancelado', '2025-07-03', 'false', '2025-06-30T23:10:00Z'],
        ['P004', '1', 'S03', 'A100', 5, 0, 'confirmado', '2025-06-29', 'true', '2025-06-30T23:10:00Z'],
    ]
    rows['recepciones.csv'] = [
        ['R001', '1', 'P001', '1', 'S03', 'A100', '2025-06-30T10:00:00Z', '2025-06-30T11:00:00Z', 10]
    ]

    sources = {}
    for filename, columns in SCHEMAS.items():
        path = destination / filename
        with path.open('w', encoding='utf-8', newline='') as stream:
            writer = csv.writer(stream, lineterminator='\n')
            writer.writerow(columns)
            writer.writerows(rows[filename])
        sources[filename] = {
            'archivo': filename,
            'filas': len(rows[filename]),
            'columnas': columns,
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'disponibilidad': ('2025-01-01T00:00:00Z' if filename in ('productos.csv', 'sucursales.csv') else 'por fila: fecha_ingesta'),
        }
    manifest = {
        'data_version': 'rednova-sintetico-v1.0.0',
        'sintetico': True,
        'generador': 'scripts/generar_datos.py',
        'corte': '2025-06-30T23:59:59Z',
        'periodo_ventas_desde': start.isoformat(),
        'periodo_ventas_hasta': end.isoformat(),
        'sucursal': 'S03',
        'productos': ['A100', 'B200', 'C300'],
        'total_filas_csv': sum(len(v) for v in rows.values()),
        'fuentes': sources,
        'supuestos': [
            'Datos completamente ficticios, fabricados para enseñanza; no representan la escala anual de 12 sucursales y 120 productos del diseño teórico.',
            'Maestros de productos y sucursales son constantes y conocidos desde 2025-01-01T00:00:00Z. Las demás fuentes tienen disponibilidad explícita por fecha_ingesta.',
            'Los inventarios son estados didácticos independientes; este extracto no contiene todos los movimientos necesarios para reconstruir su balance diario.',
            'La recepción de 10 unidades de P001 está incluida en el cierre de inventario y en cantidad_recibida; no se suma nuevamente al stock.',
            'Los pedidos son el snapshot del cierre de 30 de junio, no una historia de estados. No deben utilizarse para reconstruir pedidos de meses anteriores.',
            'El pedido P004 está atrasado. Su saldo debe excluirse del tránsito elegible hasta reconfirmar llegada; la exclusión no convierte el saldo en cero.',
            'Las reservas de 10 unidades son compromisos previamente separados de la demanda estimada del ejercicio. Esta simplificación debe mantenerse explícita en la configuración.',
            'Ventas_completas=true certifica un lote diario completo; quiebre=false es un supuesto sintético explícito. Ninguna fecha faltante debe imputarse como cero.',
            'Todas las cantidades y precios se generan sin aleatoriedad. Las variaciones históricas son artificiales; las métricas no estiman desempeño comercial real.',
            'La vigencia de la política se define en config y no se selecciona mediante este snapshot. Los cambios contrafactuales deben identificarse como escenarios.',
        ],
    }
    (destination / 'snapshot_fuentes.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--salida', type=Path, default=Path(__file__).resolve().parents[1] / 'datos',
                        help='Directorio de fuentes sintéticas; se sobrescriben solo los archivos del generador.')
    args = parser.parse_args()
    manifest = generate(args.salida)
    print(json.dumps({'estado': 'GENERADO', 'sintetico': True, 'directorio': str(args.salida),
                      'filas_csv': manifest['total_filas_csv'],
                      'fuentes': {name: value['filas'] for name, value in manifest['fuentes'].items()}},
                     ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
