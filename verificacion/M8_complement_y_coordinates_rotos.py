# M8 · MEDIO · complement y coordinates usan self.function, que es None en las subclases
#
# Qué pasa: fsets/fuzzy_set.py:108 y 395. Las subclases construyen con function=None y definen
# __call__, así que (~Gaussian(0,1))(0) lanza TypeError: 'NoneType' object is not callable, y
# coordinates() falla igual.
# Origen: F10 de Penumbra.
#
# Solucionado cuando: el complemento y coordinates() funcionan en todas las formas que no son Polygon
# (Gaussian, Gamma, SFunction, ZFunction, una subclase del usuario) con los valores correctos.
import math
from _comun import *

inicio('M8', 'Medio', 'complement y coordinates rotos en las subclases')

def formas():
    return {'Gaussian': fz('Gaussian')(5, 2), 'SFunction': fz('SFunction')((0, 0), 5, (10, 1)),
            'ZFunction': fz('ZFunction')((0, 0), 5, (10, 1)), 'Gamma': fz('Gamma')(2, 0.5, fz('Interval')(0, 10))}

for nombre in ('Gaussian', 'SFunction', 'ZFunction', 'Gamma'):
    @prueba(f'~{nombre}: vale 1 - μ(x) en 11 puntos')
    def _(nombre=nombre):
        c = formas()[nombre]
        comp = ~c
        for x in range(11):
            cerca(comp(x), 1 - c(x), 1e-12, f'~{nombre}({x})')

    @prueba(f'{nombre}.coordinates(): pares (x, μ(x)) correctos')
    def _(nombre=nombre):
        c = formas()[nombre]
        pares = list(c.coordinates(10))
        exigir(len(pares) >= 10, f'solo {len(pares)} pares')
        exigir(all(abs(y - c(x)) < 1e-12 for x, y in pares), 'algún par no coincide con μ(x)')

@prueba('complement con otra norma (Yager w=2) en una Gaussian')
def _():
    g = fz('Gaussian')(0, 1)
    comp = g.complement(lambda v: (1 - v ** 2) ** 0.5)
    return cerca(comp(1), (1 - math.exp(-0.5) ** 2) ** 0.5, 1e-12, 'valor en 1')

fin()
