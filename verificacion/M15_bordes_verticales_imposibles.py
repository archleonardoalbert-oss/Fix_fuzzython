# M15 · MEDIO · Bordes verticales: ZeroDivisionError o se pierden
#
# Qué pasa:
#   - fsets/polygon.py:357 (Rect.build_from) divide por x2 - x1. Trapezoid y Triangular lo llaman en el
#     constructor (trapezoid.py:23-25, triangular.py:24-25): Trapezoid((0,0),(0,1),(2,1),(3,0)) lanza
#     ZeroDivisionError.
#   - Polygon.add_point (polygon.py:258-261) fusiona dos puntos con la misma x quedándose con la y
#     mayor: Polygon((0,0),(0,1),(1,1)) queda como [(0,1),(1,1)]. No se puede dibujar un escalón.
# Origen: F21 de Penumbra + lo de Polygon, nuevo.
#
# Solucionado cuando: trapecios, triángulos y polígonos con bordes verticales se construyen, conservan
# sus puntos, valen lo correcto a cada lado del borde, y su área y COG son exactos.
from _comun import *

inicio('M15', 'Medio', 'Bordes verticales imposibles')

@prueba('Trapezoid((0,0),(0,1),(2,1),(3,0)) se construye y vale 1 en 0.5 y 0.5 en 2.5')
def _():
    t = fz('Trapezoid')((0, 0), (0, 1), (2, 1), (3, 0))
    cerca(t(0.5), 1, 1e-12, 't(0.5)')
    return cerca(t(2.5), 0.5, 1e-12, 't(2.5)')

@prueba('Triangular((0,0),(0,1),(2,0)) (triángulo rectángulo) se construye y vale 0.5 en 1')
def _():
    return cerca(fz('Triangular')((0, 0), (0, 1), (2, 0))(1), 0.5, 1e-12, 't(1)')

@prueba('Polygon((2,0),(2,1),(5,1),(5,0)) conserva los 4 puntos')
def _():
    pts = list(fz('Polygon')((2, 0), (2, 1), (5, 1), (5, 0)))
    exigir(len(pts) == 4, f'puntos: {pts}')

@prueba('Ese escalón vale 1 dentro (3.5) y 0 fuera (1 y 6)')
def _():
    p = fz('Polygon')((2, 0), (2, 1), (5, 1), (5, 0))
    for x, y in ((3.5, 1), (1, 0), (6, 0)):
        cerca(p(x), y, 1e-12, f'p({x})')

@prueba('Ese escalón tiene área 3 y COG 3.5')
def _():
    p = fz('Polygon')((2, 0), (2, 1), (5, 1), (5, 0))
    cerca(p.area(), 3, 1e-9, 'área')
    return cerca(p.COG(), 3.5, 1e-9, 'COG')

fin()
