# A10 · ALTO · fuzzify_with entra en bucle infinito
#
# Qué pasa: fsets/fuzzy_set.py:134-145. Si los intervalos del adjetivo y de la entrada difusa solo
# comparten un punto, step = (b - a)/100 = 0 y `while a <= b: a += step` no termina nunca. Ejecutado:
# un adjetivo Gaussian(0,1) (intervalo [-1,1]) con la entrada Triangular((1,0),(2,1),(3,0)) cuelga
# el programa.
#
# Solucionado cuando: todos los casos con intersección de un solo punto terminan enseguida y dan el
# valor correcto de sup_x T(μA(x), μB(x)).
from _comun import *

inicio('A10', 'Alto', 'fuzzify_with: bucle infinito')

FS = lambda f, a, b: fz('FuzzySet')(f, fz('Interval')(a, b))
Adj = lambda c: fz('Adjective')('a', c)

@prueba('Gaussian(0,1) con entrada Triangular((1,0),(2,1),(3,0)): termina y da un grado en [0, 1]', t=5)
def _():
    g = Adj(fz('Gaussian')(0, 1)).membership(fz('Triangular')((1, 0), (2, 1), (3, 0)))
    exigir(0 <= g <= 1, f'grado {g!r}')
    return f'grado = {g:.4g}'

@prueba('Rampa x en [0,1] y rampa 2-x en [1,2]: solo tocan en x = 1, el grado es 1', t=5)
def _():
    return cerca(Adj(FS(lambda x: x, 0, 1)).membership(FS(lambda x: 2 - x, 1, 2)), 1.0, 1e-9, 'grado')

@prueba('Entrada de intervalo [3,3] (un punto) sobre un adjetivo FuzzySet: da μ(3)', t=5)
def _():
    adj = Adj(FS(lambda x: x / 10, 0, 10))
    entrada = FS(lambda x: 1.0 if x == 3 else 0.0, 3, 3)
    return cerca(adj.membership(entrada), 0.3, 1e-9, 'grado')

@prueba('Entrada de intervalo [3,3] sobre un adjetivo Polygon: da μ(3)', t=5)
def _():
    adj = Adj(fz('Polygon')((0, 0), (10, 1)))
    entrada = FS(lambda x: 1.0 if x == 3 else 0.0, 3, 3)
    return cerca(adj.membership(entrada), 0.3, 1e-9, 'grado')

@prueba('Dentro de un Mamdani: entrada difusa que toca un adjetivo en un punto no cuelga', t=10)
def _():
    s = escenario()
    s['templado'] = fz('Adjective')('templado', FS(lambda x: max(0.0, 1 - abs(x - 25) / 5), 20, 30))
    s['temp'] = var('temp', s['templado'], s['hot'])
    m = mamdani(['if temp is templado then tm is usual', 'if temp is hot then tm is large'], s)
    r = numero(m.compute({'temp': FS(lambda x: max(0.0, 1 - abs(x - 32) / 2), 30, 34)}))
    exigir(isinstance(r, (int, float)), f'resultado {r!r}')
    return f'resultado = {r:.4g}'

fin()
