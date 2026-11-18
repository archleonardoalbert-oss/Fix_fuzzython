# M18 · MEDIO · Reglas Sugeno en Python: sin -x, ** ni //
#
# Qué pasa: variable.py:80-111. Variable define + - * /, pero no __neg__, __pow__ ni __floordiv__.
# __div__ y __rdiv__ (variable.py:106-111) son nombres de Python 2 que Python 3 nunca llama (y además
# hacen división entera). Así `z = -temp`, `z = temp**2` o `z = temp//2` lanzan TypeError.
#
# Solucionado cuando: esas operaciones (y paréntesis, y potencias con la variable a la derecha) dan su
# valor aritmético en un consecuente Sugeno.
from _comun import *

inicio('M18', 'Medio', 'Sugeno en Python: -x, ** y //')

CASOS = [('-temp', -38), ('temp**2', 1444), ('2**temp / 2**36', 4), ('temp//5', 7), ('-temp + 40', 2),
         ('(temp + 2) * 2', 80)]
for expr, esperado in CASOS:
    @prueba(f'z = {expr}  con temp = 38  ->  {esperado}')
    def _(expr=expr, esperado=esperado):
        return cerca(numero(sugeno([f'if temp is hot then z = {expr}']).compute({'temp': 38})), esperado, 1e-9, expr)

fin()
