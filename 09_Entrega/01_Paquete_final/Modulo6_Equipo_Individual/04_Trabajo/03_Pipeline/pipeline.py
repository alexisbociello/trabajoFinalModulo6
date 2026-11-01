"""Pipeline Comercial Horizonte v1.0.0; biblioteca estándar, sin red."""
import argparse
import csv
import hashlib
import io
import json
import sys
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext
from pathlib import Path

VERSION = '1.0.0'
COLUMNAS = ['id', 'fecha', 'categoria', 'cantidad', 'precio_unitario', 'costo_unitario']
CATEGORIAS = ['Oficina', 'Tecnologia', 'Hogar']

class Detencion(ValueError):
    pass

def fecha_iso(texto):
    valor = date.fromisoformat(texto)
    if valor.isoformat() != texto:
        raise ValueError('formato ISO AAAA-MM-DD requerido')
    return valor

# 1. LEER

def leer(entrada):
    contenido = entrada.read_bytes()
    filas = list(csv.reader(io.StringIO(contenido.decode('utf-8-sig'), newline='')))
    if not filas or filas[0] != COLUMNAS:
        raise Detencion('Esquema incompatible: revisar encabezado y contrato; no renombrar automáticamente.')
    if any(len(fila) != len(COLUMNAS) for fila in filas[1:]):
        raise Detencion('Esquema incompatible: una fila tiene distinto número de campos.')
    return filas[1:], hashlib.sha256(contenido).hexdigest()

# 2. VALIDAR

def validar(filas):
    vistos = {}; validas = []; decisiones = []
    for origen, fila in enumerate(filas, 1):
        datos = dict(zip(COLUMNAS, fila)); ident = datos['id']; motivos = []; referencia = None
        if ident in vistos:
            referencia, anterior = vistos[ident]
            if fila != anterior:
                raise Detencion(f'ID conflictivo {ident!r}, orígenes {referencia} y {origen}: pedir aclaración.')
            motivos.append('Duplicado exacto; conservar primera aparición')
        else:
            vistos[ident] = (origen, fila)
        if not ident.strip(): motivos.append('ID vacío')
        try: fecha_iso(datos['fecha'])
        except ValueError: motivos.append('Fecha inválida o formato no ISO')
        if datos['categoria'] not in CATEGORIAS: motivos.append('Categoría no autorizada')
        numeros = {}
        for campo in COLUMNAS[3:]:
            try: numero = Decimal(datos[campo])
            except InvalidOperation:
                motivos.append(f'{campo}: vacío o no numérico'); continue
            if not numero.is_finite():
                motivos.append(f'{campo}: no finito'); continue
            if campo == 'cantidad' and (numero <= 0 or numero != numero.to_integral_value()):
                motivos.append('cantidad: debe ser entero positivo')
            if campo == 'precio_unitario' and numero <= 0: motivos.append('precio_unitario: debe ser positivo')
            if campo == 'costo_unitario' and numero < 0: motivos.append('costo_unitario: debe ser no negativo')
            numeros[campo] = numero
        decisiones.append({'registro_origen': origen, 'id': ident, 'valores_originales': datos,
                           'decision': 'EXCLUIR' if motivos else 'ACEPTAR', 'motivos': motivos,
                           'referencia_duplicado': referencia})
        if not motivos: validas.append((origen, datos, numeros))
    return validas, {'registros_leidos': len(filas), 'registros_validos': len(validas),
                     'registros_excluidos': len(filas)-len(validas), 'decisiones': decisiones}

def seleccionar_politica(carpeta, fecha):
    try: ejecucion = fecha_iso(fecha)
    except ValueError as e: raise Detencion(f'Fecha de ejecución inválida: {e}')
    if not carpeta.is_dir(): raise Detencion('Carpeta de políticas inexistente.')
    candidatas = []
    for archivo in sorted(carpeta.glob('*.md')):
        try:
            campos = {}
            for linea in archivo.read_text().splitlines():
                if linea.strip() == '---': break
                clave, valor = linea.split(':', 1)
                if clave in campos: raise ValueError('campo repetido')
                campos[clave] = valor.strip()
            if set(campos) != {'version','desde','hasta','umbral_pct','operador'}: raise ValueError('campos de política inválidos')
            inicio = fecha_iso(campos['desde'])
            fin = None if campos['hasta'] == 'abierta' else fecha_iso(campos['hasta'])
            umbral = Decimal(campos['umbral_pct'])
            if not campos['version'] or not umbral.is_finite() or campos['operador'] != '<' or (fin and fin < inicio):
                raise ValueError('contenido de política inválido')
            if inicio <= ejecucion and (fin is None or ejecucion <= fin):
                candidatas.append(dict(campos, archivo=archivo.name))
        except (ValueError, InvalidOperation) as e:
            raise Detencion(f'Política mal formada {archivo.name}: {e}')
    if len(candidatas) != 1:
        raise Detencion(f'Política faltante o solapada para {fecha}: encontradas {len(candidatas)}; pedir aclaración.')
    return candidatas[0]

# 3. CALCULAR

def mostrar(numero):
    return format(numero.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), 'f')

def calcular(validas, politica, fecha):
    # Precisión suficiente para productos y sumas exactos de las entradas; la división
    # puede ser periódica. La clasificación usa productos cruzados, sin redondeo.
    numeros = [n for _, _, ns in validas for n in ns.values()]
    extension = max([len(n.as_tuple().digits)+abs(n.as_tuple().exponent) for n in numeros]+[28])
    with localcontext() as contexto:
        contexto.prec = max(50, 4*extension + len(str(len(validas)+1)) + 20)
        agregados = {c: {'registros': 0, 'unidades': Decimal(0), 'ventas': Decimal(0), 'costos': Decimal(0), 'margen': Decimal(0)} for c in CATEGORIAS+['TOTAL']}
        aceptadas = []
        for origen, datos, ns in validas:
            q, p, c = (ns[k] for k in COLUMNAS[3:])
            v = q*p; costo = q*c; margen = v-costo
            aceptadas.append(dict(datos, registro_origen=origen, ventas=str(v), costos=str(costo), margen=str(margen)))
            for clave in [datos['categoria'], 'TOTAL']:
                a = agregados[clave]; a['registros'] += 1; a['unidades'] += q
                a['ventas'] += v; a['costos'] += costo; a['margen'] += margen
        for a in agregados.values():
            evaluable = a['registros'] > 0 and a['ventas'] > 0
            pct = 100*a['margen']/a['ventas'] if evaluable else None
            a['estado'] = ('ALERTA' if 100*a['margen'] < Decimal(politica['umbral_pct'])*a['ventas'] else 'SIN ALERTA') if evaluable else 'NO EVALUABLE'
            for k in ['unidades','ventas','costos','margen']: a[k] = str(a[k])
            a['margen_pct'] = str(pct) if pct is not None else None
            a['margen_pct_mostrado'] = mostrar(pct) if pct is not None else None
        total = agregados.pop('TOTAL')
        return aceptadas, {'fecha_ejecucion': fecha, 'politica': politica, 'categorias': agregados, 'total': total,
                          'nota_precision': 'Porcentaje periódico representado con precisión decimal; clasificación por productos cruzados exactos.'}

# 4. GUARDAR

def guardar(salida, aceptadas, reporte, resumen, protegidos):
    if salida is None: return
    salida = salida.resolve()
    if salida.exists(): raise Detencion('Destino ya existente: usar una carpeta nueva para preservar ejecuciones anteriores.')
    if any(salida == p or salida in p.parents for p in protegidos):
        raise Detencion('Destino contiene entradas protegidas.')
    salida.parent.mkdir(parents=True, exist_ok=True)
    # Publicar los tres productos juntos; si falla la escritura, retirar el temporal.
    import tempfile, shutil
    temporal = Path(tempfile.mkdtemp(prefix='.horizonte-', dir=salida.parent))
    try:
        with (temporal/'ventas_validas.csv').open('w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNAS+['registro_origen','ventas','costos','margen'])
            writer.writeheader(); writer.writerows(aceptadas)
        for nombre, datos in [('reporte_calidad.json', reporte), ('resumen.json', resumen)]:
            (temporal/nombre).write_text(json.dumps(datos, ensure_ascii=False, indent=2)+'\n')
        temporal.rename(salida)
    finally:
        if temporal.exists(): shutil.rmtree(temporal)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--entrada', type=Path, required=True)
    parser.add_argument('--politicas', type=Path, required=True)
    parser.add_argument('--fecha-ejecucion', required=True)
    parser.add_argument('--salida', type=Path)
    args = parser.parse_args()
    try:
        filas, huella = leer(args.entrada)
        validas, reporte = validar(filas)
        politica = seleccionar_politica(args.politicas, args.fecha_ejecucion)
        aceptadas, resumen = calcular(validas, politica, args.fecha_ejecucion)
        resumen['pipeline_version'] = VERSION
        resumen['entrada_sha256'] = huella
        if hashlib.sha256(args.entrada.read_bytes()).hexdigest() != huella:
            raise Detencion('Entrada modificada durante la ejecución.')
        guardar(args.salida, aceptadas, reporte, resumen, [args.entrada.resolve()]+[p.resolve() for p in args.politicas.glob('*.md')])
        print(json.dumps({'ventas_validas': aceptadas, 'reporte_calidad': reporte, 'resumen': resumen}, ensure_ascii=False, indent=2))
        return 0
    except (Detencion, OSError, UnicodeError, csv.Error, InvalidOperation, ValueError) as e:
        print(f'DETENCIÓN: {e}', file=sys.stderr)
        return 2

if __name__ == '__main__':
    sys.exit(main())
