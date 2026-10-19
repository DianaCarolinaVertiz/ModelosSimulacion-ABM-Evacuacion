"""Parámetros del modelo didáctico de evacuación.

El experimento obligatorio varía solo N y la actualización. El foco puede
cambiarse en exploraciones opcionales. Unidades: celdas y pasos.
"""

class Configuracion:
    """Parámetros fijos, experimentales y de ejecución del ABM.

    Hay dos tipos: activación alta (probabilidad 1.0 de activación por paso)
    y activación baja (0.70). Máximo un desplazamiento de una celda por paso.
    """

    def __init__(self, ancho=39, alto=25, n_agentes=160, proporcion_activacion_baja=0.5, probabilidad_activacion_alta=1.0, probabilidad_activacion_baja=0.7, semilla=17, actualizacion="sincrona", pasos_maximos=420, usar_humo=True, posicion_foco="izquierda", difusion_humo=0.52, decaimiento_humo=0.009, aporte_humo=0.24, umbral_bloqueo=0.40, probabilidad_desvio=0.15, guardar_cada=4):
        """Inicializa todos los parámetros y verifica su validez.

        Parámetros:
            ancho (int): Número de columnas del recinto; debe ser 39.
            alto (int): Número de filas del recinto; debe ser 25.
            n_agentes (int): Cantidad inicial de personas; debe ser positiva.
            proporcion_activacion_baja (float): Fracción inicial de
                personas con activación baja, entre 0 y 1.
            probabilidad_activacion_alta (float): Probabilidad de activación
                por paso de una persona de activación alta, entre 0 y 1.
            probabilidad_activacion_baja (float): Probabilidad de
                activación por paso de una persona de activación baja.
            semilla (int): Semilla para reproducir una realización aleatoria.
            actualizacion (str): "sincrona" o "asincrona".
            pasos_maximos (int): Límite de pasos de la simulación.
            usar_humo (bool): Activa la propagación del humo y su uso
                para determinar la accesibilidad de las celdas.
            posicion_foco (str): Ubicación del foco emisor:
                "izquierda", "centro" o "derecha".
            difusion_humo (float): Coeficiente no negativo que regula
                el intercambio entre celdas vecinas.
            decaimiento_humo (float): Tasa no negativa de pérdida del humo.
            aporte_humo (float): Aporte no negativo por paso en cada fuente.
            umbral_bloqueo (float): Concentración normalizada entre 0 y 1
                que impide ingresar a una celda cuando es alcanzada.
            probabilidad_desvio (float): Probabilidad, entre 0 y 1,
                de intentar un desplazamiento alternativo cuando el
                agente no puede reducir su distancia BFS.
            guardar_cada (int): Intervalo positivo, en pasos, para
                guardar los fotogramas periódicos.

        Devuelve:
            None: Guarda los parámetros en los atributos del objeto.

        Excepciones:
            ValueError: Si los valores no superan las comprobaciones
                de validar().

        Notas:
            Se llama automáticamente a validar() al inicializar.
            El humo es adimensional y el tiempo se mide en pasos.
        """
        self.ancho = ancho
        self.alto = alto
        self.n_agentes = n_agentes
        self.proporcion_activacion_baja = proporcion_activacion_baja
        self.probabilidad_activacion_alta = probabilidad_activacion_alta
        self.probabilidad_activacion_baja = probabilidad_activacion_baja
        self.semilla = semilla
        self.actualizacion = actualizacion
        self.pasos_maximos = pasos_maximos
        self.usar_humo = usar_humo
        self.posicion_foco = posicion_foco
        self.difusion_humo = difusion_humo
        self.decaimiento_humo = decaimiento_humo
        self.aporte_humo = aporte_humo
        self.umbral_bloqueo = umbral_bloqueo
        self.probabilidad_desvio = probabilidad_desvio
        self.guardar_cada = guardar_cada
        self.validar()

    def validar(self):
        """Comprueba que los parámetros admiten una simulación.

        Devuelve:
            None: Finaliza sin cambios si la configuración es válida.

        Excepciones:
            ValueError: Cuando actualización, foco, probabilidades,
                umbral, coeficientes de humo, cantidades positivas
                o dimensiones no cumplen las restricciones del modelo.

        Notas:
            No verifica si todas las personas pueden ubicarse en
            celdas libres; eso se comprueba durante la inicialización.
        """
        if self.actualizacion not in ("sincrona", "asincrona"):
            raise ValueError("La actualización debe ser 'sincrona' o 'asincrona'.")
        if self.posicion_foco not in ("izquierda", "centro", "derecha"):
            raise ValueError("Ubicación del foco inválida.")
        for valor in (self.proporcion_activacion_baja, self.probabilidad_activacion_alta, self.probabilidad_activacion_baja, self.probabilidad_desvio, self.umbral_bloqueo):
            if not 0 <= valor <= 1:
                raise ValueError("Probabilidades y umbrales deben estar entre 0 y 1.")
        if min(self.difusion_humo, self.decaimiento_humo, self.aporte_humo) < 0:
            raise ValueError("Los coeficientes del humo deben ser no negativos.")
        if self.n_agentes < 1 or self.pasos_maximos < 1 or self.guardar_cada < 1:
            raise ValueError("N, horizonte y frecuencia de registro deben ser positivos.")
        if (self.ancho, self.alto) != (39, 25):
            raise ValueError("Esta práctica utiliza una geometría fija de 39 por 25.")

    def copiar_con(self, **cambios):
        """Crea una configuración nueva modificando campos seleccionados.

        Parámetros:
            **cambios: Pares nombre=valor que reemplazan los parámetros
                indicados; los demás conservan sus valores originales.

        Devuelve:
            Configuracion: Nuevo objeto con los cambios solicitados,
            sujeto a la validación del constructor.

        Excepciones:
            ValueError: Si algún valor no supera validar().
            TypeError: Si se indica un nombre de parámetro no admitido.

        Ejemplo:
            nueva = original.copiar_con(n_agentes=250, semilla=23)

        Notas:
            No se modifica la configuración original.
        """
        valores = self.__dict__.copy()
        valores.update(cambios)
        return Configuracion(**valores)
