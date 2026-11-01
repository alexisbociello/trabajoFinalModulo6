"""Construye, ejecuta y compara Docker real; preserva intentos anteriores."""
from pathlib import Path
import subprocess,json,hashlib,sys,platform
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[2]
D=Path(__file__).resolve().parent
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
E=R/'07_Evidencias/03_Consola_y_versiones/docker'/stamp;E.mkdir(parents=True)
def run(nombre,cmd):
    p=subprocess.run(cmd,cwd=R,text=True,capture_output=True)
    (E/(nombre+'.stdout')).write_text(p.stdout);(E/(nombre+'.stderr')).write_text(p.stderr)
    (E/(nombre+'.json')).write_text(json.dumps({'comando':cmd,'codigo_salida':p.returncode,'fecha_UTC':datetime.now(timezone.utc).isoformat()},ensure_ascii=False,indent=2)+'\n')
    if p.returncode:raise RuntimeError(f'{nombre}: {p.stderr}')
    return p.stdout
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
original=R/'01_Original_ventas_PROTEGIDO/ventas_original.csv';inicial=sha(original)
assert sha(D/'pipeline.py')==sha(R/'04_Trabajo/03_Pipeline/pipeline.py')
assert sha(D/'datos/ventas_original.csv')==inicial
for p in (D/'politicas').glob('*.md'):assert sha(p)==sha(R/'02_Insumos/02_Politicas'/p.name)
version=json.loads(run('docker_version',['docker','version','--format','{{json .}}']))
run('construccion',['docker','build','--progress=plain','--tag','horizonte-modulo6:1.0.0',str(D)])
imagen=json.loads(run('imagen',['docker','image','inspect','horizonte-modulo6:1.0.0']))[0]
id_imagen=imagen['Id']
python_docker=run('python_contenedor',['docker','run','--rm','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--entrypoint','python',id_imagen,'--version']).strip()
comparaciones=[]
for fecha,v in [('2026-10-18','v1'),('2026-10-19','v2')]:
    padre=R/f'05_Ejecuciones/02_Docker/{fecha}_{v}'/stamp;padre.mkdir(parents=True)
    cmd=['docker','run','--rm','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--mount',f'type=bind,src={padre},dst=/salidas',id_imagen,'--entrada','/app/datos/ventas_original.csv','--politicas','/app/politicas','--fecha-ejecucion',fecha,'--salida','/salidas/productos']
    stdout=run('ejecucion_'+v,cmd)
    paquete=json.loads(stdout)
    local=R/f'05_Ejecuciones/01_Python/{fecha}_{v}/ejecucion_01'
    out=padre/'productos'
    archivos={}
    for nombre in ['ventas_validas.csv','reporte_calidad.json','resumen.json']:
        iguales=(out/nombre).read_bytes()==(local/nombre).read_bytes()
        archivos[nombre]={'identicos_byte_a_byte':iguales,'sha256_python':sha(local/nombre),'sha256_docker':sha(out/nombre)}
        assert iguales,(v,nombre)
    assert paquete['resumen']==json.loads((out/'resumen.json').read_text())
    comparaciones.append({'fecha':fecha,'politica':v,'salida_python':str(local.relative_to(R)),'salida_docker':str(out.relative_to(R)),'archivos':archivos,'coinciden_resultados_y_decisiones':True})
assert sha(original)==inicial
manifiesto={'fecha_real_UTC':datetime.now(timezone.utc).isoformat(),'ejecutor':'Codex mediante terminal y Docker Desktop local','modalidad':'Ejecución real Docker, no demostración docente','imagen_id':id_imagen,'imagen_repotags':imagen.get('RepoTags'),'arquitectura':imagen['Architecture'],'sistema_contenedor':imagen['Os'],'base_fijada':(D/'Dockerfile').read_text().splitlines()[0],'docker_client':version['Client']['Version'],'docker_engine':version['Server']['Version'],'python_local':platform.python_version(),'python_docker':python_docker,'original_intacto':True,'archivos_paquete_sha256':{str(p.relative_to(D)):sha(p) for p in [D/'Dockerfile',D/'pipeline.py',D/'datos/ventas_original.csv',*sorted((D/'politicas').glob('*.md'))]},'comparaciones':comparaciones,'logs':str(E.relative_to(R)),'limites':'Comprueba ambas ejecuciones base; no acredita una repetición de P1–P8 dentro de Docker.'}
(E/'manifiesto.json').write_text(json.dumps(manifiesto,ensure_ascii=False,indent=2)+'\n')
comp=R/'05_Ejecuciones/03_Comparaciones'/f'python_docker_{stamp}.json'
comp.write_text(json.dumps(manifiesto,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'comparacion':str(comp.relative_to(R)),'logs':str(E.relative_to(R)),'imagen':id_imagen,'python_docker':python_docker,'resultado':'Las dos ejecuciones Docker coinciden byte a byte con Python; original intacto.'},ensure_ascii=False,indent=2))
