"""Empaqueta solo productos y evidencias evaluables de Horizonte."""
from pathlib import Path
from datetime import datetime,timezone
import tempfile,shutil,json,hashlib,zipfile,os
R=Path(__file__).resolve().parents[1]
NAME='Modulo6_Equipo_GrupoF'
TMP=Path(tempfile.mkdtemp(prefix='horizonte_entrega_docente_'));D=TMP/NAME;D.mkdir()
# Mantener rutas originales para reproducibilidad y referencias de evidencias.
seleccion=['00_Consigna','08_Informe/01_Borradores/fuentes_pdf','01_Original_ventas_PROTEGIDO','02_Insumos/01_Reglas_y_contrato','02_Insumos/02_Politicas','02_Insumos/05_Pruebas_provistas/documento_no_confiable_prueba.md','04_Trabajo','05_Ejecuciones','06_Pruebas','07_Evidencias/cierre_final_20261111.json','07_Evidencias/01_Integridad_original','07_Evidencias/03_Consola_y_versiones','07_Evidencias/04_Calculos_independientes','08_Informe/03_PDF_final/Informe_Final_Modulo6_GrupoF.pdf','08_Informe/01_Borradores/informe_final_editable.md','08_Informe/02_Anexos_y_reflexiones','10_Entregables_por_etapa']
for rel in seleccion:
 p=R/rel;q=D/rel;q.parent.mkdir(parents=True,exist_ok=True)
 if p.is_dir():shutil.copytree(p,q,ignore=shutil.ignore_patterns('.DS_Store','.gitkeep','__pycache__','*.pyc'))
 else:shutil.copy2(p,q)
bitacoras=['diagnostico_v1.md','pipeline_v1.md','analista_v1_v2.md','docker_v1.md','supervision_y_recuperacion_v1.md']
for nombre in bitacoras:
 q=D/'07_Evidencias/02_Bitacora'/nombre;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/'07_Evidencias/02_Bitacora'/nombre,q)
(D/'README.md').write_text((R/'09_Entrega/README_PARA_DOCENTE.md').read_text())
# Retirar directorios vacíos que no representan un producto ni evidencia.
for p in sorted(D.rglob('*'),key=lambda x:len(x.parts),reverse=True):
 if p.is_dir() and not any(p.iterdir()):p.rmdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=sorted(p for p in D.rglob('*') if p.is_file())
m={'equipo':'Grupo F','integrantes':['Alexis Gonzalez','Alexia Orce','Georgina Sicco','Luis Morales'],'fecha_UTC':datetime.now(timezone.utc).isoformat(),'estado':'Versión final: cuatro reflexiones integradas y aportes declarados registrados','inventario':[{'ruta':str(p.relative_to(D)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]}
(D/'MANIFIESTO_ENTREGA.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');files.append(D/'MANIFIESTO_ENTREGA.json')
(D/'SHA256SUMS.txt').write_text(''.join(f'{sha(p)}  {p.relative_to(D)}\n' for p in sorted(files)))
z=R/'09_Entrega/01_ZIP'/f'{NAME}.zip';z.parent.mkdir(parents=True,exist_ok=True);zt=z.with_suffix('.nuevo.zip')
with zipfile.ZipFile(zt,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as f:
 for p in [D]+sorted(D.rglob('*')):f.write(p,str(p.relative_to(D.parent)))
with zipfile.ZipFile(zt) as f:
 assert f.testzip() is None
 for line in f.read(NAME+'/SHA256SUMS.txt').decode().splitlines():
  h,n=line.split('  ',1);assert hashlib.sha256(f.read(NAME+'/'+n)).hexdigest()==h
zt.replace(z)
print(json.dumps({'zip':str(z.relative_to(R)),'archivos':len(m['inventario']),'bytes':z.stat().st_size,'sha256':sha(z)},ensure_ascii=False,indent=2))

shutil.rmtree(TMP)
