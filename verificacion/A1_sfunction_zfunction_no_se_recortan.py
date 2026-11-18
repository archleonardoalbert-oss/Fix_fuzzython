# A1 · ALTO · SFunction y ZFunction activadas no se recortan
#
# Qué pasa: fsets/sfunction.py:68-82. Con un número, `_operation` solo aplica la norma a las `y` de
# los extremos `a` y `c`, y crea siempre una SFunction. Por eso:
#   - SFunction(...).minimize(0.5) sigue valiendo 0.92 o 1.0 en el interior: no se recorta.
#   - ZFunction(...).minimize(0.5) devuelve una SFunction: la curva al revés.
#   - Mamdani con estas formas en el consecuente da resultados falsos sin avisar.
# Origen: F5 de Penumbra.
#
# Solucionado cuando: minimize y la activación PROD de S y Z coinciden punto a punto con
# min(μ(x), w) y μ(x)·w, y un Mamdani con consecuentes S o Z da el centro de gravedad real.
from _comun import *

inicio('A1', 'Alto', 'SFunction y ZFunction activadas no se recortan')

S = lambda: fz('SFunction')((0, 0), 5, (10, 1))
Z = lambda: fz('ZFunction')((0, 0), 5, (10, 1))
XS = [i / 10 for i in range(-20, 121)]

def error_max(conjunto, referencia):
    return max(abs(conjunto(x) - referencia(x)) for x in XS)

@prueba('SFunction.minimize(0.5) == min(S(x), 0.5) en todo [-2, 12]')
def _():
    s = S()
    e = error_max(s.minimize(0.5), lambda x: min(s(x), 0.5))
    exigir(e < 1e-9, f'error máximo {e:.4f}')

@prueba('ZFunction.minimize(0.5) == min(Z(x), 0.5) en todo [-2, 12]')
def _():
    z = Z()
    e = error_max(z.minimize(0.5), lambda x: min(z(x), 0.5))
    exigir(e < 1e-9, f'error máximo {e:.4f}')

@prueba('Activación PROD con 0.6: S·0.6 y Z·0.6 punto a punto')
def _():
    prod = fz('get_norm')('PROD')
    for nombre, c in (('S', S()), ('Z', Z())):
        e = error_max(c.activate(prod, 0.6), lambda x, c=c: c(x) * 0.6)
        exigir(e < 1e-9, f'{nombre}: error máximo {e:.4f}')

@prueba('maximize(0.3) de S y Z: max(μ(x), 0.3) punto a punto')
def _():
    for nombre, c in (('S', S()), ('Z', Z())):
        e = error_max(c.maximize(0.3), lambda x, c=c: max(c(x), 0.3))
        exigir(e < 1e-9, f'{nombre}: error máximo {e:.4f}')

def mamdani_con(forma):
    s = escenario()
    s['alto'] = fz('Adjective')('alto', forma)
    s['o'] = var('o', s['alto'], defuzzification='COG', default=float('nan'))
    return numero(mamdani(['if temp is hot then o is alto'], s).compute({'temp': 33}))   # hot(33) = 0.6

@prueba('Mamdani con consecuente SFunction recortado a 0.6: COG real')
def _():
    ref = cog(lambda x: min(s_curva(0, 10)(x), 0.6), 0, 10)
    return cerca(mamdani_con(S()), ref, 0.02, 'COG')

@prueba('Mamdani con consecuente ZFunction recortado a 0.6: COG real')
def _():
    z = Z()
    ref = cog(lambda x: min(z(x), 0.6), 0, 10)
    return cerca(mamdani_con(z), ref, 0.02, 'COG')

fin()
