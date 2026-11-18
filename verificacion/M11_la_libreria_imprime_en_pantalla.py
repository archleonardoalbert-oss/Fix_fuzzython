# M11 · MEDIO · La librería escribe en la salida estándar
#
# Qué pasa: varios sitios usan print en vez de logging/warnings:
#   - utils.py:35-36: el decorador `timer` imprime «[mamdani system time] compute: 0.00072s» en CADA
#     compute de los tres sistemas. Además no usa functools.wraps: compute.__name__ es 'on_call'.
#   - ruleblock.py:91 («not used input»), variable.py:71 (excepciones), norms/norms.py:108
#     («unsupported norm»), norms/max1.py:10 («--- max1 ---»), store/reader.py:39-40.
#
# Solucionado cuando: ningún uso normal escribe nada en stdout ni stderr, y los métodos decorados
# conservan su nombre y su docstring.
from _comun import *

inicio('M11', 'Medio', 'La librería imprime en pantalla')

def silencioso(f):
    _, out, err = capturar(f)
    exigir(not out.strip() and not err.strip(), f'imprime: {(out + err).strip()[:200]!r}')

@prueba('Mamdani.compute no imprime nada')
def _():
    m = mamdani()
    silencioso(lambda: m.compute({'temp': 33}))

@prueba('Sugeno.compute y Tsukamoto.compute no imprimen nada')
def _():
    s = sugeno(['if temp is hot then z = temp*0.6 + 2'])
    silencioso(lambda: s.compute({'temp': 38}))
    t = tsukamoto(['t:if temp is hot then tm is large'])
    silencioso(lambda: t.compute({'temp': 38}))

@prueba('Dos bloques que usan entradas distintas no imprimen «not used input»')
def _():
    s = escenario()
    A, P = fz('Adjective'), fz('Polygon')
    s['humedo'] = A('humedo', P((50, 0), (90, 1)))
    s['hum'] = var('hum', s['humedo'])
    s['o'] = var('o', A('x', P((0, 0), (1, 1))), defuzzification='COG', default=0)
    s['x'] = s['o'].adjectives[0]
    b1 = bloque(['if temp is hot then tm is large'], s, nombre='b1')
    b2 = bloque(['if hum is humedo then o is x'], s, nombre='b2')
    m = fz('MamdaniSystem')('m', b1, b2)
    silencioso(lambda: m.compute({'temp': 38, 'hum': 70}))

@prueba('La norma de ejemplo MAX1 no imprime al evaluarse')
def _():
    try:
        f = fz('get_norm')('MAX1')
    except Exception as e:
        return f'MAX1 ya no existe ({type(e).__name__})'
    if f is None:
        return 'MAX1 ya no existe'
    silencioso(lambda: f(0.2, 0.3))

@prueba('compute conserva su nombre y su docstring en los tres sistemas')
def _():
    for n in ('MamdaniSystem', 'SugenoSystem', 'TsukamotoSystem'):
        c = fz(n).compute
        exigir(c.__name__ == 'compute', f'{n}.compute.__name__ = {c.__name__!r}')
    exigir(fz('SugenoSystem').compute.__doc__, 'SugenoSystem.compute ha perdido su docstring')

fin()
