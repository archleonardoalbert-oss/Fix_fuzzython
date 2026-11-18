# A11 · ALTO · Entrada difusa: ignora que Polygon se prolonga fuera de sus puntos
#
# Qué pasa: fsets/fuzzy_set.py:134-136 y fsets/polygon.py:70-72 devuelven 0 si los intervalos no se
# cortan. Pero Polygon.__call__ (polygon.py:35-38) prolonga el primer y el último valor hacia fuera
# (así funcionan los «hombros»). Ejecutado con cold = Polygon((0,1),(15,1),(20,0)): la entrada nítida
# -10 da grado 1; la entrada difusa «unos -10» da 0. La misma entrada da resultados opuestos.
#
# Solucionado cuando: una entrada difusa muy estrecha alrededor de x da el mismo grado que la entrada
# nítida x, dentro y fuera de los puntos del polígono, y Mamdani da lo mismo con ambas.
# (Vale para cualquier decisión sobre la prolongación: se compara con lo que da la entrada nítida.)
from _comun import *

inicio('A11', 'Alto', 'Entrada difusa: ignora la prolongación de Polygon')

def estrecha(x):
    return fz('Triangular')((x - 0.05, 0), (x, 1), (x + 0.05, 0))

for adj, x in (('cold', -10), ('cold', -0.5), ('hot', 50), ('hot', 40.5), ('cold', 5), ('normal', 25)):
    @prueba(f'{adj}: entrada difusa estrecha en {x} == entrada nítida {x}')
    def _(adj=adj, x=x):
        a = escenario()[adj]
        return cerca(a.membership(estrecha(x)), a.membership(x), 0.02, 'grado')

@prueba('Entrada Singleton(-10) sobre cold == entrada nítida -10')
def _():
    a = escenario()['cold']
    return cerca(a.membership(fz('Singleton')(-10, 1.0)), a.membership(-10), 1e-9, 'grado')

@prueba('Mamdani de sample.py: entrada difusa estrecha en -10 da lo mismo que -10 nítido')
def _():
    nitido = numero(mamdani().compute({'temp': -10}))
    difuso = numero(mamdani().compute({'temp': estrecha(-10)}))
    return cerca(difuso, nitido, 0.05, 'resultado')

fin()
