# C3 · CRÍTICO · Un FCL con errores de sintaxis se carga igual, a medias y sin avisar
#
# Qué pasa: store/reader.py:28-42 solo captura excepciones de Python. El parser que genera ANTLR 3 se
# recupera de los errores de sintaxis: escribe «line N:M ...» en stderr, se salta lo que no entiende y
# devuelve un sistema distinto del escrito. Ejemplo: `_MAMDANI_` (bien escrito) da un sistema vacío.
# Cuando sí hay excepción, hace print y devuelve None.
#
# Solucionado cuando: cada FCL incorrecto lanza una excepción (no devuelve None ni un sistema a
# medias), el mensaje dice la línea del error o el nombre que falta, y un FCL correcto sigue cargando.
# Necesita el runtime antlr3 (incluido en verificacion/_vendor) mientras el lector use ANTLR.
from _comun import *

inicio('C3', 'Crítico', 'Un FCL con errores de sintaxis se carga igual, a medias y sin avisar')

def linea_de(texto, trozo):
    return next(i for i, l in enumerate(texto.splitlines(), 1) if trozo in l)

@prueba('Control: un FCL correcto carga y calcula (temp = 38 -> 33.667)')
def _():
    return cerca(numero(fcl().compute({'temp': 38})), 33.6666666, 1e-3, 'Mamdani FCL')

@prueba('WITH sin número lanza un error que cita la línea')
def _():
    t = texto_fcl('RULE 1: IF temp IS hot THEN tm IS large WITH ;')
    espera_error(lambda: cargar_fcl(t), contiene=[str(linea_de(t, 'RULE 1'))])

@prueba('Una instrucción desconocida dentro del bloque lanza un error')
def _():
    t = texto_fcl().replace('VAR_OUTPUT tm: REAL; END_VAR', 'VAR_OUTPUT tm: REAL; END_VAR\nFOOBAR temp;')
    espera_error(lambda: cargar_fcl(t))

@prueba('Un archivo truncado (sin END_FUNCTION_BLOCK) lanza un error')
def _():
    espera_error(lambda: cargar_fcl(texto_fcl().replace('END_FUNCTION_BLOCK', '')))

@prueba('Una regla con una variable no declarada lanza un error que la nombra')
def _():
    espera_error(lambda: cargar_fcl(texto_fcl('RULE 1: IF presion IS hot THEN tm IS large;')), contiene=['presion'])

@prueba('Una regla con un término inexistente lanza un error que lo nombra')
def _():
    espera_error(lambda: cargar_fcl(texto_fcl('RULE 1: IF temp IS tibio THEN tm IS large;')), contiene=['tibio'])

@prueba('Un consecuente Sugeno mal formado (temp * *) lanza un error')
def _():
    espera_error(lambda: cargar_fcl(texto_fcl('RULE 1: IF temp IS hot THEN temp * * ;', tipo='_SUGENO_')))

@prueba('Un peso no numérico (WITH 0.5x) lanza un error en vez de saltarse el peso')
def _():
    espera_error(lambda: cargar_fcl(texto_fcl('RULE 1: IF temp IS hot THEN tm IS large WITH 0.5x;')))

fin()
