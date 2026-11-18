# A7 · ALTO · Sugeno: eval ejecuta código arbitrario y solo ve las variables del antecedente
#
# Qué pasa: rules/srule.py:15 construye el diccionario de variables solo con las del antecedente, y
# srule.py:28,31 evalúan el consecuente con eval(texto, ese_diccionario):
#   - `if temp is hot then z = p*2` lanza NameError aunque `p` sea una entrada del sistema.
#   - `z = __import__('os')...` SE EJECUTA: eval tiene todos los builtins. Una regla o un FCL de
#     origen desconocido puede ejecutar cualquier cosa en el equipo.
# Origen: F8 de Penumbra.
#
# Solucionado cuando: el consecuente puede usar cualquier entrada del sistema, sigue admitiendo
# aritmética normal, y cualquier intento de llamar funciones, importar módulos o acceder a atributos
# se rechaza con un error sin ejecutarse.
import tempfile
from pathlib import Path
from _comun import *

inicio('A7', 'Alto', 'Sugeno: eval inseguro y limitado al antecedente')

def con_p():
    return {'p': var('p', fz('Adjective')('alguno', fz('Polygon')((0, 1), (10, 1))))}

@prueba('El consecuente puede usar una entrada que no está en el antecedente (z = p*2 -> 6)')
def _():
    return cerca(numero(sugeno(['if temp is hot then z = p*2'], con_p()).compute({'temp': 38, 'p': 3})), 6, 1e-9, 'z')

@prueba('Mezcla de entradas: z = temp + p*10 -> 68')
def _():
    return cerca(numero(sugeno(['if temp is hot then z = temp + p*10'], con_p()).compute({'temp': 38, 'p': 3})), 68, 1e-9, 'z')

@prueba('Control: la aritmética normal sigue funcionando (z = temp*0.6 + 2 -> 24.8)')
def _():
    return cerca(numero(sugeno(['if temp is hot then z = temp*0.6 + 2']).compute({'temp': 38})), 24.8, 1e-9, 'z')

@prueba('Un consecuente que importa un módulo se rechaza y NO se ejecuta')
def _():
    with tempfile.TemporaryDirectory() as d:
        marca = Path(d) / 'ejecutado'
        regla = f"s:if temp is hot then z = len(__import__('pathlib').Path(r'{marca}').touch() or 'x')"
        espera_error(lambda: sugeno([regla]).compute({'temp': 38}))
        exigir(not marca.exists(), '¡el código de la regla se ejecutó y creó el archivo!')

@prueba('Llamar a builtins (len, open, eval) se rechaza')
def _():
    for expr in ("len('abc')", "eval('1+1')", "open('/etc/hostname').read()"):
        espera_error(lambda expr=expr: sugeno([f's:if temp is hot then z = {expr}']).compute({'temp': 38}))

@prueba('El acceso a atributos (temp.value, temp.__class__) se rechaza')
def _():
    for expr in ('temp.value * 1', 'len(temp.__class__.__name__)'):
        espera_error(lambda expr=expr: sugeno([f's:if temp is hot then z = {expr}']).compute({'temp': 38}))

fin()
