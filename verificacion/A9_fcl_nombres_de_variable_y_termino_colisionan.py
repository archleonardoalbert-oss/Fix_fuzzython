# A9 · ALTO · FCL: variable + término se concatenan sin separador y colisionan
#
# Qué pasa: store/FCL.g:315 guarda cada término como self.scope[variable + término] y FCL.g:231,
# 269, 270, 283 lo buscan igual. La variable `ab` con término `c` y la variable `a` con término `bc`
# comparten la clave "abc": la regla `IF ab IS c` usa el adjetivo `bc` de la variable `a`. También
# puede chocar con el nombre de otra variable (`temp` + `o` = `tempo`).
#
# Solucionado cuando: cada regla usa el término de su propia variable, sean cuales sean los nombres.
from _comun import *

inicio('A9', 'Alto', 'FCL: colisión de nombres variable + término')

def sistema(vars_in, fuzz, regla):
    return cargar_fcl(f'''FUNCTION_BLOCK f
VAR_INPUT {vars_in} END_VAR
VAR_OUTPUT o: REAL; END_VAR
{fuzz}
DEFUZZIFY o
 TERM r := (0, 0) (10, 1);
 METHOD: COG;
 DEFAULT := -1;
END_DEFUZZIFY
RULEBLOCK b
 AND: MIN;
 ACT: MIN;
 ACCU: MAX;
 {regla}
END_RULEBLOCK
END_FUNCTION_BLOCK''')

FUZZ_AB = '''FUZZIFY ab
 TERM c := (0, 0) (10, 1);
END_FUZZIFY
FUZZIFY a
 TERM bc := (0, 1) (10, 0);
END_FUZZIFY'''
REF_R = cog(pl((0, 0), (10, 1)), 0, 10)

@prueba('«IF ab IS c» usa el término c de ab (ab = 10, a = 10 -> dispara del todo)')
def _():
    s = sistema('ab: REAL; a: REAL;', FUZZ_AB, 'RULE 1: IF ab IS c THEN o IS r;')
    return cerca(numero(s.compute({'ab': 10, 'a': 10})), REF_R, 1e-3, 'COG')

@prueba('«IF a IS bc» usa el término bc de a (a = 0 -> dispara del todo)')
def _():
    s = sistema('ab: REAL; a: REAL;', FUZZ_AB, 'RULE 1: IF a IS bc THEN o IS r;')
    return cerca(numero(s.compute({'ab': 0, 'a': 0})), REF_R, 1e-3, 'COG')

@prueba('Variable «tempo» y término «o» de «temp» conviven')
def _():
    fuzz = '''FUZZIFY temp
 TERM o := (0, 0) (10, 1);
END_FUZZIFY
FUZZIFY tempo
 TERM rapido := (0, 0) (10, 1);
END_FUZZIFY'''
    s = sistema('temp: REAL; tempo: REAL;', fuzz, 'RULE 1: IF tempo IS rapido AND temp IS o THEN o IS r;')
    return cerca(numero(s.compute({'temp': 10, 'tempo': 10})), REF_R, 1e-3, 'COG')

fin()
