# A2 · ALTO · Polygon es inexacto con normas no lineales
#
# Qué pasa: fsets/polygon.py:155-170 (y las copias de trapezoid.py:95-109 y triangular.py:84-98)
# aplican la norma solo en los vértices (y en los cruces, que solo sirven para MIN/MAX) y unen los
# resultados con rectas. Con una norma no lineal en `y`, o con un pliegue (BDIF, EPROD, DPROD, BSUM,
# ASUM, ESUM, NSUM, PROD entre dos polígonos) la forma real no es ese polígono. Errores máximos
# medidos: hasta 0.60 en la activación DPROD y 0.25 en la unión BSUM.
#
# Solucionado cuando: activación, unión e intersección con esas normas coinciden punto a punto con la
# norma aplicada a cada x (tolerancia 1e-3), y un Mamdani con ACT/ACCU no lineales da el COG real.
from _comun import *

inicio('A2', 'Alto', 'Polygon inexacto con normas no lineales')

P = lambda *p: fz('Polygon')(*p)
N = lambda n: fz('get_norm')(n)
XS = [i / 50 for i in range(0, 501)]
TRI = ((0, 0), (5, 1), (10, 0))
A, B = ((0, 0), (4, 1), (8, 0)), ((2, 0), (6, 1), (10, 0))

for n in ('BDIF', 'EPROD', 'DPROD', 'PROD'):
    @prueba(f'Activación {n} con 0.6 de un triángulo == {n}(μ(x), 0.6)')
    def _(n=n):
        t, norma = P(*TRI), N(n)
        act = t.activate(norma, 0.6)
        e = max(abs(act(x) - norma(t(x), 0.6)) for x in XS)
        exigir(e < 1e-3, f'error máximo {e:.4f}')

for n in ('BSUM', 'ASUM', 'ESUM', 'NSUM', 'MAX'):
    @prueba(f'Unión {n} de dos triángulos == {n}(μa(x), μb(x))')
    def _(n=n):
        a, b, norma = P(*A), P(*B), N(n)
        u = a.union(b, norma)
        e = max(abs(u(x) - norma(a(x), b(x))) for x in XS)
        exigir(e < 1e-3, f'error máximo {e:.4f}')

for n in ('PROD', 'EPROD', 'BDIF'):
    @prueba(f'Intersección {n} de dos triángulos == {n}(μa(x), μb(x))')
    def _(n=n):
        a, b, norma = P(*A), P(*B), N(n)
        i = a.intersect(b, norma)
        e = max(abs(i(x) - norma(a(x), b(x))) for x in XS)
        exigir(e < 1e-3, f'error máximo {e:.4f}')

SALIDAS = [(pl((0, 1), (10, 1), (15, 0)), 0.2), (pl((10, 0), (15, 1), (25, 1), (30, 0)), 0.4), (pl((25, 0), (30, 1), (40, 1)), 0.6)]
for act in ('BDIF', 'EPROD', 'DPROD'):
    @prueba(f'Mamdani de sample.py (temp = 33) con ACT {act}: COG real')
    def _(act=act):
        ref = cog(agregado(SALIDAS, N(act), max), 0, 40)
        r = numero(mamdani(activation=act).compute({'temp': 33}))
        return cerca(r, ref, 0.01, 'COG')

B2 = ((1, 0), (7, 1), (9, 0))   # asimétrico respecto de A, para que el COG no salga bien por simetría

def solapados(accu):
    """Dos consecuentes que se solapan mucho y disparan del todo: ahí se nota la S-norma."""
    s = escenario()
    Ad = fz('Adjective')
    s['ca'], s['cb'] = Ad('ca', P(*A)), Ad('cb', P(*B2))
    s['o'] = var('o', s['ca'], s['cb'], defuzzification='COG', default=float('nan'))
    return numero(mamdani(['if temp is hot then o is ca', 'if temp is hot then o is cb'], s, accumulation=accu).compute({'temp': 38}))

for accu in ('BSUM', 'ASUM', 'ESUM'):
    @prueba(f'Mamdani con dos consecuentes solapados y ACCU {accu}: COG real')
    def _(accu=accu):
        ref = cog(agregado([(pl(*A), 1.0), (pl(*B2), 1.0)], min, N(accu)), 0, 10)
        return cerca(solapados(accu), ref, 0.01, 'COG')

fin()
