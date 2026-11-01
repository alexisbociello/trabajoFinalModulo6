"""Ejecuta el pipeline y contrasta con Fraction, sin importar su implementación."""
from pathlib import Path
from fractions import Fraction as F
import csv, json, subprocess, sys, hashlib, shutil
from datetime import datetime, timezone
R=Path(__file__).resolve().parents[1]
script=R/'04_Trabajo/03_Pipeline/pipeline.py'
base=R/'06_Pruebas/02_Resultados'; entradas=R/'06_Pruebas/01_Entradas'
politicas=R/'02_Insumos/02_Politicas'
original=R/'01_Original_ventas_PROTEGIDO/ventas_original.csv'
hash_antes=hashlib.sha256(original.read_bytes()).hexdigest()
registros=[]
def ejecutar(nombre,entrada,fecha='2026-10-19',pol=politicas,fallo=False,destino=None):
    log=base/nombre; log.mkdir(parents=True,exist_ok=True)
    out=destino or log/'productos'
    cmd=[sys.executable,str(script),'--entrada',str(entrada),'--politicas',str(pol),'--fecha-ejecucion',fecha,'--salida',str(out)]
    proc=subprocess.run(cmd,cwd=R,text=True,capture_output=True)
    (log/'stdout.json').write_text(proc.stdout);(log/'stderr.txt').write_text(proc.stderr)
    info={'comando':cmd,'codigo_salida':proc.returncode,'fecha_real_UTC':datetime.now(timezone.utc).isoformat(),'modalidad':'Ejecutada por Codex en terminal; revisión humana no registrada','destino':str(out.relative_to(R))}
    (log/'ejecucion.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n')
    if fallo:
        assert proc.returncode!=0 and not out.exists(),(nombre,proc.stderr)
        return proc.stderr
    assert proc.returncode==0,(nombre,proc.stderr)
    assert {p.name for p in out.iterdir()}=={'ventas_validas.csv','reporte_calidad.json','resumen.json'}
    return json.loads(proc.stdout)
def prueba(id,criterio,observado,evidencia):
    registros.append({'prueba':id,'criterio_de_aceptacion':criterio,'resultado_observado':observado,'evidencia':evidencia,'modalidad':'Ejecutada por Codex con herramientas','revision_humana':'No registrada'})
v1=ejecutar('base_v1',original,'2026-10-18',destino=R/'05_Ejecuciones/01_Python/2026-10-18_v1/ejecucion_01')
v2=ejecutar('base_v2',original,destino=R/'05_Ejecuciones/01_Python/2026-10-19_v2/ejecucion_01')
q=v1['reporte_calidad']; assert (q['registros_leidos'],q['registros_validos'],q['registros_excluidos'])==(16,13,3)
assert [d['registro_origen'] for d in q['decisiones'] if d['decision']=='EXCLUIR']==[14,15,16]
prueba('P1','Leídas = válidas + excluidas, con decisiones por registro','16 = 13 + 3; 16 decisiones conservadas','06_Pruebas/02_Resultados/base_v1')
assert sum(r['id']=='V005' for r in v1['ventas_validas'])==1 and q['decisiones'][13]['referencia_duplicado']==5
prueba('P2','Conservar primera V005','Origen 5 aceptado; 14 excluido; una venta V005','06_Pruebas/02_Resultados/base_v1')
for id,idx,campo,valor in [('P3',14,'cantidad','-2'),('P4',15,'precio_unitario','')]:
    d=q['decisiones'][idx];assert d['decision']=='EXCLUIR' and d['valores_originales'][campo]==valor
    prueba(id,'Excluir sin corregir ni imputar',f'Origen {idx+1}: {campo}={valor!r}, excluido','06_Pruebas/02_Resultados/base_v1')
# Contraste independiente: las primeras 13 filas son las aceptables, comprobadas en diagnóstico.
with original.open() as f: rows=list(csv.DictReader(f))[:13]
ag={}
for fila in rows:
    cantidad,precio,costo=[F(fila[k]) for k in ['cantidad','precio_unitario','costo_unitario']]
    for cat in [fila['categoria'],'TOTAL']:
        a=ag.setdefault(cat,[F(0)]*4)
        for i,x in enumerate([cantidad,cantidad*precio,cantidad*costo,cantidad*(precio-costo)]):a[i]+=x
for cat,nums in ag.items():
    real=v1['resumen']['total'] if cat=='TOTAL' else v1['resumen']['categorias'][cat]
    assert [F(real[k]) for k in ['unidades','ventas','costos','margen']]==nums
prueba('P5','Importes y unidades independientes por categoría/total',str({k:[str(x) for x in v] for k,v in ag.items()}),'06_Pruebas/02_Resultados/contraste_independiente.json')
t=ag['TOTAL'];pct=100*t[3]/t[1]
assert abs(F(v1['resumen']['total']['margen_pct'])-pct)<F(1,10**40)
sub=rows[:2];sv=sum(F(x['cantidad'])*F(x['precio_unitario']) for x in sub);sm=sum(F(x['cantidad'])*(F(x['precio_unitario'])-F(x['costo_unitario'])) for x in sub)
assert sv==1450 and sm==460
contraste={'metodo':'Fraction de biblioteca estándar; primeros 13 registros contrastados con diagnóstico','agregados':{k:dict(zip(['unidades','ventas','costos','margen'],map(str,v))) for k,v in ag.items()},'porcentaje_total_fraccion_exacta':str(pct),'V001_V002':{'ventas':str(sv),'margen':str(sm),'porcentaje_fraccion_exacta':str(100*sm/sv),'promedio_simple_incorrecto':'35'}}
(base/'contraste_independiente.json').write_text(json.dumps(contraste,ensure_ascii=False,indent=2)+'\n')
prueba('P6','Razón de sumas; V001/V002','Total 100×margen/ventas contrastado como fracción; V001/V002: 460/1450×100, no 35%','06_Pruebas/02_Resultados/contraste_independiente.json')
assert v1['ventas_validas']==v2['ventas_validas'] and v1['reporte_calidad']==v2['reporte_calidad']
assert v1['resumen']['politica']['version']=='v1' and v2['resumen']['politica']['version']=='v2'
fr=ejecutar('P7_frontera',entradas/'frontera_30.csv');red=ejecutar('P7_redondeo',entradas/'redondeo_29999.csv')
assert fr['resumen']['total']['estado']=='SIN ALERTA'
assert red['resumen']['total']['estado']=='ALERTA' and red['resumen']['total']['margen_pct_mostrado']=='30.00'
prueba('P7','Política por ejecución y fronteras estrictas','v1/v2 con importes idénticos; 30% SIN ALERTA; 29.999% ALERTA y mostrado 30.00','06_Pruebas/02_Resultados/P7_frontera; 06_Pruebas/02_Resultados/P7_redondeo; base_v1; base_v2')
vacio=ejecutar('P8_sin_validas',entradas/'sin_validas.csv');assert vacio['resumen']['total']['margen_pct'] is None and vacio['resumen']['total']['estado']=='NO EVALUABLE'
assert vacio['reporte_calidad']['registros_leidos']==2 and vacio['reporte_calidad']['registros_validos']==0
prueba('P8','Sin válidas: null / NO EVALUABLE','2 leídas; 0 válidas; null; NO EVALUABLE. Orígenes locales 1/2 corresponden a originales 15/16','06_Pruebas/02_Resultados/P8_sin_validas')
with original.open() as f: todo=list(csv.reader(f))
with (entradas/'id_conflictivo.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(todo[0]);w.writerow(todo[1]);otra=todo[1].copy();otra[3]='11';w.writerow(otra)
pol_faltante=entradas/'politicas_sin_v2';pol_faltante.mkdir(exist_ok=True)
shutil.copy2(politicas/'politica_margen_v1.md',pol_faltante/'politica_margen_v1.md')
for nombre,ent,pol in [('Detencion_esquema',entradas/'esquema_incompatible.csv',politicas),('Detencion_ID_conflictivo',entradas/'id_conflictivo.csv',politicas),('Detencion_politica_faltante',original,pol_faltante)]:
    mensaje=ejecutar(nombre,ent,pol=pol,fallo=True)
    prueba(nombre,'Detener sin crear nueva salida',mensaje.strip()+'; no se creó productos/',f'06_Pruebas/02_Resultados/{nombre}')
# Sin --salida: emisión por consola y sin escritura de productos.
p=subprocess.run([sys.executable,str(script),'--entrada',str(original),'--politicas',str(politicas),'--fecha-ejecucion','2026-10-18'],capture_output=True,text=True)
assert p.returncode==0 and json.loads(p.stdout)==v1
assert hashlib.sha256(original.read_bytes()).hexdigest()==hash_antes
with (R/'06_Pruebas/03_Matriz_y_revision/matriz_8_pruebas.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(registros[0]));w.writeheader();w.writerows(registros)
print(json.dumps({'pruebas':len(registros),'resultado':'11 controles aprobados; interfaz sin salida comprobada','original_intacto':True,'total_v1':v1['resumen']['total'],'total_v2':v2['resumen']['total']},ensure_ascii=False,indent=2))
