# A12 · ALTO · Norma inexistente: None en silencio; norma de otro tipo: aceptada
#
# Qué pasa: norms/norms.py:90-109 (get_norm) y ruleblock.py:24-37.
#   - Un nombre que no existe imprime «unsupported norm X» y devuelve None. En ACT, todas las salidas
#     dan el default; en AND/OR, And/Or ponen MIN/MAX sin avisar.
#   - No se comprueba el tipo: activation='MAX' (S-norma) se acepta; operators=('ZADEH', ...) se acepta
#     y falla al calcular con TypeError.
#   - get_norm('max1') encuentra el archivo pero compara mayúsculas exactas y devuelve None sin avisar.
# Origen: F12 de Penumbra + lo demás, nuevo.
#
# Solucionado cuando: un nombre inexistente o de tipo equivocado lanza un error al crear el RuleBlock
# (no al calcular), los nombres válidos siguen funcionando, y get_norm nunca devuelve None en silencio.
from _comun import *

inicio('A12', 'Alto', 'Normas inválidas aceptadas en silencio')

RB = lambda **k: fz('RuleBlock')('b', **k)

@prueba('activation="NOEXISTE" lanza un error al crear el bloque que nombra la norma')
def _():
    espera_error(lambda: RB(activation='NOEXISTE'), contiene=['NOEXISTE'])

@prueba('accumulation="NOEXISTE" lanza un error al crear el bloque')
def _():
    espera_error(lambda: RB(accumulation='NOEXISTE'), contiene=['NOEXISTE'])

@prueba('operators=("NOEXISTE", "MAX", "ZADEH") lanza un error al crear el bloque')
def _():
    espera_error(lambda: RB(operators=('NOEXISTE', 'MAX', 'ZADEH')), contiene=['NOEXISTE'])

@prueba('activation="MAX" (una S-norma) se rechaza: la activación debe ser una T-norma')
def _():
    espera_error(lambda: RB(activation='MAX'))

@prueba('accumulation="MIN" (una T-norma) se rechaza: la acumulación debe ser una S-norma')
def _():
    espera_error(lambda: RB(accumulation='MIN'))

@prueba('operators=("ZADEH", "MAX", "ZADEH") se rechaza al crear el bloque (AND no puede ser un complemento)')
def _():
    espera_error(lambda: RB(operators=('ZADEH', 'MAX', 'ZADEH')))

@prueba('get_norm de un nombre inexistente no devuelve None en silencio')
def _():
    try:
        r, out, err = capturar(lambda: fz('get_norm')('NOEXISTE'))
    except Exception:
        return 'lanza un error'
    raise Falla(f'devuelve {r!r}' + (f' e imprime {out.strip()!r}' if out.strip() else ''))

@prueba('get_norm("max1") encuentra la norma MAX1 de norms/max1.py (o lanza un error claro)')
def _():
    try:
        r = fz('get_norm')('max1')
    except Exception:
        return 'lanza un error'
    exigir(r is not None, 'devuelve None sin avisar')

@prueba('Control: todas las normas válidas se aceptan en su sitio y el Mamdani calcula')
def _():
    for t, s_ in (('MIN', 'MAX'), ('PROD', 'ASUM'), ('BDIF', 'BSUM'), ('EPROD', 'ESUM'), ('DPROD', 'DSUM')):
        numero(mamdani(operators=(t, s_, 'ZADEH'), activation=t, accumulation=s_).compute({'temp': 33}))

fin()
