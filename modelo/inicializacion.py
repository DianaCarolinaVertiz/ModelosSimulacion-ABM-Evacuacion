"""Crear agentes iniciales sin necesitar ejecutar humo, BFS ni simulación.

Posiciones uniformes y distintas. Los tipos de activación se asignan al azar,
respetando la proporción configurada.
"""
from .agente import Agente


def crear_agentes_iniciales(configuracion, entorno, aleatorio):
    """Genera la población al inicio de una realización.

    Parámetros:
        configuracion (Configuracion): Tamaño de población, proporción
            de activación baja y probabilidades de activación.
        entorno (Entorno): Recinto con paredes y fuentes de humo,
            usado para determinar posiciones iniciales admisibles.
        aleatorio (numpy.random.Generator): Generador compartido que
            sortea posiciones y asignaciones de tipos.

    Devuelve:
        list[Agente]: Exactamente n_agentes con posiciones únicas,
        sin ubicar agentes sobre paredes ni fuentes de humo.

    Excepciones:
        ValueError: Si no hay suficientes celdas candidatas.

    Notas:
        Se usan celdas interiores, separadas del borde. El número
        de personas con activación baja es el entero más cercano
        a la proporción solicitada. La selección de posiciones
        y la asignación de tipos son aleatorias y sin reemplazo.
    """
    candidatos = []

    for y in range(2, configuracion.alto - 2): # Decisión de diseño.
        for x in range(3, configuracion.ancho - 3): # Desde 3 para evitar la salida izquierda y la pared derecha
            if not entorno.paredes[y, x] and (x, y) not in entorno.fuentes:
                candidatos.append((x, y))
    
    if configuracion.n_agentes > len(candidatos):
        raise ValueError("No hay suficientes celdas libres para la población.")

    aleatorio.shuffle(candidatos) # muestreo uniforme sin reemplazo, todas las posiciones candidatas son igualmente probables
    posiciones = candidatos[:configuracion.n_agentes] # y ninguna celda se repite, ya que se selecciona sin reemplazo

    indices = list(range(configuracion.n_agentes))
    aleatorio.shuffle(indices)
    cantidad_activacion_baja = round(configuracion.n_agentes * configuracion.proporcion_activacion_baja)
    identificadores_activacion_baja = set(indices[:cantidad_activacion_baja])

    agentes = []
    for identificador, (x, y) in enumerate(posiciones):
        tipo = "baja" if identificador in identificadores_activacion_baja else "alta"
        probabilidad = configuracion.probabilidad_activacion_baja if tipo == "baja" else configuracion.probabilidad_activacion_alta
        agentes.append(Agente(identificador, x, y, tipo, probabilidad))
    return agentes
