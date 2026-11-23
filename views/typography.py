"""Sistema tipográfico de la aplicación.

Sigue la lógica de Apple: una sola familia humanista con varios pesos y un
tamaño óptico para los títulos grandes. La familia es **Inter**, la
alternativa libre más cercana a SF Pro; se carga de forma privada desde
``assets/fonts`` para no instalar nada en el sistema.

- ``Inter``              → cuerpo, formularios, botones y navegación.
- ``Inter SemiBold``     → títulos, etiquetas y énfasis.
- ``Inter Display``      → bienvenida y cifras grandes (tamaño óptico).
- ``Cascadia Mono``      → datos tabulares: IDs, usuarios y horas.

Si las fuentes no están disponibles, se usa el sistema de Windows como
respaldo. Los tamaños están pensados para pantallas de 1366x768 en adelante.
"""

import ctypes
import os
from pathlib import Path

import customtkinter as ctk


_BASE_DIR = Path(__file__).resolve().parent.parent
_FUENTES_DIR = _BASE_DIR / "assets" / "fonts"
_FR_PRIVATE = 0x10

_FUENTES_INTER = (
    "Inter-Regular.ttf",
    "Inter-Medium.ttf",
    "Inter-SemiBold.ttf",
    "Inter-Bold.ttf",
    "InterDisplay-SemiBold.ttf",
    "InterDisplay-Bold.ttf",
)


def _registrar_fuentes():
    """Carga Inter solo para este proceso; devuelve True si lo logra."""
    if os.name != "nt":
        return False

    cargadas = 0
    try:
        for nombre in _FUENTES_INTER:
            ruta = _FUENTES_DIR / nombre
            if not ruta.exists():
                return False
            if ctypes.windll.gdi32.AddFontResourceExW(str(ruta), _FR_PRIVATE, 0):
                cargadas += 1
    except Exception:
        return False
    return cargadas == len(_FUENTES_INTER)


_INTER_DISPONIBLE = _registrar_fuentes()

if _INTER_DISPONIBLE:
    FAMILIA_UI = "Inter"
    FAMILIA_TITULOS = "Inter SemiBold"
    FAMILIA_DATOS = "Cascadia Mono"
    FAMILIA_NUMEROS = "Inter SemiBold"
    FAMILIA_DISPLAY = "Inter Display"
else:  # Respaldo: fuentes del sistema con una jerarquía equivalente.
    FAMILIA_UI = "Segoe UI Variable Text"
    FAMILIA_TITULOS = "Segoe UI Semibold"
    FAMILIA_DATOS = "Consolas"
    FAMILIA_NUMEROS = "Segoe UI Semibold"
    FAMILIA_DISPLAY = "Segoe UI Variable Display"

# Alias histórico para código que aún importa FAMILIA.
FAMILIA = FAMILIA_UI

PESO_NORMAL = "normal"
PESO_FUERTE = "bold"


def _tupla(familia, tamano, estilo=PESO_NORMAL):
    if not estilo or estilo == PESO_NORMAL:
        return (familia, int(tamano))
    return (familia, int(tamano), estilo)


def fuente(tamano=12, estilo=PESO_NORMAL):
    """Fuente de interfaz para cuerpo, formularios y controles."""
    return _tupla(FAMILIA_UI, tamano, estilo)


def fuente_titulo(tamano=16, estilo=PESO_NORMAL):
    """Títulos y énfasis; la familia ya es semibold."""
    return _tupla(FAMILIA_TITULOS, tamano, estilo)


def fuente_dato(tamano=10, estilo=PESO_NORMAL):
    """Datos tabulares (IDs, usuarios, horas) en monoespaciada."""
    return _tupla(FAMILIA_DATOS, tamano, estilo)


def fuente_numero(tamano=24, estilo=PESO_NORMAL):
    """Cifras de KPI con el tamaño óptico de los títulos."""
    return _tupla(FAMILIA_NUMEROS, tamano, estilo)


def fuente_display(tamano=24, estilo=PESO_NORMAL):
    """Acento editorial para bienvenida y calendario."""
    return _tupla(FAMILIA_DISPLAY, tamano, estilo)


def fuente_etiqueta(tamano=10):
    """Etiquetas cortas: secciones, formularios y badges."""
    return (FAMILIA_TITULOS, int(tamano))


def fuente_ctk(tamano=12, estilo=PESO_NORMAL):
    """Igual que `fuente`, pero como CTkFont (permite ajustes dinámicos)."""
    if estilo == PESO_FUERTE:
        return ctk.CTkFont(family=FAMILIA_UI, size=int(tamano), weight="bold")
    if estilo == "italic":
        return ctk.CTkFont(family=FAMILIA_UI, size=int(tamano), slant="italic")
    if estilo == "underline":
        return ctk.CTkFont(family=FAMILIA_UI, size=int(tamano), underline=True)
    return ctk.CTkFont(family=FAMILIA_UI, size=int(tamano))
