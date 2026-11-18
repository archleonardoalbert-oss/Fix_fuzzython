# C8 · CRÍTICO · Cualquier error en la desdifusión se convierte en `default`
#
# Qué pasa: Variable.defuzzify (variable.py:44-71) mete todo en `try ... except Exception: print(e);
# return self.default`. Un fallo real (C5, A3, un método mal escrito, defuzzification=None) y el caso
# normal «ninguna regla disparó» dan la misma salida, `default` (None si no se fijó). Y cuando nada
# dispara imprime el mensaje interno de Python «reduce() of empty iterable with no initial value».
# Origen: F6 de Penumbra + el mensaje, nuevo.
#
# Solucionado cuando: los errores reales llegan al usuario como excepciones, y «ninguna regla
# disparó» devuelve `default` sin imprimir mensajes internos.
from _comun import *

inicio('C8', 'Crítico', 'Errores de desdifusión ocultos tras el default')

def con_salida(**kw):
    s = escenario()
    s['tm'] = var('tm', s['short'], s['usual'], s['large'], **kw)
    return s

@prueba('Un método de desdifusión que no existe lanza un error que lo nombra')
def _():
    m = mamdani(s=con_salida(defuzzification='NOEXISTE', default=-1))
    espera_error(lambda: m.compute({'temp': 33}), contiene=['NOEXISTE'])

@prueba('defuzzification=None en una salida lanza un error (al crearla o al calcular)')
def _():
    def hacer():
        return mamdani(s=con_salida(defuzzification=None, default=-1)).compute({'temp': 33})
    espera_error(hacer)

@prueba('Un error dentro de un conjunto de salida se propaga (ValueError «boom»)')
def _():
    FS, I, A = fz('FuzzySet'), fz('Interval'), fz('Adjective')
    def roto(x):
        raise ValueError('boom')
    s = escenario()
    s['raro'] = A('raro', FS(roto, I(0, 10)))
    s['tm'] = var('tm', s['raro'], defuzzification='COG', default=-1)
    espera_error(lambda: mamdani(['if temp is hot then tm is raro'], s).compute({'temp': 38}), contiene=['boom'])

@prueba('Si ninguna regla dispara, devuelve el default (-1)')
def _():
    r = numero(mamdani(['if temp is hot then tm is large'], con_salida(defuzzification='COG', default=-1)).compute({'temp': 5}))
    return cerca(r, -1, 0, 'default')

@prueba('Si ninguna regla dispara, no imprime mensajes internos de Python')
def _():
    m = mamdani(['if temp is hot then tm is large'], con_salida(defuzzification='COG', default=-1))
    _, out, err = capturar(lambda: m.compute({'temp': 5}))
    texto = (out + err).lower()
    exigir(not any(p in texto for p in ('reduce()', 'iterable', 'division', 'nonetype')), f'imprime: {(out + err).strip()!r}')

fin()
