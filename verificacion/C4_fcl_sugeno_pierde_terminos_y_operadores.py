# C4 · CRÍTICO · FCL Sugeno: `temp*0.6+2` pierde el +2 y `**` se lee como `*`
#
# Qué pasa:
#   - store/FCL.g:401,403: los literales llevan el signo dentro del token. En `temp*0.6+2` el lexer
#     lee `+2` como un número suelto y el «más 2» se pierde (da 22.8 en vez de 24.8). `temp-1` falla.
#   - store/FCL.g:274-276: la etiqueta `o` solo recoge el primer token del operador; `**` queda como
#     `*` y `//` como `/`.
#   - dump() escribe la regla tal cual, así que un sistema Python guardado y releído cambia de valor.
#
# Solucionado cuando: todas las expresiones dan su valor aritmético con y sin espacios, y la ida y
# vuelta Python -> dump -> FCL conserva el resultado. (`temp ** 2` también necesita M18.)
import os, tempfile
from _comun import *

inicio('C4', 'Crítico', 'FCL Sugeno: términos con signo y operadores dobles')

def sug(expr, t):
    return numero(fcl(f'RULE 1: IF temp IS hot THEN {expr};', tipo='_SUGENO_').compute({'temp': t}))

CASOS = [('temp*0.6 + 2', 38, 24.8), ('temp*0.6+2', 38, 24.8), ('2+temp*0.6', 38, 24.8),
         ('temp - 1', 38, 37), ('temp-1', 38, 37), ('temp*-1', 38, -38),
         ('temp ** 2', 38, 1444), ('temp**2', 38, 1444), ('temp // 2', 39, 19), ('temp / 2', 39, 19.5)]
for expr, t, esperado in CASOS:
    @prueba(f'THEN {expr}  con temp = {t}  ->  {esperado}')
    def _(expr=expr, t=t, esperado=esperado):
        return cerca(sug(expr, t), esperado, 1e-9, expr)

@prueba('Ida y vuelta: regla Python `z = temp*0.6+2` -> dump -> lectura FCL conserva 24.8')
def _():
    s = sugeno(['if temp is hot then z = temp*0.6+2'])
    antes = numero(s.compute({'temp': 38}))
    with tempfile.TemporaryDirectory() as d:
        ruta = os.path.join(d, 's.fcl')
        s.dump(ruta)
        despues = numero(fz('load_from_file')(ruta).compute({'temp': 38}))
    cerca(antes, 24.8, 1e-9, 'antes de guardar')
    return cerca(despues, 24.8, 1e-9, 'tras releer')

fin()
