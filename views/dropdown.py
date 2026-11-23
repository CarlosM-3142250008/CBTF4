"""Lista desplegable propia, con despliegue animado hacia abajo.

Sustituye a ``CTkOptionMenu`` conservando su API básica (``get``, ``set``,
``configure(values=...)`` y ``cget('values')``) para no tocar los
controladores existentes. El panel se dibuja dentro de la ventana, no en un
``Toplevel``, para que las esquinas y el borde se vean limpios.
"""

import customtkinter as ctk

from views.icons import GRIS_OSCURO, TINTA, VERDE, icono
from views.typography import fuente


class Dropdown(ctk.CTkFrame):
    """Selector de una sola opción con lista animada."""

    def __init__(
        self,
        master,
        values=None,
        command=None,
        width=200,
        height=34,
        font=None,
        dropdown_font=None,
        fg_color="#FFFFFF",
        hover_color="#F6F9F7",
        border_color="#DDE4DF",
        text_color=TINTA,
        dropdown_fg_color="#FFFFFF",
        dropdown_text_color="#1F2937",
        dropdown_hover_color="#F1F6F2",
        corner_radius=12,
        selected_color="#EAF4EC",
        selected_text_color=VERDE,
        placeholder="Selecciona una opción",
        **kwargs,
    ):
        kwargs.pop("button_color", None)
        kwargs.pop("button_hover_color", None)
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)

        self._values = [str(valor) for valor in (values or [placeholder])]
        self._value = self._values[0]
        self._command = command
        self._placeholder = placeholder
        self._width = width
        self._height = height
        self._font = font or fuente(11)
        self._dropdown_font = dropdown_font or fuente(10)
        self._fg_color = fg_color
        self._hover_color = hover_color
        self._border_color = border_color
        self._text_color = text_color
        self._dropdown_fg_color = dropdown_fg_color
        self._dropdown_text_color = dropdown_text_color
        self._dropdown_hover_color = dropdown_hover_color
        self._selected_color = selected_color
        self._selected_text_color = selected_text_color
        self._corner_radius = corner_radius

        self._popup = None
        self._abierto = False
        self._anim_id = None
        self._bind_click = None
        self._bind_escape = None
        self._bind_config = None

        self._chevron_abajo = icono("chevron-down", 15, GRIS_OSCURO)
        self._chevron_arriba = icono("chevron-up", 15, GRIS_OSCURO)

        self._boton = ctk.CTkButton(
            self,
            text=self._texto_visible(),
            image=self._chevron_abajo,
            compound="right",
            anchor="w",
            width=width,
            height=height,
            corner_radius=corner_radius,
            border_width=1,
            border_color=border_color,
            fg_color=fg_color,
            hover_color=hover_color,
            text_color=text_color,
            font=self._font,
            command=self._alternar,
        )
        self._boton.pack(fill="x", expand=True)

    # ------------------------------------------------------------------
    # API compatible con CTkOptionMenu
    # ------------------------------------------------------------------
    def get(self):
        return self._value

    def set(self, valor):
        valor = str(valor)
        self._value = valor
        if valor not in self._values:
            self._values.append(valor)
        self._boton.configure(text=self._texto_visible())
        if self._abierto:
            self._cerrar()

    def configure(self, **kwargs):
        if "values" in kwargs:
            valores = [str(valor) for valor in (kwargs.pop("values") or [])]
            if valores:
                self._values = valores
                if self._value not in self._values:
                    self._value = self._values[0]
                self._boton.configure(text=self._texto_visible())
            if self._abierto:
                self._cerrar()

        if "command" in kwargs:
            self._command = kwargs.pop("command")

        if "state" in kwargs:
            estado = kwargs.pop("state")
            self._boton.configure(state=estado)

        if "text_color" in kwargs:
            self._text_color = kwargs.pop("text_color")
            self._boton.configure(text_color=self._text_color)

        if "values" in kwargs:
            kwargs.pop("values")

        if not kwargs:
            return None
        return super().configure(**kwargs)

    def cget(self, key):
        if key == "values":
            return list(self._values)
        if key == "value":
            return self._value
        return super().cget(key)

    # ------------------------------------------------------------------
    # Apertura y cierre
    # ------------------------------------------------------------------
    def _texto_visible(self):
        return self._value if self._value else self._placeholder

    def _alternar(self):
        if self._abierto:
            self._cerrar()
        else:
            self._abrir()

    def _abrir(self):
        if self._abierto or not self._values:
            return
        try:
            if not self.winfo_exists() or self.winfo_width() <= 1:
                return
        except Exception:
            return

        root = self.winfo_toplevel()
        ancho = max(self.winfo_width(), self._px(self._width))
        x = self.winfo_rootx() - root.winfo_rootx()
        y_trigger = self.winfo_rooty() - root.winfo_rooty()
        alto_trigger = self.winfo_height()
        separacion = self._px(4)

        fila = self._px(38)
        relleno = self._px(8)
        alto_total = len(self._values) * fila + relleno * 2
        alto_max = self._px(304)
        necesita_scroll = alto_total > alto_max
        alto_objetivo = min(alto_total, alto_max)

        root_ancho = root.winfo_width()
        root_alto = root.winfo_height()
        x = max(self._px(6), min(x, root_ancho - ancho - self._px(6)))

        espacio_abajo = root_alto - (y_trigger + alto_trigger + separacion) - self._px(6)
        espacio_arriba = y_trigger - separacion - self._px(6)
        abrir_arriba = False

        if alto_objetivo > espacio_abajo and espacio_arriba > espacio_abajo:
            abrir_arriba = True
            alto_objetivo = min(alto_objetivo, espacio_arriba)
        else:
            alto_objetivo = min(alto_objetivo, espacio_abajo)

        alto_objetivo = max(self._px(58), alto_objetivo)
        if abrir_arriba:
            y = y_trigger - alto_objetivo - separacion
        else:
            y = y_trigger + alto_trigger + separacion
        y = max(self._px(4), y)

        popup = ctk.CTkFrame(
            root,
            width=self._logical(ancho),
            height=1,
            fg_color=self._dropdown_fg_color,
            corner_radius=14,
            border_width=1,
            border_color="#DCE4DF",
        )
        # Sin propagación, el panel conserva el ancho del disparador y la
        # altura que marca la animación (los hijos no lo encogen).
        popup.pack_propagate(False)
        popup.place(x=self._logical(x), y=self._logical(y))
        popup.lift()

        if necesita_scroll or alto_total > alto_objetivo:
            lista = ctk.CTkScrollableFrame(
                popup,
                fg_color="transparent",
                corner_radius=0,
                scrollbar_button_color="#D7E1DA",
                scrollbar_button_hover_color="#C2D1C7",
            )
            lista.pack(fill="both", expand=True, padx=4, pady=4)
        else:
            lista = ctk.CTkFrame(popup, fg_color="transparent")
            lista.pack(fill="both", expand=True, padx=4, pady=4)

        for valor in self._values:
            seleccionado = valor == self._value
            boton = ctk.CTkButton(
                lista,
                text=valor,
                anchor="w",
                height=34,
                corner_radius=10,
                fg_color=self._selected_color if seleccionado else "transparent",
                hover_color=self._dropdown_hover_color,
                text_color=(
                    self._selected_text_color if seleccionado
                    else self._dropdown_text_color
                ),
                font=self._dropdown_font,
                command=lambda v=valor: self._seleccionar(v),
            )
            boton.pack(fill="x", padx=self._px(2), pady=1)

        self._popup = popup
        self._abierto = True
        self._boton.configure(image=self._chevron_arriba)
        self._instalar_bindings(root)
        self._animar_apertura(alto_objetivo)

    def _animar_apertura(self, alto_objetivo):
        pasos = 13
        self._cancelar_animacion()

        def paso(indice=1):
            self._anim_id = None
            if not self._abierto or self._popup is None:
                return
            try:
                if not self._popup.winfo_exists():
                    return
            except Exception:
                return

            t = min(1.0, indice / pasos)
            suave = 1.0 - (1.0 - t) ** 3
            alto = max(1, round(alto_objetivo * suave))
            try:
                self._popup.configure(height=self._logical(alto))
            except Exception:
                return
            if indice < pasos:
                self._anim_id = self.after(14, lambda: paso(indice + 1))

        paso(1)

    def _seleccionar(self, valor):
        self._value = valor
        self._boton.configure(text=self._texto_visible())
        self._cerrar()
        if callable(self._command):
            try:
                self._command(valor)
            except Exception:
                pass

    def _cerrar(self, destruir=True):
        self._cancelar_animacion()
        self._quitar_bindings()
        self._abierto = False

        popup = self._popup
        self._popup = None
        if popup is not None and destruir:
            try:
                popup.destroy()
            except Exception:
                pass

        try:
            self._boton.configure(image=self._chevron_abajo)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Eventos
    # ------------------------------------------------------------------
    def _instalar_bindings(self, root):
        self._quitar_bindings()
        self._bind_click = root.bind("<Button-1>", self._click_fuera, add="+")
        self._bind_escape = root.bind(
            "<Escape>", lambda _evento: self._cerrar(), add="+"
        )
        self._bind_config = root.bind("<Configure>", self._al_configurar, add="+")

    def _quitar_bindings(self):
        root = None
        try:
            root = self.winfo_toplevel()
        except Exception:
            return
        for secuencia, identificador in (
            ("<Button-1>", self._bind_click),
            ("<Escape>", self._bind_escape),
            ("<Configure>", self._bind_config),
        ):
            if identificador is None:
                continue
            try:
                root.unbind(secuencia, identificador)
            except Exception:
                pass
        self._bind_click = None
        self._bind_escape = None
        self._bind_config = None

    def _click_fuera(self, evento):
        if not self._abierto:
            return
        if self._es_descendiente(evento.widget, self._popup):
            return
        if self._es_descendiente(evento.widget, self):
            return
        self._cerrar()

    def _al_configurar(self, evento):
        if not self._abierto:
            return
        if evento.widget is not self.winfo_toplevel():
            return
        self._cerrar()

    @staticmethod
    def _es_descendiente(widget, ancestro):
        if widget is None or ancestro is None:
            return False
        actual = widget
        for _ in range(12):
            if actual is ancestro:
                return True
            actual = getattr(actual, "master", None)
            if actual is None:
                break
        return False

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------
    def _px(self, valor):
        try:
            return round(self._apply_widget_scaling(valor))
        except Exception:
            return int(valor)

    def _logical(self, valor):
        """Convierte píxeles físicos a unidades lógicas de CustomTkinter."""
        try:
            return round(self._reverse_widget_scaling(valor))
        except Exception:
            return int(valor)

    def _cancelar_animacion(self):
        if self._anim_id is not None:
            try:
                self.after_cancel(self._anim_id)
            except Exception:
                pass
            self._anim_id = None

    def destroy(self):
        self._cerrar()
        super().destroy()
