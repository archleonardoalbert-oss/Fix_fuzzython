# A6 · ALTO · ZFunction: LM, RM, CM y MM devuelven el punto de mínimo
#
# Qué pasa: fsets/sfunction.py:52-62 devuelve siempre self.c[0], que en una S es el máximo.
# ZFunction (fsets/zfunction.py) lo hereda sin redefinirlo, pero en una Z el máximo está en el otro
# extremo. Ejecutado: ZFunction((0,0),5,(10,1)) vale ≈1 en 0 y ≈0 en 10, y LM = RM = CM = MM = 10.
#
# Solucionado cuando: LM, RM, CM y MM de una ZFunction señalan dónde está de verdad su máximo (se
# averigua muestreando la propia curva, así que vale con cualquier convención de parámetros), también
# tras recortarla, y la SFunction sigue dando su máximo bien.
from _comun import *

inicio('A6', 'Alto', 'ZFunction: los métodos de máximo devuelven el mínimo')

def maximos_reales(f, a, b, n=4000):
    xs = [a + (b - a) * i / n for i in range(n + 1)]
    ys = [f(x) for x in xs]
    m = max(ys)
    pts = [x for x, y in zip(xs, ys) if y >= m - 1e-9]
    return dict(LM=pts[0], RM=pts[-1], CM=(pts[0] + pts[-1]) / 2, MM=sum(pts) / len(pts))

def comprobar(conjunto, a, b, tol=0.15, curva=None):
    ref = maximos_reales(curva or conjunto, a, b)
    for m in ('LM', 'RM', 'CM', 'MM'):
        cerca(getattr(conjunto, m)(), ref[m], tol, m)
    return ', '.join(f'{m} = {ref[m]:.3g}' for m in ref)

@prueba('ZFunction((0,0),5,(10,1)): LM, RM, CM, MM donde está su máximo')
def _():
    return comprobar(fz('ZFunction')((0, 0), 5, (10, 1)), 0, 10)

@prueba('ZFunction((2,0),6,(10,1)): ídem en otro intervalo')
def _():
    return comprobar(fz('ZFunction')((2, 0), 6, (10, 1)), 2, 10)

@prueba('ZFunction recortada a 0.5: máximos en la meseta del principio  (depende también de A1)')
def _():
    z = fz('ZFunction')((0, 0), 5, (10, 1))
    return comprobar(z.minimize(0.5), 0, 10, curva=lambda x: min(z(x), 0.5))

@prueba('Control: SFunction((0,0),5,(10,1)) sigue dando su máximo en 10')
def _():
    return comprobar(fz('SFunction')((0, 0), 5, (10, 1)), 0, 10)

@prueba('Mamdani con consecuente ZFunction y desdifusión LM da el extremo del máximo')
def _():
    z = fz('ZFunction')((0, 0), 5, (10, 1))
    s = escenario()
    s['bajo'] = fz('Adjective')('bajo', z)
    s['o'] = var('o', s['bajo'], defuzzification='LM', default=float('nan'))
    r = numero(mamdani(['if temp is hot then o is bajo'], s).compute({'temp': 38}))
    return cerca(r, maximos_reales(z, 0, 10)['LM'], 0.15, 'LM')

fin()
