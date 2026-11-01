"""Audita evidencias y ensaya recuperación con fuentes válidas conocidas."""
from pathlib import Path
from datetime import datetime,timezone
import subprocess,hashlib,json,sys
R=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
base=R/'05_Ejecuciones/04_Recuperacion'/stamp;base.mkdir(parents=True)
script=R/'04_Trabajo/03_Pipeline/pipeline.py';original=R/'01_Original_ventas_PROTEGIDO/ventas_original.csv'
politicas=R/'02_Insumos/02_Politicas'
antiguos=[p for carpeta in [R/'05_Ejecuciones/01_Python',R/'05_Ejecuciones/02_Docker',R/'06_Pruebas/02_Resultados'] for p in carpeta.rglob('*') if p.is_file()]
antes={str(p.relative_to(R)):sha(p) for p in antiguos}
assert sha(original)==json.loads((R/'07_Evidencias/01_Integridad_original/integridad_inicial.json').read_text())['sha256_antes_de_organizar']
referencia=R/'05_Ejecuciones/01_Python/2026-10-19_v2/ejecucion_01'
reanudaciones=[]
for nombre in ['Detencion_esquema','Detencion_ID_conflictivo','Detencion_politica_faltante']:
    fallo=R/'06_Pruebas/02_Resultados'/nombre
    registro=json.loads((fallo/'ejecucion.json').read_text())
    assert registro['codigo_salida']!=0 and not (R/registro['destino']).exists()
    destino=base/nombre
    cmd=[sys.executable,str(script),'--entrada',str(original),'--politicas',str(politicas),'--fecha-ejecucion','2026-10-19','--salida',str(destino/'productos')]
    p=subprocess.run(cmd,cwd=R,text=True,capture_output=True)
    destino.mkdir(exist_ok=True)
    (destino/'stdout.json').write_text(p.stdout);(destino/'stderr.txt').write_text(p.stderr)
    assert p.returncode==0,p.stderr
    comparacion={nombre_archivo:(destino/'productos'/nombre_archivo).read_bytes()==(referencia/nombre_archivo).read_bytes() for nombre_archivo in ['ventas_validas.csv','reporte_calidad.json','resumen.json']}
    assert all(comparacion.values())
    q=json.loads((destino/'productos/reporte_calidad.json').read_text())
    assert (q['registros_leidos'],q['registros_validos'],q['registros_excluidos'])==(16,13,3)
    x={'escenario_previo':nombre,'tipo':'Ensayo de recuperación con sustitución explícita por fuente válida conocida; no resolución automática del archivo defectuoso','entrada_reanudacion':str(original.relative_to(R)),'politicas_reanudacion':str(politicas.relative_to(R)),'fecha_simulada':'2026-10-19','comando':cmd,'codigo_salida':p.returncode,'coincidencia_con_v2':comparacion,'salida_nueva':str(destino.relative_to(R)),'decision_humana_sobre_datos_reales':'No aplica: prueba sintética; no se eligió entre contenidos conflictivos'}
    (destino/'ejecucion.json').write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
    reanudaciones.append(x)
# Caso vacío sigue siendo éxito técnico, no alerta de margen cero.
vacio=json.loads((R/'06_Pruebas/02_Resultados/P8_sin_validas/productos/resumen.json').read_text())
assert vacio['total']['estado']=='NO EVALUABLE' and vacio['total']['margen_pct'] is None
for ruta,huella in antes.items():assert sha(R/ruta)==huella
assert sha(original)==json.loads((R/'07_Evidencias/01_Integridad_original/integridad_inicial.json').read_text())['sha256_antes_de_organizar']
res={'fecha_real_UTC':datetime.now(timezone.utc).isoformat(),'ejecutor':'Codex con terminal','modalidad':'Auditoría y ensayos sintéticos reales; no aprobación humana de casos comerciales','pipeline_sha256':sha(script),'original_intacto':True,'evidencias_anteriores_intactas':True,'archivos_anteriores_verificados':len(antes),'huellas_anteriores':antes,'P8_confirmado':True,'recuperaciones':reanudaciones,'alcance':'Código y reglas sin cambios. Se repiten controles pertinentes de entrada completa, política y equivalencia. No se declara repetición de P1–P8 completa en esta etapa; permanece su evidencia previa.'}
(base/'auditoria_operacion.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'auditoria':str((base/'auditoria_operacion.json').relative_to(R)),'recuperaciones':len(reanudaciones),'evidencias_anteriores_verificadas':len(antes),'original_intacto':True,'resultado':'Tres ensayos recuperados; salidas idénticas a v2; P8 confirmado'},ensure_ascii=False,indent=2))
