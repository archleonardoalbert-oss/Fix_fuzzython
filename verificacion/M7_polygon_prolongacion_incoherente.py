# M7 · MEDIO · Polygon: su prolongación fuera de los puntos no se respeta en todas partes
#
# Qué pasa: Polygon.__call__ (fsets/polygon.py:35-38) prolonga el primer y el último valor hacia fuera:
# Polygon((0,1),(1,1)) vale 1 en x = 3. Pero:
#   - Polygon.area_(a, b) (polygon.py:227-243) cuenta la prolongación de la izquierda y no la de la
#     derecha: Polygon((0,1),(1,1)).area_(-1, 2) da 2.0 (sería 3 con las dos y 1 sin ninguna).
#   - La unión de polígonos (polygon.py:155-160) usa esa prolongación, así que dos polígonos con borde
#     no nulo «rellenan» el hueco entre ellos (F18 de Penumbra), y fuzzify_with la ignora (A11).
#
# Solucionado cuando: la librería trata la prolongación de forma coherente: area_ coincide con la
# integral de la propia función en cualquier tramo, y la unión vale max(μa, μb) en todo punto.
# (Sirve tanto si se decide «vale 0 fuera» como «se prolonga constante»: se compara con __call__.)
from _comun import *

inicio('M7', 'Medio', 'Polygon: prolongación incoherente')

P = lambda *p: fz('Polygon')(*p)
FORMAS = [((0, 1), (1, 1)), ((0, 0.3), (2, 1), (4, 0.6)), ((10, 0), (15, 1), (20, 0))]
TRAMOS = [(-1, 2), (-3, -1), (5, 8), (-2, 25), (0.5, 3)]

for puntos in FORMAS:
    @prueba(f'Polygon{puntos}: area_(a, b) == ∫ p(x) dx en 5 tramos, dentro y fuera')
    def _(puntos=puntos):
        p = P(*puntos)
        for a, b in TRAMOS:
            cerca(p.area_(a, b), integral(p, a, b), 1e-3, f'area_({a}, {b})')

@prueba('Control: unión de Polygon((0,1),(2,1)) y Polygon((4,1),(6,1)) == max(μa, μb) en [-2, 8]')
def _():
    a, b = P((0, 1), (2, 1)), P((4, 1), (6, 1))
    u = a.union(b)
    malos = [x / 4 for x in range(-8, 33) if abs(u(x / 4) - max(a(x / 4), b(x / 4))) > 1e-9]
    exigir(not malos, f'distinto en x = {malos[:4]}')

@prueba('Control: el área de esa unión coincide con la integral de max(μa, μb) en su intervalo')
def _():
    a, b = P((0, 1), (2, 1)), P((4, 1), (6, 1))
    u = a.union(b)
    return cerca(u.area(), integral(lambda x: max(a(x), b(x)), 0, 6), 1e-3, 'área en [0, 6]')

fin()
