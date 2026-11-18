# M17 · MEDIO · Polygon.complement ignora su argumento
#
# Qué pasa: fsets/polygon.py:59 hace `cnorm = self.cnorm or ...` en lugar de `cnorm or self.cnorm`:
# la norma que se pasa nunca se usa. Además el resultado se construye con _quick_build_ y pierde las
# normas del original.
# Origen: F11 de Penumbra.
#
# Solucionado cuando: complement(norma) usa la norma pasada en Polygon, Triangular y Trapezoid, sin
# argumento sigue usando 1 - μ, y el complemento conserva las normas del conjunto original.
from _comun import *

inicio('M17', 'Medio', 'Polygon.complement ignora su argumento')

yager2 = lambda v: (1 - v ** 2) ** 0.5
FORMAS = {'Polygon': lambda: fz('Polygon')((0, 0.2), (5, 0.5), (10, 0.9)),
          'Triangular': lambda: fz('Triangular')((0, 0.1), (5, 0.6), (10, 0.1)),
          'Trapezoid': lambda: fz('Trapezoid')((0, 0.1), (3, 0.6), (6, 0.6), (10, 0.1))}

for nombre in FORMAS:
    @prueba(f'{nombre}.complement(Yager w=2) usa esa norma en los vértices')
    def _(nombre=nombre):
        c = FORMAS[nombre]()
        comp = c.complement(yager2)
        for x, y in list(c):
            cerca(comp(x), yager2(y), 1e-9, f'en x = {x}')

@prueba('complement con una norma constante 0.123 da 0.123 en todos los vértices')
def _():
    c = fz('Polygon')((0, 0.5), (1, 0.5))
    comp = c.complement(lambda v: 0.123)
    for x in (0, 0.5, 1):
        cerca(comp(x), 0.123, 1e-12, f'en x = {x}')

@prueba('Control: sin argumento sigue siendo 1 - μ')
def _():
    c = fz('Polygon')((0, 0.2), (1, 0.7))
    return cerca((~c)(1), 0.3, 1e-12, '~c(1)')

@prueba('El complemento conserva la T-norma del original (PROD)')
def _():
    prod = fz('get_norm')('PROD')
    c = fz('Polygon')((0, 0), (5, 1), (10, 0))
    c.tnorm = prod
    exigir(c.complement().tnorm is prod, 'la T-norma vuelve a la de por defecto')

fin()
