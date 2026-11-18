# Ejecuta todos los scripts de verificación y muestra un resumen, en el orden del README.
#
# Uso:  python3 verificacion/ejecutar_todos.py [ruta-al-repo] [--rapido] [--detalle]
#   --rapido   salta C1 y M21, que crean entornos con pip y necesitan red (~1 min cada uno)
#   --detalle  muestra también la salida completa de los que no están solucionados
import re, subprocess, sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
args = [a for a in sys.argv[1:] if not a.startswith('--')]
rapido, detalle = '--rapido' in sys.argv, '--detalle' in sys.argv
LENTOS = {'C1', 'M21'}

def clave(p):
    m = re.match(r'([CAMB])(\d+)_', p.name)
    return ('CAMB'.index(m.group(1)), int(m.group(2)))

scripts = sorted((p for p in AQUI.glob('[CAMB][0-9]*_*.py')), key=clave)
resueltos = 0
print(f'{"Fallo":<6} {"Estado":<16} {"Pasan":<9} Script')
for p in scripts:
    ident = p.name.split('_')[0]
    if rapido and ident in LENTOS:
        print(f'{ident:<6} {"(saltado)":<16} {"":<9} {p.name}')
        continue
    r = subprocess.run([sys.executable, '-B', str(p), *args], capture_output=True, text=True, timeout=1200)
    m = re.search(r'RESULTADO: (SOLUCIONADO|NO SOLUCIONADO) \((.*?)\)', r.stdout)
    if not m:
        estado, pruebas = 'ERROR', ''
    else:
        estado = 'solucionado' if m.group(1) == 'SOLUCIONADO' else 'NO solucionado'
        n = re.findall(r'\d+', m.group(2))
        pruebas = f'{n[0]}/{n[0]}' if estado == 'solucionado' else f'{int(n[1]) - int(n[0])}/{n[1]}'
    resueltos += estado == 'solucionado'
    print(f'{ident:<6} {estado:<16} {pruebas:<9} {p.name}')
    if detalle and estado != 'solucionado':
        print('\n'.join('       ' + l for l in (r.stdout + r.stderr).splitlines() if 'FALLA' in l or l.startswith(' ' * 10) or 'Error' in l))
print(f'\n{resueltos} de {len(scripts)} fallos solucionados.')
