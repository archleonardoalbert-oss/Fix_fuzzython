# A5 · ALTO · PiFunction no se puede evaluar
#
# Qué pasa: fsets/pifunction.py:33 y 35 pasan NÚMEROS a SFunction/ZFunction, que esperan puntos
# (x, y): TypeError: 'int' object is not subscriptable. Además min_ y max_ (pifunction.py:22,26-27)
# se guardan y nunca se usan, la rama Z hereda la convención confusa de ZFunction, y crea dos objetos
# nuevos en cada evaluación.
# Origen: F3 de Penumbra + lo demás, nuevo.
#
# Solucionado cuando: PiFunction(centro, delta) vale 1 en el centro, 0 a ±delta, 0.5 a ±delta/2, es
# simétrica y monótona a cada lado, respeta min_ y max_, y funciona dentro de un sistema.
from _comun import *

inicio('A5', 'Alto', 'PiFunction no se puede evaluar')

Pi = lambda *a, **k: fz('PiFunction')(*a, **k)

@prueba('PiFunction(5, 2): 1 en 5, 0 en 3 y 7, 0.5 en 4 y 6, 0.125 en 3.5')
def _():
    p = Pi(5, 2)
    for x, y in ((5, 1), (3, 0), (7, 0), (4, 0.5), (6, 0.5), (3.5, 0.125), (6.5, 0.125)):
        cerca(p(x), y, 1e-9, f'P({x})')

@prueba('Fuera de [centro - delta, centro + delta] vale min_ (0)')
def _():
    p = Pi(5, 2)
    for x in (-10, 0, 2.9, 7.1, 20):
        cerca(p(x), 0, 1e-12, f'P({x})')

@prueba('Simétrica y monótona: crece en [3, 5] y decrece en [5, 7]')
def _():
    p = Pi(5, 2)
    xs = [3 + i / 50 for i in range(101)]
    exigir(all(abs(p(5 - d) - p(5 + d)) < 1e-12 for d in (0.1, 0.7, 1.3, 1.9)), 'no es simétrica')
    sube = [p(x) for x in xs]
    exigir(all(a <= b + 1e-12 for a, b in zip(sube, sube[1:])), 'no crece en [3, 5]')
    baja = [p(x + 2) for x in xs]
    exigir(all(a >= b - 1e-12 for a, b in zip(baja, baja[1:])), 'no decrece en [5, 7]')

@prueba('Respeta min_ = 0.2 y max_ = 0.8: P(5) = 0.8, P(3) = 0.2, P(4) = 0.5')
def _():
    p = Pi(5, 2, min_=0.2, max_=0.8)
    for x, y in ((5, 0.8), (3, 0.2), (7, 0.2), (4, 0.5), (0, 0.2)):
        cerca(p(x), y, 1e-9, f'P({x})')

@prueba('membership coincide con la llamada y COG = 5')
def _():
    p = Pi(5, 2)
    exigir(all(p.membership(x) == p(x) for x in (3, 4, 5, 6.2)), 'membership distinto de la llamada')
    return cerca(p.COG(), 5, 1e-6, 'COG')

@prueba('Usada como adjetivo de entrada en un Mamdani: grado y resultado correctos')
def _():
    s = escenario()
    s['templado'] = fz('Adjective')('templado', Pi(25, 10))
    s['temp'] = var('temp', s['cold'], s['templado'], s['hot'])
    r = numero(mamdani(['if temp is templado then tm is usual'], s).compute({'temp': 20}))   # P(20) = 0.5
    return cerca(r, cog(lambda x: min(pl((10, 0), (15, 1), (25, 1), (30, 0))(x), 0.5), 10, 30), 0.01, 'COG')

fin()
