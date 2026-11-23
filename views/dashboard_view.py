import os
import customtkinter as ctk
from PIL import Image

from views.sidebar import Sidebar
from views.icons import GRIS_OSCURO, VERDE, icono
from views.skeleton import SkeletonLista
from views.typography import (
    fuente,
    fuente_dato,
    fuente_etiqueta,
    fuente_numero,
    fuente_titulo,
)
from views.ui_utils import (
    COLOR_BORDE,
    COLOR_NUEVO,
    COLOR_TEXTO,
    COLOR_TEXTO_SUAVE,
    crear_badge,
    crear_tarjeta_tinte,
    es_reciente,
    formatear_fecha_hora,
    paleta_tarjeta,
)


class DashboardView(ctk.CTkToplevel):
    """Panel principal como ventana secundaria de la raíz del login.

    El login permanece vivo pero oculto detrás, de modo que cerrar sesión
    solo destruye este panel y devuelve el control a la pantalla de acceso.
    """

    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

        self.title("CBTF No. 4 - Sistema de Gestión de Academias")
        self._configurar_tamano_ventana()

        # Cerrar con la X sí termina la aplicación completa.
        self.protocol("WM_DELETE_WINDOW", self._cerrar_aplicacion)

        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        # --- Configuración de Icono de Ventana ---
        try:
            ruta_icono = os.path.join(self.base_dir, "assets", "icono_ventana.png")
            if os.path.exists(ruta_icono):
                img_pil = Image.open(ruta_icono)
                try:
                    import ImageTk
                    img_tk = ImageTk.PhotoImage(img_pil)
                    self.iconphoto(img_tk)
                except ImportError:
                    self.iconphoto(img_pil)
        except Exception:
            pass

        # Configuración de Rejilla (Barra Lateral vs Contenido Principal)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)  # Barra Lateral
        self.grid_columnconfigure(1, weight=1)  # Contenido Principal

        # ==========================================
        # BARRA LATERAL (SIDEBAR)
        # ==========================================
        self.sidebar = Sidebar(self)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Alias para mantener compatibilidad con el controlador existente.
        self.sidebar_frame = self.sidebar
        self.btn_nav_dashboard = self.sidebar.btn_nav_dashboard
        self.btn_nav_convocatorias = self.sidebar.btn_nav_convocatorias
        self.btn_nav_materiales = self.sidebar.btn_nav_materiales
        self.btn_nav_asistencia = self.sidebar.btn_nav_asistencia
        self.btn_nav_usuarios = self.sidebar.btn_nav_usuarios
        self.btn_logout = self.sidebar.btn_logout

        # ==========================================
        # CONTENEDOR PRINCIPAL DERECHO (MAIN CONTAINER)
        # ==========================================
        self.main_container = ctk.CTkFrame(self, fg_color="#F4F6F8", corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # Encabezado (Header) Superior
        self.header_frame = ctk.CTkFrame(self.main_container, fg_color="white", height=65, corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew")

        self.lbl_titulo_header = ctk.CTkLabel(
            self.header_frame, text="  Panel Principal - Gestión de Academias",
            image=icono("layout-dashboard", 19, VERDE),
            compound="left",
            font=fuente_titulo(19), text_color="#1F2937"
        )
        self.lbl_titulo_header.pack(side="left", padx=25, pady=15)

        self.lbl_info_usuario = ctk.CTkLabel(
            self.header_frame, text="Cargando usuario...",
            image=icono("user-round", 14, GRIS_OSCURO),
            compound="left",
            font=fuente(11), text_color="#6B7280"
        )
        self.lbl_info_usuario.pack(side="right", padx=25, pady=15)

        # Área Principal Desplazable (Scrollable Content del Dashboard)
        self.scroll_content = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent")
        self.scroll_content.grid(row=1, column=0, sticky="nsew", padx=20, pady=15)
        self.scroll_content.grid_columnconfigure((0, 1, 2), weight=1)

        # Inicialización de las tarjetas e información en el Dashboard
        self.crear_seccion_kpis()
        self.crear_seccion_convocatorias()
        self.crear_seccion_avisos()

    def _configurar_tamano_ventana(self):
        """Ajusta el tamaño al monitor actual y centra la ventana.

        CustomTkinter recibe medidas en unidades de diseño y las multiplica
        por la escala DPI, por eso la pantalla se convierte antes de calcular.
        """
        try:
            escala = self._get_window_scaling()
        except Exception:
            escala = 1.0
        escala = escala or 1.0

        ancho_pantalla = int(self.winfo_screenwidth() / escala)
        alto_pantalla = int(self.winfo_screenheight() / escala)

        ancho = min(1160, max(900, ancho_pantalla - 32))
        alto = min(700, max(560, alto_pantalla - 72))

        self.minsize(min(1000, ancho), min(640, alto))

        ancho_fisico = round(ancho * escala)
        alto_fisico = round(alto * escala)
        x = max(0, (self.winfo_screenwidth() - ancho_fisico) // 2)
        y = max(0, (self.winfo_screenheight() - alto_fisico) // 2 - 40)
        self.geometry(f"{ancho}x{alto}+{x}+{y}")

    def aplicar_restricciones_sidebar(self, rol, es_jefe=None):
        """Aplica visibilidad por rol:

        - Docente: no ve Gestión de Usuarios.
        - Solo Jefe de Academia (rol 1) ve Control de Asistencia.
        """
        rol_normalizado = str(rol).strip().lower()
        es_docente = rol_normalizado == "docente"
        if es_jefe is None:
            es_jefe = rol_normalizado in ("jefe de academia", "administrador")

        self.sidebar.set_visible("usuarios", not es_docente)
        self.sidebar.set_visible("asistencia", bool(es_jefe))

    def marcar_nav(self, clave):
        """Resalta en la barra lateral el módulo que se está mostrando."""
        self.sidebar.marcar_activo(clave)

    def _crear_tarjeta_kpi(self, columna, etiqueta, color, tamano):
        """Tarjeta KPI con un riel de color que identifica su categoría."""
        tarjeta = ctk.CTkFrame(self.scroll_content, fg_color="white", corner_radius=14)
        tarjeta.grid(row=0, column=columna, padx=10, pady=10, sticky="ew")
        tarjeta.grid_columnconfigure(1, weight=1)

        riel = ctk.CTkFrame(
            tarjeta, width=3, height=1, corner_radius=2, fg_color=color
        )
        riel.grid(row=0, column=0, rowspan=2, sticky="ns", padx=(16, 0), pady=14)

        ctk.CTkLabel(
            tarjeta, text=etiqueta, font=fuente_etiqueta(9),
            text_color=COLOR_TEXTO_SUAVE, anchor="w"
        ).grid(row=0, column=1, sticky="w", padx=(10, 16), pady=(15, 0))

        valor = ctk.CTkLabel(
            tarjeta, text="--", font=fuente_numero(tamano),
            text_color=color, anchor="w"
        )
        valor.grid(row=1, column=1, sticky="w", padx=(10, 16), pady=(2, 14))

        icono_kpi = {
            0: "calendar-days",
            1: "megaphone",
            2: "clipboard-check",
        }.get(columna)
        if icono_kpi:
            ctk.CTkLabel(
                tarjeta, text="", width=38, height=38,
                image=icono(icono_kpi, 19, color),
                fg_color="#F4F7F5", corner_radius=12,
            ).grid(row=0, column=2, rowspan=2, padx=(0, 16), pady=14)

        return tarjeta, valor

    def crear_seccion_kpis(self):
        # Cada tarjeta conserva su color de categoría en el valor y en el riel.
        self.card1, self.lbl_kpi_sesion = self._crear_tarjeta_kpi(
            0, "PRÓXIMA SESIÓN", "#1D6F23", 21
        )
        self.card2, self.lbl_kpi_avisos = self._crear_tarjeta_kpi(
            1, "AVISOS / MATERIALES", "#A3723E", 21
        )
        self.card3, self.lbl_kpi_asistencia = self._crear_tarjeta_kpi(
            2, "PUNTUALIDAD GENERAL", "#2B7BB9", 23
        )

    def crear_seccion_convocatorias(self):
        self.frame_convocatorias = ctk.CTkFrame(self.scroll_content, fg_color="white", corner_radius=14)
        self.frame_convocatorias.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        header = ctk.CTkFrame(self.frame_convocatorias, fg_color="transparent")
        header.pack(fill="x", padx=18, pady=(14, 6))
        ctk.CTkLabel(
            header, text="AGENDA", font=fuente_etiqueta(8),
            text_color="#1D6F23"
        ).pack(anchor="w")
        ctk.CTkLabel(
            header, text="  Próximas Academias Convocadas",
            image=icono("calendar-days", 18, "#1D6F23"),
            compound="left",
            font=fuente_titulo(15), text_color="#1F2937"
        ).pack(anchor="w")

        self.container_lista_convocatorias = ctk.CTkFrame(self.frame_convocatorias, fg_color="transparent")
        self.container_lista_convocatorias.pack(fill="x", padx=18, pady=(0, 15))
        self.skeleton_convocatorias = SkeletonLista(
            self.container_lista_convocatorias, filas=2, tono="azul", compacto=True
        )

    def crear_seccion_avisos(self):
        self.frame_avisos = ctk.CTkFrame(self.scroll_content, fg_color="white", corner_radius=14)
        self.frame_avisos.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        header = ctk.CTkFrame(self.frame_avisos, fg_color="transparent")
        header.pack(fill="x", padx=18, pady=(14, 6))
        ctk.CTkLabel(
            header, text="COMUNICADOS", font=fuente_etiqueta(8),
            text_color="#A3723E"
        ).pack(anchor="w")
        ctk.CTkLabel(
            header, text="  Avisos Recientes",
            image=icono("megaphone", 18, "#A3723E"),
            compound="left",
            font=fuente_titulo(15), text_color="#1F2937"
        ).pack(anchor="w")

        self.container_lista_avisos = ctk.CTkFrame(self.frame_avisos, fg_color="transparent")
        self.container_lista_avisos.pack(fill="x", padx=18, pady=(0, 15))
        self.skeleton_avisos = SkeletonLista(
            self.container_lista_avisos, filas=2, tono="verde", compacto=True
        )

    def actualizar_titulo_header(self, texto, nombre_icono="layout-dashboard"):
        """Cambia el título del encabezado y su icono según el módulo activo."""
        self.lbl_titulo_header.configure(
            text=f"  {texto}",
            image=icono(nombre_icono, 19, VERDE),
        )

    def mostrar_cargando_panel(self):
        """Restaura los esqueletos de las listas del panel principal."""
        for contenedor, tono in (
            (self.container_lista_convocatorias, "azul"),
            (self.container_lista_avisos, "verde"),
        ):
            for widget in contenedor.winfo_children():
                widget.destroy()
            SkeletonLista(contenedor, filas=2, tono=tono, compacto=True)

    def actualizar_usuario_header(self, nombre, rol):
        self.lbl_info_usuario.configure(text=f"  {nombre} | {rol}")

    def actualizar_kpis(self, kpis):
        proxima = kpis.get("proxima_sesion")
        self.lbl_kpi_sesion.configure(
            text=formatear_fecha_hora(proxima) if proxima else "Sin programar"
        )
        self.lbl_kpi_avisos.configure(text=f"{kpis['avisos_pendientes']} Registrados")
        self.lbl_kpi_asistencia.configure(text=kpis["porcentaje_asistencia"])

    def mostrar_convocatorias(self, lista):
        for widget in self.container_lista_convocatorias.winfo_children():
            widget.destroy()

        if not lista:
            ctk.CTkLabel(
                self.container_lista_convocatorias,
                text="No hay convocatorias registradas.",
                font=fuente(11),
                text_color=COLOR_TEXTO_SUAVE
            ).pack(pady=10)
            return

        for conv in lista:
            es_nuevo = es_reciente(conv.get('fecha_publicacion'))
            paleta = paleta_tarjeta("azul")

            item_frame = crear_tarjeta_tinte(
                self.container_lista_convocatorias, "azul"
            )
            if es_nuevo:
                item_frame.configure(border_color=COLOR_NUEVO)
            item_frame.pack(fill="x", pady=5)

            top_line = ctk.CTkFrame(item_frame, fg_color="transparent")
            top_line.pack(fill="x", padx=12, pady=(8, 2))
            top_line.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                top_line,
                text="  " + conv['academia'],
                image=icono("school", 14, paleta["acento"]),
                compound="left",
                font=fuente_titulo(13),
                text_color="#1D6F23",
                anchor="w",
                justify="left",
                wraplength=400
            ).grid(row=0, column=0, sticky="w")

            color_tipo = "#A3723E" if conv['tipo'] == "Extraordinaria" else "#6B7280"
            crear_badge(
                top_line,
                conv['tipo'].upper(),
                color=color_tipo,
                ancho=110
            ).grid(row=0, column=1, padx=(8, 0), sticky="e")

            if es_nuevo:
                crear_badge(
                    top_line,
                    "NUEVO",
                    color=COLOR_NUEVO,
                    ancho=60
                ).grid(row=0, column=2, padx=(6, 0), sticky="e")

            ctk.CTkLabel(
                item_frame,
                text=f"  Sesión: {formatear_fecha_hora(conv.get('fecha_hora'))}",
                image=icono("calendar", 12, paleta["acento"]),
                compound="left",
                font=fuente_titulo(11),
                text_color=COLOR_TEXTO,
                anchor="w"
            ).pack(anchor="w", padx=12)

            ctk.CTkLabel(
                item_frame,
                text=f"  Publicado: {formatear_fecha_hora(conv.get('fecha_publicacion'))}",
                image=icono("clock-3", 11, GRIS_OSCURO),
                compound="left",
                font=fuente_dato(9),
                text_color=COLOR_TEXTO_SUAVE,
                anchor="w"
            ).pack(anchor="w", padx=12, pady=(0, 2))

            ctk.CTkLabel(
                item_frame,
                text=f"  Orden: {str(conv['orden_dia']).replace('\\n', chr(10))}",
                image=icono("list-filter", 12, GRIS_OSCURO),
                compound="left",
                font=fuente(11),
                text_color=COLOR_TEXTO_SUAVE,
                anchor="w",
                justify="left",
                wraplength=680
            ).pack(anchor="w", padx=12, pady=(0, 8))

    def mostrar_avisos(self, lista):
        for widget in self.container_lista_avisos.winfo_children():
            widget.destroy()

        if not lista:
            ctk.CTkLabel(
                self.container_lista_avisos,
                text="No hay avisos recientes.",
                font=fuente(11),
                text_color=COLOR_TEXTO_SUAVE
            ).pack(pady=10)
            return

        for aviso in lista:
            es_nuevo = es_reciente(aviso.get('fecha_publicacion'))
            paleta = paleta_tarjeta("verde")

            item_frame = crear_tarjeta_tinte(self.container_lista_avisos, "verde")
            if es_nuevo:
                item_frame.configure(border_color=COLOR_NUEVO)
            item_frame.pack(fill="x", pady=5)

            top_line = ctk.CTkFrame(item_frame, fg_color="transparent")
            top_line.pack(fill="x", padx=12, pady=(8, 2))
            top_line.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                top_line,
                text="  " + aviso['titulo'],
                image=icono("megaphone", 14, paleta["acento"]),
                compound="left",
                font=fuente_titulo(13),
                text_color="#1D6F23",
                anchor="w",
                justify="left",
                wraplength=500
            ).grid(row=0, column=0, sticky="w")

            if es_nuevo:
                crear_badge(
                    top_line,
                    "NUEVO",
                    color=COLOR_NUEVO,
                    ancho=60
                ).grid(row=0, column=1, padx=(6, 0), sticky="e")

            fecha_evento = formatear_fecha_hora(aviso.get('fecha_evento'), incluir_hora=False)
            ctk.CTkLabel(
                item_frame,
                text=f"  De: {aviso['emisor']}   |   Evento: {fecha_evento}",
                image=icono("user-round", 12, GRIS_OSCURO),
                compound="left",
                font=fuente(11),
                text_color=COLOR_TEXTO,
                anchor="w"
            ).pack(anchor="w", padx=12)

            ctk.CTkLabel(
                item_frame,
                text=f"  Publicado: {formatear_fecha_hora(aviso.get('fecha_publicacion'))}",
                image=icono("clock-3", 11, GRIS_OSCURO),
                compound="left",
                font=fuente_dato(9),
                text_color=COLOR_TEXTO_SUAVE,
                anchor="w"
            ).pack(anchor="w", padx=12, pady=(0, 2))

            ctk.CTkLabel(
                item_frame,
                text=aviso['detalle'],
                font=fuente(11),
                text_color=COLOR_TEXTO_SUAVE,
                anchor="w",
                justify="left",
                wraplength=680
            ).pack(anchor="w", padx=12, pady=(0, 8))

    def cambiar_vista_modulo(self, vista_widget):
        """Oculta completamente las vistas anteriores con grid_forget para evitar que se encimen."""
        for widget in self.main_container.grid_slaves():
            if int(widget.grid_info()["row"]) == 1:
                widget.grid_forget()
        vista_widget.grid(row=1, column=0, sticky="nsew", padx=20, pady=15)

    def mostrar_pantalla_dashboard(self):
        """Regresa al panel principal ocultando los submódulos."""
        self.actualizar_titulo_header("Panel Principal - Gestión de Academias")
        for widget in self.main_container.grid_slaves():
            if int(widget.grid_info()["row"]) == 1:
                widget.grid_forget()
        self.scroll_content.grid(row=1, column=0, sticky="nsew", padx=20, pady=15)

    def _cerrar_aplicacion(self):
        """Cierra el panel y la raíz oculta: la aplicación termina por completo."""
        raiz = self.master
        try:
            self.destroy()
        finally:
            try:
                if raiz is not None and raiz.winfo_exists():
                    raiz.destroy()
            except Exception:
                pass