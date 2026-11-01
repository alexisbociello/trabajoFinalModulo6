"""Repite P1-P8 y detenciones en una carpeta nueva sin tocar evidencias previas."""
from pathlib import Path
import argparse,tempfile,shutil,subprocess,json,sys,hashlib
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--destino',type=Path);args=p.parse_args()
if args.destino:
    T=args.destino.resolve()
    if T.exists():raise SystemExit('El destino debe ser nuevo.')
    T.mkdir(parents=True)
else:T=Path(tempfile.mkdtemp(prefix='horizonte_reproduccion_'))
archivos=['01_Original_ventas_PROTEGIDO/ventas_original.csv','04_Trabajo/03_Pipeline/pipeline.py','06_Pruebas/verificar_pipeline.py']
archivos += [str(x.relative_to(R)) for x in (R/'02_Insumos/02_Politicas').glob('*.md')]
archivos += [str(x.relative_to(R)) for x in (R/'06_Pruebas/01_Entradas').glob('*.csv')]
for ruta in archivos:
    d=T/ruta;d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/ruta,d)
(T/'06_Pruebas/03_Matriz_y_revision').mkdir(parents=True)
comando=[sys.executable,str(T/'06_Pruebas/verificar_pipeline.py')]
resultado=subprocess.run(comando,cwd=T,text=True,capture_output=True)
(T/'stdout.json').write_text(resultado.stdout);(T/'stderr.txt').write_text(resultado.stderr)
registro={'comando':comando,'codigo_salida':resultado.returncode,'fuente_pipeline_sha256':hashlib.sha256((R/'04_Trabajo/03_Pipeline/pipeline.py').read_bytes()).hexdigest(),'destino_nuevo':str(T),'nota':'Los archivos del repositorio y evidencias originales no se sobrescriben.'}
(T/'reproduccion.json').write_text(json.dumps(registro,ensure_ascii=False,indent=2)+'\n')
if resultado.returncode:
    print(resultado.stderr,file=sys.stderr);raise SystemExit(resultado.returncode)
print(json.dumps({'estado':'11 controles aprobados en copia nueva','directorio':str(T),'resultado':json.loads(resultado.stdout)},ensure_ascii=False,indent=2))
