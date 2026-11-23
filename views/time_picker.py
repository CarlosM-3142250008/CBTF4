"""Selector de hora interactivo en formato de 24 horas."""

from datetime import datetime

import customtkinter as ctk

from views.icons import GRIS_OSCURO, icono
from views.typography import (
    fuente,
    fuente_dato,
    fuente_etiqueta,
    fuente_numero,
    fuente_titulo,
)


COLOR_PRIMARIO = "#1D6F23"
COLOR_PRIMARIO_HOVER = "#15531A"
COLOR_CAJA = "#F0F4F1"
COLOR_CAJA_HOVER = "#E3ECE6"
COLOR_BORDE = "#CCCCCC"
COLOR_TEXTO = "#111827"
COLOR_TEXTO_SUAVE = "#6B7280"
COLOR_FONDO_POPUP = "#FFFFFF"


def _parse_hora(valor):
    """Convierte un texto 'HH:MM' en una tupla (hora, minuto)."""
    try:
        partes = str(valor).strip().split(":")
        hora = int(partes[0])
        minuto = int(partes[1]) if len(partes) > 1 else 0
        if 0 <= hora <= 23 and 0 <= minuto <= 59:
            return hora, minuto
    except (ValueError, TypeError, IndexError):
        pass
    return 10, 0


class TimePicker(ctk.CTkFrame):
    """Caja interactiva que permite elegir una hora en formato 24 h."""

    def __init__(self, parent, initial="10:00", **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(parent, **kwargs)

        self._hora, self._minuto = _parse_hora(initial)
        self._popup = None

        self._caja = ctk.CTkFrame(
            self,
            fg_color=COLOR_CAJA,
            corner_radius=10,
            border_width=0,
            border_color=COLOR_BORDE,
            height=32,
        )
        self._caja.pack(fill="x", expand=True)
        self._caja.pack_propagate(False)
        self._caja.grid_columnconfigure(1, weight=1)

        self._lbl_icono = ctk.CTkLabel(
            self._caja,
            text="",
            image=icono("clock-3", 15, COLOR_PRIMARIO),
            width=24,
            fg_color="transparent",
        )
        self._lbl_icono.grid(row=0, column=0, padx=(9, 0))

        self._lbl_valor = ctk.CTkLabel(
            self._caja,
            text=self.get(),
            font=fuente_numero(13),
            text_color=COLOR_TEXTO,
            anchor="w",
            fg_color="transparent",
        )
        self._lbl_valor.grid(row=0, column=1, sticky="w", padx=(2, 0))

        self._lbl_flecha = ctk.CTkLabel(
            self._caja,
            text="",
            image=icono("chevron-down", 13, GRIS_OSCURO),
            width=20,
            fg_color="transparent",
        )
        self._lbl_flecha.grid(row=0, column=2, padx=(0, 8))

        for widget in (self._caja, self._lbl_icono, self._lbl_valor, self._lbl_flecha):
            widget.bind("<Button-1>", lambda _evento: self.abrir_popup())
            widget.bind("<Enter>", self._al_entrar)
            widget.bind("<Leave>", self._al_salir)
            try:
                widget.configure(cursor="hand2")
            except Exception:
                pass

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------
    def get(self):
        """Devuelve la hora seleccionada como texto HH:MM."""
        return f"{self._hora:02d}:{self._minuto:02d}"

    def set(self, valor):
        """Establece la hora mostrada. Si el texto no es válido, usa 10:00."""
        self._hora, self._minuto = _parse_hora(valor)
        self._lbl_valor.configure(text=self.get())

    # ------------------------------------------------------------------
    # Efectos visuales
    # ------------------------------------------------------------------
    def _al_entrar(self, _evento=None):
        self._caja.configure(fg_color=COLOR_CAJA_HOVER, border_color=COLOR_PRIMARIO)

    def _al_salir(self, _evento=None):
        self._caja.configure(fg_color=COLOR_CAJA, border_color=COLOR_BORDE)

    # ------------------------------------------------------------------
    # Popup de selección
    # ------------------------------------------------------------------
    def abrir_popup(self):
        if self._popup is not None:
            try:
                if self._popup.winfo_exists():
                    self._popup.lift()
                    self._popup.focus_force()
                    return
            except Exception:
                pass
            self._popup = None

        popup = ctk.CTkToplevel(self)
        self._popup = popup
        popup.title("Seleccionar hora")
        popup.resizable(False, False)
        popup.configure(fg_color=COLOR_FONDO_POPUP)
        popup.transient(self.winfo_toplevel())
        popup.attributes("-topmost", True)
        try:
            # Barra de título compacta: solo el botón de cerrar.
            popup.attributes("-toolwindow", True)
        except Exception:
            pass
        popup.protocol("WM_DELETE_WINDOW", self._cerrar_popup)
        popup.bind("<Escape>", lambda _evento: self._cerrar_popup())

        ancho, alto = 360, 450
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height() + 6
        x = max(8, min(x, popup.winfo_screenwidth() - ancho - 8))
        y = max(8, min(y, popup.winfo_screenheight() - alto - 60))
        popup.geometry(f"{ancho}x{alto}+{x}+{y}")

        contenedor = ctk.CTkFrame(popup, fg_color=COLOR_FONDO_POPUP, corner_radius=16)
        contenedor.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            contenedor,
            text="  Seleccionar hora",
            image=icono("clock-3", 17, COLOR_PRIMARIO),
            compound="left",
            font=fuente_titulo(16),
            text_color=COLOR_TEXTO,
        ).pack(anchor="w", padx=16, pady=(10, 0))

        ctk.CTkLabel(
            contenedor,
            text="Formato de 24 horas",
            font=fuente(10),
            text_color=COLOR_TEXTO_SUAVE,
        ).pack(anchor="w", padx=16)

        preview = ctk.CTkFrame(contenedor, fg_color=COLOR_CAJA, corner_radius=12)
        preview.pack(fill="x", padx=16, pady=(10, 8))

        lbl_preview = ctk.CTkLabel(
            preview,
            text=self.get(),
            font=fuente_numero(30),
            text_color=COLOR_PRIMARIO,
        )
        lbl_preview.pack(pady=5)

        columnas = ctk.CTkFrame(contenedor, fg_color="transparent")
        columnas.pack(fill="both", expand=True, padx=12)
        columnas.grid_columnconfigure((0, 1), weight=1)
        columnas.grid_rowconfigure(0, weight=1)

        seleccion = {"hora": self._hora, "minuto": self._minuto}
        botones_hora = {}
        botones_minuto = {}

        def actualizar_estilos():
            for valor, boton in botones_hora.items():
                es_seleccionado = valor == seleccion["hora"]
                boton.configure(
                    fg_color=COLOR_PRIMARIO if es_seleccionado else "transparent",
                    hover_color=COLOR_PRIMARIO_HOVER if es_seleccionado else COLOR_CAJA,
                    text_color="#FFFFFF" if es_seleccionado else COLOR_TEXTO,
                    font=fuente_dato(11, "bold" if es_seleccionado else "normal"),
                )
            for valor, boton in botones_minuto.items():
                es_seleccionado = valor == seleccion["minuto"]
                boton.configure(
                    fg_color=COLOR_PRIMARIO if es_seleccionado else "transparent",
                    hover_color=COLOR_PRIMARIO_HOVER if es_seleccionado else COLOR_CAJA,
                    text_color="#FFFFFF" if es_seleccionado else COLOR_TEXTO,
                    font=fuente_dato(11, "bold" if es_seleccionado else "normal"),
                )
            lbl_preview.configure(text=f"{seleccion['hora']:02d}:{seleccion['minuto']:02d}")

        def crear_columna(columna, titulo, valores, botones, clave):
            marco = ctk.CTkFrame(columnas, fg_color="transparent")
            marco.grid(row=0, column=columna, padx=4, sticky="nsew")

            ctk.CTkLabel(
                marco,
                text=titulo,
                font=fuente_etiqueta(9),
                text_color=COLOR_TEXTO_SUAVE,
            ).pack(anchor="w", padx=6, pady=(0, 3))

            scroll = ctk.CTkScrollableFrame(
                marco,
                fg_color="#FAFBFC",
                corner_radius=10,
                width=130,
                height=190,
            )
            scroll.pack(fill="both", expand=True, padx=2)

            for valor in valores:
                boton = ctk.CTkButton(
                    scroll,
                    text=f"{valor:02d}",
                    width=100,
                    height=27,
                    corner_radius=8,
                    fg_color="transparent",
                    hover_color=COLOR_CAJA,
                    text_color=COLOR_TEXTO,
                    font=fuente_dato(11),
                    command=lambda v=valor: seleccionar(clave, v),
                )
                boton.pack(pady=1, padx=4)
                botones[valor] = boton

            return scroll

        def seleccionar(clave, valor):
            seleccion[clave] = valor
            actualizar_estilos()

        def desplazar(scroll, valores, valor):
            try:
                indice = valores.index(valor)
                scroll.update_idletasks()
                scroll._parent_canvas.yview_moveto(max(0.0, (indice - 2) / max(len(valores), 1)))
            except Exception:
                pass

        horas = list(range(24))
        minutos = list(range(60))
        scroll_horas = crear_columna(0, "HORA", horas, botones_hora, "hora")
        scroll_minutos = crear_columna(1, "MINUTO", minutos, botones_minuto, "minuto")
        actualizar_estilos()

        popup.after(
            120,
            lambda: (
                desplazar(scroll_horas, horas, seleccion["hora"]),
                desplazar(scroll_minutos, minutos, seleccion["minuto"]),
            ),
        )

        footer = ctk.CTkFrame(contenedor, fg_color="transparent")
        footer.pack(fill="x", padx=16, pady=(10, 10))

        def usar_ahora():
            ahora = datetime.now()
            seleccion["hora"] = ahora.hour
            seleccion["minuto"] = ahora.minute
            actualizar_estilos()
            desplazar(scroll_horas, horas, ahora.hour)
            desplazar(scroll_minutos, minutos, ahora.minute)

        def confirmar():
            self._hora = seleccion["hora"]
            self._minuto = seleccion["minuto"]
            self._lbl_valor.configure(text=self.get())
            self._cerrar_popup()

        ctk.CTkButton(
            footer,
            text="Ahora",
            width=76,
            height=32,
            corner_radius=10,
            fg_color="transparent",
            hover_color=COLOR_CAJA,
            border_width=0,
            border_color=COLOR_BORDE,
            text_color=COLOR_TEXTO,
            font=fuente_titulo(10),
            command=usar_ahora,
        ).pack(side="left")

        btn_aceptar = ctk.CTkButton(
            footer,
            text="Aceptar",
            width=90,
            height=32,
            corner_radius=10,
            fg_color=COLOR_PRIMARIO,
            hover_color=COLOR_PRIMARIO_HOVER,
            text_color="white",
            font=fuente_titulo(10),
            command=confirmar,
        )
        btn_aceptar.pack(side="right")

        ctk.CTkButton(
            footer,
            text="Cancelar",
            width=80,
            height=32,
            corner_radius=10,
            fg_color="transparent",
            hover_color=COLOR_CAJA,
            text_color=COLOR_TEXTO_SUAVE,
            font=fuente(10),
            command=self._cerrar_popup,
        ).pack(side="right", padx=(0, 6))

        def activar_popup():
            try:
                popup.lift()
                popup.focus_force()
                popup.grab_set()
                btn_aceptar.focus_set()
            except Exception:
                pass

        popup.after(80, activar_popup)

    def _cerrar_popup(self):
        if self._popup is not None:
            try:
                self._popup.grab_release()
            except Exception:
                pass
            try:
                self._popup.destroy()
            except Exception:
                pass
            self._popup = None
