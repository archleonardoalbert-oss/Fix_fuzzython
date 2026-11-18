# M19 · MEDIO · FCL: otros fallos de la gramática
#
# Qué pasa (store/FCL.g):
#   - :87  `_MAMDAMI_`, con errata; `_MAMDANI_` bien escrito no se reconoce (sistema vacío, ver C3).
#   - :158 ACT es opcional y sin valor por defecto: get_norm(None) y todas las salidas dan el default.
#   - :287 `WITH nombre` usa `scope`, que no existe (NameError).
#   - :305 RANGE se lee y se descarta; Variable.interval no se usa en ningún sitio.
#   - :386-389, 406-410: el token FLOAT (1e-1, .5) existe pero el parser no lo usa.
#   - :328 `TERM x := nombre` pasa un Variable como lista de parámetros.
#   - :266-267 en Tsukamoto toma solo la primera conclusión y descarta las demás sin aviso.
#   - :149-151 exige FUZZIFY antes que DEFUZZIFY, y METHOD antes que DEFAULT.
# No se comprueban aquí NSUM, FAND/FOR ni SUGENO/YAGER (M19 del README): son decisiones de diseño.
#
# Solucionado cuando: cada caso se lee bien y calcula lo esperado, o lanza un error claro donde la
# entrada no tiene sentido (nunca un sistema vacío, un default silencioso o un NameError interno).
from _comun import *

inicio('M19', 'Medio', 'FCL: otros fallos de la gramática')

REF = 33.6666666   # una regla «hot -> large» con temp = 38

@prueba('FUNCTION_BLOCK _MAMDANI_ (bien escrito) carga un Mamdani que calcula 33.667')
def _():
    return cerca(numero(fcl(tipo='_MAMDANI_').compute({'temp': 38})), REF, 1e-3, 'COG')

@prueba('Sin ACT: usa MIN por defecto (33.667) o lanza un error claro, pero no da el default')
def _():
    try:
        r = numero(fcl(act='').compute({'temp': 38}))
    except Falla:
        raise
    except Exception as e:
        exigir('none' not in str(e).lower(), f'error interno: {e}')
        return f'lanza {type(e).__name__}: {e}'
    return cerca(r, REF, 1e-3, 'COG')

@prueba('WITH seguido de un nombre: funciona o da un error claro, no NameError de «scope»')
def _():
    try:
        cargar_fcl(texto_fcl('RULE 1: IF temp IS hot THEN tm IS large WITH w;'))
    except Falla:
        raise
    except Exception as e:
        exigir("'scope'" not in str(e), f'lanza {type(e).__name__}: {e}')
        return f'lanza {type(e).__name__}: {e}'

@prueba('RANGE := (0 .. 40) se guarda en la variable de salida')
def _():
    s = cargar_fcl(texto_fcl().replace(' DEFAULT := 0;', ' DEFAULT := 0;\n RANGE := (0 .. 40);'))
    iv = s.output_variables()['tm'].interval
    exigir(iv is not None and tuple(float(v) for v in iv) == (0.0, 40.0), f'interval = {iv!r}')

for escrito, normal in (('1e-1', '0.1'), ('.5', '0.5'), ('5e-1', '0.5')):
    @prueba(f'WITH {escrito} da lo mismo que WITH {normal}')
    def _(escrito=escrito, normal=normal):
        a = numero(fcl(f'RULE 1: IF temp IS hot THEN tm IS large WITH {escrito}; RULE 2: IF temp IS cold THEN tm IS short;').compute({'temp': 33}))
        b = numero(fcl(f'RULE 1: IF temp IS hot THEN tm IS large WITH {normal}; RULE 2: IF temp IS cold THEN tm IS short;').compute({'temp': 33}))
        return cerca(a, b, 1e-12, escrito)

@prueba('Puntos con exponente: TERM large := (25, 0) (3e1, 1) (40, 1) carga y calcula 33.667')
def _():
    t = texto_fcl().replace('(25, 0) (30, 1) (40, 1)', '(25, 0) (3e1, 1) (40, 1)')
    return cerca(numero(cargar_fcl(t).compute({'temp': 38})), REF, 1e-3, 'COG')

@prueba('TERM x := nombre no rompe con «argument after * must be an iterable»')
def _():
    try:
        cargar_fcl(texto_fcl().replace('TERM short := (0, 1) (10, 1) (15, 0);', 'TERM short := temp;'))
    except Falla:
        raise
    except Exception as e:
        exigir('iterable' not in str(e), f'lanza {type(e).__name__}: {e}')
        return f'lanza {type(e).__name__}: {e}'

@prueba('Tsukamoto con dos conclusiones en una regla lanza un error (no descarta la segunda)')
def _():
    espera_error(lambda: cargar_fcl(texto_fcl('RULE 1: IF temp IS hot THEN tm IS large, tm IS short;', tipo='_TSUKAMOTO_')))

@prueba('DEFUZZIFY antes que FUZZIFY se acepta y calcula 33.667')
def _():
    t = texto_fcl()
    fuzz = t[t.index('FUZZIFY temp'):t.index('END_FUZZIFY') + len('END_FUZZIFY')]
    defu = t[t.index('DEFUZZIFY tm'):t.index('END_DEFUZZIFY') + len('END_DEFUZZIFY')]
    t = t.replace(fuzz, '@@F').replace(defu, fuzz).replace('@@F', defu)
    return cerca(numero(cargar_fcl(t).compute({'temp': 38})), REF, 1e-3, 'COG')

@prueba('DEFAULT antes que METHOD se acepta y calcula 33.667')
def _():
    t = texto_fcl().replace(' METHOD: COG;\n DEFAULT := 0;', ' DEFAULT := 0;\n METHOD: COG;')
    return cerca(numero(cargar_fcl(t).compute({'temp': 38})), REF, 1e-3, 'COG')

fin()
