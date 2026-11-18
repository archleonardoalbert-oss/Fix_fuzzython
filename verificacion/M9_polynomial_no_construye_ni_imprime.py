# M9 · MEDIO · Polynomial no se puede construir con tupla ni imprimir
#
# Qué pasa: fsets/polynomial.py:18 usa Interval sin importarlo (NameError al pasar interval=(a, b)), y
# polynomial.py:189 hace ','.join sobre números (TypeError en str(p), y por tanto en dump()).
# Además, `grade` (polynomial.py:143-147) es el número de coeficientes, no el grado: x² da 3.
# Origen: F14 de Penumbra.
#
# Solucionado cuando: Polynomial se construye con tupla o Interval, evalúa, integra, se imprime con
# str() mostrando sus coeficientes y `grade` da el grado matemático.
from _comun import *

inicio('M9', 'Medio', 'Polynomial: construcción e impresión')

Poly = lambda *c, **k: fz('Polynomial')(*c, **k)

@prueba('Polynomial(1, 0, interval=(0, 1)) se construye y vale 0.5 en 0.5')
def _():
    return cerca(Poly(1, 0, interval=(0, 1))(0.5), 0.5, 1e-12, 'p(0.5)')

@prueba('Control: con interval=Interval(0, 2): x² - x evalúa y su área es 2/3')
def _():
    p = Poly(1, -1, 0, interval=fz('Interval')(0, 2))
    cerca(p(2), 2, 1e-12, 'p(2)')
    return cerca(p.area(), 2 / 3, 1e-9, 'área')

@prueba('str(p) no falla y muestra los coeficientes')
def _():
    s = str(Poly(3, 2, interval=(0, 1)))
    exigir('3' in s and '2' in s, f'str = {s!r}')
    return f'str = {s!r}'

@prueba('grade de x² es 2 y de una constante es 0')
def _():
    exigir(Poly(1, 0, 0, interval=(0, 1)).grade == 2, f'x²: grade = {Poly(1, 0, 0, interval=(0, 1)).grade}')
    exigir(Poly(5, interval=(0, 1)).grade == 0, f'constante: grade = {Poly(5, interval=(0, 1)).grade}')

@prueba('Suma y producto de polinomios construidos con tupla')
def _():
    a, b = Poly(1, 0, interval=(0, 1)), Poly(1, 1, interval=(0, 1))
    cerca((a + b)(2), 5, 1e-12, '(a+b)(2)')
    return cerca((a * b)(2), 6, 1e-12, '(a·b)(2)')

fin()
