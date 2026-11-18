# M13 · MEDIO · Polygon.MM promedia solo vértices
#
# Qué pasa: fsets/polygon.py:102-111 hace la media de los VÉRTICES que alcanzan el máximo, no de todos
# los puntos de la meseta. Si la meseta tiene vértices repartidos de forma desigual, sale sesgado.
# Ejecutado con sample.py (temp = 33): MM da 32.667 (media de 28, 30 y 40); la meseta [28, 40] da 34.
# Origen: F20 de Penumbra.
#
# Solucionado cuando: MM devuelve la media de la región de máximo (el punto medio de la meseta, o la
# media de las mesetas ponderada por su longitud) sin depender de cuántos vértices haya.
from _comun import *

inicio('M13', 'Medio', 'Polygon.MM promedia vértices')

P = lambda *p: fz('Polygon')(*p)

@prueba('Mamdani de sample.py con MM (temp = 33): 34, no 32.667')
def _():
    s = escenario()
    s['tm'].defuzzification = 'MM'
    return cerca(numero(mamdani(s=s).compute({'temp': 33})), 34, 1e-6, 'MM')

@prueba('Meseta [1, 5] con un vértice extra en 1.5: MM = 3')
def _():
    return cerca(P((0, 0), (1, 1), (1.5, 1), (5, 1), (6, 0)).MM(), 3, 1e-6, 'MM')

@prueba('Meseta [2, 8] con vértices en 2, 3, 3.5, 8: MM = 5')
def _():
    return cerca(P((0, 0), (2, 1), (3, 1), (3.5, 1), (8, 1), (9, 0)).MM(), 5, 1e-6, 'MM')

@prueba('Control: dos picos sueltos en 1 y 9: MM = 5')
def _():
    return cerca(P((0, 0), (1, 1), (2, 0), (8, 0), (9, 1), (10, 0)).MM(), 5, 1e-6, 'MM')

fin()
