# C7 · CRÍTICO · Una entrada que falta reutiliza el valor de la llamada anterior
#
# Qué pasa: Variable.reset no borra el valor (variable.py:37, `#self.value = None` comentado) y
# RuleBlock.fuzzify (ruleblock.py:82-91) no comprueba que estén todas las entradas.
#   - compute({'temp': 33}) y luego compute({}) devuelven lo mismo: usa temp = 33 de antes.
#   - Si falta en la primera llamada: TypeError '<=' entre NoneType e int, sin decir qué falta.
#
# Solucionado cuando: compute sin alguna entrada lanza un error que nombra la variable que falta, en
# la primera llamada y en las siguientes, y después una llamada correcta sigue funcionando.
from _comun import *

inicio('C7', 'Crítico', 'Una entrada ausente reutiliza el valor anterior')

@prueba('Tras compute({temp: 33}), compute({}) lanza un error que nombra «temp»')
def _():
    m = mamdani()
    m.compute({'temp': 33})
    espera_error(lambda: m.compute({}), contiene=['temp'])

@prueba('En la primera llamada, compute({}) lanza un error que nombra «temp»')
def _():
    espera_error(lambda: mamdani().compute({}), contiene=['temp'])

@prueba('Con dos entradas, olvidar «hum» lanza un error que nombra «hum»')
def _():
    s = escenario()
    A, P = fz('Adjective'), fz('Polygon')
    s['humedo'] = A('humedo', P((50, 0), (90, 1)))
    s['hum'] = var('hum', s['humedo'])
    m = mamdani(['if temp is hot and hum is humedo then tm is large'], s)
    m.compute({'temp': 33, 'hum': 70})
    espera_error(lambda: m.compute({'temp': 33}), contiene=['hum'])

@prueba('Sugeno y Tsukamoto también avisan de la entrada que falta')
def _():
    s = sugeno(['if temp is hot then z = temp*0.6 + 2'])
    s.compute({'temp': 38})
    espera_error(lambda: s.compute({}), contiene=['temp'])
    t = tsukamoto(['t:if temp is hot then tm is large'])
    t.compute({'temp': 38})
    espera_error(lambda: t.compute({}), contiene=['temp'])

@prueba('Después del error, una llamada correcta da 24.144')
def _():
    m = mamdani()
    try:
        m.compute({})
    except Exception:
        pass
    return cerca(numero(m.compute({'temp': 33})), 24.1440329, 1e-4, 'Mamdani')

fin()
