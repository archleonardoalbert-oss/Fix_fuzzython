# B2 · BAJO · Variable(nombre, adjetivo) toma el adjetivo como unidad
#
# Qué pasa: variable.py:12 define `__init__(self, name, unit='', *adjectives, ...)`. Como unit es
# posicional, Variable('t', frio, calor) guarda frio como unidad y solo calor como adjetivo, sin error.
#
# Solucionado cuando: pasar adjetivos sin unidad no pierde ninguno (o da un error claro), y la unidad
# se puede seguir indicando (por nombre).
from _comun import *

inicio('B2', 'Bajo', 'Variable toma el adjetivo como unidad')

def adjs():
    A, P = fz('Adjective'), fz('Polygon')
    return A('frio', P((0, 1), (10, 0))), A('calor', P((10, 0), (20, 1)))

@prueba("Variable('t', frio, calor) conserva los dos adjetivos o lanza un error")
def _():
    frio, calor = adjs()
    try:
        v = fz('Variable')('t', frio, calor)
    except Exception as e:
        return f'lanza {type(e).__name__}: {e}'
    exigir(list(v.adjectives) == [frio, calor], f'adjetivos = {[a.name for a in v.adjectives]}, unidad = {v.unit!r}')

@prueba('La unidad nunca es un Adjective')
def _():
    frio, calor = adjs()
    try:
        v = fz('Variable')('t', frio)
    except Exception as e:
        return f'lanza {type(e).__name__}: {e}'
    exigir(not isinstance(v.unit, fz('Adjective')), f'unidad = {v.unit!r}')

def _acepta_unit_kw():
    frio, calor = adjs()
    try:
        fz('Variable')('t', frio, calor, unit='C')
        return True
    except TypeError:
        return False

@prueba("Control: Variable('t', frio, calor, unit='C') funciona y guarda la unidad")
def _():
    frio, calor = adjs()
    v = fz('Variable')('t', frio, calor, unit='C') if _acepta_unit_kw() else fz('Variable')('t', 'C', frio, calor)
    exigir(v.unit == 'C' and len(v.adjectives) == 2, f'unidad {v.unit!r}, {len(v.adjectives)} adjetivos')

fin()
