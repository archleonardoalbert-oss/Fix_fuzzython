# C1 · CRÍTICO · El paquete no se puede instalar ni importar
#
# Qué pasa: todos los módulos importan desde la raíz del repo como si estuviera en sys.path
# (`from fsets.fuzzy_set import ...`, `from utils import norm`, ...). Por eso:
#   - `from fuzzython.systems.mamdani import MamdaniSystem` falla con ModuleNotFoundError.
#   - `pip install .` mete en site-packages seis paquetes genéricos (fsets, norms, operators, rules,
#     store, systems) y no instala `fuzzython` ni los módulos sueltos (adjective, variable, ...).
#   - Un `utils.py`, `rules.py`, etc. del usuario tapa los de fuzzython.
#   - setup.py importa distutils (retirado en Python 3.12) y apunta a un LICENSE.txt que no existe.
# Dónde: setup.py:1,8,11 y los import de todos los archivos (README, C1).
#
# Solucionado cuando: se instala con pip en un entorno limpio, se importa como `fuzzython` desde
# cualquier carpeta, no instala nombres genéricos de primer nivel, no le afectan módulos del usuario
# con nombres comunes y un sistema Mamdani calcula con la copia instalada.
# Nota: la prueba de pip crea un entorno temporal y descarga setuptools: necesita red y ~1 minuto.
import shutil, subprocess, sys, tempfile, textwrap
from pathlib import Path
from _comun import *

inicio('C1', 'Crítico', 'No se puede instalar ni importar como paquete')

CLASES = ['MamdaniSystem', 'SugenoSystem', 'TsukamotoSystem', 'RuleBlock', 'Variable', 'Adjective',
          'Polygon', 'Trapezoid', 'Triangular', 'Gaussian', 'Singleton', 'Interval', 'get_norm']
IMPORTAR = textwrap.dedent(f'''
    import importlib, fuzzython
    RUTAS = {RUTAS!r}
    fallan = []
    for n in {CLASES!r}:
        try:
            if not hasattr(fuzzython, n):
                getattr(importlib.import_module('fuzzython.' + RUTAS[n]), n)
        except Exception as e:
            fallan.append(f'{{n}} ({{type(e).__name__}}: {{e}})')
    print('; '.join(fallan))
''')

def base_paquete():
    for b in (REPO / 'src', REPO.parent, REPO):
        if (b / 'fuzzython' / '__init__.py').is_file():
            return b
    raise Falla('no hay ninguna carpeta fuzzython/ con __init__.py')

def python_con(rutas, codigo, py=sys.executable, cwd=None):
    pre = 'import sys\nsys.dont_write_bytecode = True\n' + ''.join(f'sys.path.insert(0, {str(r)!r})\n' for r in reversed(rutas))
    pre += 'import time\nif not hasattr(time, "clock"): time.clock = time.perf_counter\n'  # aislar de C2
    with tempfile.TemporaryDirectory() as d:
        return subprocess.run([py, '-I', '-c', pre + codigo], cwd=cwd or d, capture_output=True, text=True, timeout=300)

@prueba('Con solo la carpeta del paquete en sys.path se importan todas las clases públicas', t=60)
def _():
    r = python_con([base_paquete()], IMPORTAR)
    exigir(r.returncode == 0, r.stderr.strip().splitlines()[-1] if r.stderr.strip() else f'código {r.returncode}')
    exigir(not r.stdout.strip(), 'fallan: ' + r.stdout.strip())

@prueba('Módulos del usuario llamados utils, rules, store, systems, interval... no rompen la importación', t=60)
def _():
    with tempfile.TemporaryDirectory() as usuario:
        for n in ('utils', 'rules', 'store', 'systems', 'operators', 'norms', 'interval', 'variable',
                  'adjective', 'predicate', 'ruleblock', 'fsets'):
            Path(usuario, n + '.py').write_text('raise ImportError("este es un módulo del usuario")\n')
        r = python_con([usuario, base_paquete()], IMPORTAR)
    exigir(r.returncode == 0, r.stderr.strip().splitlines()[-1] if r.stderr.strip() else f'código {r.returncode}')
    exigir(not r.stdout.strip(), 'fallan: ' + r.stdout.strip())

ESTADO = {}

@prueba('pip install en un entorno limpio termina bien', t=600)
def _():
    tmp = Path(tempfile.mkdtemp(prefix='fz_c1_'))
    ESTADO['tmp'] = tmp
    copia = tmp / 'fuzzython'
    shutil.copytree(REPO, copia, ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc'))
    subprocess.run([sys.executable, '-m', 'venv', str(tmp / 'venv')], check=True, capture_output=True)
    py = tmp / 'venv' / 'bin' / 'python'
    sp = Path(subprocess.run([str(py), '-c', 'import sysconfig;print(sysconfig.get_paths()["purelib"])'],
                             capture_output=True, text=True).stdout.strip())
    antes = set(p.name for p in sp.iterdir())
    r = subprocess.run([str(py), '-m', 'pip', 'install', '-q', str(copia)], capture_output=True, text=True, timeout=500)
    exigir(r.returncode == 0, 'pip falla: ' + ' | '.join(r.stderr.strip().splitlines()[-3:]))
    ESTADO.update(py=py, nuevos=sorted(set(p.name for p in sp.iterdir()) - antes))
    return 'instalado: ' + ', '.join(ESTADO['nuevos'])

@prueba('La instalación no añade paquetes de primer nivel con nombres genéricos')
def _():
    exigir('nuevos' in ESTADO, 'la instalación anterior falló')
    raros = [n for n in ESTADO['nuevos'] if not n.lower().startswith('fuzzython') and not n.endswith('.pth')]
    exigir(not raros, 'instala además: ' + ', '.join(raros))

@prueba('Con la copia instalada: import fuzzython y un Mamdani completo desde otra carpeta', t=120)
def _():
    exigir('py' in ESTADO, 'la instalación anterior falló')
    codigo = IMPORTAR + textwrap.dedent('''
        import importlib, fuzzython
        def fz(n):
            return getattr(fuzzython, n) if hasattr(fuzzython, n) else getattr(importlib.import_module('fuzzython.' + RUTAS[n]), n)
        A, P, RB, M = fz('Adjective'), fz('Polygon'), fz('RuleBlock'), fz('MamdaniSystem')
        V = fz('Variable')
        def var(n, *a, **k):
            try: return V(n, *a, unit='u', **k)
            except TypeError: return V(n, 'u', *a, **k)
        hot = A('hot', P((30, 0), (35, 1), (40, 1))); temp = var('temp', hot)
        large = A('large', P((25, 0), (30, 1), (40, 1))); tm = var('tm', large, defuzzification='COG', default=0)
        b = RB('b'); b.add_rules('if temp is hot then tm is large', scope=dict(hot=hot, temp=temp, large=large, tm=tm))
        r = M('m', b).compute({'temp': 38})
        while isinstance(r, dict): r = next(iter(r.values()))
        print('RESULTADO', r)
    ''')
    r = python_con([], codigo, py=str(ESTADO['py']))
    shutil.rmtree(ESTADO['tmp'], ignore_errors=True)
    exigir(r.returncode == 0, ' | '.join(r.stderr.strip().splitlines()[-2:]))
    lineas = r.stdout.strip().splitlines()
    exigir(lineas and lineas[0] == '', 'fallan: ' + (lineas[0] if lineas else '?'))
    v = float(lineas[-1].split()[-1])
    return cerca(v, 33.6666666, 1e-3, 'Mamdani instalado')

fin()
