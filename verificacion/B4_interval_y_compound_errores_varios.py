# B4 · BAJO · Interval y Compound: errores varios
#
# Qué pasa (interval.py):
#   - :47 middle devuelve (max - min)/2, la mitad del ancho (F15).
#   - :164 __eq__ compara _min dos veces: Interval(2,4) == (2,4) da False (F16).
#   - :160-166 define __eq__ sin __hash__: no se puede meter en un set.
#   - :158 `return TypeError(...)` en vez de raise: Interval(0,1) < 5 devuelve un objeto verdadero.
#   - :139-143 __mul__ solo admite float: Interval(0,1) * 2 devuelve None.
#   - :81-82 __bool__ es falso para un intervalo de un punto (el de un Singleton).
#   - :237-261 Compound.union no fusiona los tramos que se solapan.
#   - :72-73 sampling de un intervalo infinito devuelve solo los extremos.
#
# Solucionado cuando: cada operación da el resultado matemático correcto o lanza el error adecuado.
from _comun import *

inicio('B4', 'Bajo', 'Interval y Compound')

I = lambda a, b: fz('Interval')(a, b)

@prueba('Interval(2, 4).middle == 3')
def _():
    return cerca(I(2, 4).middle, 3, 0, 'middle')

@prueba('Interval(2, 4) == (2, 4) y != (2, 5)')
def _():
    exigir(I(2, 4) == (2, 4), 'Interval(2,4) == (2,4) da False')
    exigir(not (I(2, 4) == (2, 5)), 'Interval(2,4) == (2,5) da True')

@prueba('Interval se puede usar en un set y como clave de dict')
def _():
    exigir(len({I(0, 1), I(0, 1), I(1, 2)}) == 2, 'el set no deduplica')

@prueba('Interval(0, 1) < 5 lanza TypeError')
def _():
    espera_error(lambda: I(0, 1) < 5)

@prueba('Interval(0, 1) * 2 == Interval(0, 2), y * -1 == Interval(-1, 0)')
def _():
    exigir((I(0, 1) * 2) == I(0, 2), f'* 2 da {I(0, 1) * 2!r}')
    exigir((I(0, 1) * -1) == I(-1, 0), f'* -1 da {I(0, 1) * -1!r}')

@prueba('Un intervalo de un punto, Interval(3, 3), no está vacío: bool() es True')
def _():
    exigir(bool(I(3, 3)), 'bool(Interval(3, 3)) es False')

@prueba('Compound([0,1], [5,6]) ∪ [0.5, 5.5] == un solo tramo [0, 6]')
def _():
    C = fz('Compound')
    u = C(I(0, 1), I(5, 6)).union(I(0.5, 5.5))
    tramos = list(u) if isinstance(u, C) else [u]
    tramos = [tuple(t) if not isinstance(t, (int, float)) else t for t in tramos]
    exigir(tramos in ([(0, 6)], [0, 6]), f'resultado: {u!r}')

@prueba('sampling de un intervalo infinito lanza un error (no devuelve solo los extremos)')
def _():
    espera_error(lambda: list(fz('Interval')().sampling(1)))

fin()
