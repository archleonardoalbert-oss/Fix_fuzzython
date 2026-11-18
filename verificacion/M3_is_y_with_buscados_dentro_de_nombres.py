# M3 · MEDIO · «is» y «with» se buscan como texto dentro de nombres
#
# Qué pasa:
#   - rules/parser.py:35: `not IS in then_` busca la subcadena «is». `z = dist*2` se toma por Mamdani
#     y falla (AssertionError). Pasa con cualquier nombre que contenga «is» (dist, basis, crisis...).
#   - rules/parser.py:39-41: `WITH in consequent` busca la subcadena «with». `z = within*2` se parte
#     y lanza ValueError: could not convert string to float.
# Origen: F9 de Penumbra + «with», nuevo.
#
# Solucionado cuando: nombres que contienen «is» o «with» funcionan en consecuentes Sugeno (con y sin
# peso), y las reglas Mamdani siguen detectándose bien.
from _comun import *

inicio('M3', 'Medio', '«is» y «with» buscados dentro de nombres')

def con(nombre):
    A, P = fz('Adjective'), fz('Polygon')
    alto = A('alto', P((0, 0), (10, 1)))
    return {nombre: var(nombre, alto), 'alto': alto}

for nombre in ('dist', 'basis', 'within', 'without', 'this'):
    @prueba(f'Sugeno con la variable «{nombre}»: z = {nombre}*2 -> 20')
    def _(nombre=nombre):
        s = sugeno([f'if {nombre} is alto then z = {nombre}*2'], con(nombre))
        return cerca(numero(s.compute({nombre: 10})), 20, 1e-9, 'z')

@prueba('Sugeno con «within» y peso: z = within*2 with 0.5 (sigue valiendo 20 en la media ponderada)')
def _():
    s = sugeno(['if within is alto then z = within*2 with 0.5'], con('within'))
    return cerca(numero(s.compute({'within': 10})), 20, 1e-9, 'z')

@prueba('Control: una regla Mamdani con variable «crisis» se sigue tratando como Mamdani')
def _():
    s = escenario()
    s['crisis'] = s['tm']
    return cerca(numero(mamdani(['if temp is hot then crisis is large'], s).compute({'temp': 38})), 33.6666666, 1e-3, 'COG')

fin()
