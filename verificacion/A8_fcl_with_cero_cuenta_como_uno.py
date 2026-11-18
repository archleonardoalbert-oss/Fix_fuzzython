# A8 · ALTO · FCL: WITH 0.0 se convierte en peso 1
#
# Qué pasa: store/FCL.g:199 hace `Rule.get_rule(c1, c2, w or 1)`, y `0.0 or 1` es 1. Una regla con
# WITH 0.0 cuenta con peso completo. En Python (`with 0`) el peso sí es 0: los caminos no coinciden.
#
# Solucionado cuando: WITH 0.0 y WITH 0 anulan la regla, los pesos intermedios se respetan, y FCL y
# Python dan lo mismo para el mismo peso.
from _comun import *

inicio('A8', 'Alto', 'FCL: WITH 0.0 cuenta como peso 1')

SOLO_SHORT = 'RULE 2: IF temp IS hot THEN tm IS short;'
REF_SHORT = cog(pl((0, 1), (10, 1), (15, 0)), 0, 15)

for peso in ('0.0', '0'):
    @prueba(f'WITH {peso}: la regla no aporta nada (resultado = solo la otra regla)')
    def _(peso=peso):
        r = numero(fcl(f'RULE 1: IF temp IS hot THEN tm IS large WITH {peso}; {SOLO_SHORT}').compute({'temp': 38}))
        return cerca(r, REF_SHORT, 1e-3, 'COG')

@prueba('WITH 0.5 en FCL da lo mismo que `with 0.5` en Python')
def _():
    f = numero(fcl('RULE 1: IF temp IS hot THEN tm IS large WITH 0.5;').compute({'temp': 38}))
    p = numero(mamdani(['if temp is hot then tm is large with 0.5']).compute({'temp': 38}))
    return cerca(f, p, 1e-9, 'FCL vs Python')

@prueba('WITH 0.0 en FCL da lo mismo que `with 0` en Python (dos reglas)')
def _():
    f = numero(fcl(f'RULE 1: IF temp IS hot THEN tm IS large WITH 0.0; {SOLO_SHORT}').compute({'temp': 38}))
    p = numero(mamdani(['if temp is hot then tm is large with 0', 'if temp is hot then tm is short']).compute({'temp': 38}))
    return cerca(f, p, 1e-9, 'FCL vs Python')

@prueba('Única regla con WITH 0.0: se comporta como «nada disparó» (devuelve el DEFAULT 0)')
def _():
    return cerca(numero(fcl('RULE 1: IF temp IS hot THEN tm IS large WITH 0.0;').compute({'temp': 38})), 0, 1e-12, 'resultado')

fin()
