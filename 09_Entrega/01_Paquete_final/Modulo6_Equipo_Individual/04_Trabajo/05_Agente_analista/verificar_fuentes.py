"""Contrasta las fuentes del analista; no genera respuestas conversacionales."""
from pathlib import Path
from fractions import Fraction as F
from datetime import datetime, timezone
import csv,json,hashlib,platform
R=Path(__file__).resolve().parents[2]
base=R/'05_Ejecuciones/01_Python'
original=R/'01_Original_ventas_PROTEGIDO/ventas_original.csv'
sha=hashlib.sha256(original.read_bytes()).hexdigest()
fuentes={};resultados={}
for fecha,version,umbral in [('2026-10-18','v1',25),('2026-10-19','v2',30)]:
    carpeta=base/f'{fecha}_{version}/ejecucion_01'
    resumen=json.loads((carpeta/'resumen.json').read_text())
    calidad=json.loads((carpeta/'reporte_calidad.json').read_text())
    with (carpeta/'ventas_validas.csv').open() as f: filas=list(csv.DictReader(f))
    assert resumen['fecha_ejecucion']==fecha and resumen['politica']['version']==version
    assert resumen['entrada_sha256']==sha
    assert calidad['registros_validos']==len(filas)==13
    valores={}
    for cat in ['Oficina','Tecnologia','Hogar','TOTAL']:
        datos=filas if cat=='TOTAL' else [x for x in filas if x['categoria']==cat]
        v=sum(F(x['cantidad'])*F(x['precio_unitario']) for x in datos)
        c=sum(F(x['cantidad'])*F(x['costo_unitario']) for x in datos)
        m=v-c; estado='ALERTA' if 100*m<umbral*v else 'SIN ALERTA'
        a=resumen['total'] if cat=='TOTAL' else resumen['categorias'][cat]
        assert [F(a[k]) for k in ['ventas','costos','margen']]==[v,c,m]
        assert a['estado']==estado
        valores[cat]={'ventas':str(v),'costos':str(c),'margen':str(m),'porcentaje_fraccion_exacta':str(100*m/v),'estado':estado}
    resultados[version]={'fecha_ejecucion':fecha,'politica':resumen['politica'],'agregados_verificados':valores}
    for p in carpeta.iterdir(): fuentes[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
for nombre in ['politica_margen_v1.md','politica_margen_v2.md']:
    p=R/'02_Insumos/02_Politicas'/nombre;fuentes[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
with original.open() as f: columnas=next(csv.reader(f))
assert 'cliente' not in columnas
assert resultados['v1']['agregados_verificados']['TOTAL']['ventas']==resultados['v2']['agregados_verificados']['TOTAL']['ventas']
e={'fecha_real_UTC':datetime.now(timezone.utc).isoformat(),'ejecutor':'Codex mediante terminal','python':platform.python_version(),'comando':'python3 04_Trabajo/05_Agente_analista/verificar_fuentes.py','metodo':'Fraction, recalculo desde cantidad/precio/costo de ventas_validas; contraste con resumen y calidad','original_intacto':sha==json.loads((R/'07_Evidencias/01_Integridad_original/integridad_inicial.json').read_text())['sha256_antes_de_organizar'],'columnas_disponibles':columnas,'fuentes_sha256':fuentes,'resultados':resultados}
assert e['original_intacto']
(R/'04_Trabajo/05_Agente_analista/evidencia_verificacion.json').write_text(json.dumps(e,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(e,ensure_ascii=False,indent=2))
