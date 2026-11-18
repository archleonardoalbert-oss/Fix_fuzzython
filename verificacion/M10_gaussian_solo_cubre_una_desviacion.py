# M10 · MEDIO · Gaussian solo cubre ±1 desviación
#
# Qué pasa: fsets/gaussian.py:18 usa Interval(center - width, center + width). Todo lo que integra o
# muestrea la gaussiana se queda en ese tramo: el área de Gaussian(0,1) sale 1.711 (la real es 2.507,
# se pierde el 32 %), un consecuente gaussiano activado se integra solo ahí y una entrada difusa
# gaussiana solo se mira entre ±1 desviación. Además __repr__ escribe el intervalo en vez de `height`.
#
# Solucionado cuando: área, COG de consecuentes gaussianos activados y entradas difusas gaussianas dan
# lo mismo que la gaussiana completa (tolerancia 0.5 %), y repr/str muestran la altura.
import math
from _comun import *

inicio('M10', 'Medio', 'Gaussian solo cubre ±1 desviación')

G = lambda *a: fz('Gaussian')(*a)
gauss = lambda c, w, h=1: (lambda x: h * math.exp(-((x - c) ** 2) / (2 * w * w)))

@prueba('Área de Gaussian(0, 1) ≈ √(2π) = 2.5066')
def _():
    return cerca(fz('FuzzySet').area(G(0, 1)), math.sqrt(2 * math.pi), 0.0125, 'área')

@prueba('Área de Gaussian(10, 3, height=0.5) ≈ 0.5·3·√(2π) = 3.7599')
def _():
    return cerca(fz('FuzzySet').area(G(10, 3, 0.5)), 0.5 * 3 * math.sqrt(2 * math.pi), 0.02, 'área')

@prueba('Mamdani con consecuentes gaussianos solapados recortados: COG de las gaussianas completas')
def _():
    s = escenario()
    A = fz('Adjective')
    s['ga'], s['gb'] = A('ga', G(10, 4)), A('gb', G(16, 4))
    s['o'] = var('o', s['ga'], s['gb'], defuzzification='COG', default=float('nan'))
    r = numero(mamdani(['if temp is hot then o is ga', 'if temp is normal then o is gb'], s).compute({'temp': 33}))
    ref = cog(agregado([(gauss(10, 4), 0.6), (gauss(16, 4), 0.4)]), -30, 60)
    return cerca(r, ref, 0.05, 'COG')

@prueba('Entrada difusa Gaussian(12, 1) sobre el adjetivo Triangular((0,0),(5,1),(10,0)): sup-min completo')
def _():
    adj = fz('Adjective')('t', fz('Triangular')((0, 0), (5, 1), (10, 0)))
    ref = max(min(pl((0, 0), (5, 1), (10, 0))(x / 1000), gauss(12, 1)(x / 1000)) for x in range(0, 10001))
    return cerca(adj.membership(G(12, 1)), ref, 0.01, 'grado')

@prueba('repr y str de Gaussian(0, 1, 0.5) muestran la altura 0.5')
def _():
    g = G(0, 1, 0.5)
    exigir('0.5' in repr(g) and '0.5' in str(g), f'repr = {g!r}, str = {g}')

fin()
