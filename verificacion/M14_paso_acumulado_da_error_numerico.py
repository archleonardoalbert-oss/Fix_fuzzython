# M14 · MEDIO · Paso acumulado con +=: áreas y muestreos con error
#
# Qué pasa: fsets/fuzzy_set.py:142-144 (fuzzify_with), 225-232 (MM), 245-250 (LM), 263-268 (RM),
# 359-365 (area), 378-383 (area_), 396-398 (coordinates) y fsets/polygon.py:299-302 (create_from)
# avanzan con `a += step`. El error se acumula: el área de la función 1 en [0, 1] da 1.143 con
# resolución 7 y 1.1 con 10. Además LM, RM y MM usan `while a < b` y casi nunca miran x = b.
# Origen: F19 de Penumbra + lo de x = b, nuevo.
#
# Solucionado cuando: las integrales y muestreos son exactos para funciones constantes o lineales con
# cualquier resolución, y se evalúan los dos extremos del intervalo.
from _comun import *

inicio('M14', 'Medio', 'Paso acumulado con +=')

FS = lambda f, a, b: fz('FuzzySet')(f, fz('Interval')(a, b))

@prueba('area() de la función 1 en [0, 1] vale 1 con resoluciones 3, 7, 10, 49 y 100')
def _():
    for r in (3, 7, 10, 49, 100):
        cerca(FS(lambda x: 1, 0, 1).area(r), 1, 1e-9, f'resolución {r}')

@prueba('area() de f(x) = x en [0, 1] vale 0.5 con resolución 7')
def _():
    return cerca(FS(lambda x: x, 0, 1).area(7), 0.5, 1e-9, 'área')

@prueba('RM de f(x) = x en [0, 1] es 1 (el máximo está en el extremo derecho)')
def _():
    return cerca(FS(lambda x: x, 0, 1).RM(), 1, 1e-9, 'RM')

@prueba('MM de la función 1 en [0, 1] es 0.5 (media de todo el intervalo, extremos incluidos)')
def _():
    return cerca(FS(lambda x: 1, 0, 1).MM(), 0.5, 1e-9, 'MM')

@prueba('coordinates(10) en [0, 1] da 11 puntos y el último es x = 1')
def _():
    xs = [x for x, _ in FS(lambda x: x, 0, 1).coordinates(10)]
    exigir(len(xs) == 11 and abs(xs[-1] - 1) < 1e-12, f'{len(xs)} puntos, último {xs[-1] if xs else None!r}')

@prueba('Polygon.create_from(f, 0, 1, 10) da 11 puntos con el último en x = 1 exacto')
def _():
    p = fz('Polygon').create_from(lambda x: x, 0, 1, 10)
    xs = [x for x, _ in p]
    exigir(len(xs) == 11 and xs[-1] == 1, f'{len(xs)} puntos, último {xs[-1]!r}')

fin()
