"""Carga y tinte de los iconos Lucide usados por la interfaz.

Los PNG se descargan en ``assets/icons/png`` con trazo negro y fondo
transparente. Aquí se tiñen al color exacto de cada sección y se cachean
para no reconstruir la imagen en cada repintado.
"""

from functools import lru_cache
import os

import customtkinter as ctk
from PIL import Image

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ICONOS_DIR = os.path.join(BASE_DIR, "assets", "icons", "png")

# Colores de la paleta institucional usados por los iconos.
VERDE = "#1D6F23"
VERDE_OSCURO = "#14532D"
BRONCE = "#A3723E"
AZUL = "#2B7BB9"
GRIS = "#6B7280"
GRIS_OSCURO = "#374151"
TINTA = "#1F2937"
BLANCO = "#F7F5EF"
ROJO = "#B03A2E"


def _color_rgba(color):
    color = color.lstrip("#")
    if len(color) == 3:
        color = "".join(caracter * 2 for caracter in color)
    return tuple(int(color[indice:indice + 2], 16) for indice in (0, 2, 4)) + (255,)


@lru_cache(maxsize=1024)
def _imagen_icono(nombre, color, tamano):
    """Devuelve una imagen PIL cuadrada, tintada y con transparencia."""
    ruta = os.path.join(ICONOS_DIR, f"{nombre}.png")
    if not os.path.isfile(ruta):
        return None

    original = Image.open(ruta).convert("RGBA")
    alpha = original.getchannel("A")
    solida = Image.new("RGBA", original.size, _color_rgba(color))
    solida.putalpha(alpha)
    return solida.resize((int(tamano), int(tamano)), Image.Resampling.LANCZOS)


@lru_cache(maxsize=1024)
def icono(nombre, tamano=18, color=GRIS_OSCURO):
    """Devuelve un ``CTkImage`` listo para usar en labels y botones.

    Si el archivo no existe devuelve ``None`` para que la interfaz pueda
    seguir funcionando aunque falte un asset.
    """
    imagen = _imagen_icono(nombre, color, int(tamano))
    if imagen is None:
        return None
    return ctk.CTkImage(light_image=imagen, dark_image=imagen, size=(int(tamano), int(tamano)))


def icono_existe(nombre):
    return os.path.isfile(os.path.join(ICONOS_DIR, f"{nombre}.png"))


def icono_en_label(label, nombre, tamano=16, color=GRIS_OSCURO):
    """Aplica un icono a un CTkLabel existente conservando su texto."""
    imagen = icono(nombre, tamano, color)
    if imagen is not None:
        label.configure(image=imagen, compound="left")


def icono_en_boton(boton, nombre, tamano=16, color=GRIS_OSCURO):
    """Aplica un icono a un CTkButton existente conservando su texto."""
    imagen = icono(nombre, tamano, color)
    if imagen is not None:
        boton.configure(image=imagen, compound="left")
