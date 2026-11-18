# M6 · MEDIO · Tsukamoto con consecuente no monótono da cualquier cosa
#
# Qué pasa: rules/trule.py:60-92. La bisección supone que el consecuente es monótono y no lo comprueba.
# Ejecutado: con Polygon((0,0),(20,1),(40,0)) como consecuente, fuerzas 0.5 y 0.85 dan (0, 0).
# Origen: F22 de Penumbra.
#
# Solucionado cuando: una regla Tsukamoto con consecuente no monótono se rechaza con un error (al
# crearla o al calcular), y los consecuentes monótonos (también los que tienen mesetas) siguen bien.
from _comun import *

inicio('M6', 'Medio', 'Tsukamoto acepta consecuentes no monótonos')

def con(*puntos):
    s = escenario_tsukamoto()
    s['raro'] = fz('Adjective')('raro', fz('Polygon')(*puntos))
    s['tm'] = var('tm', s['short'], s['large'], s['raro'], defuzzification='COG', default=0)
    return s

for puntos in (((0, 0), (20, 1), (40, 0)), ((0, 1), (20, 0), (40, 1)), ((0, 0), (10, 1), (20, 0.5), (40, 1))):
    @prueba(f'Consecuente no monótono {puntos} se rechaza')
    def _(puntos=puntos):
        espera_error(lambda: tsukamoto(['t:if temp is hot then tm is raro'], con(*puntos)).compute({'temp': 33}))

@prueba('Control: el Tsukamoto de sample.py (consecuentes con meseta) sigue dando 20')
def _():
    r = numero(tsukamoto(['t:if temp is cold then tm is short', 't:if temp is normal then tm is large with 0.5',
                          't:if temp is hot then tm is large']).compute({'temp': 33}))
    return cerca(r, 20.0, 1e-4, 'Tsukamoto')

fin()
