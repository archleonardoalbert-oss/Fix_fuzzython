# C2 · CRÍTICO · time.clock no existe: todo compute() falla
#
# Qué pasa: el decorador `timer` de utils.py:29,31 llama a time.clock(), retirado en Python 3.8.
# Ese decorador envuelve compute() en systems/mamdani.py:34, sugeno.py:27 y tsukamoto.py:30, así que
# en un Python actual ningún sistema calcula: AttributeError: module 'time' has no attribute 'clock'.
# Origen: F1 de Penumbra.
#
# Solucionado cuando: los tres sistemas calculan en un proceso limpio, sin parchear time, y el
# código ya no usa time.clock en ningún sitio.
# (Los demás scripts parchean time.clock para que este fallo no tape los suyos; este no.)
from _comun import *

inicio('C2', 'Crítico', 'time.clock no existe: todo compute() falla')

def en_limpio(codigo):
    r = aislado(codigo, parche_clock=False)
    exigir(r.returncode == 0, ' | '.join(r.stderr.strip().splitlines()[-1:]) or f'código {r.returncode}')
    return float(r.stdout.strip().splitlines()[-1])

@prueba('Mamdani calcula sin parchear time (sample, temp = 33)', t=60)
def _():
    return cerca(en_limpio("print(numero(mamdani().compute({'temp': 33})))"), 24.1440329, 1e-4, 'Mamdani')

@prueba('Sugeno calcula sin parchear time', t=60)
def _():
    v = en_limpio("print(numero(sugeno(['if temp is normal then z = temp*0.3 + 1', 'if temp is hot then z = temp*0.6 + 2']).compute({'temp': 33})))")
    return cerca(v, 17.44, 1e-6, 'Sugeno')

@prueba('Tsukamoto calcula sin parchear time', t=60)
def _():
    v = en_limpio("print(numero(tsukamoto(['t:if temp is cold then tm is short', 't:if temp is normal then tm is large with 0.5', 't:if temp is hot then tm is large']).compute({'temp': 33})))")
    return cerca(v, 20.0, 1e-4, 'Tsukamoto')

@prueba('Ningún .py del repo usa time.clock')
def _():
    usos = [f'{p.relative_to(REPO)}:{i}' for p in REPO.rglob('*.py') if '.git' not in p.parts
            for i, l in enumerate(p.read_text(errors='replace').splitlines(), 1) if 'time.clock' in l or 'clock()' in l]
    exigir(not usos, 'aparece en ' + ', '.join(usos))

fin()
