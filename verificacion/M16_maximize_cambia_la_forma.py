# M16 · MEDIO · maximize con un número da otra forma
#
# Qué pasa: fsets/fuzzy_set.py:289-293 llama a _operation(maximum, número), que en Polygon
# (polygon.py:161-163) solo aplica max a los vértices, sin añadir los cruces (al revés que
# Polygon.minimize, polygon.py:135-150). Ejecutado: Polygon((0,0),(5,1),(10,0)).maximize(0.5) vale 0.6
# en x = 1, cuando debería valer 0.5.
#
# Solucionado cuando: maximize(w) de Polygon, Triangular y Trapezoid coincide punto a punto con
# max(μ(x), w), y su área es la correcta.
from _comun import *

inicio('M16', 'Medio', 'maximize con un número cambia la forma')

XS = [i / 20 for i in range(-20, 221)]
FORMAS = {'Polygon': lambda: fz('Polygon')((0, 0), (5, 1), (10, 0)),
          'Triangular': lambda: fz('Triangular')((0, 0), (5, 1), (10, 0)),
          'Trapezoid': lambda: fz('Trapezoid')((0, 0), (3, 1), (6, 1), (10, 0))}

for nombre in FORMAS:
    @prueba(f'{nombre}.maximize(0.5) == max(μ(x), 0.5) en [-1, 11]')
    def _(nombre=nombre):
        c = FORMAS[nombre]()
        m = c.maximize(0.5)
        e = max(abs(m(x) - max(c(x), 0.5)) for x in XS)
        exigir(e < 1e-9, f'error máximo {e:.4f}')

@prueba('Área de Polygon((0,0),(5,1),(10,0)).maximize(0.5) en [0, 10] = 6.25')
def _():
    m = fz('Polygon')((0, 0), (5, 1), (10, 0)).maximize(0.5)
    return cerca(m.area(), 6.25, 1e-6, 'área')

fin()
