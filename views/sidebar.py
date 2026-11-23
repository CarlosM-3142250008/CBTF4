"""Barra lateral institucional con indicador deslizante.

La animación se dispara únicamente al seleccionar un módulo (click): un
riel bronce se desplaza hasta el elemento activo. El color de los botones
se aplica una sola vez por clic, no en cada frame, para que el movimiento
no compita con el repintado de cinco widgets de CustomTkinter.

El riel se coloca fuera del área del botón para no depender de la
transparencia de CustomTkinter, que dibuja el fondo del propio widget.
"""

import math
import os
import time
import tkinter

import customtkinter as ctk
from PIL import Image, ImageEnhance

from views.icons import icono
from views.typography import (
    FAMILIA_TITULOS,
    FAMILIA_UI,
    fuente_display,
    fuente_etiqueta,
)


COLOR_FONDO = "#14532D"
# El estado activo usa bronce: no se confunde con el hover verde.
COLOR_FONDO_ACTIVO = "#8A5A2E"
COLOR_HOVER = "#1C6A3B"
COLOR_ACTIVO_HOVER = "#9A6634"
COLOR_BORDE = "#0D3B20"
COLOR_LINEA = "#2A7A45"
COLOR_RIEL = "#F2D7AE"
COLOR_TEXTO = "#F7F5EF"
COLOR_TEXTO_INACTIVO = "#D8E7DD"
COLOR_TEXTO_SUAVE = "#9CC0A6"
COLOR_SALIR = "#8B3A3A"
COLOR_SALIR_HOVER = "#9C4646"

ANCHO = 224
MARGEN_LATERAL = 16
ALTO_BASE = 44
SEPARACION = 6
TAMANO_BASE = 12
TOPE_NAV = 148

RIEL_X = 6
RIEL_ANCHO = 4
RIEL_ALTO = 22

# El logo se agranda con frames precalculados: durante el hover no se
# redimensiona ninguna imagen, así el efecto nunca se siente trabado.
LOGO_BASE = 82
LOGO_MAX = 94
LOGO_CENTRO_Y = 60
LOGO_DURACION = 0.18

DURACION = 0.26          # segundos
DURACION_PULSO = 0.22
INTERVALO = 16           # ~60 fps


class Sidebar(ctk.CTkFrame):
    """Barra lateral con navegación y selección animada por click."""

    def __init__(self, master, **kwargs):
        kwargs.setdefault("width", ANCHO)
        kwargs.setdefault("corner_radius", 0)
        kwargs.setdefault("fg_color", COLOR_FONDO)
        super().__init__(master, **kwargs)

        self.grid_propagate(False)

        self._items = {}
        self._orden = []
        self._visibles = []
        self._cache_geo = {}

        self._activo = None
        self._anim_id = None
        self._anim_inicio = 0.0
        self._anim_duracion = 0.0
        self._riel_y = 0.0
        self._riel_alto = 0.0
        self._riel_desde = (0.0, 0.0)
        self._riel_hasta = (0.0, 0.0)
        self._pulso = False
        self._destruido = False

        # Logo: callback de navegación y estado de la animación fisheye.
        self._logo = None
        self._logo_frames = {}
        self._logo_tamano = LOGO_BASE
        self._logo_anim_id = None
        self._logo_inicio = 0.0
        self._logo_desde = float(LOGO_BASE)
        self._logo_hasta = float(LOGO_BASE)
        self._logo_encima = False
        self.accion_logo = None

        self._crear_logo()
        self._crear_navegacion()
        self._crear_logout()

        self._linea_borde = ctk.CTkFrame(
            self, width=1, corner_radius=0, fg_color=COLOR_BORDE
        )
        self._linea_borde.place(relx=1.0, rely=0.0, anchor="ne", relheight=1.0)

        # `CTkFrame.bind` redirige al canvas interno; para el tamaño real del
        # frame hay que enlazar el evento en el propio widget Tk.
        tkinter.Frame.bind(self, "<Configure>", self._al_redimensionar, add="+")
        tkinter.Frame.bind(self, "<Destroy>", self._al_destruir, add="+")

        self.after_idle(lambda: self._aplicar_layout(forzar=True))

    # ------------------------------------------------------------------
    # Construcción
    # ------------------------------------------------------------------
    def _crear_logo(self):
        self._base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        # Contenedor fijo: el frame interno cambia de tamaño sin mover el
        # punto de anclaje, así el fisheye se siente estable.
        self._logo = ctk.CTkLabel(
            self,
            text="",
            width=LOGO_MAX,
            height=LOGO_MAX,
            fg_color="transparent",
            cursor="hand2",
        )
        self._logo.place(relx=0.5, y=LOGO_CENTRO_Y, anchor="center")

        try:
            ruta_logo = os.path.join(self._base_dir, "assets", "logo_CBTF.png")
            if not os.path.exists(ruta_logo):
                raise FileNotFoundError("Logo no encontrado")

            original = Image.open(ruta_logo).convert("RGBA")
            iluminado = ImageEnhance.Brightness(original).enhance(1.07)

            # Todos los tamaños posibles se generan una sola vez al iniciar.
            for tamano in range(LOGO_BASE, LOGO_MAX + 1):
                normal = original.resize((tamano, tamano), Image.Resampling.LANCZOS)
                brillo = iluminado.resize((tamano, tamano), Image.Resampling.LANCZOS)
                self._logo_frames[tamano] = {
                    False: ctk.CTkImage(
                        light_image=normal, dark_image=normal, size=(tamano, tamano)
                    ),
                    True: ctk.CTkImage(
                        light_image=brillo, dark_image=brillo, size=(tamano, tamano)
                    ),
                }

            self._logo_tamano = LOGO_BASE
            self._logo.configure(image=self._logo_frames[LOGO_BASE][False])
        except Exception:
            self._logo.configure(
                text="CBTF\n#4",
                font=fuente_display(17, "bold"),
                text_color=COLOR_TEXTO,
                justify="center",
            )

        self._logo.bind("<Enter>", self._logo_entrar)
        self._logo.bind("<Leave>", self._logo_salir)
        self._logo.bind("<Button-1>", self._logo_click)

        # Separador y etiqueta de sección: estructura visual sin recargar.
        linea = ctk.CTkFrame(self, height=1, corner_radius=0, fg_color=COLOR_LINEA)
        linea.place(x=22, y=114, relwidth=0.58)

        ctk.CTkLabel(
            self,
            text="MENÚ PRINCIPAL",
            font=fuente_etiqueta(9),
            text_color=COLOR_TEXTO_SUAVE,
            anchor="w",
        ).place(x=22, y=123, anchor="nw")

    # ------------------------------------------------------------------
    # Logo interactivo
    # ------------------------------------------------------------------
    def establecer_accion_logo(self, comando):
        """Define qué ocurre al hacer click en el logo (volver al panel)."""
        self.accion_logo = comando

    def _logo_click(self, evento=None):
        if callable(self.accion_logo):
            self.accion_logo()
        return "break"

    def _logo_entrar(self, evento=None):
        self._logo_encima = True
        self._animar_logo(LOGO_MAX)

    def _logo_salir(self, evento=None):
        self._logo_encima = False
        self._animar_logo(LOGO_BASE)

    def _animar_logo(self, destino):
        if self._destruido or not self.winfo_exists():
            return
        self._cancelar_logo()
        self._logo_desde = float(self._logo_tamano)
        self._logo_hasta = float(destino)
        self._logo_inicio = time.perf_counter()
        self._logo_anim_id = self.after(0, self._paso_logo)

    def _cancelar_logo(self):
        if self._logo_anim_id is not None:
            try:
                self.after_cancel(self._logo_anim_id)
            except Exception:
                pass
            self._logo_anim_id = None

    def _aplicar_frame_logo(self, tamano):
        if not self._logo_frames:
            return
        tamano = max(LOGO_BASE, min(LOGO_MAX, int(tamano)))
        self._logo.configure(image=self._logo_frames[tamano][self._logo_encima])
        self._logo_tamano = tamano

    def _paso_logo(self):
        self._logo_anim_id = None
        if self._destruido or not self.winfo_exists():
            return

        t = (time.perf_counter() - self._logo_inicio) / LOGO_DURACION
        if t >= 1.0:
            t = 1.0
        # Salida suave; el tamaño final se fija exacto para evitar temblores.
        e = 1.0 - (1.0 - t) ** 3
        tamano = self._logo_desde + (self._logo_hasta - self._logo_desde) * e
        self._aplicar_frame_logo(round(tamano))

        if t < 1.0:
            self._logo_anim_id = self.after(INTERVALO, self._paso_logo)
        else:
            self._aplicar_frame_logo(round(self._logo_hasta))

    def _crear_navegacion(self):
        definiciones = [
            ("dashboard", "layout-dashboard", "Panel Principal"),
            ("convocatorias", "calendar-days", "Convocatorias"),
            ("materiales", "folder-open", "Avisos y Materiales"),
            ("asistencia", "clipboard-check", "Control Asistencia"),
            ("usuarios", "users-round", "Gestión Usuarios"),
        ]

        # El riel se crea antes que los botones y queda en el margen izquierdo,
        # así nunca compite con el fondo que dibuja cada CTkButton.
        self._riel = ctk.CTkFrame(
            self,
            width=RIEL_ANCHO,
            height=RIEL_ALTO,
            corner_radius=2,
            fg_color=COLOR_RIEL,
        )

        fuente_boton = ctk.CTkFont(family=FAMILIA_TITULOS, size=TAMANO_BASE)

        for clave, nombre_icono, texto in definiciones:
            imagen_normal = icono(nombre_icono, 17, COLOR_TEXTO_INACTIVO)
            imagen_activa = icono(nombre_icono, 17, COLOR_TEXTO)
            boton = ctk.CTkButton(
                self,
                text="  " + texto,
                image=imagen_normal,
                compound="left",
                anchor="w",
                width=ANCHO - 2 * MARGEN_LATERAL,
                height=ALTO_BASE,
                corner_radius=12,
                border_width=0,
                fg_color=COLOR_FONDO,
                hover_color=COLOR_HOVER,
                text_color=COLOR_TEXTO_INACTIVO,
                font=fuente_boton,
            )
            boton.place(x=MARGEN_LATERAL, y=TOPE_NAV)

            self._items[clave] = {
                "boton": boton,
                "visible": True,
                "icono_normal": imagen_normal,
                "icono_activo": imagen_activa,
            }
            self._orden.append(clave)

        self.btn_nav_dashboard = self._items["dashboard"]["boton"]
        self.btn_nav_convocatorias = self._items["convocatorias"]["boton"]
        self.btn_nav_materiales = self._items["materiales"]["boton"]
        self.btn_nav_asistencia = self._items["asistencia"]["boton"]
        self.btn_nav_usuarios = self._items["usuarios"]["boton"]

    def _crear_logout(self):
        self._font_logout = ctk.CTkFont(
            family=FAMILIA_UI, size=11, weight="bold"
        )

        linea_pie = ctk.CTkFrame(
            self, height=1, corner_radius=0, fg_color=COLOR_LINEA
        )
        linea_pie.place(relx=0.5, rely=1.0, y=-68, anchor="s", relwidth=0.72)

        self.btn_logout = ctk.CTkButton(
            self,
            text="  Cerrar sesión",
            image=icono("log-out", 16, COLOR_TEXTO),
            compound="left",
            anchor="w",
            width=ANCHO - 2 * MARGEN_LATERAL,
            height=36,
            corner_radius=12,
            border_width=0,
            fg_color=COLOR_SALIR,
            hover_color=COLOR_SALIR_HOVER,
            text_color=COLOR_TEXTO,
            font=self._font_logout,
        )
        self.btn_logout.place(relx=0.5, rely=1.0, y=-16, anchor="s")

    # ------------------------------------------------------------------
    # API para el controlador
    # ------------------------------------------------------------------
    def marcar_activo(self, clave):
        """Mueve el riel al módulo elegido y actualiza el estado activo."""
        if clave not in self._items or not self._items[clave]["visible"]:
            clave = None

        if clave == self._activo:
            if clave is not None and self._cache_geo:
                self._pulsar_riel()
            return

        anterior = self._activo
        self._activo = clave
        self._actualizar_texto_botones()

        objetivos = {}
        for nombre in self._items:
            if nombre == clave:
                objetivos[nombre] = (COLOR_FONDO_ACTIVO, COLOR_ACTIVO_HOVER)
            else:
                objetivos[nombre] = (COLOR_FONDO, COLOR_HOVER)

        # Antes de que la ventana tenga geometría real, el estado se aplica
        # sin animación; el layout posterior colocará el riel en su sitio.
        if not self._hay_geometria() or clave is None:
            self._aplicar_colores(objetivos)
            if clave is None:
                self._ocultar_riel()
            return

        self._iniciar_transicion(anterior, clave, objetivos)

    def set_visible(self, clave, visible):
        """Muestra u oculta un módulo (por ejemplo, Usuarios para docentes)."""
        item = self._items.get(clave)
        if item is None:
            return
        visible = bool(visible)
        if item["visible"] == visible:
            return

        item["visible"] = visible
        self._cancelar_animacion()

        if visible:
            item["boton"].place()
        else:
            item["boton"].place_forget()
            if self._activo == clave:
                self._activo = None
                self._actualizar_texto_botones()
                self._ocultar_riel()

        self._aplicar_layout(forzar=True)

    # ------------------------------------------------------------------
    # Geometría
    # ------------------------------------------------------------------
    def _px(self, valor):
        try:
            return round(self._apply_widget_scaling(valor))
        except Exception:
            return int(valor)

    def _hay_geometria(self):
        return self.winfo_width() > 1 and bool(self._cache_geo)

    def _aplicar_layout(self, forzar=False):
        if not self.winfo_exists():
            return
        # Antes de que la ventana se mapee, el ancho real es 1 y colocar los
        # botones con ese dato los dejaría fuera de sitio.
        if self.winfo_width() <= 1:
            return

        self._visibles = [k for k in self._orden if self._items[k]["visible"]]

        alto = self._px(ALTO_BASE)
        separacion = self._px(SEPARACION)
        tope = self._px(TOPE_NAV)
        margen = self._px(MARGEN_LATERAL)
        ancho = max(80, self.winfo_width() - 2 * margen)

        y = tope
        for clave in self._visibles:
            firma = (margen, y, ancho, alto)
            if forzar or self._cache_geo.get(clave) != firma:
                self._items[clave]["boton"].place_configure(
                    x=margen, y=y, width=ancho, height=alto
                )
                self._cache_geo[clave] = firma
            y += alto + separacion

        for clave in self._orden:
            if clave not in self._visibles:
                self._cache_geo.pop(clave, None)

        if self._anim_id is None:
            self._posicionar_riel_activo()

    # ------------------------------------------------------------------
    # Animación
    # ------------------------------------------------------------------
    def _aplicar_colores(self, objetivos):
        """Aplica el estado de los botones en un solo repintado."""
        for nombre, (fg, hover) in objetivos.items():
            item = self._items.get(nombre)
            if item is None:
                continue
            item["boton"].configure(fg_color=fg, hover_color=hover)

    def _actualizar_texto_botones(self):
        """El módulo activo usa texto blanco; el resto queda atenuado."""
        for nombre, item in self._items.items():
            activo = nombre == self._activo
            color = COLOR_TEXTO if activo else COLOR_TEXTO_INACTIVO
            item["boton"].configure(
                text_color=color,
                image=item["icono_activo"] if activo else item["icono_normal"],
            )

    def _posicionar_riel(self, y, alto):
        if alto <= 0.5 or not self.winfo_exists():
            self._riel.place_forget()
            return
        self._riel.place_configure(
            x=self._px(RIEL_X),
            y=round(y),
            width=self._px(RIEL_ANCHO),
            height=max(2, round(alto)),
        )

    def _posicionar_riel_activo(self):
        if self._activo is None or self._activo not in self._cache_geo:
            self._ocultar_riel()
            return
        _, y, _, h = self._cache_geo[self._activo]
        alto = self._px(RIEL_ALTO)
        self._riel_y = y + (h - alto) / 2.0
        self._riel_alto = float(alto)
        self._posicionar_riel(self._riel_y, self._riel_alto)

    def _ocultar_riel(self):
        self._riel_alto = 0.0
        self._riel.place_forget()

    def _iniciar_transicion(self, anterior, nuevo, objetivos):
        self._cancelar_animacion()

        # Los botones cambian de estado una sola vez. Animar sus colores
        # obligaba a repintar cinco widgets en cada frame y era la causa
        # del tirón; ahora solo se mueve el riel.
        self._aplicar_colores(objetivos)

        base_alto = self._px(RIEL_ALTO)
        if nuevo is not None:
            _, y, _, h = self._cache_geo[nuevo]
            destino = (y + (h - base_alto) / 2.0, float(base_alto))
        else:
            destino = (self._riel_y + self._riel_alto / 2.0, 0.0)

        if self._riel_alto <= 0.5 and nuevo is not None:
            origen = (destino[0] + base_alto / 2.0, 0.0)
        else:
            origen = (self._riel_y, self._riel_alto)

        self._riel_desde = origen
        self._riel_hasta = destino
        self._pulso = False
        self._anim_duracion = DURACION
        self._anim_inicio = time.perf_counter()
        self._anim_id = self.after(0, self._animar)

    def _pulsar_riel(self):
        """Pequeño pulso al volver a seleccionar el módulo ya activo."""
        if self._riel_alto <= 0.5:
            return
        self._cancelar_animacion()
        self._pulso = True
        self._riel_desde = (self._riel_y, self._riel_alto)
        self._riel_hasta = (self._riel_y, self._riel_alto)
        self._anim_duracion = DURACION_PULSO
        self._anim_inicio = time.perf_counter()
        self._anim_id = self.after(0, self._animar)

    def _cancelar_animacion(self):
        if self._anim_id is not None:
            try:
                self.after_cancel(self._anim_id)
            except Exception:
                pass
            self._anim_id = None

    def _animar(self):
        self._anim_id = None
        if self._destruido or not self.winfo_exists():
            return

        duracion = self._anim_duracion or DURACION
        t = (time.perf_counter() - self._anim_inicio) / duracion
        if t >= 1.0:
            t = 1.0
        # Curva de salida suave: rápida al inicio, precisa al final.
        e = 1.0 - (1.0 - t) ** 3

        y0, h0 = self._riel_desde
        y1, h1 = self._riel_hasta
        y = y0 + (y1 - y0) * e
        alto = h0 + (h1 - h0) * e

        if self._pulso:
            alto += 8.0 * math.sin(math.pi * t)
        elif h1 > 0 and abs(y1 - y0) > 2:
            # Estiramiento mínimo durante el recorrido, como una gota.
            alto += 5.0 * math.sin(math.pi * t)

        self._riel_y = y
        self._riel_alto = max(0.0, alto)
        self._posicionar_riel(self._riel_y, self._riel_alto)

        if t < 1.0:
            self._anim_id = self.after(INTERVALO, self._animar)
            return

        # Estado final exacto, sin residuos de interpolación.
        self._pulso = False
        self._riel_y = y1
        self._riel_alto = h1
        self._posicionar_riel(y1, h1)

    # ------------------------------------------------------------------
    # Eventos de ventana
    # ------------------------------------------------------------------
    def _al_redimensionar(self, evento):
        if evento.widget is not self:
            return
        self._cancelar_animacion()
        self._aplicar_layout(forzar=True)

    def _al_destruir(self, evento):
        if evento.widget is not self:
            return
        self._destruido = True
        self._cancelar_animacion()
        self._cancelar_logo()
