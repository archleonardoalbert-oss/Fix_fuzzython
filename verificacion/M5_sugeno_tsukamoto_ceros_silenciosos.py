# M5 · MEDIO · Sugeno y Tsukamoto devuelven 0 si nada dispara; Tsukamoto anula reglas en silencio
#
# Qué pasa:
#   - systems/sugeno.py:21-24 y systems/tsukamoto.py:20-27 hacen `except ZeroDivisionError: res = 0`.
#     Un 0 real y «ninguna regla disparó» no se distinguen.
#   - rules/trule.py:69-70,81-82: si la fuerza de la regla supera la altura del consecuente, devuelve
#     (0, 0) y la regla deja de contar sin avisar.
#
# Solucionado cuando: «nada disparó» se distingue de un 0 real (error, None o NaN, nunca 0), y una regla
# Tsukamoto más fuerte que su consecuente se recorta a su máximo o lanza un error, pero no desaparece.
from _comun import *

inicio('M5', 'Medio', 'Ceros silenciosos en Sugeno y Tsukamoto')

def nada_o_error(f):
    try:
        r = numero(f())
    except Exception as e:
        return f'lanza {type(e).__name__}'
    exigir(r is None or es_nan(r), f'devuelve {r!r}, indistinguible de un resultado real')
    return f'devuelve {r!r}'

@prueba('Sugeno sin ninguna regla disparada no devuelve 0')
def _():
    return nada_o_error(lambda: sugeno(['if temp is hot then z = temp*0.6 + 2']).compute({'temp': 5}))

@prueba('Tsukamoto sin ninguna regla disparada no devuelve 0')
def _():
    return nada_o_error(lambda: tsukamoto(['t:if temp is hot then tm is large']).compute({'temp': 5}))

@prueba('Control: Sugeno con un 0 real (z = temp*0) devuelve 0')
def _():
    return cerca(numero(sugeno(['if temp is hot then z = temp*0']).compute({'temp': 38})), 0, 1e-12, 'z')

@prueba('Tsukamoto: regla de fuerza 1 sobre un consecuente de altura 0.8 no se anula en silencio')
def _():
    s = escenario_tsukamoto()
    s['sub'] = fz('Adjective')('sub', fz('Polygon')((0, 0), (10, 0.8)))
    s['tm'] = var('tm', s['short'], s['large'], s['sub'], defuzzification='COG', default=0)
    reglas = ['t:if temp is hot then tm is sub', 't:if temp is hot then tm is large with 0.5']
    try:
        r = numero(tsukamoto(reglas, s).compute({'temp': 38}))
    except Exception as e:
        return f'lanza {type(e).__name__}: {e}'
    # si la 1.ª regla se recorta a su máximo (x = 10): (w·10 + 0.5·20)/(w + 0.5) con w entre 0.8 y 1
    exigir(13.3 <= r <= 13.9, f'resultado {r!r}: la regla 1 se ha perdido (solo la regla 2 daría 20)')
    return f'resultado = {r:.4g}'

fin()
