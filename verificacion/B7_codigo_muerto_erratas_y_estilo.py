# B7 · BAJO · Código muerto, erratas y estilo
#
# Qué pasa: README.md:6 dice «Mandani»; hay código que no se usa (_COA en fuzzy_set.py:192-204,
# TRule.get_x en trule.py:20-58, SRule.crisp en srule.py:30-31, el raise inalcanzable de
# polygon.py:44, `_lines` en los __slots__ de Polygon); Parser define __repr__ dos veces
# (operators/parser.py:130-137); Variable.__repr__ oculta el valor 0 (variable.py:135);
# Binary.print_tree pone mal la sangría (operators/binary.py:48,52); Triangular.built_from frente a
# Rect.build_from; la norma de ejemplo max1 se llama `maximum` como la de norms.py.
#
# Solucionado cuando: ninguno de esos restos sigue en el código.
import ast
from _comun import *

inicio('B7', 'Bajo', 'Código muerto, erratas y estilo')

def fuente(rel):
    p = REPO / rel
    return p.read_text(errors='replace') if p.is_file() else None

def definiciones(rel, clase):
    t = fuente(rel)
    if t is None:
        return None
    for nodo in ast.walk(ast.parse(t)):
        if isinstance(nodo, ast.ClassDef) and nodo.name == clase:
            return [n.name for n in nodo.body if isinstance(n, ast.FunctionDef)]
    return []

@prueba('README sin la errata «Mandani»')
def _():
    exigir('Mandani' not in (fuente('README.md') or ''), 'sigue escrito «Mandani»')

for rel, clase, metodo in (('fsets/fuzzy_set.py', 'FuzzySet', '_COA'), ('rules/trule.py', 'TRule', 'get_x'),
                           ('rules/srule.py', 'SRule', 'crisp')):
    @prueba(f'{clase}.{metodo} (sin uso) eliminado')
    def _(rel=rel, clase=clase, metodo=metodo):
        d = definiciones(rel, clase)
        if d is None:
            return 'el archivo ya no existe'
        exigir(metodo not in d, f'sigue en {rel}')

@prueba('Parser define __repr__ una sola vez')
def _():
    d = definiciones('operators/parser.py', 'Parser')
    if d is None:
        return 'el archivo ya no existe'
    exigir(d.count('__repr__') <= 1, f'__repr__ aparece {d.count("__repr__")} veces')

@prueba('Polygon sin el raise inalcanzable «interval not found» ni `_lines`')
def _():
    t = fuente('fsets/polygon.py') or ''
    exigir("'interval not found'" not in t, 'sigue el raise inalcanzable')
    exigir("'_lines'" not in t, 'sigue `_lines` en __slots__')

@prueba('repr de una Variable con valor 0 muestra el 0')
def _():
    v = var('t')
    v.value = 0
    exigir('0' in repr(v).replace('t(', ''), f'repr = {v!r}')

@prueba('print_tree sangra los hijos después del prefijo')
def _():
    r = list(bloque(['if temp is hot and temp is cold then tm is large'], escenario()).rules)[0]
    _, out, _ = capturar(lambda: r._antecedent.print_tree('>'))
    hojas = [l for l in out.splitlines() if 'IS' in l and 'AND' not in l]
    exigir(hojas and all(l.startswith('>') for l in hojas), f'salida: {out!r}')

@prueba('Triangular usa build_from, como Rect')
def _():
    T = fz('Triangular')
    exigir(hasattr(T, 'build_from'), 'no existe Triangular.build_from')

fin()
