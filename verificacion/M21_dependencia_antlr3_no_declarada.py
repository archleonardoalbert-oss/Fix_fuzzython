# M21 · MEDIO · Dependencia antlr3 no declarada ni instalable desde PyPI
#
# Qué pasa: store/reader.py:8 importa antlr3 y sample.py:1 importa store.reader en la primera línea.
#   - setup.py no declara la dependencia.
#   - En PyPI solo existe antlr_python_runtime 3.1.3, que es para Python 2. El runtime de ANTLR 3.5 para
#     Python 3 solo está en GitHub. Sin él, sample.py falla antes de llegar a la parte de Python.
#   - El comentario de reader.py:12-14 («change AL method by AT») está desfasado.
#
# Solucionado cuando: la parte Python funciona sin antlr3, y la lectura de FCL funciona en un entorno
# limpio instalando solo lo que declara el paquete (o ya no necesita antlr3).
# Nota: la última prueba crea un entorno temporal e instala desde PyPI: necesita red y ~1 minuto.
import re, shutil, subprocess, sys, tempfile
from pathlib import Path
from _comun import *

inicio('M21', 'Medio', 'Dependencia antlr3 no declarada')

LEER = 'r = numero(fcl().compute({"temp": 38})); print("OK", r)'

@prueba('Control: sin antlr3, la parte Python (Mamdani) importa y calcula, y no carga antlr3', t=60)
def _():
    r = aislado('print(numero(mamdani().compute({"temp": 33}))); import sys; print("antlr3" in sys.modules)',
                sin_antlr=True, parche_clock=True)
    exigir(r.returncode == 0, r.stderr.strip()[-200:])
    lineas = r.stdout.split()
    exigir(lineas[-1] == 'False', 'importar la parte Python carga antlr3')

def lee_sin_antlr():
    r = aislado(LEER, sin_antlr=True, parche_clock=True)
    return r.returncode == 0 and 'OK' in r.stdout

def dependencias_declaradas():
    texto = ''
    for n in ('pyproject.toml', 'setup.py', 'setup.cfg'):
        if (REPO / n).is_file():
            texto += (REPO / n).read_text()
    return [l for l in re.findall(r'["\']([A-Za-z0-9_.\-]*antlr[A-Za-z0-9_.\-]*[^"\']*)["\']', texto)]

@prueba('Si leer FCL necesita antlr3, el paquete declara esa dependencia', t=60)
def _():
    if lee_sin_antlr():
        return 'lee FCL sin antlr3: no hace falta declararla'
    deps = dependencias_declaradas()
    exigir(deps, 'leer FCL necesita antlr3 y ni pyproject.toml, ni setup.py, ni setup.cfg la declaran')
    return 'declarada: ' + ', '.join(deps)

@prueba('El comentario desfasado «change AL method by AT» ya no está')
def _():
    exigir(not any('AL method' in p.read_text(errors='replace') for p in REPO.rglob('*.py') if '.git' not in p.parts),
           'sigue en store/reader.py')

@prueba('En un entorno limpio, instalando solo lo declarado desde PyPI, se lee un FCL', t=600)
def _():
    if lee_sin_antlr():
        return 'lee FCL sin antlr3'
    deps = dependencias_declaradas()
    exigir(deps, 'no hay dependencia declarada que instalar')
    tmp = Path(tempfile.mkdtemp(prefix='fz_m21_'))
    try:
        subprocess.run([sys.executable, '-m', 'venv', str(tmp / 'venv')], check=True, capture_output=True)
        py = str(tmp / 'venv' / 'bin' / 'python')
        r = subprocess.run([py, '-m', 'pip', 'install', '-q', *deps], capture_output=True, text=True, timeout=500)
        exigir(r.returncode == 0, 'pip no instala ' + ' '.join(deps) + ': ' + r.stderr.strip()[-200:])
        pre = (f'import sys\nsys.path.insert(0, {str(AQUI)!r})\nimport os\nos.environ["FZ_SIN_ANTLR"] = "1"\n'
               f'os.environ["FUZZYTHON_REPO"] = {str(REPO)!r}\nfrom _comun import *\n')
        r = subprocess.run([py, '-c', pre + LEER], capture_output=True, text=True, timeout=120, cwd=str(tmp))
        exigir(r.returncode == 0 and 'OK' in r.stdout, 'no lee el FCL: ' + r.stderr.strip()[-200:])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

fin()
