# B6 · BAJO · SyntaxWarning por los dibujos de los docstrings
#
# Qué pasa: los dibujos ASCII de los docstrings contienen «\_» o «\ » (secuencias de escape inválidas):
# fsets/gamma.py:10, pifunction.py:14, trapezoid.py:14, triangular.py:13 y 70, zfunction.py:12.
# Python 3.14 avisa con SyntaxWarning al importar; en una versión futura será un error de sintaxis.
# Origen: F24 de Penumbra (que no listaba gamma.py).
#
# Solucionado cuando: ningún .py del repo produce avisos al compilarse.
import warnings
from _comun import *

inicio('B6', 'Bajo', 'SyntaxWarning en los docstrings')

ARCHIVOS = sorted(p for p in REPO.rglob('*.py') if '.git' not in p.parts)

@prueba(f'Los {len(ARCHIVOS)} .py del repo compilan sin SyntaxWarning')
def _():
    malos = []
    for p in ARCHIVOS:
        with warnings.catch_warnings(record=True) as avisos:
            warnings.simplefilter('always')
            compile(p.read_text(errors='replace'), str(p), 'exec')
        malos += [f'{p.relative_to(REPO)}:{a.lineno}' for a in avisos if issubclass(a.category, SyntaxWarning)]
    exigir(not malos, 'avisos en ' + ', '.join(malos))

for nombre in ('gamma', 'pifunction', 'trapezoid', 'triangular', 'zfunction'):
    @prueba(f'fsets/{nombre}.py compila sin avisos')
    def _(nombre=nombre):
        rutas = [p for p in ARCHIVOS if p.name == f'{nombre}.py']
        if not rutas:
            return 'el archivo ya no existe'
        with warnings.catch_warnings(record=True) as avisos:
            warnings.simplefilter('always')
            compile(rutas[0].read_text(), str(rutas[0]), 'exec')
        exigir(not avisos, f'{len(avisos)} aviso(s)')

fin()
