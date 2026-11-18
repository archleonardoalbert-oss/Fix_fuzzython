# B1 · BAJO · outputs= se aplica a todos los bloques; bloques con igual nombre se pisan
#
# Qué pasa:
#   - systems/mamdani.py:28 hace `outs = outputs or ruleblock.outputs`: si se pasa outputs, se
#     desdifusionan esas variables en CADA bloque, también en los que no las usan.
#   - systems/system.py:31 guarda los bloques por nombre: un segundo bloque con el mismo nombre
#     sustituye al primero sin aviso.
#   - Sugeno y Tsukamoto aceptan `outputs` en compute y lo ignoran.
#
# Solucionado cuando: outputs= solo afecta a los bloques que tienen esas variables, dos bloques con el
# mismo nombre dan error, y Sugeno/Tsukamoto no aceptan en silencio un parámetro que ignoran.
from _comun import *

inicio('B1', 'Bajo', 'outputs= y bloques con el mismo nombre')

def dos_bloques():
    s1, s2 = escenario(), escenario()
    b1 = bloque(['if temp is hot then tm is large'], s1, nombre='b1')
    b2 = bloque(['if temp is hot then tm is short'], s2, nombre='b2')
    return fz('MamdaniSystem')('m', b1, b2), s1

@prueba('outputs={tm de b1}: b2 no devuelve el valor de b1 (33.667)')
def _():
    m, s1 = dos_bloques()
    r = m.compute({'temp': 38}, outputs={'tm': s1['tm']})
    if 'b2' not in r or not r['b2']:
        return 'b2 no aparece'
    v = numero(r['b2'])
    exigir(abs(v - 33.6666666) > 1e-3, f'b2 = {v}: es el resultado de b1')
    return cerca(v, cog(pl((0, 1), (10, 1), (15, 0)), 0, 15), 1e-3, 'b2 (su propia tm)')

@prueba('Control: outputs={tm de b1}: b1 sigue dando 33.667')
def _():
    m, s1 = dos_bloques()
    return cerca(numero(m.compute({'temp': 38}, outputs={'tm': s1['tm']})['b1']), 33.6666666, 1e-3, 'b1')

@prueba('Dos bloques con el mismo nombre en un sistema lanzan un error')
def _():
    s = escenario()
    espera_error(lambda: fz('MamdaniSystem')('m', bloque(['if temp is hot then tm is large'], s, nombre='x'),
                                             bloque(['if temp is cold then tm is short'], s, nombre='x')))

@prueba('Sugeno.compute(..., outputs=...) no ignora el parámetro en silencio')
def _():
    s = sugeno(['if temp is hot then z = temp*0.6 + 2'])
    espera_error(lambda: s.compute({'temp': 38}, outputs={'z': None}))

fin()
