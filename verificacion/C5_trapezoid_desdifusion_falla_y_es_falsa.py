# C5 · CRÍTICO · Trapezoid: la desdifusión falla, y su atajo es falso para trapecios asimétricos
#
# Qué pasa: fsets/trapezoid.py:47-69. COG, COA, CM y MM hacen
#     if b[1] == c[1]: return sum(b[0]+c[0])/2
#   1. sum() de un número lanza TypeError (F2). En Mamdani, C8 lo convierte en `default`: con
#      activation='PROD' y una sola regla sobre un trapecio, la salida es el default.
#   2. Aunque se arregle el sum, (b_x + c_x)/2 solo es el COG/COA de un trapecio SIMÉTRICO, y en un
#      trapecio en U (meseta = mínimo) CM/MM devuelven el centro del valle.
#
# Solucionado cuando: los seis métodos de Trapezoid dan el valor exacto (el mismo que Polygon con
# los mismos puntos) en trapecios simétricos, asimétricos y en U, y Mamdani con trapecios y PROD
# devuelve el centro de gravedad real, no el default.
from _comun import *

inicio('C5', 'Crítico', 'Trapezoid: desdifusión que falla y atajo falso')

T = lambda *p: fz('Trapezoid')(*p)
SIM = ((0, 0), (1, 1), (2, 1), (3, 0))
ASIM = ((0, 0), (1, 1), (2, 1), (5, 0))
U = ((0, 1), (1, 0), (2, 0), (5, 1))

ESPERADO = [  # (forma, método, valor exacto, tolerancia)
    (SIM, 'COG', 1.5, 1e-6), (SIM, 'COA', 1.5, 1e-4), (SIM, 'CM', 1.5, 0.05), (SIM, 'MM', 1.5, 0.05),
    (ASIM, 'COG', 19 / 9, 1e-6), (ASIM, 'COA', 2.0, 1e-4), (ASIM, 'LM', 1.0, 0.05), (ASIM, 'RM', 2.0, 0.05),
    (ASIM, 'CM', 1.5, 0.05), (ASIM, 'MM', 1.5, 0.05),
    (U, 'LM', 0.0, 0.06), (U, 'RM', 5.0, 0.06), (U, 'CM', 2.5, 0.06), (U, 'MM', 2.5, 0.06),
]
NOMBRE = {SIM: 'simétrico (0,0)(1,1)(2,1)(3,0)', ASIM: 'asimétrico (0,0)(1,1)(2,1)(5,0)', U: 'en U (0,1)(1,0)(2,0)(5,1)'}
for forma, metodo, valor, tol in ESPERADO:
    @prueba(f'Trapezoid {NOMBRE[forma]}: {metodo} = {valor:.4g}')
    def _(forma=forma, metodo=metodo, valor=valor, tol=tol):
        return cerca(getattr(T(*forma), metodo)(), valor, tol, metodo)

@prueba('El COG de un Trapezoid coincide con el de un Polygon con los mismos puntos (5 formas)')
def _():
    formas = [SIM, ASIM, ((0, 0), (4, 1), (5, 1), (6, 0)), ((10, 0), (15, 1), (25, 1), (30, 0)), ((0, 0.2), (1, 0.7), (3, 0.7), (4, 0))]
    for f in formas:
        cerca(T(*f).COG(), fz('Polygon')(*f).COG(), 1e-6, f'COG de {f}')

@prueba('Mamdani con salida Trapezoid y activación PROD (una regla) da el COG real (20), no el default')
def _():
    s = escenario()
    s['usual'] = fz('Adjective')('usual', T((10, 0), (15, 1), (25, 1), (30, 0)))
    s['tm'] = var('tm', s['short'], s['usual'], s['large'], defuzzification='COG', default=float('nan'))
    r = numero(mamdani(['if temp is normal then tm is usual'], s, activation='PROD').compute({'temp': 25}))
    return cerca(r, 20.0, 1e-6, 'COG')

@prueba('Mamdani con salida Trapezoid asimétrico y PROD da 2.111, no 1.5 ni el default')
def _():
    s = escenario()
    s['usual'] = fz('Adjective')('usual', T(*ASIM))
    s['tm'] = var('tm', s['usual'], defuzzification='COG', default=float('nan'))
    r = numero(mamdani(['if temp is hot then tm is usual'], s, activation='PROD').compute({'temp': 38}))
    return cerca(r, 19 / 9, 1e-6, 'COG')

fin()
