"""Animación Matplotlib compatible con VS Code y Jupyter."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from IPython.display import HTML
from .graficos import _base_recinto, MARCADOR_PERSONA, COLOR_ACTIVACION_BAJA, COLOR_ACTIVACION_ALTA


def crear_animacion(simulacion, intervalo_ms=100):
    """Construye una animación a partir de fotogramas registrados.

    Parámetros:
        simulacion (Simulacion): Simulación con fotogramas almacenados.
        intervalo_ms (int): Intervalo entre cuadros en milisegundos.

    Devuelve:
        matplotlib.animation.FuncAnimation: Animación creada.

    Notas:
        No ejecuta nuevos pasos del modelo; conserve una referencia.
    """
    fig, ax = plt.subplots(figsize=(11, 7))
    fig.patch.set_facecolor("#FFFFFF")
    _base_recinto(ax, simulacion.entorno, "EVACUACIÓN  /  EVOLUCIÓN TEMPORAL")
    inicial = simulacion.fotogramas[0]
    capa_humo = ax.imshow(inicial["humo"], origin="lower", cmap="magma", vmin=0, vmax=1, interpolation="bilinear", alpha=np.zeros_like(inicial["humo"]), zorder=3)
    agentes_activacion_baja = ax.scatter([], [], s=75, c=COLOR_ACTIVACION_BAJA, marker=MARCADOR_PERSONA, edgecolors="white", linewidths=0.25, zorder=9, label="Activación baja")
    agentes_activacion_alta = ax.scatter([], [], s=75, c=COLOR_ACTIVACION_ALTA, marker=MARCADOR_PERSONA, edgecolors="white", linewidths=0.25, zorder=9, label="Activación alta")
    contador = ax.text(0.02, 0.97, "", transform=ax.transAxes, va="top", fontsize=10, color="#24445C", bbox={"facecolor": "white", "alpha": 0.92, "edgecolor": "none", "boxstyle": "round,pad=0.5"})
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.08), frameon=False, ncol=2)

    def cambiar_fotograma(indice):
        """Actualiza los artistas correspondientes al cuadro seleccionado.

        Parámetros:
            indice (int): Índice del fotograma (desde cero).

        Devuelve:
            tuple: Capa de humo, marcadores y texto actualizados.
        """
        fotograma = simulacion.fotogramas[indice]
        humo = fotograma["humo"]
        capa_humo.set_data(humo)
        capa_humo.set_alpha(np.clip(humo * 1.75, 0, 0.78))
        posiciones_activacion_baja = [(x, y) for x, y, tipo in fotograma["posiciones"] if tipo == "baja"]
        posiciones_activacion_alta = [(x, y) for x, y, tipo in fotograma["posiciones"] if tipo == "alta"]
        agentes_activacion_baja.set_offsets(np.array(posiciones_activacion_baja).reshape(-1, 2))
        agentes_activacion_alta.set_offsets(np.array(posiciones_activacion_alta).reshape(-1, 2))
        contador.set_text(f"Paso {fotograma['paso']}   ·   Restantes: {fotograma['restantes']}   ·   Salidas: {fotograma['izquierda']} / {fotograma['derecha']}")
        return capa_humo, agentes_activacion_baja, agentes_activacion_alta, contador

    animacion = FuncAnimation(fig, cambiar_fotograma, frames=len(simulacion.fotogramas), interval=intervalo_ms, blit=False, repeat=False)
    plt.close(fig)  # En Jupyter, mostrar solo la animación, sin figura estática adicional.
    return animacion


def mostrar_en_notebook(simulacion, intervalo_ms=100):
    """Prepara la animación para su presentación en Jupyter.

    Parámetros:
        simulacion (Simulacion): Simulación con fotogramas.
        intervalo_ms (int): Intervalo entre cuadros en milisegundos.

    Devuelve:
        IPython.display.HTML: Animación en formato HTML.
    """
    animacion = crear_animacion(simulacion, intervalo_ms)
    return HTML(animacion.to_jshtml())

