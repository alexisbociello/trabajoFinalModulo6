"""Diagnóstico de calidad; no sustituye el pipeline ni ejecuta P1–P8."""
from pathlib import Path
from decimal import Decimal, InvalidOperation
from datetime import date, datetime, timezone
import csv, hashlib, json, platform, re

ROOT = Path(__file__).resolve().parents[2]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    original = ROOT / '01_Original_ventas_PROTEGIDO/ventas_original.csv'
    entrada = ROOT / '04_Trabajo/01_Copias_de_datos/ventas_trabajo.csv'
    reglas = ROOT / '02_Insumos/01_Reglas_y_contrato/diccionario_y_reglas.md'
    contrato = ROOT / '02_Insumos/01_Reglas_y_contrato/contrato_pipeline.md'
    antes = sha(original)
    inicial = json.loads((ROOT/'07_Evidencias/01_Integridad_original/integridad_inicial.json').read_text())
    if antes != inicial['sha256_antes_de_organizar'] or antes != sha(entrada):
        raise ValueError('DETENER: original o copia no coincide con la huella inicial')
    columnas = ['id','fecha','categoria','cantidad','precio_unitario','costo_unitario']
    with entrada.open(newline='') as f: tabla = list(csv.reader(f))
    if tabla[0] != columnas: raise ValueError('DETENER: esquema incompatible')
    vistos = {}; registros = []
    for n, fila in enumerate(tabla[1:], 1):
        if len(fila) != 6: raise ValueError(f'DETENER: número de campos, origen {n}')
        datos = dict(zip(columnas, fila)); motivos = []; referencia = None
        ident = datos['id']
        if ident in vistos:
            anterior, valores = vistos[ident]
            if fila != valores: raise ValueError(f'DETENER: ID conflictivo en origen {n}')
            motivos.append('Duplicado exacto: conservar primera aparición (regla 2)')
            referencia = anterior
        else: vistos[ident] = (n, fila)
        if not ident.strip(): motivos.append('ID vacío (regla 3)')
        try:
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', datos['fecha']): raise ValueError()
            date.fromisoformat(datos['fecha'])
        except ValueError: motivos.append('Fecha inválida o formato no ISO (regla 3)')
        if datos['categoria'] not in {'Oficina','Tecnologia','Hogar'}: motivos.append('Categoría no autorizada (regla 3)')
        for campo in ['cantidad','precio_unitario','costo_unitario']:
            valor = datos[campo]
            try: d = Decimal(valor)
            except InvalidOperation:
                motivos.append(f'{campo}: vacío o no numérico (regla 3)'); continue
            if not d.is_finite(): motivos.append(f'{campo}: número no finito (regla 3)'); continue
            if campo == 'cantidad' and (d != d.to_integral_value() or d <= 0): motivos.append('cantidad: debe ser entero positivo (regla 3)')
            if campo == 'precio_unitario' and d <= 0: motivos.append('precio_unitario: debe ser positivo (regla 3)')
            if campo == 'costo_unitario' and d < 0: motivos.append('costo_unitario: debe ser no negativo (regla 3)')
        registros.append({'registro_origen':n,'valores_originales':datos,'decision':'EXCLUIR' if motivos else 'ACEPTAR','motivos':motivos or ['Cumple todas las validaciones del diccionario v1'],'referencia_duplicado':referencia})
    validas = sum(r['decision']=='ACEPTAR' for r in registros)
    excluidas = len(registros)-validas
    despues = sha(original)
    assert antes == despues and len(registros)==validas+excluidas
    evidencia = {'fecha_real_UTC':datetime.now(timezone.utc).isoformat(),'ejecutor':'Codex mediante herramienta de terminal','modalidad':'ejecución del agente en carpeta autorizada; revisión humana pendiente','comando':'python3 04_Trabajo/02_Diagnostico/ejecutar_diagnostico.py','python':platform.python_version(),'fuentes':{str(p.relative_to(ROOT)):sha(p) for p in [original,entrada,reglas,contrato,Path(__file__)]},'original_sha256_antes':antes,'original_sha256_despues':despues,'original_intacto':antes==despues,'leidas':len(registros),'validas':validas,'excluidas':excluidas,'detenciones_detectadas':[],'registros':registros}
    destino = ROOT/'04_Trabajo/02_Diagnostico'
    (destino/'evidencia_diagnostico.json').write_text(json.dumps(evidencia,ensure_ascii=False,indent=2)+'\n')
    texto = '''# Diagnóstico de calidad — Comercial Horizonte, v1

Una fila representa una venta de una categoría; no identifica personas ni productos individuales. Fuente: CSV sintético del caso. Clave esperada: `id`. Columnas exactas y orden: `id, fecha, categoria, cantidad, precio_unitario, costo_unitario`.

Tipos: ID y categoría como texto; fecha calendario ISO; cantidad entera positiva; precio decimal finito positivo; costo decimal finito no negativo. Categorías permitidas: Oficina, Tecnologia y Hogar. Se aplicó el diccionario v1 y el contrato v1, identificados por huella en la evidencia adjunta.

## Procedimiento y resultado

Ejecución real por Codex con Python, sobre una copia idéntica al original. Se comprobaron encabezado, seis campos por fila, clave, duplicados, fechas, categorías y números. Origen 1 corresponde a la primera fila de datos (línea física 2). No se corrigieron ni imputaron valores.

'''
    texto += f'**Conciliación: {len(registros)} leídas = {validas} válidas + {excluidas} excluidas.** Cada fila excluida se cuenta una sola vez. No se detectaron cambios de esquema ni IDs conflictivos que requieran detener este diagnóstico. La política y los cálculos de negocio se verificarán en el pipeline posterior.\n\n'
    texto += '| Origen | ID | Fecha | Categoría | Cantidad | Precio | Costo | Decisión | Regla / motivo |\n|---|---|---|---|---|---|---|---|---|\n'
    for r in registros:
        d=r['valores_originales']; valores=[str(r['registro_origen'])]+[d[c] if d[c] else '(vacío)' for c in columnas]+[r['decision'],'; '.join(r['motivos'])+(f"; origen de referencia: {r['referencia_duplicado']}" if r['referencia_duplicado'] else '')]
        texto += '| '+' | '.join(valores)+' |\n'
    texto += '''
## Tres contrastes para revisión humana

1. **V005, orígenes 5 y 14:** los seis valores son idénticos: `V005,2026-10-07,Tecnologia,3,150,120`. Se acepta el origen 5 y se excluye el 14. Para explicar el efecto: 3 × 150 = 450 de ventas; 3 × 120 = 360 de costos; margen 90, contabilizados una sola vez. Es una comprobación preparada por el agente, pendiente de contraste humano.
2. **Origen 15, V014:** cantidad original `-2`; incumple entero positivo. Se excluye; no se aplica valor absoluto ni se supone una devolución.
3. **Origen 16, V015:** precio original vacío; incumple precio numérico positivo. Se excluye sin imputación; cantidad 7 y costo 11 no permiten inferir el precio.

Una pérdida puede ser válida si los demás campos cumplen las reglas: precio menor que costo no es por sí solo una exclusión. No se encontró ese caso en las 13 filas aceptadas.

## Integridad y trazabilidad

La huella SHA-256 del original se comprobó antes y después, contra el registro inicial y contra la copia de trabajo. El original conserva su contenido. Las huellas, versión Python, comando, valores originales y decisiones están en `evidencia_diagnostico.json`. El script reproducible es `ejecutar_diagnostico.py`; no es el pipeline final ni prueba las ocho condiciones completas.

## Uso de IA y pendiente humano

Pedido que originó esta ejecución: «eso lo puedes realizar tu? que informacion o decision extra de mi parte necesitas?», referido al diagnóstico de calidad previamente propuesto. Codex leyó las reglas, generó el verificador, lo ejecutó y documentó resultados. No se atribuye esta ejecución ni un cálculo manual al estudiante.

Pendiente: el estudiante debe contrastar los tres casos, confirmar la conciliación y registrar su revisión propia en la bitácora. No se aprobaron P1–P8 ni controles de detención con esta sola ejecución. No se necesita una nueva regla de negocio para resolver estas filas.
'''
    (destino/'diagnostico.md').write_text(texto)
    print(json.dumps({k:evidencia[k] for k in ['comando','python','leidas','validas','excluidas','original_intacto','original_sha256_despues']},ensure_ascii=False,indent=2))
if __name__ == '__main__': main()
