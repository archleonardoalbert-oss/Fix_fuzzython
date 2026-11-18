# B5 · BAJO · Polygon y FuzzySet: errores varios de API
#
# Qué pasa:
#   - rules/rule.py:50 errata `p.adective`: input_adj() falla con antecedentes compuestos (F13).
#   - fsets/polygon.py:311-324 `p[i] = valor`: un entero menor que la longitud es índice; mayor, una x.
#   - fsets/polygon.py:201-202 merge_points con un polígono vacío devuelve tuplas en vez de x.
#   - fsets/gamma.py:22-23 no convierte una tupla en Interval (Polynomial sí).
#   - fsets/fuzzy_set.py:85-87,97-99 `&` y `|` con un número fallan.
#   - fsets/fuzzy_set.py:409-410 iterar un FuzzySet da sus normas; iterar un Polygon, sus puntos.
#   - fsets/fuzzy_set.py:162 y polygon.py:99 COG divide por el área sin comprobar que no sea 0.
#
# Solucionado cuando: cada caso da el resultado esperado o un error claro.
from _comun import *

inicio('B5', 'Bajo', 'API de Polygon y FuzzySet')

P = lambda *p: fz('Polygon')(*p)

@prueba('input_adj() de una regla con antecedente compuesto devuelve sus adjetivos')
def _():
    r = list(bloque(['if temp is hot and temp is cold then tm is large'], escenario()).rules)[0]
    nombres = sorted(a.name for a in r.input_adj())
    exigir(nombres == ['cold', 'hot'], f'devuelve {nombres}')

@prueba('p[1] = 0.5 cambia la y del punto 1 o lanza un error sin estropear el polígono')
def _():
    p = P((0, 0), (1, 1), (2, 0))
    try:
        p[1] = 0.5
    except Exception as e:
        exigir(list(p) == [(0, 0), (1, 1), (2, 0)], f'tras el error el polígono queda {list(p)}')
        return f'lanza {type(e).__name__}'
    exigir(list(p) == [(0, 0), (1, 0.5), (2, 0)], f'queda {list(p)}')

@prueba('fuzzify_with contra un polígono vacío da 0 o un error claro (ValueError/TypeError)')
def _():
    try:
        r = P((0, 0), (1, 1)).fuzzify_with(P())
    except (ValueError, TypeError) as e:
        return f'lanza {type(e).__name__}: {e}'
    return cerca(r, 0, 0, 'grado')

@prueba('Gamma con intervalo en tupla admite unión')
def _():
    G = fz('Gamma')
    u = G(0, 1, (0, 10)).union(G(5, 1, (0, 10)))
    return cerca(u(3), max(G(0, 1, (0, 10))(3), G(5, 1, (0, 10))(3)), 1e-12, 'u(3)')

@prueba('Polygon & 0.5 y Polygon | 0.5 funcionan como min/max con el número')
def _():
    p = P((0, 0), (5, 1), (10, 0))
    cerca((p & 0.5)(5), 0.5, 1e-12, '(p & 0.5)(5)')
    return cerca((p | 0.5)(0), 0.5, 1e-12, '(p | 0.5)(0)')

@prueba('Iterar cualquier conjunto da lo mismo en todas las clases (no las normas en unas y puntos en otras)')
def _():
    g, p = fz('Gaussian')(0, 1), P((0, 0), (1, 1))
    try:
        eg = list(g)
    except TypeError:
        eg = None
    exigir(eg is None or not callable(eg[0]), 'iterar un FuzzySet devuelve sus normas')

@prueba('COG de un conjunto con área 0 da un error claro o NaN, no ZeroDivisionError')
def _():
    FS, I = fz('FuzzySet'), fz('Interval')
    for c in (FS(lambda x: 0, I(0, 1)), P((0, 0), (1, 0))):
        try:
            r = c.COG()
        except ZeroDivisionError:
            raise Falla(f'{type(c).__name__}: ZeroDivisionError')
        except Exception:
            continue
        exigir(es_nan(r), f'{type(c).__name__}: devuelve {r!r}')

fin()
