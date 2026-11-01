"""Pruebas de evidencia Git, comparacion y entrega usando copias temporales."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]


class HerramientasTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='rednova con espacios ')
        self.root = Path(self.tmp.name) / 'caso'
        self.root.mkdir()
        for directory in ('scripts', 'src', 'datos', 'config'):
            shutil.copytree(ROOT / directory, self.root / directory,
                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        for name in ('requirements.lock', 'Dockerfile', '.dockerignore'):
            shutil.copy2(ROOT / name, self.root / name)
        (self.root / '.gitignore').write_text('salidas/\nentregas/\n__pycache__/\n*.pyc\n', encoding='utf-8')

    def tearDown(self):
        self.tmp.cleanup()

    def command(self, *args, expected=0):
        result = subprocess.run(args, cwd=self.root, capture_output=True, text=True,
                                encoding='utf-8', errors='replace', check=False)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def script(self, name, *args, expected=0):
        return self.command(sys.executable, '-B', 'scripts/' + name, *args, expected=expected)

    def init_git(self):
        self.command('git', 'init')
        self.command('git', 'config', '--local', 'user.name', 'Equipo de prueba')
        self.command('git', 'config', '--local', 'user.email', 'equipo@example.invalid')
        self.command('git', 'add', '.')
        self.command('git', 'commit', '-m', 'Version inicial de prueba')

    @unittest.skipUnless(shutil.which('git'), 'Git no disponible en este equipo')
    def test_corrida_identifica_commit_y_no_ensucia_repositorio(self):
        self.init_git()
        self.script('ejecutar.py', 'local', '--nombre', 'local_v1')
        evidence = json.loads((self.root / 'salidas/local_v1/ejecucion.json').read_text())
        expected = self.command('git', 'rev-parse', 'HEAD').stdout.strip()
        self.assertEqual(evidence['git_inicio']['commit'], expected)
        self.assertEqual(evidence['git_fin']['commit'], expected)
        self.assertTrue(evidence['git_inicio']['arbol_limpio'])
        self.assertTrue(evidence['git_fin']['arbol_limpio'])

    def test_comparacion_distingue_local_y_rechaza_misma_corrida(self):
        for name in ('local_1', 'local_2'):
            self.script('ejecutar.py', 'local', '--nombre', name)
        result = self.script('comparar.py', 'salidas/local_1', 'salidas/local_2')
        report = json.loads(result.stdout)
        self.assertTrue(report['reproducibilidad_comprobada'])
        self.assertEqual(report['modos_observados'], ['local', 'local'])
        self.assertFalse(report['contraste_local_docker'])
        self.script('comparar.py', 'salidas/local_1', 'salidas/local_1', expected=2)

    @unittest.skipUnless(shutil.which('git'), 'Git no disponible en este equipo')
    def test_entrega_conserva_git_y_construccion_sin_copiar_config_git(self):
        self.init_git()
        self.script('ejecutar.py', 'local', '--nombre', 'local_v1')
        build = self.root / 'salidas/construccion_prueba'
        build.mkdir()
        # Registro artificial limitado a comprobar empaquetado; no acredita Docker real.
        (build / 'construccion.json').write_text('{"codigo_salida": 1}\n', encoding='utf-8')
        (build / 'consola.txt').write_text('Fallo simulado de construccion para esta prueba\n', encoding='utf-8')
        self.script('entregar.py', '--nombre', 'EquipoPrueba', '--corridas', 'local_v1')
        with zipfile.ZipFile(self.root / 'entregas/EquipoPrueba.zip') as archive:
            names = set(archive.namelist())
            self.assertIn('EquipoPrueba/salidas/construccion_prueba/construccion.json', names)
            self.assertIn('EquipoPrueba/.gitignore', names)
            self.assertIn('EquipoPrueba/evidencia_git/historial.txt', names)
            state = json.loads(archive.read('EquipoPrueba/evidencia_git/estado.json'))
            self.assertTrue(state['disponible'])
            self.assertTrue(state['arbol_limpio'])
            self.assertFalse(any('/.git/' in name for name in names))


if __name__ == '__main__':
    unittest.main()
