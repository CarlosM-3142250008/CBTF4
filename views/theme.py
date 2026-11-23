"""Tema global de la aplicación.

CustomTkinter dibuja los bordes como polígonos y Tkinter no aplica
antialiasing, por eso un borde de 1-2 px con esquinas redondeadas se ve
como "dientes de sierra". La estrategia es eliminar los bordes duros y
separar los bloques por color de fondo, que se dibuja limpio.
"""

import customtkinter as ctk

from views.typography import FAMILIA


COLOR_FONDO_APP = "#F4F6F8"
COLOR_SUPERFICIE = "#FFFFFF"
COLOR_SUPERFICIE_SUAVE = "#F5F7F5"


def aplicar_tema():
    """Debe llamarse antes de crear la primera ventana."""
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")

    tema = ctk.ThemeManager.theme

    # Sin bordes en los widgets que más se notaban con aliasing.
    for nombre in (
        "CTkEntry",
        "CTkTextbox",
        "CTkSegmentedButton",
        "CTkOptionMenu",
        "CTkComboBox",
        "CTkButton",
        "CTkFrame",
    ):
        if nombre in tema:
            tema[nombre]["border_width"] = 0

    # Radios generosos, al estilo de las superficies de macOS/iOS. Los
    # controles pequeños (checkbox, radio, switch) conservan su forma.
    radios = {
        "CTkFrame": 14,
        "CTkButton": 12,
        "CTkEntry": 10,
        "CTkTextbox": 12,
        "CTkOptionMenu": 10,
        "CTkComboBox": 10,
        "CTkSegmentedButton": 10,
    }
    for nombre, radio in radios.items():
        if nombre in tema:
            tema[nombre]["corner_radius"] = radio

    # Fuente base para cualquier widget que no especifique una.
    if "CTkFont" in tema:
        for plataforma in ("Windows", "Linux", "macOS"):
            if plataforma in tema["CTkFont"]:
                tema["CTkFont"][plataforma]["family"] = FAMILIA
        tema["CTkFont"]["family"] = FAMILIA

    # Scrollbars discretas acordes a la paleta clara.
    if "CTkScrollbar" in tema:
        tema["CTkScrollbar"]["button_color"] = "#C9D3CC"
        tema["CTkScrollbar"]["button_hover_color"] = "#A9B7AD"
