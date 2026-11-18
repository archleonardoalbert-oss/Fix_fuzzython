# M20 · MEDIO · dump() no siempre se puede volver a leer
#
# Qué pasa: System.dump (systems/system.py:91-118), Variable.terms/methods (variable.py:119-131) y
# RuleBlock.dump (ruleblock.py:96-105) escriben un FCL que a veces no se puede leer o que al releerlo
# da otro sistema:
#   - Solo escribe AND, ACT y ACCU: se pierden OR y NOT (OR = ASUM: 33.40 antes, 33.22 después).
#   - `temp*0.6+2` vuelve como `temp*0.6` (C4); un número 1e-05 hace fallar la lectura.
#   - Singleton(5, 0.3) se escribe como `5`: la altura se pierde.
#   - Gaussian y Gamma escriben su Interval `(a .. b)`; default=None omite DEFAULT. Se releen solo
#     gracias a la recuperación de errores de ANTLR (avisos en stderr, C3).
#   - Una norma propia sin `.name` hace fallar dump con AttributeError; un FuzzySet genérico se escribe
#     como «Fuzzy Set»; Polynomial falla en str() (M9).
#   - Los números de regla son un contador global (RULE 47: ...).
#
# Solucionado cuando: guardar y releer cada sistema da exactamente el mismo resultado sin avisos en
# stderr, o dump lanza un error claro cuando algo no se puede representar en FCL.
import os, tempfile
from _comun import *

inicio('M20', 'Medio', 'dump() no siempre se puede volver a leer')

def ida_y_vuelta(sistema, entradas):
    antes = numero(sistema.compute(entradas))
    with tempfile.TemporaryDirectory() as d:
        ruta = os.path.join(d, 'sistema.fcl')
        sistema.dump(ruta)
        texto = open(ruta).read()
        nuevo, out, err = capturar(lambda: fz('load_from_file')(ruta))
    exigir(nuevo is not None, 'la lectura devuelve None: ' + (out + err).strip()[:200])
    exigir(not err.strip(), f'la lectura escribe avisos en stderr: {err.strip()[:200]!r}')
    despues = numero(nuevo.compute(entradas))
    cerca(despues, antes, 1e-9, 'tras releer')
    return texto, f'antes = {antes:.6g}, después = {despues:.6g}'

def con_salida(*adjs, metodo='COG', default=0):
    s = escenario()
    s.update({a.name: a for a in adjs})
    s['o'] = var('o', *adjs, defuzzification=metodo, default=default)
    return s

@prueba('Control: el Mamdani de sample.py se guarda y se relee igual')
def _():
    return ida_y_vuelta(mamdani(), {'temp': 33})[1]

@prueba('OR = ASUM con AND = MIN (no es su pareja) se conserva  (temp = 17.5: cold y normal a 0.5)')
def _():
    m = mamdani(operators=('MIN', 'ASUM', 'ZADEH'))
    texto, d = ida_y_vuelta(m, {'temp': 17.5})
    exigir('ASUM' in texto, 'el FCL no menciona la norma OR')
    return d

@prueba('NOT con otra norma (SUGENO) y una regla con «is not» se conserva')
def _():
    m = mamdani(['if temp is not cold then tm is large'], operators=('MIN', 'MAX', 'SUGENO'))
    texto, d = ida_y_vuelta(m, {'temp': 18})
    exigir('SUGENO' in texto, 'el FCL no menciona la norma NOT')
    return d

@prueba('Sugeno con `temp*0.6+2` se conserva')
def _():
    return ida_y_vuelta(sugeno(['if temp is hot then z = temp*0.6+2']), {'temp': 38})[1]

@prueba('Un polígono con un valor 1e-05 se guarda y se relee')
def _():
    s = escenario()
    s['raro'] = fz('Adjective')('raro', fz('Polygon')((0, 0.00001), (10, 1)))
    s['tm'] = var('tm', s['short'], s['raro'], defuzzification='COG', default=0)
    return ida_y_vuelta(mamdani(['if temp is hot then tm is raro'], s), {'temp': 38})[1]

@prueba('Singleton(5, 0.3) con COGS conserva la altura')
def _():
    A, S = fz('Adjective'), fz('Singleton')
    a, b = A('a', S(5, 0.3)), A('b', S(20, 1.0))
    m = mamdani(['if temp is hot then o is a', 'if temp is hot then o is b'], con_salida(a, b, metodo='COGS'))
    texto, d = ida_y_vuelta(m, {'temp': 38})
    exigir('0.3' in texto, 'el FCL no guarda la altura 0.3 del singleton')
    return d

@prueba('Trapezoid y Gaussian como adjetivos se releen sin avisos')
def _():
    A = fz('Adjective')
    s = escenario()
    s['normal'] = A('normal', fz('Trapezoid')((15, 0), (20, 1), (30, 1), (35, 0)))
    s['templado'] = A('templado', fz('Gaussian')(25, 5))
    s['temp'] = var('temp', s['normal'], s['templado'], s['hot'])
    m = mamdani(['if temp is normal then tm is usual', 'if temp is templado then tm is short', 'if temp is hot then tm is large'], s)
    return ida_y_vuelta(m, {'temp': 28})[1]

@prueba('default=None se guarda y se relee sin avisos')
def _():
    s = escenario()
    s['tm'].default = None
    return ida_y_vuelta(mamdani(s=s), {'temp': 33})[1]

@prueba('Una norma propia (función sin .name): dump funciona o lanza un error claro, no AttributeError')
def _():
    m = mamdani()
    for b in m.blocks.values():
        b.activation = lambda a, w: a * w
    with tempfile.TemporaryDirectory() as d:
        try:
            m.dump(os.path.join(d, 'x.fcl'))
        except AttributeError as e:
            raise Falla(f'lanza AttributeError: {e}')
        except Exception as e:
            return f'lanza {type(e).__name__}: {e}'

@prueba('Un FuzzySet genérico: dump lanza un error (no escribe «Fuzzy Set»)')
def _():
    FS, I = fz('FuzzySet'), fz('Interval')
    g = fz('Adjective')('g', FS(lambda x: x / 40, I(0, 40)))
    m = mamdani(['if temp is hot then o is g'], con_salida(g))
    with tempfile.TemporaryDirectory() as d:
        espera_error(lambda: m.dump(os.path.join(d, 'x.fcl')))

@prueba('Las reglas de un sistema nuevo se numeran desde 1 en el FCL')
def _():
    with tempfile.TemporaryDirectory() as d:
        ruta = os.path.join(d, 'x.fcl')
        mamdani().dump(ruta)
        texto = open(ruta).read()
    exigir('RULE 1:' in texto and 'RULE 3:' in texto, 'numeración: ' + ', '.join(l.strip()[:8] for l in texto.splitlines() if 'RULE ' in l))

fin()
