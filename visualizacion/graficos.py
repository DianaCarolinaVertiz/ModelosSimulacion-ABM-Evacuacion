"""Gráficos ofrecidos por la cátedra: vista del recinto, curvas y mapas.

Pueden importarse directamente desde un notebook. No ejecutan el modelo.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import PowerNorm
from matplotlib.path import Path
from matplotlib.patches import Rectangle

COLOR_ACTIVACION_BAJA = "#197AB0"
COLOR_ACTIVACION_ALTA = "#E6A34A"
COLOR_PARED = "#354655"
COLOR_SALIDA = "#199D85"
COLOR_FONDO = "#F0F4F4"


def _crear_marcador_persona():
    """Crea una silueta vectorial para representar personas.

    Devuelve:
        matplotlib.path.Path: Contorno con cabeza, cuerpo y extremidades.
    """
    poligonos = []
    angulos = np.linspace(0, 2 * np.pi, 13)
    poligonos.append([(0.19 * np.cos(a), 0.48 + 0.19 * np.sin(a)) for a in angulos])
    poligonos.append([(-0.22, 0.22), (0.22, 0.22), (0.19, -0.18), (-0.19, -0.18)])
    poligonos.append([(-0.21, 0.18), (-0.38, -0.22), (-0.29, -0.27), (-0.10, 0.05)])
    poligonos.append([(0.21, 0.18), (0.38, -0.22), (0.29, -0.27), (0.10, 0.05)])
    poligonos.append([(-0.18, -0.16), (-0.02, -0.16), (-0.07, -0.55), (-0.25, -0.55)])
    poligonos.append([(0.02, -0.16), (0.18, -0.16), (0.25, -0.55), (0.07, -0.55)])
    vertices = []
    codigos = []
    for poligono in poligonos:
        vertices.extend(poligono + [poligono[0]])
        codigos.extend([Path.MOVETO] + [Path.LINETO] * (len(poligono) - 1) + [Path.CLOSEPOLY])
    return Path(vertices, codigos)


MARCADOR_PERSONA = _crear_marcador_persona()


def _base_recinto(ax, entorno, titulo):
    """Dibuja la geometría del recinto en unos ejes existentes.

    Parámetros:
        ax (matplotlib.axes.Axes): Ejes a modificar.
        entorno (Entorno): Recinto con paredes, salidas y fuentes.
        titulo (str): Título de la figura.

    Devuelve:
        None: Agrega elementos gráficos a los ejes.
    """
    alto, ancho = entorno.paredes.shape
    colores = np.zeros((alto, ancho, 3))
    colores[:] = (0.94, 0.96, 0.96)
    colores[entorno.paredes] = (0.21, 0.27, 0.33)
    ax.imshow(colores, origin="lower", interpolation="nearest", extent=(-0.5, ancho - 0.5, -0.5, alto - 0.5))
    for x, y in entorno.salidas:
        ax.add_patch(Rectangle((x - 0.48, y - 0.48), 0.96, 0.96, color=COLOR_SALIDA, zorder=4))
    for x, y in entorno.fuentes:
        if entorno.configuracion.usar_humo:
            ax.plot(x, y, marker="x", color="#C64C34", markersize=7, markeredgewidth=2, zorder=8)
    ax.set_xlim(-2, ancho + 1)
    ax.set_ylim(-1.5, alto + 1)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for borde in ax.spines.values():
        borde.set_visible(False)
    ax.set_facecolor(COLOR_FONDO)
    ax.text(-1.1, 7.5, "SALIDA\nIZQ.", ha="center", va="center", fontsize=8, color=COLOR_SALIDA, rotation=90, weight="bold")
    ax.text(ancho - 0.1, 16.5, "SALIDA\nDER.", ha="center", va="center", fontsize=8, color=COLOR_SALIDA, rotation=270, weight="bold")
    ax.set_title(titulo, fontsize=14, weight="bold", color="#21394A", loc="left", pad=15)


def _separar_tipos(posiciones):
    """Agrupa las posiciones de agentes según su activación.

    Parámetros:
        posiciones (iterable[tuple[int, int, str]]): Tripletas
            (x, y, tipo), donde tipo es "alta" o "baja".

    Devuelve:
        tuple[list, list]: Posiciones (x, y) de activación baja
        y de activación alta, respectivamente.
    """
    baja = [(x, y) for x, y, tipo in posiciones if tipo == "baja"]
    alta = [(x, y) for x, y, tipo in posiciones if tipo == "alta"]
    return baja, alta


def _dibujar_personas(ax, posiciones):
    """Dibuja los agentes presentes en el recinto.

    Parámetros:
        ax (matplotlib.axes.Axes): Ejes en los que se dibuja.
        posiciones (iterable[tuple[int, int, str]]): Posiciones
            (x, y, tipo) de los agentes.

    Devuelve:
        None: Agrega marcadores a los ejes existentes.
    """
    baja, alta = _separar_tipos(posiciones)
    for grupo, color, etiqueta in ((baja, COLOR_ACTIVACION_BAJA, "Activación baja"), (alta, COLOR_ACTIVACION_ALTA, "Activación alta")):
        if grupo:
            xs, ys = zip(*grupo)
            ax.scatter(xs, ys, s=74, c=color, marker=MARCADOR_PERSONA, edgecolors="#FFFFFF", linewidths=0.35, zorder=9, label=etiqueta)


def _humo_sobre_plano(ax, campo_humo):
    """Superpone la concentración de humo al gráfico del recinto.

    Parámetros:
        ax (matplotlib.axes.Axes): Ejes a modificar.
        campo_humo (numpy.ndarray): Matriz de concentraciones [y, x].

    Devuelve:
        None: Agrega una capa gráfica transparente.
    """
    transparencia = np.clip(campo_humo * 1.75, 0, 0.78)
    ax.imshow(campo_humo, origin="lower", cmap="magma", vmin=0, vmax=1, interpolation="bilinear", alpha=transparencia, zorder=3)


def mostrar_estado(simulacion, indice_fotograma=-1, tamaño=(13, 7)):
    """Muestra un fotograma con personas, humo e indicadores.

    Parámetros:
        simulacion (Simulacion): Simulación con fotogramas.
        indice_fotograma (int): Fotograma a mostrar; -1 es el último.
        tamaño (tuple[float, float]): Tamaño de la figura en pulgadas.

    Devuelve:
        matplotlib.figure.Figure: Figura con plano y panel numérico.
    """
    fotograma = simulacion.fotogramas[indice_fotograma]
    fig = plt.figure(figsize=tamaño, facecolor="#FFFFFF")
    ax = fig.add_axes((0.04, 0.16, 0.73, 0.72))
    panel = fig.add_axes((0.79, 0.17, 0.19, 0.68))
    panel.axis("off")
    _base_recinto(ax, simulacion.entorno, "EVACUACIÓN  /  MODELO BASADO EN AGENTES")
    _humo_sobre_plano(ax, fotograma["humo"])
    _dibujar_personas(ax, fotograma["posiciones"])
    panel.text(0, 0.94, f"PASO {fotograma['paso']:03d}", fontsize=14, weight="bold", color="#284456")
    panel.text(0, 0.80, "EN EL RECINTO", fontsize=9, color="#607585")
    panel.text(0, 0.72, f"{fotograma['restantes']}", fontsize=30, weight="bold", color="#1C3851")
    panel.text(0, 0.56, "SALIDA IZQUIERDA", fontsize=9, color="#607585")
    panel.text(0, 0.49, f"{fotograma['izquierda']}", fontsize=22, color=COLOR_SALIDA, weight="bold")
    panel.text(0, 0.34, "SALIDA DERECHA", fontsize=9, color="#607585")
    panel.text(0, 0.27, f"{fotograma['derecha']}", fontsize=22, color=COLOR_SALIDA, weight="bold")
    panel.text(0, 0.07, "Azul: baja  ·  Ocre: alta\nRojo: foco de humo", fontsize=9, color="#607585")
    fig.text(0.05, 0.07, "Unidades de simulación · representación conceptual, no una simulación validada de evacuaciones reales", fontsize=9, color="#647987")
    return fig


def graficar_curvas_evacuacion(simulaciones, etiquetas=None):
    """Dibuja la evolución temporal de la fracción evacuada.

    Parámetros:
        simulaciones (Simulacion | list[Simulacion]): Una o varias
            simulaciones para comparar.
        etiquetas (list[str] | None): Leyendas; por defecto, esquema
            de actualización de cada simulación.

    Devuelve:
        matplotlib.figure.Figure: Curvas de evacuación por paso.
    """
    if not isinstance(simulaciones, list):
        simulaciones = [simulaciones]
    if etiquetas is None:
        etiquetas = [sim.configuracion.actualizacion for sim in simulaciones]
    fig, ax = plt.subplots(figsize=(10, 4.8))
    for simulacion, etiqueta in zip(simulaciones, etiquetas):
        tiempos = [fila["paso"] for fila in simulacion.historial]
        evacuados = [fila["fraccion_evacuada"] for fila in simulacion.historial]
        ax.plot(tiempos, evacuados, linewidth=2.5, label=etiqueta)
    ax.set(title="Evolución de la evacuación", xlabel="Paso de simulación", ylabel="Fracción evacuada")
    ax.grid(alpha=0.17)
    ax.legend(frameon=False)
    fig.tight_layout()
    return fig


def graficar_ocupacion_acumulada(simulacion):
    """Representa los pasos acumulados de ocupación de cada celda.

    Parámetros:
        simulacion (Simulacion): Objeto con ocupacion_acumulada.

    Devuelve:
        matplotlib.figure.Figure: Mapa de calor del tiempo ocupado.

    Notas:
        Permanencia no equivale necesariamente a flujo de personas.
    """
    valores = simulacion.ocupacion_acumulada.astype(float)
    valores = np.ma.masked_where(simulacion.entorno.paredes, valores)
    maximo = max(1.0, float(valores.max()))
    fig, ax = plt.subplots(figsize=(12, 6.5))
    _base_recinto(ax, simulacion.entorno, "MAPA DE OCUPACIÓN ACUMULADA")
    imagen = ax.imshow(valores, origin="lower", cmap="YlOrRd", norm=PowerNorm(gamma=0.62, vmin=0, vmax=maximo), interpolation="nearest", alpha=0.85, zorder=2)
    for x, y in simulacion.entorno.salidas:
        ax.add_patch(Rectangle((x - 0.5, y - 0.5), 1, 1, color=COLOR_SALIDA, zorder=4))
    fig.colorbar(imagen, ax=ax, fraction=0.024, pad=0.02, label="Pasos con la celda ocupada")
    fig.text(0.05, 0.03, "El valor suma ocupación durante toda la trayectoria temporal; no mide directamente velocidad ni flujo.", fontsize=9, color="#617889")
    return fig


def graficar_campos(simulacion):
    """Representa las matrices actuales de humo y distancias BFS.

    Parámetros:
        simulacion (Simulacion): Simulación con entorno y humo.

    Devuelve:
        matplotlib.figure.Figure: Dos paneles, humo y distancias.
    """
    distancias = simulacion.entorno.calcular_distancias()
    campo = np.ma.masked_where(distancias < 0, distancias)
    fig, ejes = plt.subplots(1, 2, figsize=(13, 5))
    a = ejes[0].imshow(simulacion.entorno.humo, origin="lower", cmap="magma", vmin=0, vmax=1)
    ejes[0].set_title("Humo H(x, y, t)")
    fig.colorbar(a, ax=ejes[0], shrink=0.72)
    b = ejes[1].imshow(campo, origin="lower", cmap="viridis_r")
    ejes[1].set_title("Distancia BFS a una salida")
    fig.colorbar(b, ax=ejes[1], shrink=0.72)
    for ax in ejes:
        ax.contour(simulacion.entorno.paredes.astype(int), levels=[0.5], colors="#B7C1C5", linewidths=0.75, origin="lower")
        ax.set_xticks([])
        ax.set_yticks([])
    fig.tight_layout()
    return fig


def mostrar_escenario(entorno, agentes=None):
    """Muestra el recinto y, opcionalmente, la población.

    Parámetros:
        entorno (Entorno): Recinto que se dibujará.
        agentes (list[Agente] | None): Personas no evacuadas a mostrar;
            si es None, se dibuja el recinto sin personas.

    Devuelve:
        matplotlib.figure.Figure: Figura del escenario.

    Notas:
        No necesita ejecutar propagación de humo ni simulación.
    """
    if agentes is None:
        agentes = []
    posiciones = [(agente.x, agente.y, agente.tipo) for agente in agentes if not agente.evacuado]
    fig, ax = plt.subplots(figsize=(12, 6.5))
    _base_recinto(ax, entorno, "RECINTO Y POBLACIÓN INICIAL")
    _dibujar_personas(ax, posiciones)
    if posiciones:
        ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.07), frameon=False, ncol=2)
    fig.tight_layout()
    return fig


def mostrar_humo(entorno):
    """Muestra el campo actual de concentración de humo.

    Parámetros:
        entorno (Entorno): Recinto con el campo de humo.

    Devuelve:
        matplotlib.figure.Figure: Mapa de humo normalizado.
    """
    fig, ax = plt.subplots(figsize=(11, 5.5))
    _base_recinto(ax, entorno, "CONCENTRACIÓN DE HUMO")
    imagen = ax.imshow(entorno.humo, origin="lower", cmap="magma", vmin=0, vmax=1, alpha=0.78, interpolation="nearest", zorder=2)
    fig.colorbar(imagen, ax=ax, fraction=0.025, pad=0.02, label="Concentración normalizada")
    fig.tight_layout()
    return fig


def mostrar_distancias(entorno, distancias=None):
    """Dibuja el campo BFS de distancias a las salidas.

    Parámetros:
        entorno (Entorno): Recinto utilizado en la visualización.
        distancias (numpy.ndarray | None): Campo BFS [y, x]; si es
            None se calcula nuevamente desde el entorno.

    Devuelve:
        matplotlib.figure.Figure: Gráfico de distancias con las
        celdas de valor -1 ocultas.
    """
    if distancias is None:
        distancias = entorno.calcular_distancias()
    visibles = np.ma.masked_where(distancias < 0, distancias)
    fig, ax = plt.subplots(figsize=(11, 5.5))
    _base_recinto(ax, entorno, "CAMPO DE DISTANCIAS HACIA LAS SALIDAS")
    imagen = ax.imshow(visibles, origin="lower", cmap="viridis_r", interpolation="nearest", alpha=0.83, zorder=2)
    fig.colorbar(imagen, ax=ax, fraction=0.025, pad=0.02, label="Movimientos mínimos")
    fig.tight_layout()
    return fig
