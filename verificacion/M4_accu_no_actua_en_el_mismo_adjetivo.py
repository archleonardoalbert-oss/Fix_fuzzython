# M4 · MEDIO · ACCU no actúa entre reglas con el mismo adjetivo
#
# Qué pasa: adjective.py:54-59. set_strength se queda con el MÁXIMO de la fuerza anterior y la nueva,
# sea cual sea `accumulation`. Dos reglas sobre `large` se combinan siempre con máximo; ACCU solo actúa
# entre adjetivos distintos. Con BSUM no se obtiene la suma acotada que dicta la teoría.
# Origen: F7 de Penumbra.
#
# Solucionado cuando: con ACCU BSUM o ASUM, dos reglas sobre el mismo adjetivo se acumulan con esa
# S-norma (como en la teoría: acumulación punto a punto de todas las salidas de regla), y con MAX el
# resultado no cambia.
# (Los consecuentes son FuzzySet con funciones propias para no depender de A2.)
from _comun import *

inicio('M4', 'Medio', 'ACCU no actúa entre reglas con el mismo adjetivo')

# Valen 0 fuera de [0, 41] para que el paso de integración no sume área de más (eso es M14, no M4).
LARGE = lambda x: 0.0 if x > 41 or x < 25 else min(1.0, (x - 25) / 5, 41 - x)
SHORT = lambda x: 0.0 if x < 0 else (1.0 if x <= 10 else max(0.0, (15 - x) / 5))
REGLAS = ['if temp is normal then tm is large', 'if temp is hot then tm is large', 'if temp is normal then tm is short']
SALIDAS = [(LARGE, 0.4), (LARGE, 0.6), (SHORT, 0.4)]   # temp = 33: normal 0.4, hot 0.6

def calcular(accu):
    FS, I, A = fz('FuzzySet'), fz('Interval'), fz('Adjective')
    s = escenario()
    s['large'], s['short'] = A('large', FS(LARGE, I(0, 42))), A('short', FS(SHORT, I(0, 42)))
    s['tm'] = var('tm', s['short'], s['large'], defuzzification='COG', default=float('nan'))
    return numero(mamdani(REGLAS, s, accumulation=accu).compute({'temp': 33}))

for accu in ('BSUM', 'ASUM', 'MAX'):
    @prueba(('Control: ' if accu == 'MAX' else '') + f'ACCU {accu}: las dos reglas sobre «large» se acumulan con {accu}')
    def _(accu=accu):
        ref = cog(agregado(SALIDAS, min, fz('get_norm')(accu)), 0, 42)
        return cerca(calcular(accu), ref, 0.05, 'COG')

@prueba('BSUM y MAX dan resultados distintos (con MAX la fuerza 0.4 se pierde)')
def _():
    b, m = calcular('BSUM'), calcular('MAX')
    exigir(abs(b - m) > 0.1, f'BSUM = {b:.4f} y MAX = {m:.4f} coinciden')

fin()
