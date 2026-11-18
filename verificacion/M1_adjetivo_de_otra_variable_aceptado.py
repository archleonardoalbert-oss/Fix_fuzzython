# M1 · MEDIO · Se acepta un adjetivo que no pertenece a la variable
#
# Qué pasa: rules/parser.py:106-111 y operators/parser.py:117-127 solo buscan los nombres en `scope`;
# nunca comprueban que el adjetivo sea de esa variable.
#   - `if temp is short then tm is large` (short es de tm) calcula short(temp) y da 33.67 sin avisar.
#   - `if temp is hot then tm is hot` (hot es de temp) activa un adjetivo de temp; tm no recibe nada.
#
# Solucionado cuando: las reglas que mezclan variable y adjetivo ajeno se rechazan al añadirlas, en el
# antecedente y en el consecuente, y las reglas correctas se siguen aceptando.
from _comun import *

inicio('M1', 'Medio', 'Adjetivo de otra variable aceptado')

for regla, donde in (('if temp is short then tm is large', 'antecedente'),
                     ('if temp is hot then tm is hot', 'consecuente'),
                     ('if temp is hot and temp is usual then tm is large', 'antecedente compuesto'),
                     ('if temp is hot then tm is large, tm is cold', 'segundo consecuente'),
                     ('t:if temp is hot then tm is normal', 'consecuente Tsukamoto')):
    @prueba(f'Se rechaza ({donde}): «{regla}»')
    def _(regla=regla):
        espera_error(lambda: bloque([regla], escenario()))

@prueba('Se rechaza en Sugeno: «if temp is short then z = temp*2»')
def _():
    espera_error(lambda: sugeno(['if temp is short then z = temp*2']))

@prueba('Control: las reglas correctas de sample.py se aceptan y calculan 24.144')
def _():
    return cerca(numero(mamdani().compute({'temp': 33})), 24.1440329, 1e-4, 'Mamdani')

fin()
