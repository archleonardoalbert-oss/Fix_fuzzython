# A4 · ALTO · `membership` enlazado a la clase equivocada
#
# Qué pasa: fsets/fuzzy_set.py:56 y fsets/sfunction.py:44 hacen `membership = __call__`, que queda
# ligado a la función de la clase donde se escribe. Las subclases que redefinen __call__ sin repetir
# esa línea heredan un membership viejo: ZFunction (da la S), Singleton y PiFunction (dan siempre 0).
# fuzzify_with (entradas difusas) usa membership, así que con estas formas el grado sale mal.
# Origen: F4 de Penumbra.
#
# Solucionado cuando: membership(x) == conjunto(x) en todas las formas (también en una subclase
# nueva del usuario que solo define __call__), y las entradas difusas dan el grado correcto.
# Nota: el caso de PiFunction no puede pasar mientras A5 siga sin arreglar.
from _comun import *

inicio('A4', 'Alto', 'membership enlazado a la clase equivocada')

XS = [i / 4 for i in range(-4, 45)]

def formas():
    return {'Polygon': fz('Polygon')((0, 0), (5, 1), (10, 0)),
            'Triangular': fz('Triangular')((0, 0), (5, 1), (10, 0)),
            'Trapezoid': fz('Trapezoid')((0, 0), (2, 1), (6, 1), (10, 0)),
            'Gaussian': fz('Gaussian')(5, 2),
            'SFunction': fz('SFunction')((0, 0), 5, (10, 1)),
            'ZFunction': fz('ZFunction')((0, 0), 5, (10, 1)),
            'Singleton': fz('Singleton')(3, 0.8),
            'Gamma': fz('Gamma')(2, 0.5, fz('Interval')(0, 10))}

for nombre in ('Polygon', 'Triangular', 'Trapezoid', 'Gaussian', 'SFunction', 'ZFunction', 'Singleton', 'Gamma'):
    @prueba(f'{nombre}: membership(x) == {nombre}(x) en 49 puntos')
    def _(nombre=nombre):
        c = formas()[nombre]
        malos = [(x, c(x), c.membership(x)) for x in XS + [3] if c(x) != c.membership(x)]
        exigir(not malos, f'distintos, p. ej. x={malos[0][0]}: call={malos[0][1]:.4g}, membership={malos[0][2]:.4g}' if malos else '')

@prueba('PiFunction: membership(x) == PiFunction(x)  (depende también de A5)')
def _():
    p = fz('PiFunction')(5, 2)
    malos = [x for x in XS if p(x) != p.membership(x)]
    exigir(not malos, f'distintos en x = {malos[:3]}')

@prueba('Una subclase del usuario que solo define __call__ tiene membership coherente')
def _():
    FS, I = fz('FuzzySet'), fz('Interval')
    class Rampa(FS):
        def __init__(self):
            super().__init__(None, I(0, 10))
        def __call__(self, x):
            return min(1.0, max(0.0, x / 10))
    r = Rampa()
    return cerca(r.membership(7), 0.7, 1e-12, 'membership(7)')

@prueba('Entrada difusa Singleton(8) sobre un adjetivo ZFunction da Z(8)')
def _():
    z = fz('ZFunction')((0, 0), 5, (10, 1))
    adj = fz('Adjective')('z', z)
    return cerca(adj.membership(fz('Singleton')(8, 1.0)), z(8), 1e-9, 'grado')

@prueba('Entrada difusa triangular estrecha sobre un adjetivo ZFunction ≈ Z en su centro')
def _():
    z = fz('ZFunction')((0, 0), 5, (10, 1))
    adj = fz('Adjective')('z', z)
    g = adj.membership(fz('Triangular')((7.9, 0), (8, 1), (8.1, 0)))
    return cerca(g, z(7.9), 0.03, 'grado')

fin()
