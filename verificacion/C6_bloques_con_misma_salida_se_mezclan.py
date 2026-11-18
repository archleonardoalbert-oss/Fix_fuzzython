# C6 · CRÍTICO · Dos bloques con la misma variable de salida se contaminan
#
# Qué pasa: la fuerza y el conjunto activado se guardan DENTRO del Adjective (adjective.py:54-59 y
# 75-85). MamdaniSystem.inference (systems/mamdani.py:14-18) ejecuta las reglas de todos los bloques
# antes de desdifusionar cada uno (mamdani.py:21-32), así que cada bloque ve las activaciones de los
# demás. Ejecutado: el bloque b1 solo da 33.67; junto a b2 da 20.0, y b2 también 20.0.
# El mismo estado compartido hace que la librería no sea segura con hilos.
#
# Solucionado cuando: el resultado de cada bloque no depende de los otros bloques ni de otros sistemas
# que compartan objetos, también ejecutando en varios hilos a la vez.
import sys, threading
from _comun import *

inicio('C6', 'Crítico', 'Dos bloques con la misma salida se contaminan')

def sistemas():
    s = escenario()
    b1 = bloque(['if temp is hot then tm is large'], s, nombre='b1')
    b2 = bloque(['if temp is hot then tm is short'], s, nombre='b2')
    M = fz('MamdaniSystem')
    return M('solo1', b1), M('solo2', b2), M('juntos', b1, b2)

@prueba('b1 da lo mismo solo que acompañado de b2')
def _():
    s1, _, j = sistemas()
    solo = numero(s1.compute({'temp': 38}))
    junto = j.compute({'temp': 38})['b1']
    return cerca(numero(junto), solo, 1e-9, 'b1 acompañado')

@prueba('b2 da lo mismo solo que acompañado de b1')
def _():
    _, s2, j = sistemas()
    solo = numero(s2.compute({'temp': 38}))
    return cerca(numero(j.compute({'temp': 38})['b2']), solo, 1e-9, 'b2 acompañado')

@prueba('Los valores son los esperados: b1 = 33.667 (large), b2 = 6.333 (short)')
def _():
    r = sistemas()[2].compute({'temp': 38})
    cerca(numero(r['b1']), 33.6666666, 1e-3, 'b1')
    return cerca(numero(r['b2']), cog(pl((0, 1), (10, 1), (15, 0)), 0, 15), 1e-3, 'b2')

@prueba('Cuatro hilos calculando a la vez sistemas que comparten adjetivos dan siempre el valor correcto', t=60)
def _():
    s = escenario()
    M = fz('MamdaniSystem')
    a = M('a', bloque(['if temp is hot then tm is large'], s, nombre='a'))
    b = M('b', bloque(['if temp is cold then tm is short'], s, nombre='b'))
    esperado = {38: 33.6666666, 5: cog(pl((0, 1), (10, 1), (15, 0)), 0, 15)}
    malos = []
    def trabajar(sistema, t):
        for _ in range(300):
            v = numero(sistema.compute({'temp': t}))
            if not isinstance(v, (int, float)) or abs(v - esperado[t]) > 1e-3:
                malos.append(v)
    sys.setswitchinterval(1e-6)   # fuerza cambios de hilo frecuentes para que el choque aparezca
    hilos = [threading.Thread(target=trabajar, args=(x, t)) for x, t in ((a, 38), (b, 5), (a, 38), (b, 5))]
    for h in hilos: h.start()
    for h in hilos: h.join()
    sys.setswitchinterval(0.005)
    exigir(not malos, f'{len(malos)} resultados erróneos de 1200, p. ej. {malos[:3]}')

fin()
