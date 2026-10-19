"""Representación individual de personas y reglas de movimiento.

Cada agente propone un destino. La clase Simulacion acepta o rechaza
la propuesta y ejecuta los desplazamientos autorizados.
Las posiciones usan (x, y); las matrices NumPy se indexan [y, x].
"""
from .entorno import VECINOS

class Agente:
    """Representa una persona que participa en la evacuación.

    Los tipos de activación determinan la probabilidad de activación
    por paso, pero no la distancia máxima de desplazamiento.
    Un agente puede avanzar como máximo una celda por paso.
    """

    def __init__(self, identificador, x, y, tipo, probabilidad_activacion):
        """Inicializa una persona y sus atributos.

        Parámetros:
            identificador (int): Identificador único del agente.
            x (int): Columna inicial, con índices desde cero.
            y (int): Fila inicial, con índices desde cero.
            tipo (str): Categoría "alta" o "baja".
            probabilidad_activacion (float): Probabilidad de obtener una
                oportunidad de actuar en cada paso; valor entre 0 y 1.

        Notas:
            La persona comienza sin evacuar y sin tiempo ni salida
            de evacuación asignados.
        """
        self.identificador = identificador
        self.x = int(x)
        self.y = int(y)
        self.tipo = tipo
        self.probabilidad_activacion = float(probabilidad_activacion)
        self.evacuado = False
        self.tiempo_evacuacion = None
        self.salida_utilizada = None

    def posicion(self):
        """Devuelve la posición actual.

        Devuelve:
            tuple[int, int]: Coordenadas (x, y), columna y fila.
        """
        return (self.x, self.y)

    def esta_habilitado(self, aleatorio):
        """Sortea si el agente tiene oportunidad de actuar en este paso.

        Parámetros:
            aleatorio (numpy.random.Generator): Generador de números
                aleatorios compartido por la simulación.

        Devuelve:
            bool: True si no está evacuado y supera el sorteo de
            activación; False en los demás casos.

        Notas:
            Estar habilitado no garantiza movimiento: puede no haber
            destinos libres o el agente puede perder un conflicto.
            Este método no modifica su posición.
        """
        # TODO: Un agente que ya evacuó no vuelve a activarse.
        # Para los demás, sortear la activación según su probabilidad.
        raise NotImplementedError("Completar esta_habilitado")

    def _seleccionar_mejor_opcion(self, opciones, aleatorio):
        """Selecciona el destino preferido entre candidatos ya filtrados.

        Parámetros:
            opciones (list[tuple[int, float, tuple[int, int]]]): Lista
                no vacía de candidatos, cada uno con formato
                (distancia_bfs, concentracion_humo, (x, y)).
                Puede corresponder a todos los vecinos admisibles
                ('opciones') o solo a los que acercan a una salida
                ('avances') dentro de elegir_destino().
            aleatorio (numpy.random.Generator): Generador compartido
                usado para desempatar candidatos equivalentes.

        Devuelve:
            tuple[int, int]: Posición (x, y) del vecino seleccionado.

        Notas:
            Se prioriza la menor distancia BFS; entre los empatados,
            la menor concentración de humo; y luego un sorteo uniforme.
            Concentraciones que difieren menos de 1e-10 se consideran
            equivalentes. No se modifica la posición del agente.
        """
        # TODO: Elegir primero las opciones de menor distancia BFS.
        # Si hay empate, priorizar la menor concentración de humo.
        # Si persiste el empate, sortear uniformemente una opción.
        raise NotImplementedError("Completar _seleccionar_mejor_opcion")

    def elegir_destino(self, entorno, ocupadas, distancias, salidas_utilizadas, aleatorio):
        """Propone una celda vecina como destino, sin mover al agente.

        Parámetros:
            entorno (Entorno): Recinto, paredes, salidas, humo y regla
                es_transitable() para comprobar la accesibilidad.
            ocupadas (dict[tuple[int, int], int]): Diccionario que asocia
                posiciones (x, y) ocupadas con identificadores de agentes.
                En modo síncrono se usa la ocupación al inicio de la
                ronda; en asíncrono se actualiza tras cada movimiento.
            distancias (numpy.ndarray): Campo de distancias BFS hasta
                las salidas, indexado por [y, x]. El valor -1 significa
                celda bloqueada o sin ruta. No considera la ocupación.
            salidas_utilizadas (set[tuple[int, int]]): Celdas de salida
                que ya evacuaron a una persona en este paso.
                Los conflictos síncronos se resuelven posteriormente.
            aleatorio (numpy.random.Generator): Generador compartido
                empleado en los sorteos de desvío y desempate.

        Devuelve:
            tuple[int, int] | None: Posición (x, y) propuesta o None
            cuando el agente decide no desplazarse.

        Notas:
            'opciones' reúne los cuatro vecinos ortogonales que son
            transitables, están desocupados, no son salidas utilizadas
            y tienen una distancia BFS válida.
            'avances' contiene únicamente las opciones con distancia
            BFS estrictamente menor que la de la posición actual.

            Si existen avances, se selecciona uno de ellos. Si no,
            se intenta un desvío con probabilidad configurada.
            Cuando la distancia actual es -1 pero existe una opción
            válida, se selecciona un vecino directamente, permitiendo
            escapar de una celda que quedó bloqueada por humo.

            La clase Simulacion decide si acepta la propuesta.
        """
        # TODO: Obtener los cuatro vecinos ortogonales de la posición.
        # Descartar celdas no transitables, ocupadas, sin ruta BFS
        # o salidas que ya hayan sido utilizadas en este paso.
        # Si es posible, elegir una opción que reduzca la distancia BFS.
        # Si no hay avance, decidir si se intenta un desvío.
        # Si la posición actual se bloqueó por humo, intentar salir
        # a una celda segura con ruta disponible.
        # IMPORTANTE: este método PROPONE un destino, no lo ejecuta.
        raise NotImplementedError("Completar elegir_destino")

    def mover(self, nueva_posicion):
        """Ejecuta un movimiento ya aceptado por la simulación.

        Parámetros:
            nueva_posicion (tuple[int, int]): Posición de destino (x, y).

        Devuelve:
            None: Actualiza los atributos x e y del agente.

        Notas:
            No verifica ocupación ni accesibilidad; la simulación
            ya debe haber aceptado el destino propuesto.
        """
        # TODO: Actualizar x e y con las coordenadas del destino aprobado.
        raise NotImplementedError("Completar mover")

    def evacuar(self, salida, tiempo):
        """Registra el resultado de la evacuación del agente.

        Parámetros:
            salida (str): Nombre de la salida utilizada:
                "izquierda" o "derecha".
            tiempo (int): Paso de simulación en que evacúa.

        Devuelve:
            None: Actualiza los atributos evacuado,
            salida_utilizada y tiempo_evacuacion.
        """
        # TODO: Registrar que evacuó, qué salida utilizó
        # y en qué paso de simulación ocurrió.
        raise NotImplementedError("Completar evacuar")

