# Consigna del trabajo práctico — Modelos basados en agentes

**Cátedra Modelos y Simulación**

**Facultad de Ingeniería y Ciencias Hídricas (FICH) — Universidad Nacional del Litoral (UNL)**

## Objetivos

Implementar y analizar un modelo basado en agentes (ABM) de evacuación. Se espera reconocer las diferencias entre las reglas individuales y la dinámica colectiva, aplicar algoritmos para actualizar el entorno y coordinar agentes, y comparar resultados mediante experimentos reproducibles.

**Pregunta central:** ¿Cómo influye la cantidad de personas sobre el proceso de evacuación y qué diferencias aparecen entre la actualización síncrona y la asíncrona?

## Descripción del modelo

Se simula la **evacuación de personas de un recinto**. Cada persona es un *agente* con una posición y reglas propias para intentar alcanzar alguna de las dos salidas. Los agentes comparten el mismo espacio: sus movimientos pueden verse limitados por obstáculos, humo y otras personas.

**El recinto** se representa mediante una grilla de 39 × 25 celdas, con paredes, dos obstáculos interiores y dos salidas de dos celdas cada una. Hay un foco de incendio fijo de cuatro celdas, que no se puede atravesar. En cada paso, el humo se propaga, se atenúa parcialmente y recibe un nuevo aporte del foco. Una celda con humo igual o superior al umbral configurado deja de admitir nuevos ingresos. Por simplificación, las salidas no se bloquean por humo.

**Los agentes** comienzan en posiciones distintas, distribuidas aleatoriamente. Pueden desplazarse como máximo una celda por paso, hacia arriba, abajo, izquierda o derecha. La mitad tiene **activación alta** (probabilidad 1,0 de intentar actuar en un paso) y la otra mitad **activación baja** (0,7). Que un agente se active no significa necesariamente que consiga moverse.

**La simulación** avanza en pasos discretos. En cada uno se actualiza el humo, se calculan las distancias a las salidas, se coordinan los movimientos y se registran los resultados. Cada celda de salida admite como máximo una evacuación por paso.

### ¿Cómo se calculan las distancias con BFS?

Para orientarse, los agentes utilizan un **campo de distancias**: una matriz que indica cuántos movimientos mínimos hacen falta desde cada celda para llegar a **alguna salida**, evitando paredes y zonas bloqueadas. No es una ruta ya trazada para cada persona.

El algoritmo **BFS (*Breadth-First Search*, búsqueda en anchura)** construye ese campo comenzando en las cuatro celdas de salida, todas con distancia **0**. Las incorpora a una cola FIFO y explora sus vecinos transitables: los vecinos nuevos reciben distancia **1**, luego sus vecinos distancia **2**, y así sucesivamente. Las celdas bloqueadas o sin camino hacia una salida quedan con **-1**.

BFS **no considera dónde están las personas**; esas posiciones se comprueban al decidir los movimientos. El campo se vuelve a calcular en cada paso porque el humo puede modificar los caminos disponibles.

### ¿Cómo decide moverse cada agente?

Cuando un agente está habilitado para actuar:

1. Examina sus **cuatro celdas vecinas** y descarta las que no son transitables, están ocupadas, no tienen camino a una salida o corresponden a una celda de salida ya utilizada en ese paso.
2. Prefiere los vecinos que **disminuyen su distancia BFS**. Por ejemplo, si está a distancia 8, avanzar a una celda de distancia 7 lo acerca a una salida. Si existen varias opciones, elige la de menor distancia; luego la de menor humo; y, si persiste el empate, sortea.
3. Si no puede acercarse, tiene una **probabilidad de 0,15 de intentar un desvío** hacia un vecino admisible; de lo contrario permanece donde está. Si su celda actual quedó bloqueada por humo (distancia -1), puede intentar salir directamente hacia un vecino seguro que tenga camino a una salida.

El agente **propone** el destino, pero todavía no se mueve: la simulación determina si puede ejecutar ese desplazamiento. En la actualización **síncrona**, todos proponen usando la ocupación inicial del paso y, si varios eligen la misma celda, se sortea un ganador. En la **asíncrona**, los agentes actúan en orden aleatorio y la ocupación se actualiza después de cada movimiento, de modo que los siguientes pueden aprovechar espacios liberados.

## Actividades de implementación

El código está organizado en clases y métodos. Deben completarse los métodos señalados con `TODO`, manteniendo sus firmas e interfaces.

| Etapa | Notebook | Qué se debe implementar |
|---|---|---|
| 1. Recinto y agentes iniciales | `01_escenario.ipynb` | Explorar el entorno; no requiere implementación |
| 2. Propagación del humo | `02_humo.ipynb` | `Entorno.actualizar_humo()` |
| 3. Distancias a las salidas | `03_distancias_bfs.ipynb` | `Entorno.calcular_distancias()` |
| 4. Decisiones individuales | `04_agentes.ipynb` | `Agente.esta_habilitado()`, `_seleccionar_mejor_opcion()`, `elegir_destino()`, `mover()` y `evacuar()` |
| 5. Coordinación temporal | `05_simulacion.ipynb` | `Simulacion._hacer_paso_movimiento()` y `avanzar()` |
| 6. Experimentación | `06_experimento.ipynb` | Ejecutar las condiciones experimentales, graficar y analizar resultados |

**¿Para qué sirven las notebooks `01` a `05`?** Son guías para **probar progresivamente los métodos implementados en los archivos de `modelo/`**. Incluyen visualizaciones y comprobaciones con `assert`. La notebook `01` funciona antes de programar; después, al completar cada etapa, se ejecuta la notebook correspondiente para observar el resultado y comprobar propiedades del modelo. No es necesario programar los métodos dentro de las notebooks: el código a completar está en los módulos `.py`. Si alguna comprobación falla, se revisa la implementación y se vuelve a ejecutar esa etapa.

Estas notebooks son herramientas de trabajo y no forman parte de la entrega. El avance debe respetar las condiciones del modelo: no superponer agentes, impedir ingreso a paredes y focos, no superar la capacidad de las salidas y conservar `N = restantes + evacuados`.

## Experimento obligatorio

Comparar las cuatro condiciones formadas por:

- **Poblaciones iniciales:** 80 y 250 agentes.
- **Actualización:** síncrona y asíncrona.
- **Semillas para cada condición:** 11, 23, 37, 41 y 53.

Son **20 realizaciones**. Los demás parámetros deben mantenerse constantes, incluida la ubicación del foco de incendio.

Presentar una tabla de resultados individuales y un resumen por condición con **media y desviación estándar** del tiempo medio individual de evacuación y la fracción evacuada. El tiempo medio sólo considera los agentes que lograron evacuar; si una realización es incompleta, esto deberá señalarse.

Generar gráficos que permitan comparar los tiempos medios y, para ambas poblaciones, las **curvas de fracción evacuada** en función de los pasos para los dos esquemas (elegir la misma semilla al compararlos). Interpretar diferencias, congestión observable y variación entre realizaciones.

Discutir brevemente las **limitaciones** del modelo. Entre ellas pueden considerarse la discretización del espacio y del tiempo, el campo BFS con conocimiento global, las reglas simplificadas, las salidas que no se bloquean por humo y la falta de calibración con datos observados.

## Entrega

Entregar `notebooks/06_experimento.ipynb` ejecutada, con los resultados del experimento, tablas, gráficos, interpretación y una breve discusión de las limitaciones del modelo.

Para permitir su ejecución y corrección, deben acompañar la entrega los tres archivos Python implementados: `modelo/agente.py`, `modelo/entorno.py` y `modelo/simulacion.py`.

La notebook debe poder ejecutarse desde el principio, con el entorno de dependencias instalado, sin requerir variables creadas anteriormente en otras notebooks. Los gráficos deben identificar ejes, unidades, leyendas y condiciones.

## Criterios de evaluación

| Criterio | Aspectos a evaluar |
|---|---|
| **Funcionamiento** | Ejecución consistente y reproducible; conservación de la población |
| **Corrección de las reglas** | Difusión de humo, BFS, decisiones de agentes, coordinación y capacidad de salidas |
| **Experimentación** | Ejecución de todas las condiciones, comparación controlada y uso de varias semillas |
| **Calidad del análisis** | Gráficos claros, interpretación de las diferencias observadas y reconocimiento de las limitaciones del modelo |

**Aclaración:** es un ejercicio de modelado y simulación con fines académicos. El modelo no está validado para evaluar la seguridad de evacuaciones reales.
