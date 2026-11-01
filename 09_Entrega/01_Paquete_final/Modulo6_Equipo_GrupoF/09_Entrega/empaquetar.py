"""Crea paquete y ZIP con inventario. No publica ni modifica el original."""
from pathlib import Path
from datetime import datetime,timezone
import shutil,hashlib,json,zipfile,stat,os
R=Path(__file__).resolve().parents[1]
NOMBRE='Modulo6_Equipo_GrupoF'
D=R/'09_Entrega/01_Paquete_final'/NOMBRE
Z=R/'09_Entrega/02_ZIP'/f'{NOMBRE}.zip'
if D.exists() or Z.exists():raise SystemExit('Ya existe el paquete: preservar el anterior y usar un nombre nuevo.')
D.mkdir(parents=True)
excluir={'.git','.DS_Store','__pycache__','tmp','09_Entrega','06_Recursos_del_caso'}
for p in sorted(R.iterdir()):
 if p.name in excluir:continue
 if p.is_dir():
  # copytree conserva permisos; evitar el modo 0555 de la carpeta canónica hasta terminar.
  shutil.copytree(p,D/p.name,ignore=shutil.ignore_patterns('.DS_Store','__pycache__','*.pyc','Informe_Final_Modulo6_Individual.pdf','Informe_Final_Modulo6_Gonzalez_Orce_Sicco_Morales.pdf'))
 else:shutil.copy2(p,D/p.name)
# Las herramientas de empaquetado quedan disponibles en el paquete sin recursión de resultados.
(D/'09_Entrega').mkdir()
shutil.copy2(Path(__file__),D/'09_Entrega/empaquetar.py')
(D/'09_Entrega/01_Paquete_final').mkdir();(D/'09_Entrega/02_ZIP').mkdir()
archivos=sorted(p for p in D.rglob('*') if p.is_file())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
man={'fecha_UTC':datetime.now(timezone.utc).isoformat(),'equipo':'Grupo F','integrantes':['Alexis Gonzalez','Alexia Orce','Georgina Sicco','Luis Morales'],'estado':'Paquete técnico generado; reflexiones y aportes individuales pendientes','nombre_zip':Z.name,'inventario':[{'ruta':str(p.relative_to(D)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in archivos],'nota':'El inventario no se incluye a sí mismo. SHA256SUMS.txt incluye también este manifiesto; ninguno incluye el checksum para evitar circularidad.'}
(D/'MANIFIESTO_ENTREGA.json').write_text(json.dumps(man,ensure_ascii=False,indent=2)+'\n')
archivos.append(D/'MANIFIESTO_ENTREGA.json')
(D/'SHA256SUMS.txt').write_text(''.join(f'{sha(p)}  {p.relative_to(D)}\n' for p in sorted(archivos)))
Z.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(Z,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in [D]+sorted(D.rglob('*')):
  z.write(p,arcname=str(p.relative_to(D.parent)))
print(json.dumps({'paquete':str(D.relative_to(R)),'zip':str(Z.relative_to(R)),'archivos_inventariados':len(man['inventario']),'bytes_zip':Z.stat().st_size,'sha256_zip':sha(Z)},ensure_ascii=False,indent=2))
