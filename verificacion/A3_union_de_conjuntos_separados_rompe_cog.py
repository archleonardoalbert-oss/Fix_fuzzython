# A3 · ALTO · Unión de conjuntos separados: COG y similares fallan
#
# Qué pasa: interval.py:110-133. Si dos intervalos no se tocan, union() devuelve un Compound, y
# Compound.__iter__ produce intervalos, no dos números. FuzzySet.COG/COA/MM/LM/RM/area/coordinates
# (fsets/fuzzy_set.py:172,222,242,260,355,393) hacen `a, b = self.interval` y fallan:
# Gaussian(0,1).union(Gaussian(10,1)).COG() lanza TypeError. En Mamdani se convierte en el default (C8).
# Origen: F17 de Penumbra.
#
# Solucionado cuando: la unión de dos conjuntos no poligonales separados admite area, COG, COA, LM,
# RM, CM, MM y coordinates con los valores correctos, y un Mamdani con consecuentes así calcula.
# (Se usan FuzzySet con funciones propias para no depender de M10, el intervalo de Gaussian.)
from _comun import *

inicio('A3', 'Alto', 'Unión de conjuntos separados rompe la desdifusión')

def tri(c):
    return lambda x: max(0.0, 1 - abs(x - c))

def separados(recorte2=None):
    FS, I = fz('FuzzySet'), fz('Interval')
    f1, f2 = FS(tri(1), I(0, 2)), FS(tri(9), I(8, 10))
    if recorte2 is not None:
        f2 = f2.minimize(recorte2)
    return f1.union(f2)

REF_U = lambda x: max(tri(1)(x), tri(9)(x))
REF_R = lambda x: max(tri(1)(x), min(tri(9)(x), 0.5))

@prueba('Unión simétrica: área = 2 y COG = 5')
def _():
    u = separados()
    cerca(u.area(), 2.0, 0.02, 'área')
    return cerca(u.COG(), 5.0, 0.02, 'COG')

@prueba('Unión simétrica: COA dentro del hueco [2, 8], LM ≈ 1, RM ≈ 9, CM ≈ 5')
def _():
    u = separados()
    coa = u.COA()
    exigir(2 - 1e-6 <= coa <= 8 + 1e-6, f'COA = {coa!r}')
    cerca(u.LM(), 1.0, 0.06, 'LM'); cerca(u.RM(), 9.0, 0.06, 'RM')
    return cerca(u.CM(), 5.0, 0.06, 'CM')

@prueba('Segundo conjunto recortado a 0.5: área 1.75 y COG 4.4286')
def _():
    u = separados(0.5)
    cerca(u.area(), integral(REF_R, 0, 10), 0.02, 'área')
    return cerca(u.COG(), cog(REF_R, 0, 10), 0.02, 'COG')

@prueba('Recortado: LM = RM = MM ≈ 1 (el único máximo está en x = 1)')
def _():
    u = separados(0.5)
    for m in ('LM', 'RM', 'MM'):
        cerca(getattr(u, m)(), 1.0, 0.06, m)

@prueba('coordinates() de la unión recorre los dos tramos con los valores correctos')
def _():
    u = separados()
    pares = list(u.coordinates())
    exigir(pares, 'no devuelve ningún punto')
    malos = [(x, y) for x, y in pares if abs(y - REF_U(x)) > 1e-9]
    exigir(not malos, f'puntos erróneos, p. ej. {malos[:2]}')
    exigir(min(x for x, _ in pares) < 0.5 and max(x for x, _ in pares) > 9.5, 'no cubre los dos tramos')

@prueba('Gaussian(0,1) ∪ Gaussian(10,1): COG ≈ 5 sin error')
def _():
    G = fz('Gaussian')
    return cerca(G(0, 1).union(G(10, 1)).COG(), 5.0, 0.05, 'COG')

@prueba('Mamdani con dos consecuentes separados (no poligonales) calcula el COG real')
def _():
    FS, I, Ad = fz('FuzzySet'), fz('Interval'), fz('Adjective')
    s = escenario()
    s['izq'], s['der'] = Ad('izq', FS(tri(1), I(0, 2))), Ad('der', FS(tri(9), I(8, 10)))
    s['o'] = var('o', s['izq'], s['der'], defuzzification='COG', default=float('nan'))
    r = numero(mamdani(['if temp is normal then o is izq', 'if temp is hot then o is der'], s).compute({'temp': 33}))
    ref = cog(agregado([(tri(1), 0.4), (tri(9), 0.6)]), 0, 10)
    return cerca(r, ref, 0.02, 'COG')

fin()
