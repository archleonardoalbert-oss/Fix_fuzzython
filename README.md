# Fix fuzzython: inventario de fallos

Inventario de todos los fallos encontrados en [yudivian/fuzzython](https://github.com/yudivian/fuzzython), **ordenados de más a menos importante**. Aquí no se arregla nada: es la lista de trabajo para los fixes.

- **Versión revisada:** commit `9650204` (2018-05-02), clon en `fuzzython/`.
- **Cómo se revisó:** lectura completa del código (salvo `store/FCLLexer.py` y `store/FCLParser.py`, que ANTLR genera a partir de `store/FCL.g`) y **ejecución de cada fallo** con Python 3.14.10. La lectura de FCL se probó con el runtime oficial de ANTLR 3.5 para Python 3 (carpeta `runtime/Python3` de [antlr/antlr3](https://github.com/antlr/antlr3)), sin parches.
- **Origen:** la columna «Origen» dice si el fallo ya estaba en la documentación interna del curso Penumbra (`F1`–`F24`, en `~/Leo/Tutoriales/LogicaDifusa/fuentes/referencias/fuzzython/doc.md`) o si es **nuevo** de esta revisión. Los 24 de Penumbra se han vuelto a ejecutar sobre este clon y **todos se reproducen**.
- **Criterio de fondo:** una librería se instala, se importa y funciona. Todo lo que obliga a tocar `sys.path`, parchear `time` o leer el código para no recibir un resultado falso cuenta como fallo.
- **Rutas:** relativas a `fuzzython/`. Las líneas corresponden al commit `9650204`.

## Cómo comprobar un fix

Cada fallo tiene su script en `verificacion/`, nombrado con su identificador y el fallo, por ejemplo `verificacion/C5_trapezoid_desdifusion_falla_y_es_falsa.py`. Al principio de cada script, un comentario explica el fallo, su gravedad y qué se considera «solucionado». Cada script prueba el arreglo de varias formas: casos distintos, valores calculados aparte sin fuzzython, el uso dentro de un sistema completo y, cuando aplica, `python -O`, varios hilos o un entorno limpio con pip.

```bash
python3 verificacion/C5_trapezoid_desdifusion_falla_y_es_falsa.py   # un solo fallo
python3 verificacion/ejecutar_todos.py                               # resumen de los 48
python3 verificacion/ejecutar_todos.py --rapido --detalle            # sin C1 ni M21 (usan pip y red), con detalle
```

- Cada prueba escribe `PASA` o `FALLA` con lo obtenido frente a lo esperado. Al final sale `RESULTADO: SOLUCIONADO` solo si pasan todas (código de salida 0); si no, `NO SOLUCIONADO` (código 1).
- Las pruebas marcadas `Control:` ya pasan hoy: comprueban que el arreglo no rompe lo que ya funcionaba.
- Sin argumentos usan `../fuzzython`; se puede pasar otra ruta al repo como primer argumento.
- Funcionan antes y después de arreglar C1: si `import fuzzython` funciona lo importan como paquete, y si no, con la raíz del repo en `sys.path`. Para que C2 no tape a los demás, parchean `time.clock`; el script de C2 lo comprueba aparte, sin ese parche.
- `verificacion/_vendor/antlr3` es el runtime oficial de ANTLR 3.5 para Python 3 (licencia BSD), necesario para los fallos de FCL mientras el lector use ANTLR.
- Algunas pruebas dependen también de otro fallo, y lo dicen en su descripción (por ejemplo, `PiFunction` en A4 depende de A5).

## Niveles de gravedad

| Nivel | Significado |
|---|---|
| **Crítico** | Impide usar la librería, o da un resultado **falso sin avisar** en un uso normal |
| **Alto** | Rompe o falsea una función concreta que un usuario normal va a usar |
| **Medio** | Falla en casos menos frecuentes, o acepta errores en silencio |
| **Bajo** | Rarezas, API incoherente, avisos, estilo |

---

## Resumen, de más a menos importante

| # | Gravedad | Fallo | Dónde | Origen |
|---|---|---|---|---|
| C1 | Crítico | No se puede instalar ni importar como paquete | `setup.py`, todos los `import` | Nuevo (F1 de Penumbra lo apuntaba en parte) |
| C2 | Crítico | `time.clock` no existe: todo `compute()` falla | `utils.py:29,31` | F1 |
| C3 | Crítico | Un FCL con errores de sintaxis se carga igual, a medias y sin avisar | `store/reader.py:28-42` | Nuevo |
| C4 | Crítico | FCL Sugeno: `temp*0.6+2` pierde el `+2`; `**` se lee como `*` | `store/FCL.g:274-276,401,403` | Nuevo |
| C5 | Crítico | `Trapezoid`: la desdifusión falla, y su atajo es falso para trapecios asimétricos | `fsets/trapezoid.py:47-69` | F2 + nuevo |
| C6 | Crítico | Dos bloques con la misma salida se contaminan | `adjective.py:54-59`, `systems/mamdani.py:14-32` | Nuevo |
| C7 | Crítico | Una entrada que falta reutiliza el valor de la llamada anterior | `variable.py:37`, `ruleblock.py:82-91` | Nuevo |
| C8 | Crítico | Cualquier error en la desdifusión se convierte en `default`, y «ninguna regla disparó» imprime un error interno | `variable.py:44-71` | F6 + nuevo |
| A1 | Alto | `SFunction`/`ZFunction` activadas no se recortan | `fsets/sfunction.py:68-82` | F5 |
| A2 | Alto | `Polygon` es inexacto con normas no lineales (`BDIF`, `EPROD`, `DPROD`, `BSUM`, `ASUM`, ...) | `fsets/polygon.py:155-170` | Nuevo |
| A3 | Alto | Unión de conjuntos separados: `COG` y similares fallan | `interval.py:110-133`, `fsets/fuzzy_set.py` | F17 |
| A4 | Alto | `membership` enlazado a la clase equivocada | `fsets/fuzzy_set.py:56`, `sfunction.py:44` | F4 |
| A5 | Alto | `PiFunction` no se puede evaluar | `fsets/pifunction.py:29-35` | F3 + nuevo |
| A6 | Alto | `ZFunction`: `LM`, `RM`, `CM` y `MM` devuelven el mínimo | `fsets/sfunction.py:52-62` | Nuevo |
| A7 | Alto | Sugeno: `eval` ejecuta código arbitrario y solo ve las variables del antecedente | `rules/srule.py:15,28,31` | F8 |
| A8 | Alto | FCL: `WITH 0.0` se convierte en peso 1 | `store/FCL.g:199` | Nuevo |
| A9 | Alto | FCL: variable + término se concatenan sin separador y colisionan | `store/FCL.g:231,269,270,283,315` | Nuevo |
| A10 | Alto | `fuzzify_with` entra en bucle infinito | `fsets/fuzzy_set.py:134-145` | Nuevo |
| A11 | Alto | Entrada difusa: ignora que `Polygon` se prolonga constante | `fsets/fuzzy_set.py:134-136`, `polygon.py:70-72` | Nuevo |
| A12 | Alto | Norma inexistente: `None` en silencio; norma de otro tipo: aceptada | `norms/norms.py:90-109`, `ruleblock.py:24-37` | F12 + nuevo |
| M1 | Medio | Se acepta un adjetivo que no pertenece a la variable | `rules/parser.py:106-111`, `operators/parser.py:117-127` | Nuevo |
| M2 | Medio | El analizador ignora el texto sobrante y valida con `assert` | `operators/parser.py:37-39,66,71,74,105` | Nuevo |
| M3 | Medio | «is» y «with» se buscan como texto dentro de nombres | `rules/parser.py:35,39-41` | F9 + nuevo |
| M4 | Medio | `ACCU` no actúa entre reglas con el mismo adjetivo | `adjective.py:54-59` | F7 |
| M5 | Medio | Sugeno y Tsukamoto devuelven `0` si nada dispara; Tsukamoto anula reglas en silencio | `systems/sugeno.py:21-24`, `tsukamoto.py:20-27`, `rules/trule.py:69-70,81-82` | Nuevo |
| M6 | Medio | Tsukamoto con consecuente no monótono da cualquier cosa | `rules/trule.py:60-92` | F22 |
| M7 | Medio | `Polygon`: su prolongación fuera de los puntos no se respeta en todas partes | `fsets/polygon.py:35-38,155-160,227-243` | F18 + nuevo |
| M8 | Medio | `complement` y `coordinates` usan `self.function`, que es `None` | `fsets/fuzzy_set.py:108,395` | F10 |
| M9 | Medio | `Polynomial` no se puede construir con tupla ni imprimir | `fsets/polynomial.py:17-18,189` | F14 |
| M10 | Medio | `Gaussian` solo cubre ±1 desviación | `fsets/gaussian.py:18` | Penumbra (sección 4) |
| M11 | Medio | La librería escribe en la salida estándar | `utils.py:35-36` y otros | Nuevo |
| M12 | Medio | Salidas `Singleton`: `COG` da `default`; `COGS` ignora la altura | `fsets/singleton.py:62-63`, `variable.py:49-62` | Nuevo |
| M13 | Medio | `Polygon.MM` promedia solo vértices | `fsets/polygon.py:102-111` | F20 |
| M14 | Medio | Paso acumulado con `+=`: áreas y muestreos con error | `fsets/fuzzy_set.py` (varias) | F19 |
| M15 | Medio | Bordes verticales: `ZeroDivisionError` o se pierden | `fsets/polygon.py:258-261,357`, `trapezoid.py:23-25` | F21 + nuevo |
| M16 | Medio | `maximize` con un número da otra forma | `fsets/polygon.py:161-163` | Nuevo |
| M17 | Medio | `Polygon.complement` ignora su argumento | `fsets/polygon.py:59` | F11 |
| M18 | Medio | Reglas Sugeno en Python: sin `-x`, `**` ni `//` | `variable.py:80-111` | Nuevo (Penumbra lo anotaba) |
| M19 | Medio | FCL: otros fallos de la gramática | `store/FCL.g` (varias) | F23 + nuevo |
| M20 | Medio | `dump()` no siempre se puede volver a leer | `systems/system.py:91-118`, `variable.py:119-131`, `ruleblock.py:96-105` | Penumbra (sección 9) + nuevo |
| M21 | Medio | Dependencia `antlr3` no declarada ni instalable desde PyPI | `store/reader.py:8`, `sample.py:1` | Nuevo |
| B1 | Bajo | `outputs=` se aplica a todos los bloques; bloques con igual nombre se pisan | `systems/mamdani.py:28`, `system.py:31` | Nuevo |
| B2 | Bajo | `Variable(nombre, adjetivo)` toma el adjetivo como unidad | `variable.py:12` | Nuevo (Penumbra lo anotaba) |
| B3 | Bajo | Detalles del analizador de reglas | `rules/parser.py`, `operators/parser.py` | Nuevo |
| B4 | Bajo | `Interval` y `Compound`: errores varios | `interval.py` | F15, F16 + nuevo |
| B5 | Bajo | `Polygon` y `FuzzySet`: errores varios de API | `fsets/*.py` | F13 + nuevo |
| B6 | Bajo | `SyntaxWarning` por los dibujos de los docstrings | `fsets/*.py` | F24 |
| B7 | Bajo | Código muerto, erratas y estilo | varios | Nuevo |

---

## Crítico

### C1. No se puede instalar ni importar como paquete

**Origen:** nuevo. Penumbra ya lo describía como «el primer obstáculo».

**Dónde:**

- Todos los módulos importan desde la raíz del repositorio como si fuera `sys.path`: `from fsets.fuzzy_set import FuzzySet` (`adjective.py:1`), `from norms.norms import get_norm` (`ruleblock.py:1`), `from utils import norm` (`norms/norms.py:1`), `from ruleblock import RuleBlock` (`systems/system.py:1`), y lo mismo en todos los demás archivos y en la cabecera de `store/FCL.g:17-27`.
- `setup.py:1`: `from distutils.core import setup`. `distutils` se retiró en Python 3.12.
- `setup.py:8`: `packages=find_packages()` encuentra `fsets`, `norms`, `operators`, `rules`, `store` y `systems`, pero no los módulos sueltos de la raíz (`adjective`, `variable`, `interval`, `utils`, `predicate`, `ruleblock`) ni el propio paquete `fuzzython`.
- `setup.py:11`: `license='LICENSE.txt'`, pero el archivo se llama `LICENSE`.
- No hay `pyproject.toml`, ni `python_requires`, ni `install_requires`.

**Qué pasa, ejecutado:**

| Prueba | Resultado |
|---|---|
| `from fuzzython.systems.mamdani import MamdaniSystem`, con la carpeta padre en `sys.path` | `ModuleNotFoundError: No module named 'systems'` |
| `pip install ./fuzzython` en un entorno limpio | Instala en `site-packages` seis paquetes de primer nivel: `fsets`, `norms`, `operators`, `rules`, `store`, `systems` |
| `import fuzzython`, tras instalar | `ModuleNotFoundError: No module named 'fuzzython'` |
| `from systems.mamdani import MamdaniSystem`, tras instalar | `ModuleNotFoundError: No module named 'ruleblock'` |
| Un `utils.py` propio en la carpeta del usuario | `ImportError: cannot import name 'norm' from 'utils'`: fuzzython importa el del usuario |

**Efecto:** la única forma de usarla es meter la raíz del repo en `sys.path`. Además, nombres tan genéricos como `utils`, `rules`, `store`, `systems` u `operators` chocan con cualquier módulo del usuario o de otra librería que se llame igual.

**Esperado:** `pip install .` y luego `import fuzzython` / `from fuzzython import MamdaniSystem`, con imports relativos dentro del paquete.

### C2. `time.clock` no existe: todo `compute()` falla

**Origen:** F1.

**Dónde:** `utils.py:29` y `utils.py:31` (`time.clock()`), dentro del decorador `timer`, que decora `compute` en `systems/mamdani.py:34`, `systems/sugeno.py:27` y `systems/tsukamoto.py:30`.

**Qué pasa:** `time.clock` se retiró en Python 3.8. Cualquier `compute()` lanza `AttributeError: module 'time' has no attribute 'clock'`. Sin parchear `time` a mano, **ningún sistema calcula nada**.

### C3. Un FCL con errores de sintaxis se carga igual, a medias y sin avisar

**Origen:** nuevo.

**Dónde:** `store/reader.py:28-42`. Solo captura excepciones de Python. El parser generado por ANTLR 3 **se recupera de los errores de sintaxis**: escribe `line N:M ...` en `stderr`, se salta lo que no entiende y sigue construyendo el sistema.

**Qué pasa, ejecutado:**

| FCL | Resultado |
|---|---|
| `FUNCTION_BLOCK _MAMDANI_ f ...` (bien escrito; la gramática solo conoce `_MAMDAMI_`) | Devuelve un sistema **vacío**: `compute()` da `{}`, sin excepción |
| `... WITH 1e-1;` o `WITH .5;` | Se salta el peso y calcula como si no lo hubiera |
| `... THEN temp*0.6+2;` | Se salta el `+2` (ver C4) |
| `DEFAULT` ausente, `RANGE` de un `Gaussian` escrito por `dump()` | Errores en `stderr`, pero el sistema se carga |

**Efecto:** el usuario recibe un sistema que **no es el que escribió** y no se entera, salvo que mire `stderr`. Además, cuando sí hay excepción, `reader.py:38-42` hace `print` y devuelve `None`, así que el error salta después, como `AttributeError: 'NoneType' object has no attribute 'compute'`.

**Esperado:** cualquier error de sintaxis o de semántica en el FCL lanza una excepción con línea y columna.

### C4. FCL Sugeno: `temp*0.6+2` pierde el `+2`, y `**` se lee como `*`

**Origen:** nuevo. Penumbra afirmaba que los consecuentes Sugeno de FCL admiten `+ - * ** / //`; ejecutado, no es así.

**Dónde:**

- `store/FCL.g:401` y `store/FCL.g:403`: los literales llevan signo dentro del token (`('+'|'-')? DIGIT+ ...`). En `temp*0.6+2`, el lexer lee `+2` como **un número**, no como «más 2».
- `store/FCL.g:274`: `o=('+'|'-'|'*''*'?|'/''/'?)`. La etiqueta `o` solo recoge **el primer token**, y `store/FCL.g:276` construye el texto con `$o.text`: `**` queda como `*` y `//` como `/`.

**Qué pasa, ejecutado con `temp = 38` y la regla `IF temp IS hot THEN ...`:**

| Consecuente FCL | Esperado | Obtenido |
|---|---|---|
| `temp*0.6 + 2` | 24.8 | 24.8 |
| `temp*0.6+2` | 24.8 | **22.8**: el `+2` desaparece |
| `temp - 1` | 37 | 37 |
| `temp-1` | 37 | `TypeError: eval() arg 1 must be a string...` |
| `temp ** 2` | 1444 | **76** (`temp*2`) |
| `temp // 2` | 19 | 19 (`temp/2`; coincide por casualidad, con `temp = 39` daría 19.5) |

**Efecto:** resultados Sugeno **falsos** según se pongan o no espacios. Y lo escribe el propio `dump()`: un sistema Python con la regla `z = temp*0.6+2` da 24.8, se guarda, se vuelve a leer y da 22.8.

### C5. `Trapezoid`: la desdifusión falla, y su atajo es falso para trapecios asimétricos

**Origen:** F2 (el `TypeError`) + nuevo (la fórmula).

**Dónde:** `fsets/trapezoid.py:47-69`. Los cuatro métodos `COG`, `COA`, `CM` y `MM` hacen:

```python
if b[1] == c[1]:
    return sum(b[0]+c[0])/2     # líneas 50, 56, 62, 68
```

**Fallo 1 (F2):** `b[0]+c[0]` es un número; `sum(número)` lanza `TypeError: 'int' object is not iterable`. Afecta a todo trapecio de meseta plana, es decir, a casi todos. En Mamdani, `Variable.defuzzify` se traga el error (C8) y devuelve `default`: con `activation='PROD'` y una sola regla activa sobre un trapecio, la salida es `default` (ejecutado: `{'b': {'tm': 0}}`).

**Fallo 2 (nuevo):** aunque se arregle el `sum`, la fórmula `(b_x + c_x)/2` solo es el centro de gravedad de un trapecio **simétrico**. Ejecutado con el trapecio `(0,0) (1,1) (2,1) (5,0)`:

| Método | Exacto (calculado con `Polygon`) | Atajo `(b_x + c_x)/2` |
|---|---|---|
| `COG` | 2.111 | 1.5 |
| `COA` | 2.0 | 1.5 |

Y si la meseta es el **mínimo**, como en un trapecio en U `(0,1) (1,0) (2,0) (3,1)`, el atajo de `CM`/`MM` devuelve el centro del valle, donde la pertenencia vale 0.

**Esperado:** quitar el atajo y heredar los métodos exactos de `Polygon`. Solo `CM`/`MM` admiten atajo, y solo si la meseta es el máximo.

### C6. Dos bloques con la misma variable de salida se contaminan

**Origen:** nuevo. Penumbra ya hablaba de «estado compartido».

**Dónde:** la fuerza y el conjunto activado se guardan **dentro del `Adjective`** (`adjective.py:54-59` y `adjective.py:75-85`). `MamdaniSystem.inference` (`systems/mamdani.py:14-18`) ejecuta las reglas de **todos** los bloques antes de que `defuzzify` (`systems/mamdani.py:21-32`) desdifusione cada bloque.

**Qué pasa, ejecutado con `temp = 38`:** bloque `b1` = `if temp is hot then tm is large`; bloque `b2` = `if temp is hot then tm is short`.

| Sistema | Resultado de `b1` |
|---|---|
| Solo `b1` | `33.67` |
| `b1` y `b2` juntos | `20.0`, y `b2` también da `20.0` |

**Efecto:** el resultado de un bloque depende de los demás bloques; los dos devuelven la mezcla. Lo mismo ocurre con dos sistemas que compartan objetos `Variable`/`Adjective`. Tampoco es seguro con hilos.

**Esperado:** el estado de la inferencia debe vivir en la llamada a `compute`, no en los adjetivos.

### C7. Una entrada que falta reutiliza el valor de la llamada anterior

**Origen:** nuevo.

**Dónde:** `variable.py:37` (`#self.value = None` está **comentado** en `reset`) y `ruleblock.py:82-91`, que no comprueba que estén todas las entradas.

**Qué pasa, ejecutado:**

```python
m.compute({'temp': 33})   # {'b': {'tm': 24.144}}
m.compute({})             # {'b': {'tm': 24.144}}   ← usa temp = 33 de antes
```

Y si falta en la **primera** llamada: `TypeError: '<=' not supported between instances of 'NoneType' and 'int'`, que no dice qué variable falta.

**Esperado:** error claro que nombre la variable que falta.

### C8. Cualquier error en la desdifusión se convierte en `default`, y «ninguna regla disparó» imprime un error interno

**Origen:** F6 + nuevo (el mensaje).

**Dónde:** `variable.py:44-71`. Todo el cuerpo de `defuzzify` está dentro de `try ... except Exception as e: print(e); return self.default` (`variable.py:70-72`).

**Qué pasa:**

- Un fallo real (C5, A3, M12, un nombre de método mal escrito en `defuzzification`, `defuzzification=None`) y el caso normal de que ninguna regla dispare dan **la misma salida**: `default`, que es `None` si no se fijó.
- Cuando ninguna regla dispara, `FuzzySet.disjunction(*sets)` (`variable.py:66`) recibe una lista vacía y la librería imprime el mensaje interno de Python `reduce() of empty iterable with no initial value`. Ejecutado: `{'b': {'tm': None}}` más ese texto en pantalla.

**Esperado:** los errores se propagan; «ninguna regla disparó» es un caso propio, documentado, que devuelve `default` sin imprimir nada (o avisa con `warnings`).

---

## Alto

### A1. `SFunction` y `ZFunction` activadas no se recortan

**Origen:** F5.

**Dónde:** `fsets/sfunction.py:68-74` y `fsets/sfunction.py:76-82`. Con un número, `_operation` solo aplica la norma a las `y` de los extremos `a` y `c` y crea **siempre una `SFunction`**.

**Qué pasa, ejecutado:** `SFunction((0,0),5,(10,1)).minimize(0.5)` vale `0.5, 0.92, 1.0, 0.5` en `x = 5, 8, 9.99, 10`: el interior no se recorta a 0.5. `ZFunction(...).minimize(0.5)` devuelve una `SFunction`, es decir, la curva al revés.

**Efecto:** Mamdani con estas formas en el consecuente da resultados **falsos sin avisar**.

### A2. `Polygon` es inexacto con normas no lineales

**Origen:** nuevo. Penumbra daba `Polygon` por «exacto»; solo lo es con `MIN`, `MAX` y el producto por un número.

**Dónde:** `fsets/polygon.py:155-170` (`_operation`, `_operation_`), y las copias en `fsets/trapezoid.py:95-109` y `fsets/triangular.py:84-98`. Aplica la norma **solo en los vértices** (y en los cruces, que solo sirven para `MIN`/`MAX`) y une los resultados con rectas. Si la norma no es lineal en `y`, o tiene un pliegue, la forma real no es un polígono con esos vértices.

**Qué pasa, ejecutado.** Error máximo entre lo que devuelve `Polygon` y la norma aplicada punto a punto:

| Operación | Dónde se usa | Error máximo |
|---|---|---|
| Activación `BDIF` con 0.6 de un triángulo | `ACT: BDIF` | 0.24 |
| Activación `EPROD` con 0.6 | `ACT: EPROD` | 0.05 |
| Activación `DPROD` con 0.6 | `ACT: DPROD` | 0.60 |
| Unión `BSUM` de dos triángulos | `ACCU: BSUM` | 0.25 |
| Unión `ESUM` | `ACCU: ESUM` | 0.09 |
| Unión `ASUM` | `ACCU: ASUM` | 0.06 |
| Intersección `PROD` entre dos polígonos | `AND: PROD` con entradas difusas | 0.06 |

`NSUM` es igual que `BSUM` (ver M19), así que tiene el mismo error.

**Efecto:** cualquier sistema Mamdani con `ACT` o `ACCU` distinto de `MIN`/`MAX`/`PROD` da un resultado aproximado sin decirlo.

### A3. Unión de conjuntos separados: `COG` y similares fallan

**Origen:** F17.

**Dónde:** `interval.py:110-133`. Si dos intervalos no se tocan, `union` devuelve un `Compound`, y `Compound.__iter__` (`interval.py` clase `Compound`) produce **intervalos**, no dos números. `FuzzySet.COG/COA/MM/LM/RM/area/coordinates` (`fsets/fuzzy_set.py:172,222,242,260,355,393`) hacen `a, b = self.interval`.

**Qué pasa, ejecutado:** `Gaussian(0,1).union(Gaussian(10,1)).COG()` lanza `TypeError: unsupported operand type(s) for -: 'Interval' and 'Interval'`. Dentro de Mamdani se convierte en `default` (C8).

### A4. `membership` enlazado a la clase equivocada

**Origen:** F4.

**Dónde:** `fsets/fuzzy_set.py:56` y `fsets/sfunction.py:44`: `membership = __call__` se enlaza a la función **de la clase donde se escribe**. Las subclases que redefinen `__call__` sin repetir esa línea heredan el `membership` viejo: `ZFunction` (`zfunction.py:26`), `Singleton` (`singleton.py:24`) y `PiFunction` (`pifunction.py:29`).

**Qué pasa, ejecutado:** `ZFunction((0,0),5,(10,1))` en `x = 8` vale `0.08` con `z(8)` y `0.92` con `z.membership(8)`. `Singleton(3, 0.8).membership(3)` da `0.0`.

**Efecto:** `fuzzify_with` (entradas difusas) usa `membership`: con estas formas como adjetivo, el grado sale mal.

### A5. `PiFunction` no se puede evaluar

**Origen:** F3 + nuevo.

**Dónde:** `fsets/pifunction.py:33` y `fsets/pifunction.py:35` pasan **números** a `SFunction`/`ZFunction`, que esperan puntos `(x, y)`: `TypeError: 'int' object is not subscriptable`.

**Además (nuevo):**

- `min_` y `max_` (`pifunction.py:22,26-27`) se guardan y **nunca se usan**.
- Aunque se pasaran puntos, la rama Z hereda el problema de convención de `ZFunction` (ver A6 y Penumbra, sección 4.2).
- Crea dos objetos nuevos en cada evaluación (`pifunction.py:33,35`).

### A6. `ZFunction`: `LM`, `RM`, `CM` y `MM` devuelven el punto de mínimo

**Origen:** nuevo.

**Dónde:** `fsets/sfunction.py:52-62` devuelve siempre `self.c[0]`, que en una S es el máximo. `ZFunction` (`fsets/zfunction.py`) lo hereda sin redefinirlo, pero en una Z el máximo está en `a`.

**Qué pasa, ejecutado:** `ZFunction((0,0),5,(10,1))` vale ≈1 en `x = 0` y ≈0 en `x = 10`, y sus `LM`, `RM`, `CM` y `MM` devuelven `10`.

### A7. Sugeno: `eval` ejecuta código arbitrario y solo ve las variables del antecedente

**Origen:** F8.

**Dónde:** `rules/srule.py:15` construye el diccionario solo con las variables del antecedente; `rules/srule.py:28` y `rules/srule.py:31` evalúan el consecuente con `eval(texto, ese_diccionario)`.

**Qué pasa, ejecutado:**

- `if temp is hot then z = p*2` lanza `NameError: name 'p' is not defined` aunque `p` sea una entrada del sistema.
- `if temp is hot then z = len(__import__('os').getcwd())` **se ejecuta**: `eval` tiene acceso a todos los `builtins`. Un archivo FCL (que también acaba en `eval`) o una regla de origen desconocido puede ejecutar cualquier cosa.
- `eval` añade la clave `__builtins__` al diccionario `_inputs` de la regla.

### A8. FCL: `WITH 0.0` se convierte en peso 1

**Origen:** nuevo.

**Dónde:** `store/FCL.g:199`: `Rule.get_rule(c1, c2, w or 1)`. `0.0 or 1` es `1`.

**Qué pasa, ejecutado:** con `RULE 1: ... THEN tm IS large WITH 0.0; RULE 2: ... THEN tm IS short;`, la regla 1 cuenta con peso 1 y el resultado es `20.0`, no el de la regla 2 sola. En Python (`with 0`) el peso sí es 0: los dos caminos no coinciden.

### A9. FCL: variable + término se concatenan sin separador y colisionan

**Origen:** nuevo.

**Dónde:** `store/FCL.g:315` guarda cada término como `self.scope[variable.name + name.text]`, y `store/FCL.g:231`, `269`, `270` y `283` lo buscan igual.

**Qué pasa, ejecutado:** con una variable `ab` y término `c`, y otra variable `a` con término `bc`, ambas claves son `"abc"`. La regla `IF ab IS c` usa el adjetivo **`bc` de la variable `a`**.

### A10. `fuzzify_with` entra en bucle infinito

**Origen:** nuevo.

**Dónde:** `fsets/fuzzy_set.py:134-145`. Si la intersección de intervalos es un solo punto, `step = (b - a)/100 = 0` y `while a <= b: a += step` no termina.

**Qué pasa, ejecutado:** `Adjective('g', Gaussian(0,1)).membership(Triangular((1,0),(2,1),(3,0)))`: la gaussiana cubre `[-1, 1]` y el triángulo `[1, 3]`; solo comparten `x = 1`, y el programa **se cuelga**.

### A11. Entrada difusa: ignora que `Polygon` se prolonga constante

**Origen:** nuevo.

**Dónde:** `fsets/fuzzy_set.py:134-136` y `fsets/polygon.py:70-72` devuelven `0.0` si los intervalos no se cortan. Pero `Polygon.__call__` (`fsets/polygon.py:35-38`) prolonga el primer y el último valor hacia los lados, que es lo que hace funcionar los «hombros».

**Qué pasa, ejecutado,** con `cold = Polygon((0,1),(15,1),(20,0))`:

| Entrada | Grado de `cold` |
|---|---|
| `-10` (nítida) | `1` |
| `Triangular((-12,0),(-10,1),(-8,0))`, «unos -10» | `0.0` |

La misma entrada da resultados opuestos según sea nítida o difusa.

### A12. Norma inexistente: `None` en silencio; norma de otro tipo: aceptada

**Origen:** F12 + nuevo.

**Dónde:** `norms/norms.py:90-109` (`get_norm`) y `ruleblock.py:24-25,35-37`.

**Qué pasa, ejecutado:**

- Nombre que no existe: imprime `unsupported norm X` y devuelve `None` (`norms/norms.py:107-109`). En `ACT`, todas las salidas dan `default` (`{'b': {'tm': 0}}`). En `AND`/`OR`, `And`/`Or` sustituyen `None` por `MIN`/`MAX` sin avisar (`operators/_and.py:12`, `operators/_or.py:11`).
- **Nuevo:** no se comprueba el tipo. `activation='MAX'` (una S-norma) se acepta y da otro resultado (`20.06` en vez de `24.14`). `operators=('ZADEH', ...)` se acepta y falla al calcular: `TypeError: zadeh_complement() takes 1 positional argument but 2 were given`.
- **Nuevo:** `get_norm('max1')` importa `norms/max1.py` pero compara `f.name == name` con mayúsculas exactas (`norms/norms.py:105`): devuelve `None` sin imprimir nada.
- El `except Exception` de `norms/norms.py:107` también oculta cualquier error dentro de un módulo de normas del usuario.

---

## Medio

### M1. Se acepta un adjetivo que no pertenece a la variable

**Origen:** nuevo.

**Dónde:** `rules/parser.py:106-111` y `operators/parser.py:117-127` solo buscan los nombres en `scope`; nunca comprueban `adj in var.adjectives`.

**Qué pasa, ejecutado:**

- `if temp is short then tm is large` (`short` es de `tm`): calcula `short(temp)` y da `33.67` como si nada.
- `if temp is hot then tm is hot` (`hot` es de `temp`): la regla activa un adjetivo de `temp`, `tm` no recibe nada, y sale `default` más el mensaje `reduce() of empty iterable...`.

### M2. El analizador ignora el texto sobrante y valida con `assert`

**Origen:** nuevo.

**Dónde:**

- `operators/parser.py:37-39`: `parse()` no comprueba que se hayan consumido todos los tokens.
- `operators/parser.py:66,71,74,105`, `rules/parser.py:20,94` y `systems/system.py:30` usan `assert` para validar la entrada del usuario. Con `python -O`, los `assert` desaparecen y esos errores pasan sin detectarse.

**Qué pasa, ejecutado:** las tres reglas siguientes se aceptan y quedan como `IF temp IS hot THEN tm IS large`:

```
if temp is hot cold blah then tm is large
if temp is hot xor temp is cold then tm is large
if temp is hot ) ) then tm is large
```

### M3. «is» y «with» se buscan como texto dentro de nombres

**Origen:** F9 + nuevo (`with`).

**Dónde:**

- `rules/parser.py:35`: `not IS in then_` busca la subcadena `is`. `z = dist*2` se toma por Mamdani y falla (`AssertionError: expected 'is' word`). Pasa con cualquier nombre que contenga «is».
- `rules/parser.py:39-41` (nuevo): `WITH in consequent` busca la subcadena `with`. `z = within*2` se parte en `within` y lanza `ValueError: could not convert string to float: 'in*2'`.

### M4. `ACCU` no actúa entre reglas con el mismo adjetivo

**Origen:** F7.

**Dónde:** `adjective.py:54-59`: `set_strength` se queda con el **máximo** de la fuerza anterior y la nueva, sea cual sea `accumulation`.

**Qué pasa, ejecutado:** dos reglas sobre `usual` dan `19.99` con `ACCU: MAX` y también con `ACCU: BSUM`. La teoría acumula todas las reglas con la S-norma elegida.

### M5. Sugeno y Tsukamoto devuelven `0` si nada dispara; Tsukamoto anula reglas en silencio

**Origen:** nuevo.

**Dónde:**

- `systems/sugeno.py:21-24` y `systems/tsukamoto.py:20-27`: `except ZeroDivisionError: res = 0`. Un `0` real y «ninguna regla disparó» no se distinguen, y se ignora el `default` de la variable.
- `rules/trule.py:69-70` y `rules/trule.py:81-82`: si la fuerza de la regla supera la altura del consecuente, devuelve `(0, 0)` y la regla deja de contar. Ejecutado: consecuente `Polygon((0,0),(10,0.8))` con fuerza 0.9 da `(0, 0)`.

### M6. Tsukamoto con consecuente no monótono da cualquier cosa

**Origen:** F22.

**Dónde:** `rules/trule.py:60-92`. La bisección supone monotonía y no lo comprueba.

**Qué pasa, ejecutado:** con `Polygon((0,0),(20,1),(40,0))` como consecuente, `get_strength_x` devuelve `(0, 0)` para fuerzas 0.5 y 0.85: el conjunto empieza y acaba en 0, así que «se sale de rango».

### M7. `Polygon`: su prolongación fuera de los puntos no se respeta en todas partes

**Origen:** F18 + nuevo. Corrección a la primera versión de este README: la unión no es incoherente por sí misma, el problema es que la librería no decide qué vale un `Polygon` fuera de sus puntos.

**Dónde:** `Polygon.__call__` (`fsets/polygon.py:35-38`) prolonga el primer y el último valor hacia fuera: `Polygon((0,1),(1,1))` vale 1 en `x = 3`. El resto de la librería no es coherente con eso:

- `Polygon.area_` (`fsets/polygon.py:227-243`) cuenta la prolongación de la izquierda y no la de la derecha. Ejecutado: `Polygon((0,1),(1,1)).area_(-1, 2)` da `2.0`; sería `3` con las dos prolongaciones y `1` sin ninguna. Con `Polygon((10,0),(15,1),(20,0))`, `area_(-1, 2)` da `6.4` en un tramo donde la función vale 0.
- La unión (`fsets/polygon.py:155-160`) sí usa la prolongación: `Polygon((0,1),(2,1)) ∪ Polygon((4,1),(6,1))` vale 1 en el hueco y tiene área 6. Es coherente con `__call__`, pero sorprende: con «vale 0 fuera» el área sería 4.
- La entrada difusa la ignora (A11).

**Esperado:** decidir una sola semántica («se prolonga» o «vale 0 fuera») y aplicarla en `__call__`, `area_`, la unión y `fuzzify_with`.

### M8. `complement` y `coordinates` usan `self.function`, que es `None` en las subclases

**Origen:** F10.

**Dónde:** `fsets/fuzzy_set.py:108` y `fsets/fuzzy_set.py:395`. Las subclases construyen con `function=None` y definen `__call__`.

**Qué pasa, ejecutado:** `(~Gaussian(0,1))(0)` lanza `TypeError: 'NoneType' object is not callable`.

### M9. `Polynomial` no se puede construir con tupla ni imprimir

**Origen:** F14.

**Dónde:** `fsets/polynomial.py:18` usa `Interval` sin importarlo (`NameError`). `fsets/polynomial.py:189` hace `','.join` sobre números (`TypeError`), así que `str(p)` y `dump()` fallan.

**Además:** `grade` (`polynomial.py:143-147`) es el número de coeficientes, no el grado: `x²` da 3.

### M10. `Gaussian` solo cubre ±1 desviación

**Origen:** Penumbra, sección 4.2.

**Dónde:** `fsets/gaussian.py:18`: `Interval(center - width, center + width)`.

**Qué pasa, ejecutado:** el área que usa la librería para `Gaussian(0,1)` es `1.711`; la real es `2.507`: se pierde el 32 % de la masa. Las entradas difusas gaussianas solo se miran en ese tramo, y un conjunto activado se integra solo ahí. Además, `__repr__`/`__str__` (`gaussian.py:53-54`) escriben el intervalo en lugar de `height`.

### M11. La librería escribe en la salida estándar

**Origen:** nuevo.

**Dónde:**

| Lugar | Qué imprime |
|---|---|
| `utils.py:35-36` (decorador `timer`, activado en los tres `compute`) | `[mamdani system time] compute: 0.00072s` **en cada llamada** |
| `ruleblock.py:91` | `not used input: X`, en cada bloque que no use esa entrada |
| `variable.py:71` | el mensaje de cualquier excepción (C8) |
| `norms/norms.py:108` | `unsupported norm X` |
| `norms/max1.py:10` | `--- max1 ---` en cada evaluación de la norma de ejemplo |
| `store/reader.py:39-40` | `--- incorrect FCL-E file ---` |

**Efecto:** un bucle de 10 000 `compute` imprime 10 000 líneas. Además, `timer` no usa `functools.wraps` (`utils.py:27-39`): `MamdaniSystem.compute.__name__` es `'on_call'` y se pierde el docstring.

**Esperado:** `logging` o `warnings`, nunca `print`.

### M12. Salidas `Singleton`: `COG` da `default`; `COGS` ignora la altura

**Origen:** nuevo.

**Dónde:**

- `fsets/singleton.py:62-63`: el área de un `Singleton` es 0. Un `Singleton` activado se convierte en un `FuzzySet` de intervalo `[x, x]`, y `COG` divide por un área 0. Ejecutado: `division by zero` impreso y salida `default`.
- `variable.py:49-62` (`COGS`): pondera con `adjective.strength` e ignora la altura `y` del singleton. Ejecutado: `Singleton(10, 0.1)` y `Singleton(20, 1.0)` con la misma fuerza dan `15.0`, como si las alturas fueran iguales. Además, salta en silencio los adjetivos que no son `Singleton`, y si ninguno tiene fuerza divide por 0 (que C8 convierte en `default`).

### M13. `Polygon.MM` promedia solo vértices

**Origen:** F20.

**Dónde:** `fsets/polygon.py:102-111`.

**Qué pasa, ejecutado:** en el ejemplo de `sample.py` con `temp = 33`, `MM` da `32.667` (media de los vértices 28, 30 y 40); la media real de la meseta `[28, 40]` es `34`.

### M14. Paso acumulado con `+=`: áreas y muestreos con error

**Origen:** F19.

**Dónde:** `fsets/fuzzy_set.py:142-144` (`fuzzify_with`), `225-232` (`MM`), `245-250` (`LM`), `263-268` (`RM`), `359-365` (`area`), `378-383` (`area_`), `396-398` (`coordinates`), y `fsets/polygon.py:299-302` (`create_from`). Todos avanzan con `a += step`.

**Qué pasa, ejecutado:** el área de la función constante 1 en `[0, 1]` da `1.143` con resolución 7 y `1.1` con 10. Con la resolución por defecto (100) el error es pequeño. Además, `LM`, `RM` y `MM` usan `while a < b` y casi nunca evalúan `x = b`; `RM` de un conjunto cuyo máximo está en `b` no lo encuentra.

### M15. Bordes verticales: `ZeroDivisionError` o se pierden

**Origen:** F21 + nuevo.

**Dónde:**

- `fsets/polygon.py:357` (`Rect.build_from`) divide por `x2 - x1`. `Trapezoid` y `Triangular` lo llaman en el constructor (`trapezoid.py:23-25`, `triangular.py:24-25`): `Trapezoid((0,0),(0,1),(2,1),(3,0))` lanza `ZeroDivisionError`.
- **Nuevo:** `Polygon.add_point` (`fsets/polygon.py:258-261`) fusiona dos puntos con la misma `x` quedándose con la `y` mayor. `Polygon((0,0),(0,1),(1,1))` queda como `[(0,1), (1,1)]`. No hay forma de representar un escalón (un conjunto nítido).

### M16. `maximize` con un número da otra forma

**Origen:** nuevo.

**Dónde:** `fsets/fuzzy_set.py:289-293` llama a `_operation(maximum, número)`, que en `Polygon` (`fsets/polygon.py:161-163`) solo aplica `max` a los vértices, sin añadir los cruces (al revés que `Polygon.minimize`, `polygon.py:135-150`).

**Qué pasa, ejecutado:** `Polygon((0,0),(5,1),(10,0)).maximize(0.5)` vale `0.6` en `x = 1`; debería valer `0.5`.

### M17. `Polygon.complement` ignora su argumento

**Origen:** F11.

**Dónde:** `fsets/polygon.py:59`: `cnorm = self.cnorm or ...` en lugar de `cnorm or self.cnorm`. Además, el resultado se construye con `_quick_build_` y pierde las normas del original.

### M18. Reglas Sugeno en Python: sin `-x`, `**` ni `//`

**Origen:** nuevo (Penumbra lo anotaba como limitación).

**Dónde:** `variable.py:80-111`. `Variable` define `+ - * /`, pero no `__neg__`, `__pow__` ni `__floordiv__`. `__div__` y `__rdiv__` (`variable.py:106-111`) son nombres de Python 2 que Python 3 nunca llama, y además hacen división **entera**.

**Qué pasa, ejecutado:**

| Consecuente | Resultado |
|---|---|
| `z = -temp` | `TypeError: bad operand type for unary -: 'Variable'` |
| `z = temp**2` | `TypeError: unsupported operand type(s) for ** or pow()` |
| `z = temp//2` | `TypeError: unsupported operand type(s) for //` |

### M19. FCL: otros fallos de la gramática

**Origen:** F23 + nuevo.

| Lugar | Fallo | Efecto, ejecutado | Origen |
|---|---|---|---|
| `store/FCL.g:87` | `_MAMDAMI_`, con errata; `_MAMDANI_` no se reconoce | Sistema vacío (C3) | F23 |
| `store/FCL.g:158` | `ACT` opcional y sin valor por defecto | `get_norm(None)` imprime `unsupported norm None` y todas las salidas dan `default` | F23 |
| `store/FCL.g:287` | `WITH nombre` usa `scope`, que no existe (debería ser `self.scope`) | `name 'scope' is not defined`; devuelve `None` | F23 |
| `store/FCL.g:305` | `RANGE` se lee y se descarta; `Variable.interval` (`variable.py:12,27`) no se usa en ningún sitio | El rango no tiene efecto | F23 |
| `store/FCL.g:386-389,406-410` | El token `FLOAT` (con exponente, `.5`, `5.`) existe pero el parser no lo usa | `1e-1`, `.5` o `1e-05` son errores de sintaxis | Nuevo |
| `store/FCL.g:328` | `TERM x := nombre` pasa un `Variable` como lista de parámetros | `Singleton() argument after * must be an iterable, not Variable` | Nuevo |
| `store/FCL.g:335` | Si un punto usa un nombre en vez de número, `$x` es `None` | `float(None.text)` falla | Nuevo |
| `store/FCL.g:266-267` | En Tsukamoto toma solo la primera conclusión | Las demás se descartan sin aviso | Nuevo |
| `store/FCL.g:149-151` | Exige todos los `FUZZIFY` antes que los `DEFUZZIFY`, y `METHOD` antes que `DEFAULT` | Orden más rígido que la norma IEC 61131-7 | Nuevo |
| `norms/norms.py:64-67` | `NSUM` con dos argumentos es exactamente `BSUM` | No normaliza sobre todas las reglas, como la `NSUM` de la literatura | Penumbra (sección 5) |
| `norms/norms.py:55-61` | `FAND` y `FOR` no son normas (sin neutro: `FAND(0.5, 1) = 0.625`) | Se ofrecen como `AND`/`OR` | Penumbra (sección 5) |
| `norms/norms.py:77-83` | `SUGENO` y `YAGER` por nombre usan λ = 0 y w = 1 | Equivalen a `ZADEH` | Penumbra (sección 5) |

### M20. `dump()` no siempre se puede volver a leer

**Origen:** Penumbra (sección 9) + nuevo. Corrección a Penumbra: con el runtime actual de ANTLR, los `Gaussian` y el `DEFAULT` ausente **sí se cargan**, pero gracias a la recuperación de errores de C3 (avisos en `stderr`).

| Caso | Qué pasa, ejecutado | Origen |
|---|---|---|
| `OR`/`NOT` distintos del par por defecto | `ruleblock.py:96-105` solo escribe `AND`, `ACT`, `ACCU`. Con `OR = ASUM`: `33.40` antes de guardar, `33.22` al volver a leer | Penumbra |
| Sugeno con `temp*0.6+2` | `24.8` antes, `22.8` después (C4) | Nuevo |
| Un número con exponente, como `1e-05` | La lectura falla y devuelve `None` | Nuevo |
| `Singleton(5, 0.3)` | `singleton.py:73-74` escribe `TERM a := 5;`: la altura 0.3 se pierde y vuelve como 1 | Nuevo |
| `Trapezoid`, `Triangular` | Se escriben como puntos y vuelven como `Polygon` | Penumbra |
| `Gaussian`, `Gamma` | Escriben su `Interval` como `(a .. b)`, que la gramática no admite (`gaussian.py:53`, `gamma.py:58`) | Penumbra |
| `Polynomial` | `str()` lanza `TypeError` (M9) | F14 |
| `default=None` | No escribe `DEFAULT`, que la gramática exige | Penumbra |
| Norma que es una función propia (sin `.name`) | `ruleblock.py:98`: `AttributeError: 'function' object has no attribute 'name'` | Nuevo |
| Salida con `defuzzification=None` | `variable.py:127`: `TypeError: can only concatenate str (not "NoneType")` | Nuevo |
| Un `FuzzySet` genérico | Se escribe `Fuzzy Set` (`fuzzy_set.py:412-415`), que no se puede leer | Nuevo |
| Números de regla | `RULE 47:` etc.: el contador es global a todo el proceso (B3) | Nuevo |

### M21. Dependencia `antlr3` no declarada ni instalable desde PyPI

**Origen:** nuevo (Penumbra lo anotaba en parte).

**Dónde:** `store/reader.py:8` (`import antlr3`) y `sample.py:1`, que importa `store.reader` **en la primera línea**.

**Qué pasa:**

- `setup.py` no declara la dependencia.
- En PyPI solo existe `antlr_python_runtime` 3.1.3, que es para Python 2. El runtime de ANTLR 3.5 para Python 3 solo está en el repositorio de GitHub de ANTLR 3.
- `sample.py`, el único ejemplo, falla con `ModuleNotFoundError: No module named 'antlr3'` antes de llegar a la parte de Python, aunque esa parte no lo necesite.
- El comentario de `store/reader.py:12-14` («error in antlr-3.5 lexer... change AL method by AT») está desfasado: con el runtime actual de GitHub, el FCL se lee sin parches y `sample.py` funciona entero (tras resolver C2).

---

## Bajo

### B1. `outputs=` se aplica a todos los bloques; bloques con igual nombre se pisan

**Origen:** nuevo.

- `systems/mamdani.py:28`: `outs = outputs or ruleblock.outputs`. Si se pasa `outputs`, se desdifusionan esas variables **en cada bloque**, también en los que no las usan. Ejecutado: los dos bloques devuelven `33.67`.
- `systems/system.py:31`: `self.blocks[block.name] = block`. Dos bloques con el mismo nombre: el segundo sustituye al primero sin aviso.
- `compute(inputs, outputs=None)` de Sugeno y Tsukamoto acepta `outputs` y lo ignora.

### B2. `Variable(nombre, adjetivo)` toma el adjetivo como unidad

**Origen:** nuevo (Penumbra lo anotaba en un comentario).

**Dónde:** `variable.py:12`: `def __init__(self, name, unit='', *adjectives, ...)`. Como `unit` es posicional, `Variable('t', frio, calor)` guarda `frio` como unidad y solo `calor` como adjetivo, sin error. Ejecutado: `Variable('t', a)` queda con `unit = a` y `adjectives = []`.

### B3. Detalles del analizador de reglas

**Origen:** nuevo, salvo donde se indica.

| Lugar | Fallo | Ejecutado |
|---|---|---|
| `rules/parser.py:29` | `if`, ` then `, `with` y el `is` del consecuente solo en minúsculas, y ` then ` con espacios exactos (no tabuladores) | `IF ... THEN ...` lanza `ValueError: not enough values to unpack` (Penumbra) |
| `operators/parser.py:68` | `NOT (` solo en mayúsculas | `not (` lanza `AssertionError` (Penumbra) |
| `rules/parser.py:24-27` | Prefijo sin `strip()`; uno desconocido se ignora | `' t:if ...'` y `'x:if ...'` dan `MRule` sin aviso |
| `rules/parser.py:24` | Cualquier `:` en la regla se toma como prefijo | Una regla con `:` en la expresión se parte mal |
| `rules/parser.py:30` | `if_.index('if')` busca la subcadena | Si falta el `if` inicial y un nombre contiene «if», corta por ahí |
| `rules/parser.py:37` | Sin `=` ni `is`: mensaje críptico | `ValueError: substring not found` |
| `rules/parser.py:72-79` | Tras cada predicado del consecuente salta un token suponiendo que es `,`, sin comprobarlo | Sin coma: `AssertionError`; `WITH` en mayúsculas: `IndexError` |
| `rules/parser.py:76`, `rules/rule.py:31-33` | `with 2` se acepta sin comprobar; `rule.weight = 2` se ignora en silencio | (Penumbra) |
| `operators/parser.py:31` | `scope or globals()` usa los globales del módulo del analizador | `scope=None` da `predicate sentence not well formed` |
| `operators/parser.py:117-118`, `rules/parser.py:108-109` | El error no dice qué nombre falta | `predicate sentence not well formed` |
| `operators/parser.py:62` | Regla que acaba tras `and`/`or`: `IndexError` sin explicación | |
| `rules/rule.py:11,25-26` | El número de regla es un contador global del proceso | Las reglas de un sistema nuevo salen como `17, 18, 19` |
| `rules/rule.py:65,84` | `input_vars`/`inputs` construyen un `set`: el orden de las entradas cambia entre ejecuciones | Afecta al orden de `dump()` |
| `rules/parser.py` + `systems/tsukamoto.py` | Sin `t:`, `TsukamotoSystem` falla al desempaquetar | `TypeError: cannot unpack non-iterable NoneType object` (Penumbra) |
| `rules/mrule.py` + `systems/sugeno.py` | Una regla Mamdani en un sistema Sugeno lanza un error; una Sugeno en Mamdani no aporta nada | (Penumbra) |

### B4. `Interval` y `Compound`: errores varios

**Origen:** F15, F16 + nuevo.

| Lugar | Fallo | Ejecutado | Origen |
|---|---|---|---|
| `interval.py:47` | `middle` devuelve `(max - min)/2`, la mitad del ancho | `Interval(2,4).middle` da `1.0` | F15 |
| `interval.py:164` | Compara `_min` dos veces | `Interval(2,4) == (2,4)` da `False` | F16 |
| `interval.py:160-166` | Define `__eq__` sin `__hash__` | `{Interval(0,1)}` lanza `TypeError: unhashable` | Nuevo |
| `interval.py:158` | `return TypeError(...)` en vez de `raise` | `Interval(0,1) < 5` devuelve un objeto `TypeError`, que es verdadero | Nuevo |
| `interval.py:139-143` | `__mul__` solo admite `float` | `Interval(0,1) * 2` devuelve `None` | Nuevo |
| `interval.py:81-82` | `__bool__` es falso para un intervalo de un punto | `bool(Interval(3,3))` da `False` (el de un `Singleton`) | Nuevo |
| `interval.py:237-261` | `Compound.union` une cada tramo por separado y no fusiona los que se solapan | `{[0,1],[5,6]} ∪ [0.5,5.5]` da `[0,5.5] ∪ [0.5,6]` | Nuevo |
| `interval.py:72-73` | `sampling` de un intervalo infinito devuelve solo los extremos | `list(Interval().sampling(1))` da `[-inf, inf]` | Nuevo |

### B5. `Polygon` y `FuzzySet`: errores varios de API

**Origen:** F13 + nuevo.

| Lugar | Fallo | Ejecutado | Origen |
|---|---|---|---|
| `rules/rule.py:50` | Errata `p.adective` | `input_adj()` lanza `AttributeError` con antecedentes compuestos | F13 |
| `fsets/polygon.py:311-324` | `p[i] = valor`: un entero menor que la longitud es un índice, uno mayor es una `x` | `p[1] = 0.5` lanza `TypeError` al ordenar | Nuevo |
| `fsets/polygon.py:201-202` | `merge_points` con un polígono vacío devuelve tuplas en vez de `x` | `fuzzify_with(Polygon())` lanza una excepción | Nuevo |
| `fsets/gamma.py:22-23` | No convierte una tupla en `Interval` (`Polynomial` sí lo hace) | `Gamma(0,1,(0,10)).union(...)` lanza `AttributeError` | Nuevo |
| `fsets/fuzzy_set.py:85-87`, `97-99` | `&` y `\|` con un número fallan, aunque `_operation` sí admite números | `Polygon(...) & 0.5` lanza `AttributeError` | Nuevo |
| `fsets/fuzzy_set.py:409-410`, `polygon.py:329-330` | Iterar un `FuzzySet` devuelve sus tres normas; iterar un `Polygon`, sus puntos | Incoherente | Nuevo |
| `fsets/fuzzy_set.py:162`, `polygon.py:99` | `COG` divide por el área sin comprobar que no sea 0 | `ZeroDivisionError` (que C8 oculta) | Nuevo |
| `fsets/trapezoid.py:75-86`, `triangular.py:46-57` | `add_point`, `add_points` y `clear` devuelven otro objeto; en `Polygon` modifican el original | (Penumbra) | Penumbra |
| `fsets/sfunction.py:31-42` | `b` solo decide el cambio de rama; si no está en el centro, la curva da un salto; las `y` de `a` y `c` solo actúan fuera del intervalo | (Penumbra) | Penumbra |
| `fsets/zfunction.py:16-18` | El docstring dice que `a` es el máximo, pero la fórmula es `1 - S` y hay que pasar `a = (ax, 0)` | (Penumbra) | Penumbra |
| `fsets/gamma.py:7-18` | El docstring la describe como una V, pero el código es de un solo lado | (Penumbra) | Penumbra |
| `fsets/polygon.py:35-38` | Fuera de sus puntos se prolonga constante, no vale 0 | `Polygon((0,1),(10,0.5))(-5)` da `1` (Penumbra) | Penumbra |
| `fsets/fuzzy_set.py:313-343` | La aritmética entre conjuntos no comprueba que el resultado siga en `[0, 1]` | (Penumbra) | Penumbra |

### B6. `SyntaxWarning` por los dibujos de los docstrings

**Origen:** F24 (Penumbra no listaba `gamma.py`).

**Dónde:** `fsets/gamma.py:10` (`\ `), `fsets/pifunction.py:14`, `fsets/trapezoid.py:14`, `fsets/triangular.py:13` y `70`, `fsets/zfunction.py:12` (`\_`).

**Qué pasa:** Python 3.14 avisa con `SyntaxWarning: "\_" is an invalid escape sequence` al importar; en una versión futura será un error de sintaxis. Basta con docstrings `r"""..."""`.

### B7. Código muerto, erratas y estilo

**Origen:** nuevo, salvo donde se indica.

| Lugar | Detalle |
|---|---|
| `README.md:6` | «Mandani» en vez de «Mamdani» (Penumbra) |
| `fsets/fuzzy_set.py:192-204` | `_COA` no se usa y puede devolver `None` |
| `rules/trule.py:20-58` | `get_x` duplica `get_strength_x` y no se usa |
| `rules/srule.py:30-31` | `crisp()` no se usa |
| `variable.py:39-41` | `Variable.fuzzify` no la usa ningún sistema y su nombre engaña: no calcula grados (Penumbra, sección 3) |
| `variable.py:135` | `__repr__` oculta el valor `0` (`if self.value`) |
| `fsets/polygon.py:13` | `_lines` en `__slots__`, nunca usado |
| `fsets/polygon.py:44` | `raise Exception('interval not found')` inalcanzable |
| `operators/parser.py:130-137` | `__repr__` definido dos veces |
| `operators/binary.py:48,52` | `print_tree` pone el tabulador antes del prefijo: la sangría sale mal |
| `operators/binary.py`, `operators/operator.py` | `Unary` declara `__slots__`, pero `Operator` y `Binary` no, así que no sirve de nada |
| `fsets/triangular.py:63` | `built_from`, mientras `Rect` usa `build_from` |
| `norms/max1.py:6` | La norma de ejemplo se llama `maximum`, igual que la de `norms.py` |
| `__init__.py`, todos | `__author__ = ''` vacío |
| `sample.py:154-159` | Escribe tres archivos en la carpeta actual y los vuelve a leer |
| `sample.py:139` | Reutiliza el nombre de bloque `second` |

---

## Correcciones a la documentación de Penumbra

Lo que esta revisión cambia respecto a `doc.md`:

1. **FCL sí se puede ejecutar** con el runtime de ANTLR 3.5 para Python 3 de GitHub, sin parchear nada. El comentario de `store/reader.py` está desfasado.
2. **«Consecuentes Sugeno con `+ - * ** / //`» no es cierto:** `**` y `//` se leen como `*` y `/`, y un `+n`/`-n` sin espacio se pierde o falla (C4).
3. **`Gaussian` y `DEFAULT` ausente sí se vuelven a leer**, pero por la recuperación de errores de ANTLR (C3), no porque la gramática los admita.
4. **`Polygon` no es exacto con cualquier norma:** solo con `MIN`, `MAX` y el producto por un número (A2).
5. **F24 también afecta a `fsets/gamma.py:10`.**
