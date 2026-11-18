"""Utilidades compartidas por los scripts de verificación. No es una prueba: no lo ejecutes.

Cada script de esta carpeta comprueba UN fallo del README. Se ejecuta así:

    python3 verificacion/C5_trapezoid_desdifusion_falla_y_es_falsa.py [ruta-al-repo]

Sin ruta, usa ../fuzzython. Al final imprime SOLUCIONADO o NO SOLUCIONADO y sale con código 0 o 1.

Cómo encuentra la librería:
  1. Primero intenta importarla como paquete (`import fuzzython`), que es lo correcto.
  2. Si eso falla (C1 sin arreglar), mete la raíz del repo en sys.path e importa los módulos sueltos.
Así las pruebas de cada fallo siguen funcionando antes y después de arreglar C1.

Para que un fallo no tape a los demás, aquí se parchea time.clock si falta (C2). El script de C2 lo
comprueba aparte, en un proceso sin ese parche.
"""
import contextlib
import importlib
import io
import math
import os
import signal
import subprocess
import sys
import tempfile
import textwrap
import time
import warnings
from functools import reduce
from pathlib import Path

sys.dont_write_bytecode = True          # no dejar __pycache__ dentro del repo
warnings.simplefilter('ignore')         # B6 comprueba los avisos aparte

AQUI = Path(__file__).resolve().parent
_ARG = next((a for a in sys.argv[1:] if not a.startswith('-')), None)
REPO = Path(_ARG or os.environ.get('FUZZYTHON_REPO') or AQUI.parent / 'fuzzython').resolve()
VENDOR = AQUI / '_vendor'               # runtime antlr3 para Python 3 (no está en PyPI)

if not hasattr(time, 'clock') and not os.environ.get('FZ_SIN_PARCHE'):
    time.clock = time.perf_counter

# Dónde vive cada nombre público hoy. Si tras el arreglo se exporta desde `fuzzython`, se usa eso.
RUTAS = {
    'Adjective': 'adjective', 'Variable': 'variable', 'RuleBlock': 'ruleblock', 'Predicate': 'predicate',
    'Interval': 'interval', 'Compound': 'interval',
    'MamdaniSystem': 'systems.mamdani', 'SugenoSystem': 'systems.sugeno', 'TsukamotoSystem': 'systems.tsukamoto',
    'FuzzySet': 'fsets.fuzzy_set', 'Polygon': 'fsets.polygon', 'Trapezoid': 'fsets.trapezoid',
    'Triangular': 'fsets.triangular', 'Gaussian': 'fsets.gaussian', 'Gamma': 'fsets.gamma',
    'Singleton': 'fsets.singleton', 'SFunction': 'fsets.sfunction', 'ZFunction': 'fsets.zfunction',
    'PiFunction': 'fsets.pifunction', 'Polynomial': 'fsets.polynomial',
    'Rule': 'rules.rule', 'And': 'operators._and', 'Or': 'operators._or', 'Not': 'operators._not',
    'get_norm': 'norms.norms', 'load_from_string': 'store.reader', 'load_from_file': 'store.reader',
}


def _decidir_modo():
    for base in (REPO / 'src', REPO.parent, REPO):
        if not (base / 'fuzzython' / '__init__.py').is_file():
            continue
        sys.path.insert(0, str(base))
        try:
            import fuzzython  # noqa: F401
            if not hasattr(fuzzython, 'MamdaniSystem'):
                importlib.import_module('fuzzython.' + RUTAS['MamdaniSystem'])
            return 'paquete', base
        except Exception:
            sys.path.remove(str(base))
            for m in [m for m in sys.modules if m == 'fuzzython' or m.startswith('fuzzython.')]:
                del sys.modules[m]
    sys.path.insert(0, str(REPO))
    return 'raiz', REPO


MODO, BASE = _decidir_modo()
if not os.environ.get('FZ_SIN_ANTLR'):
    sys.path.append(str(VENDOR))


def fz(nombre):
    """Devuelve una clase o función pública de fuzzython por su nombre."""
    if MODO == 'paquete':
        import fuzzython
        if hasattr(fuzzython, nombre):
            return getattr(fuzzython, nombre)
        return getattr(importlib.import_module('fuzzython.' + RUTAS[nombre]), nombre)
    return getattr(importlib.import_module(RUTAS[nombre]), nombre)


# ---------------------------------------------------------------- ejecución de pruebas

class Falla(Exception):
    pass


class _Colgado(BaseException):
    pass


def _alarma(*_):
    raise _Colgado()


_RESULTADOS = []


def inicio(ident, gravedad, titulo):
    modo = 'como paquete fuzzython' if MODO == 'paquete' else 'como módulos sueltos, con la raíz en sys.path'
    print(f'{ident} · {gravedad} · {titulo}')
    print(f'repo: {REPO}  (importado {modo})\n')


def prueba(descripcion, t=10):
    """Decorador: ejecuta la función en el acto, con límite de t segundos, y anota PASA o FALLA."""
    def deco(f):
        out, err = io.StringIO(), io.StringIO()
        signal.signal(signal.SIGALRM, _alarma)
        signal.alarm(t)
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                detalle = f()
            ok = True
        except _Colgado:
            ok, detalle = False, f'no termina en {t} s (bucle infinito)'
        except Falla as e:
            ok, detalle = False, str(e)
        except Exception as e:
            ok, detalle = False, f'lanza {type(e).__name__}: {str(e)[:300]}'
        finally:
            signal.alarm(0)
        _RESULTADOS.append(ok)
        print(f'  [{"PASA " if ok else "FALLA"}] {descripcion}')
        if detalle:
            print(textwrap.indent(textwrap.fill(str(detalle), 100), ' ' * 10))
        return f
    return deco


def fin():
    n, k = len(_RESULTADOS), _RESULTADOS.count(False)
    print()
    if k == 0:
        print(f'RESULTADO: SOLUCIONADO ({n}/{n} pruebas pasan)')
        sys.exit(0)
    print(f'RESULTADO: NO SOLUCIONADO ({k} de {n} pruebas fallan)')
    sys.exit(1)


def exigir(condicion, mensaje):
    if not condicion:
        raise Falla(mensaje)


def cerca(obtenido, esperado, tol=1e-6, que='valor'):
    try:
        ok = abs(float(obtenido) - esperado) <= tol
    except (TypeError, ValueError):
        ok = False
    exigir(ok, f'{que}: se esperaba {esperado:.6g} (±{tol:g}) y se obtuvo {obtenido!r}')
    return f'{que} = {float(obtenido):.6g}'


def espera_error(f, contiene=None, no_valen=()):
    """Exige que f() lance una excepción. `contiene`: palabras que debe mencionar el mensaje."""
    try:
        r = f()
    except _Colgado:
        raise
    except Falla as e:
        raise Falla(f'no lanza ningún error ({e})')
    except Exception as e:
        if no_valen and isinstance(e, no_valen):
            raise Falla(f'lanza {type(e).__name__}: «{e}»; ese error no explica el problema al usuario')
        if contiene and not any(c.lower() in str(e).lower() for c in contiene):
            raise Falla(f'lanza {type(e).__name__}: «{e}», pero el mensaje no menciona {contiene}')
        return e
    raise Falla(f'no lanza ningún error (devuelve {r!r})')


def capturar(f):
    """Ejecuta f() y devuelve (resultado, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        r = f()
    return r, out.getvalue(), err.getvalue()


def numero(resultado):
    """Saca el número de un resultado tipo {'bloque': {'variable': v}} o {'bloque': v} o v."""
    r = resultado
    while isinstance(r, dict):
        if len(r) != 1:
            raise Falla(f'el resultado tiene varias claves: {resultado!r}')
        r = next(iter(r.values()))
    return r


def es_nan(x):
    try:
        return math.isnan(float(x))
    except (TypeError, ValueError):
        return False


def aislado(codigo, opciones=(), parche_clock=False, cwd=None, timeout=300, sin_antlr=False):
    """Ejecuta código en un Python nuevo (-I) con estas mismas utilidades ya importadas."""
    env = dict(os.environ, FUZZYTHON_REPO=str(REPO))
    if not parche_clock:
        env['FZ_SIN_PARCHE'] = '1'
    if sin_antlr:
        env['FZ_SIN_ANTLR'] = '1'
    pre = f'import sys\nsys.path.insert(0, {str(AQUI)!r})\nfrom _comun import *\n'
    with tempfile.TemporaryDirectory() as d:
        return subprocess.run([sys.executable, '-I', '-B', *opciones, '-c', pre + textwrap.dedent(codigo)],
                              cwd=cwd or d, env=env, capture_output=True, text=True, timeout=timeout)


# ---------------------------------------------------------------- escenario de sample.py

def var(nombre, *adjetivos, unidad='u', **kw):
    """Crea una Variable tanto con la firma actual (unit posicional) como con unit por nombre."""
    V = fz('Variable')
    try:
        return V(nombre, *adjetivos, unit=unidad, **kw)
    except TypeError:
        return V(nombre, unidad, *adjetivos, **kw)


def escenario():
    """El ejemplo de sample.py, solo con Polygon para no tropezar con C5."""
    A, P = fz('Adjective'), fz('Polygon')
    cold = A('cold', P((0, 1), (15, 1), (20, 0)))
    normal = A('normal', P((15, 0), (20, 1), (30, 1), (35, 0)))
    hot = A('hot', P((30, 0), (35, 1), (40, 1)))
    short = A('short', P((0, 1), (10, 1), (15, 0)))
    usual = A('usual', P((10, 0), (15, 1), (25, 1), (30, 0)))
    large = A('large', P((25, 0), (30, 1), (40, 1)))
    return dict(cold=cold, normal=normal, hot=hot, short=short, usual=usual, large=large,
                temp=var('temp', cold, normal, hot, unidad='C'),
                tm=var('tm', short, usual, large, unidad='min', defuzzification='COG', default=0))


REGLAS = ['if temp is cold or temp is normal then tm is short with 0.5',
          'if temp is normal then tm is usual',
          'if temp is hot then tm is large']


def bloque(reglas, s, nombre='b', **kw):
    b = fz('RuleBlock')(nombre, **kw)
    b.add_rules(*reglas, scope=s)
    return b


def mamdani(reglas=REGLAS, s=None, **kw):
    return fz('MamdaniSystem')('m', bloque(reglas, s or escenario(), **kw))


def sugeno(reglas, extra=None, **kw):
    s = escenario()
    s.update(extra or {})
    return fz('SugenoSystem')('s', bloque(reglas, s, **kw))


def escenario_tsukamoto():
    A, P = fz('Adjective'), fz('Polygon')
    s = escenario()
    s['short'] = A('short', P((0, 1), (15, 1), (25, 0)))
    s['large'] = A('large', P((15, 0), (25, 1), (40, 1)))
    s['tm'] = var('tm', s['short'], s['large'], unidad='min', defuzzification='COG', default=0)
    return s


def tsukamoto(reglas, s=None):
    return fz('TsukamotoSystem')('t', bloque(reglas, s or escenario_tsukamoto()))


# ---------------------------------------------------------------- cálculo de referencia (sin fuzzython)

def pl(*puntos):
    """Función lineal a trozos independiente de fuzzython; constante fuera de los puntos."""
    def f(x):
        if x <= puntos[0][0]:
            return puntos[0][1]
        if x >= puntos[-1][0]:
            return puntos[-1][1]
        for (a, ya), (b, yb) in zip(puntos, puntos[1:]):
            if x <= b:
                return ya + (yb - ya) * (x - a) / (b - a)
    return f


def integral(f, a, b, n=20000):
    h = (b - a) / n
    return h * (sum(f(a + i * h) for i in range(1, n)) + (f(a) + f(b)) / 2)


def cog(f, a, b, n=20000):
    return integral(lambda x: x * f(x), a, b, n) / integral(f, a, b, n)


def agregado(salidas, act=min, accu=max):
    """salidas = [(conjunto, fuerza)] por consecuente de regla. Devuelve la función acumulada."""
    return lambda x: reduce(accu, [act(f(x), w) for f, w in salidas])


def s_curva(a, c):
    """Función S estándar entre a y c, con el cambio de rama en el punto medio."""
    def f(x):
        if x <= a:
            return 0.0
        if x >= c:
            return 1.0
        t = (x - a) / (c - a)
        return 2 * t * t if t <= 0.5 else 1 - 2 * (1 - t) ** 2
    return f


# ---------------------------------------------------------------- FCL

FCL = '''FUNCTION_BLOCK {tipo} f
VAR_INPUT temp: REAL; END_VAR
VAR_OUTPUT tm: REAL; END_VAR
FUZZIFY temp
 TERM cold := (0, 1) (15, 1) (20, 0);
 TERM hot := (30, 0) (35, 1) (40, 1);
END_FUZZIFY
DEFUZZIFY tm
 TERM short := (0, 1) (10, 1) (15, 0);
 TERM large := (25, 0) (30, 1) (40, 1);
 METHOD: COG;
 DEFAULT := 0;
END_DEFUZZIFY
RULEBLOCK b
 AND: MIN;
 {act}
 ACCU: MAX;
 {reglas}
END_RULEBLOCK
END_FUNCTION_BLOCK'''


def texto_fcl(reglas='RULE 1: IF temp IS hot THEN tm IS large;', tipo='', act='ACT: MIN;'):
    return FCL.format(tipo=tipo, act=act, reglas=reglas)


def fcl(reglas='RULE 1: IF temp IS hot THEN tm IS large;', tipo='', act='ACT: MIN;'):
    return cargar_fcl(texto_fcl(reglas, tipo, act))


def cargar_fcl(texto):
    sistema = fz('load_from_string')(texto)
    exigir(sistema is not None, 'load_from_string devolvió None (no se pudo leer el FCL)')
    return sistema
