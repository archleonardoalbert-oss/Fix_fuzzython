# M2 · MEDIO · El analizador ignora el texto sobrante y valida con assert
#
# Qué pasa:
#   - operators/parser.py:37-39: parse() no comprueba que se hayan consumido todos los tokens.
#     `if temp is hot cold blah then ...`, `... xor ...` o paréntesis de más se aceptan en silencio.
#   - operators/parser.py:66,71,74,105, rules/parser.py:20,94 y systems/system.py:30 validan la entrada
#     del usuario con assert. Con `python -O` los assert desaparecen y esos errores pasan.
#
# Solucionado cuando: todo texto que sobra o falta en una regla produce un error, también ejecutando
# Python con -O, y las reglas correctas (con paréntesis y NOT) siguen aceptándose.
from _comun import *

inicio('M2', 'Medio', 'El analizador ignora texto sobrante y valida con assert')

SOBRAN = ['if temp is hot cold blah then tm is large',
          'if temp is hot xor temp is cold then tm is large',
          'if temp is hot ) ) then tm is large',
          'if temp is hot and then tm is large',
          'if temp is hot then tm is large tm']
for regla in SOBRAN:
    @prueba(f'Se rechaza: «{regla}»')
    def _(regla=regla):
        espera_error(lambda: bloque([regla], escenario()))

MAL_CON_O = ['if ( temp is hot then tm is large',
             'if temp is hot then tm was large',
             'if temp equals hot then tm is large',
             'if NOT temp is hot ) then tm is large']

@prueba('Con python -O también se rechazan reglas mal formadas', t=60)
def _():
    codigo = f'''
s = escenario()
for regla in {MAL_CON_O!r}:
    try:
        bloque([regla], s)
        print('ACEPTA', regla)
    except Exception:
        print('RECHAZA', regla)
'''
    r = aislado(codigo, opciones=['-O'], parche_clock=True)
    exigir(r.returncode == 0, r.stderr.strip()[-300:])
    aceptadas = [l[7:] for l in r.stdout.splitlines() if l.startswith('ACEPTA')]
    exigir(not aceptadas, 'con -O se aceptan: ' + ' | '.join(aceptadas))

@prueba('Control: con python -O, System rechaza algo que no es un RuleBlock', t=60)
def _():
    r = aislado('''
try:
    fz('MamdaniSystem')('m', 'no soy un bloque'); print('ACEPTA')
except Exception:
    print('RECHAZA')
''', opciones=['-O'], parche_clock=True)
    exigir('RECHAZA' in r.stdout, 'con -O acepta un str como bloque')

@prueba('Control: reglas correctas con paréntesis, NOT e «is not» se aceptan')
def _():
    bloque(['if (temp is hot or temp is cold) and temp is not normal then tm is large',
            'if NOT (temp is hot) then tm is short'], escenario())

fin()
