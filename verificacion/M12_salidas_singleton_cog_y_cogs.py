# M12 · MEDIO · Salidas Singleton: COG da el default; COGS ignora la altura
#
# Qué pasa:
#   - fsets/singleton.py:62-63: el área de un Singleton es 0. Activado se convierte en un FuzzySet de
#     intervalo [x, x] y COG divide por 0: imprime «division by zero» y devuelve el default.
#   - variable.py:49-62 (COGS) pondera con la fuerza de la regla e ignora la altura `y` del singleton,
#     salta en silencio los adjetivos que no son Singleton y divide por 0 si nada dispara.
#
# Solucionado cuando: COG con salidas Singleton da la media ponderada (igual que COGS) o un error claro,
# COGS tiene en cuenta la altura activada, y mezclar Singleton con otras formas en COGS da error.
from _comun import *

inicio('M12', 'Medio', 'Salidas Singleton: COG y COGS')

def con_singletons(metodo, *puntos):
    s = escenario()
    A, S = fz('Adjective'), fz('Singleton')
    adjs = [A(f's{i}', S(x, y)) for i, (x, y) in enumerate(puntos)]
    s.update({a.name: a for a in adjs})
    s['o'] = var('o', *adjs, defuzzification=metodo, default=float('nan'))
    return s

@prueba('COG con un único Singleton(5) que dispara: 5 (o un error que lo explique)')
def _():
    try:
        r = numero(mamdani(['if temp is hot then o is s0'], con_singletons('COG', (5, 1))).compute({'temp': 38}))
    except Exception as e:
        return f'lanza {type(e).__name__}: {e}'
    return cerca(r, 5, 1e-9, 'COG')

@prueba('COG con Singleton(10) a 0.6 y Singleton(20) a 0.4: 14 (o un error que lo explique)')
def _():
    s = con_singletons('COG', (10, 1), (20, 1))
    try:
        r = numero(mamdani(['if temp is hot then o is s0', 'if temp is normal then o is s1'], s).compute({'temp': 33}))
    except Exception as e:
        return f'lanza {type(e).__name__}: {e}'
    return cerca(r, 14, 1e-9, 'COG')

@prueba('COGS tiene en cuenta la altura: Singleton(10, 0.1) y Singleton(20, 1.0) con fuerza 1 -> 19.09')
def _():
    s = con_singletons('COGS', (10, 0.1), (20, 1.0))
    r = numero(mamdani(['if temp is hot then o is s0', 'if temp is hot then o is s1'], s).compute({'temp': 38}))
    return cerca(r, (10 * 0.1 + 20 * 1.0) / 1.1, 1e-9, 'COGS')

@prueba('Control: COGS con alturas 1 y fuerzas 0.6 / 0.4 -> 14')
def _():
    s = con_singletons('COGS', (10, 1), (20, 1))
    r = numero(mamdani(['if temp is hot then o is s0', 'if temp is normal then o is s1'], s).compute({'temp': 33}))
    return cerca(r, 14, 1e-9, 'COGS')

@prueba('COGS con un adjetivo que no es Singleton lanza un error')
def _():
    s = con_singletons('COGS', (10, 1))
    s['tri'] = fz('Adjective')('tri', fz('Polygon')((0, 0), (5, 1), (10, 0)))
    s['o'] = var('o', s['s0'], s['tri'], defuzzification='COGS', default=float('nan'))
    espera_error(lambda: mamdani(['if temp is hot then o is s0', 'if temp is hot then o is tri'], s).compute({'temp': 38}))

fin()
