# B3 · BAJO · Detalles del analizador de reglas
#
# Qué pasa (rules/parser.py y operators/parser.py):
#   - :29 if/then/with y el `is` del consecuente solo en minúsculas, y ` then ` con espacios exactos.
#   - operators/parser.py:68 `NOT (` solo en mayúsculas.
#   - :24-27 prefijo sin strip(); uno desconocido (`x:`) se ignora.
#   - :37 sin `=` ni `is`: «substring not found».
#   - :72-79 tras cada predicado del consecuente salta un token suponiendo que es `,`: sin coma da
#     AssertionError y `WITH` en mayúsculas da IndexError.
#   - operators/parser.py:31 con scope=None usa los globales del módulo del analizador.
#   - rules/rule.py:11,25-26 el número de regla es un contador global del proceso.
#
# Solucionado cuando: las palabras clave valen en mayúsculas o minúsculas y con cualquier espacio, los
# prefijos se validan, y cada error da un mensaje que explica el problema.
from _comun import *

inicio('B3', 'Bajo', 'Detalles del analizador de reglas')

def regla(texto):
    return bloque([texto], escenario())

@prueba('«IF temp IS hot THEN tm IS large» (mayúsculas) calcula lo mismo que en minúsculas')
def _():
    return cerca(numero(mamdani(['IF temp IS hot THEN tm IS large']).compute({'temp': 38})), 33.6666666, 1e-3, 'COG')

@prueba('«if not (temp is cold) then ...» (not en minúsculas) se acepta')
def _():
    regla('if not (temp is cold) then tm is large')

@prueba('Tabulador o dos espacios alrededor de then se aceptan')
def _():
    regla('if temp is hot\tthen tm is large')
    regla('if temp is hot  then  tm is large')

@prueba('«... WITH 0.5» en mayúsculas se acepta con peso 0.5')
def _():
    a = numero(mamdani(['if temp is hot then tm is large WITH 0.5']).compute({'temp': 38}))
    b = numero(mamdani(['if temp is hot then tm is large with 0.5']).compute({'temp': 38}))
    return cerca(a, b, 1e-12, 'WITH 0.5')

@prueba('Prefijo con espacio « t:if ...» crea una regla Tsukamoto que calcula')
def _():
    return cerca(numero(tsukamoto([' t:if temp is hot then tm is large']).compute({'temp': 38})), 40, 1e-3, 'x')

@prueba('Prefijo desconocido «x:if ...» lanza un error')
def _():
    espera_error(lambda: regla('x:if temp is hot then tm is large'))

@prueba('Regla sin «=» ni «is» en el consecuente: el error no es «substring not found»')
def _():
    e = espera_error(lambda: regla('if temp is hot then tm usual'))
    exigir('substring not found' not in str(e), f'mensaje: {e}')

@prueba('Consecuente sin coma entre predicados: error que no es AssertionError ni IndexError')
def _():
    espera_error(lambda: regla('if temp is hot then tm is short tm is large'), no_valen=(AssertionError, IndexError))

@prueba('scope=None da un error que menciona «scope»')
def _():
    def hacer():
        b = fz('RuleBlock')('b')
        b.add_rules('if temp is hot then tm is large', scope=None)
    espera_error(hacer, contiene=['scope'])

@prueba('Las reglas de cada bloque se numeran desde 1')
def _():
    texto = ' '.join(str(r) for r in mamdani().blocks['b'].rules)
    exigir('RULE 1:' in texto or 'Rule 1' in texto, f'reglas: {texto[:120]}')

fin()
