"""Indicador circular de carga para operaciones breves.

Se dibuja sobre un ``Canvas`` de Tkinter para controlar por completo el
trazo: una pista tenue, un arco bronce giratorio y dos puntos que suavizan
los extremos. La animación solo corre mientras el overlay está visible.
"""

import math
import tkinter

import customtkinter as ctk

from views.typography import fuente, fuente_etiqueta, fuente_titulo


class OverlayCarga(ctk.CTkFrame):
    """Overlay opaco con spinner circular y mensaje de estado."""

    def __init__(
        self,
        master,
        color_fondo="#213629",
        color_pista="#2E4A39",
        color_arco="#C48A4C",
        texto="Validando credenciales",
        subtitulo="Verificando tus datos de acceso",
        corner_radius=22,
        **kwargs,
    ):
        kwargs.setdefault("fg_color", color_fondo)
        kwargs.setdefault("corner_radius", corner_radius)
        super().__init__(master, **kwargs)

        self._color_fondo = color_fondo
        self._color_pista = color_pista
        self._color_arco = color_arco
        self._activo = False
        self._anim_id = None
        self._angulo = 0.0

        self._lado = max(38, round(self._apply_widget_scaling(54)))
        self._grosor = max(3, round(self._apply_widget_scaling(4)))
        margen = self._grosor + round(self._apply_widget_scaling(2))
        self._margen = margen

        self._canvas = tkinter.Canvas(
            self,
            width=self._lado,
            height=self._lado,
            bg=color_fondo,
            highlightthickness=0,
            bd=0,
        )
        self._canvas.place(relx=0.5, rely=0.42, anchor="center")

        self._pista = self._canvas.create_oval(
            margen,
            margen,
            self._lado - margen,
            self._lado - margen,
            outline=color_pista,
            width=self._grosor,
        )
        self._arco = self._canvas.create_arc(
            margen,
            margen,
            self._lado - margen,
            self._lado - margen,
            start=90,
            extent=104,
            style="arc",
            outline=color_arco,
            width=self._grosor,
        )
        self._punta = self._canvas.create_oval(
            0, 0, 0, 0, fill=color_arco, outline=color_arco
        )
        self._cola = self._canvas.create_oval(
            0, 0, 0, 0, fill=color_arco, outline=color_arco
        )

        ctk.CTkLabel(
            self,
            text="ACCESO AL SISTEMA",
            font=fuente_etiqueta(8),
            text_color=color_arco,
        ).place(relx=0.5, rely=0.26, anchor="center")

        self._lbl_texto = ctk.CTkLabel(
            self,
            text=texto,
            font=fuente_titulo(14),
            text_color="#F7F5EF",
        )
        self._lbl_texto.place(relx=0.5, rely=0.61, anchor="center")

        self._lbl_subtitulo = ctk.CTkLabel(
            self,
            text=subtitulo,
            font=fuente(10),
            text_color="#A0B0A5",
        )
        self._lbl_subtitulo.place(relx=0.5, rely=0.67, anchor="center")

        self._pintar_arco(0.0)

    # ------------------------------------------------------------------
    # Control de visibilidad
    # ------------------------------------------------------------------
    def iniciar(self):
        """Muestra el overlay y arranca la rotación."""
        if self._activo:
            return
        self._activo = True
        self.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)
        self.lift()
        self._angulo = 0.0
        self._pintar_arco(self._angulo)
        self._animar()

    def detener(self):
        """Oculta el overlay y detiene por completo la animación."""
        self._activo = False
        if self._anim_id is not None:
            try:
                self.after_cancel(self._anim_id)
            except Exception:
                pass
            self._anim_id = None
        try:
            self.place_forget()
        except Exception:
            pass

    def destroy(self):
        self.detener()
        super().destroy()

    # ------------------------------------------------------------------
    # Animación
    # ------------------------------------------------------------------
    def _pintar_arco(self, angulo):
        inicio = (90 - angulo) % 360
        self._canvas.itemconfigure(self._arco, start=inicio)

        centro = self._lado / 2.0
        radio = centro - self._margen
        punto = max(1.6, self._grosor * 0.62)

        for item, desfase in ((self._punta, 0.0), (self._cola, 104.0)):
            theta = math.radians(inicio + desfase)
            x = centro + radio * math.cos(theta)
            y = centro - radio * math.sin(theta)
            self._canvas.coords(item, x - punto, y - punto, x + punto, y + punto)

    def _animar(self):
        self._anim_id = None
        if not self._activo:
            return
        try:
            if not self.winfo_exists():
                return
            self._angulo = (self._angulo + 4.5) % 360.0
            self._pintar_arco(self._angulo)
        except tkinter.TclError:
            return
        self._anim_id = self.after(16, self._animar)
