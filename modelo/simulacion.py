"""Coordinación del modelo de evacuación: tiempo, turnos y resultados.

La clase Simulacion organiza una sola ronda de movimiento por paso.
Las decisiones microscópicas corresponden a Agente; la accesibilidad,
el humo y el campo de distancias BFS corresponden a Entorno.
"""
import numpy as np
from .entorno import Entorno
from .inicializacion import crear_agentes_iniciales


class Simulacion:
    """Coordinar agentes y entorno sin elegir destinos por ellos.

    Un paso completo sigue este orden:
        1. Actualizar el campo de humo.
        2. Recalcular el campo de distancias BFS.
        3. Activar probabilísticamente a los agentes y coordinar una ronda.
        4. Registrar observables para las curvas y visualizaciones.

    Tanto en actualización síncrona como asíncrona los agentes utilizan las
    mismas reglas individuales. Solo cambia cómo se organizan sus turnos.
    """

    def __init__(self, configuracion):
        """Prepara una realización completa del modelo de evacuación.

        Parámetros:
            configuracion (Configuracion): Parámetros de agentes,
                ambiente, esquema temporal, semilla y registros.

        Devuelve:
            None: Crea el generador aleatorio, entorno, agentes
            e historiales, y registra el estado inicial (paso cero).
        """
        self.configuracion = configuracion
        self.aleatorio = np.random.default_rng(configuracion.semilla)

        self.entorno = Entorno(configuracion)
        self.agentes = crear_agentes_iniciales(self.configuracion, self.entorno, self.aleatorio)
        
        self.tiempo = 0
        # Historial temporal para las curvas y fotogramas para animaciones.
        self.historial = []
        self.fotogramas = []

        # Apoyo visual para identificar zonas de permanencia y congestión.
        # Registra la cantidad de pasos que cada celda estuvo ocupada por agentes no evacuados.
        self.ocupacion_acumulada = np.zeros((configuracion.alto, configuracion.ancho), dtype=int)
        self._registrar()

    def _ocupadas(self):
        """Consulta las celdas ocupadas por agentes no evacuados.

        Devuelve:
            dict[tuple[int, int], int]: Diccionario que asocia
            cada posición (x, y) con el identificador del agente.

        Notas:
            Las posiciones de personas evacuadas no aparecen.
            BFS no consulta este diccionario: la ocupación afecta
            solamente a las propuestas de movimiento.
        """
        ocupadas = {}
        for agente in self.agentes:
            if not agente.evacuado:
                ocupadas[agente.posicion()] = agente.identificador
        return ocupadas

    def _aplicar_movimiento(self, agente, destino, salidas_utilizadas):
        """Ejecuta un movimiento aceptado y registra una salida, si ocurre.

        Parámetros:
            agente (Agente): Persona cuya propuesta fue aceptada.
            destino (tuple[int, int]): Celda (x, y) de llegada.
            salidas_utilizadas (set[tuple[int, int]]): Conjunto
                mutable de salidas ya utilizadas en este paso.

        Devuelve:
            None: Modifica la posición del agente y, si llega a
            una salida, su estado de evacuación y el conjunto recibido.

        Notas:
            No decide el destino ni comprueba conflictos.
            Cada celda de salida puede evacuar una persona por paso.
        """
        agente.mover(destino)

        if destino in self.entorno.salidas:
            nombre = "izquierda" if destino[0] == 0 else "derecha"
            agente.evacuar(nombre, self.tiempo)
            salidas_utilizadas.add(destino)

    def _hacer_paso_movimiento(self, distancias, salidas_utilizadas):
        """Coordina una ronda de decisiones y movimientos individuales.

        Parámetros:
            distancias (numpy.ndarray): Campo BFS [y, x] calculado
                con el estado actual de paredes y humo.
            salidas_utilizadas (set[tuple[int, int]]): Conjunto mutable
                inicialmente vacío que registra las celdas de salida
                usadas durante el paso actual.

        Devuelve:
            None: Ejecuta las propuestas aceptadas y actualiza
            posiciones y evacuaciones de los agentes.

        Notas:
            Primero se sortea qué agentes quedan habilitados.
            En modo síncrono todos proponen usando la ocupación
            inicial: las propuestas en conflicto por una celda
            se resuelven mediante un sorteo y se ejecutan después.
            En modo asíncrono se sortea el orden de los habilitados;
            cada agente consulta la ocupación ya actualizada y,
            si propone un destino, se mueve inmediatamente.
            Las reglas individuales son las mismas en ambos modos.
        """
        # La lista de activos contiene a los agentes habilitados en este paso.
        activos = []
        for agente in self.agentes:
            if agente.esta_habilitado(self.aleatorio):
                activos.append(agente)

        ocupadas = self._ocupadas()

        if self.configuracion.actualizacion == "sincrona":
            propuestas = {}

            # TODO: Pedir propuestas sin mover todavía a nadie.
            # Todos deben consultar la misma ocupación inicial.
            # Agrupar por destino los agentes que solicitan esa celda.

            # TODO: Si varios agentes proponen el mismo destino,
            # sortear un único ganador y aplicar su movimiento.
            raise NotImplementedError("Completar actualización síncrona")

        else:
            # TODO: Mezclar el orden de los agentes activos.
            # Procesar los agentes uno por uno, utilizando siempre
            # la ocupación actualizada hasta ese momento.
            # Si el agente puede moverse, liberar su antigua celda,
            # aplicar el movimiento y, si no evacuó, ocupar el destino.
            raise NotImplementedError("Completar actualización asíncrona")

    def _registrar(self):
        """Registra indicadores y, cuando corresponde, un fotograma.

        Devuelve:
            None: Agrega un elemento a historial; actualiza la
            ocupación acumulada y, según guardar_cada o la finalización,
            agrega un fotograma.

        Notas:
            Cada fila del historial contiene paso, personas restantes,
            evacuados, fracción evacuada y acumulados por salida.
            La ocupación acumulada suma pasos de permanencia por celda;
            no mide directamente flujo de personas.
            Los fotogramas contienen posiciones de agentes no evacuados,
            matriz de humo y conteos de evacuación.
        """
        total = len(self.agentes)
        restantes = 0
        izquierda = 0
        derecha = 0

        for agente in self.agentes:
            if not agente.evacuado:
                restantes += 1
                self.ocupacion_acumulada[agente.y, agente.x] += 1
            # cantidad acumulada de personas evacuadas por cada salida hasta el paso actual
            if agente.salida_utilizada == "izquierda":
                izquierda += 1

            elif agente.salida_utilizada == "derecha":
                derecha += 1

        evacuados = total - restantes

        self.historial.append({
            "paso": self.tiempo,
            "restantes": restantes,
            "evacuados": evacuados,
            "fraccion_evacuada": evacuados / total,
            "salida_izquierda": izquierda,
            "salida_derecha": derecha,
        })

        # Registrar un fotograma si corresponde: cada guardar_cada pasos o al final de la simulación.
        if self.tiempo % self.configuracion.guardar_cada == 0 or restantes == 0:
            posiciones = []
            for agente in self.agentes:
                if not agente.evacuado:
                    posiciones.append((agente.x, agente.y, agente.tipo))
            
            self.fotogramas.append({
                "paso": self.tiempo,
                "posiciones": posiciones,
                "humo": self.entorno.humo.copy(),
                "restantes": restantes,
                "izquierda": izquierda,
                "derecha": derecha,
            })

    def avanzar(self):
        """Intenta ejecutar el siguiente paso de simulación.

        Devuelve:
            bool: True si ejecutó un paso y registró el resultado;
            False si todos evacuaron o ya se alcanzó pasos_maximos.

        Notas:
            El orden del paso es: avanzar el tiempo, actualizar humo,
            recalcular BFS, coordinar movimientos y registrar datos.
            Una persona puede moverse como máximo una celda por paso.
        """
        # TODO: Comprobar si debe detenerse la simulación y devolver False.
        # Si puede continuar:
        #   - Incrementar el tiempo.
        #   - Actualizar el humo y recalcular el campo BFS.
        #   - Crear el conjunto de salidas utilizadas en este paso.
        #   - Coordinar el movimiento mediante _hacer_paso_movimiento().
        #   - Registrar el estado resultante.
        # Devolver True si efectivamente se ejecutó un paso.
        raise NotImplementedError("Completar avanzar")

    def ejecutar(self):
        """Ejecuta pasos sucesivos hasta detener la simulación.

        Devuelve:
            Simulacion: El mismo objeto tras completar la evacuación
            o alcanzar el máximo de pasos configurado.

        Notas:
            Los datos quedan disponibles en historial, fotogramas
            y ocupacion_acumulada.
        """
        while self.avanzar():
            pass
        return self

    def indicadores(self):
        """Calcula los indicadores resumidos de una realización.

        Devuelve:
            dict: Diccionario con semilla (int), n_agentes (int),
            actualizacion (str), fraccion_evacuada (float)
            y tiempo_medio_individual (float).

        Notas:
            El tiempo medio individual se calcula únicamente entre
            quienes evacuaron. Si nadie evacúa, se devuelve NaN.
            Si fraccion_evacuada es menor que 1, el promedio no
            representa a toda la población inicial.
        """
        tiempos = []
        for agente in self.agentes:
            if agente.evacuado:
                tiempos.append(agente.tiempo_evacuacion)

        total = len(self.agentes)
        evacuados = len(tiempos)
        tiempo_medio = float(np.mean(tiempos)) if tiempos else np.nan

        return {
            "semilla": self.configuracion.semilla,
            "n_agentes": total,
            "actualizacion": self.configuracion.actualizacion,
            "fraccion_evacuada": evacuados / total,
            "tiempo_medio_individual": tiempo_medio,
        }
