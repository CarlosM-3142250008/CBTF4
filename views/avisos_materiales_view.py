import os
import webbrowser
from datetime import datetime
from tkinter import filedialog, messagebox

import customtkinter as ctk

from views.typography import (
    fuente,
    fuente_dato,
    fuente_etiqueta,
    fuente_titulo,
)

try:
    from views.custom_calendar import CustomCalendar
    HAS_CUSTOM_CALENDAR = True
except ImportError:
    try:
        from custom_calendar import CustomCalendar
        HAS_CUSTOM_CALENDAR = True
    except ImportError:
        HAS_CUSTOM_CALENDAR = False

from views.dropdown import Dropdown
from views.icons import GRIS_OSCURO, icono
from views.skeleton import SkeletonLista
from views.ui_utils import (
    COLOR_BORDE,
    COLOR_INPUT_BG,
    COLOR_INPUT_BORDER,
    COLOR_NUEVO,
    COLOR_PRIMARIO,
    COLOR_PRIMARIO_HOVER,
    COLOR_SECUNDARIO,
    COLOR_SECUNDARIO_HOVER,
    COLOR_TEXTO,
    COLOR_TEXTO_SUAVE,
    crear_badge,
    crear_boton_editar,
    crear_boton_eliminar,
    crear_tarjeta_tinte,
    es_reciente,
    fecha_coincide,
    formatear_fecha_hora,
    limpiar_entry,
    coincide_busqueda,
    paleta_tarjeta,
    parse_fecha,
)


class AvisosMaterialesView(ctk.CTkFrame):
    def __init__(self, parent_container):
        super().__init__(parent_container, fg_color="transparent")

        self.grid_columnconfigure(0, weight=1, uniform="panel")
        self.grid_columnconfigure(1, weight=1, uniform="panel")
        self.grid_rowconfigure(0, weight=1)

        # Paleta de colores clara y uniforme
        self.COLOR_LABEL = "#222222"
        self.COLOR_ENTRY_BG = COLOR_INPUT_BG
        self.COLOR_ENTRY_BORDER = COLOR_INPUT_BORDER
        self.COLOR_TEXT_INSIDE = "#111111"
        self.COLOR_PLACEHOLDER = "#777777"

        self.fecha_seleccionada = datetime.now().strftime("%Y-%m-%d")

        # Permisos y callbacks administrados por el DashboardController.
        self.puede_eliminar = False
        self.puede_editar = False
        self.on_eliminar_aviso = None
        self.on_eliminar_material = None
        self.on_editar_aviso = None
        self.on_editar_material = None
        self.on_cancelar_edicion_aviso = None
        self.on_cancelar_edicion_material = None

        # Carga múltiple de archivos (solo administrador)
        self.puede_subir_archivos = False
        self.archivos_seleccionados = []

        self._solo_lectura = False
        self._form_aviso_visible = False
        self._form_material_visible = False
        self._en_edicion_aviso = False
        self._en_edicion_material = False

        self._avisos = []
        self._materiales = []
        self._academias = []

        self._crear_panel_avisos()
        self._crear_panel_materiales()

    # ==================================================================
    # CONSTRUCCIÓN DE LA COLUMNA DE AVISOS
    # ==================================================================
    def _crear_panel_avisos(self):
        self.panel_avisos = ctk.CTkFrame(self, fg_color="white", corner_radius=18)
        self.panel_avisos.grid(row=0, column=0, padx=(0, 6), pady=0, sticky="nsew")
        self.panel_avisos.grid_columnconfigure(0, weight=1)
        self.panel_avisos.grid_rowconfigure(3, weight=1)

        encabezado = ctk.CTkFrame(self.panel_avisos, fg_color="transparent")
        encabezado.grid(row=0, column=0, sticky="ew", padx=15, pady=(13, 4))
        encabezado.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            encabezado, text="AVISOS", font=fuente_etiqueta(8),
            text_color=COLOR_PRIMARIO
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            encabezado, text="  Avisos",
            image=icono("megaphone", 19, COLOR_PRIMARIO),
            compound="left",
            font=fuente_titulo(17), text_color=COLOR_PRIMARIO
        ).grid(row=1, column=0, sticky="w")

        self.lbl_contador_avisos = ctk.CTkLabel(
            encabezado, text="0",
            font=fuente_dato(10), text_color=COLOR_PRIMARIO,
            fg_color="#EAF4EC", corner_radius=8, height=22, width=42
        )
        self.lbl_contador_avisos.grid(row=1, column=1, sticky="w", padx=(8, 0))

        self.btn_nuevo_aviso = ctk.CTkButton(
            encabezado, text="  Nuevo aviso", width=112, height=28,
            image=icono("plus", 14, "#FFFFFF"),
            compound="left",
            fg_color=COLOR_PRIMARIO, hover_color=COLOR_PRIMARIO_HOVER,
            font=fuente_titulo(10), command=self._alternar_formulario_aviso
        )
        self.btn_nuevo_aviso.grid(row=0, column=2, rowspan=2, sticky="e")

        ctk.CTkLabel(
            encabezado,
            text="Publica información y consulta los avisos vigentes.",
            font=fuente(11), text_color=COLOR_TEXTO_SUAVE
        ).grid(row=2, column=0, columnspan=3, sticky="w", pady=(2, 0))

        # Formulario plegable de avisos
        self.frame_formulario_aviso = ctk.CTkFrame(
            self.panel_avisos, fg_color="#F8FAF9", corner_radius=14,
            border_width=0, border_color="#E8EDEA"
        )
        self.frame_formulario_aviso.grid(row=1, column=0, sticky="ew", padx=12, pady=(5, 8))
        self.frame_formulario_aviso.grid_columnconfigure((0, 1), weight=1)

        self.lbl_form_aviso = ctk.CTkLabel(
            self.frame_formulario_aviso, text="  Publicar aviso",
            image=icono("megaphone", 16, COLOR_PRIMARIO),
            compound="left",
            font=fuente_titulo(13), text_color=COLOR_PRIMARIO
        )
        self.lbl_form_aviso.grid(row=0, column=0, columnspan=2, padx=12, pady=(10, 3), sticky="w")

        self.entry_aviso_titulo = ctk.CTkEntry(
            self.frame_formulario_aviso, placeholder_text="Título del aviso",
            fg_color="white", border_color=self.COLOR_ENTRY_BORDER,
            text_color=self.COLOR_TEXT_INSIDE,
            placeholder_text_color=self.COLOR_PLACEHOLDER, font=fuente(11), height=30
        )
        self.entry_aviso_titulo.grid(row=1, column=0, columnspan=2, padx=12, pady=3, sticky="ew")

        ctk.CTkLabel(
            self.frame_formulario_aviso, text="EMISOR",
            font=fuente_etiqueta(9), text_color=self.COLOR_LABEL
        ).grid(row=2, column=0, padx=(12, 5), pady=(4, 1), sticky="w")
        ctk.CTkLabel(
            self.frame_formulario_aviso, text="DESTINATARIO",
            font=fuente_etiqueta(9), text_color=self.COLOR_LABEL
        ).grid(row=2, column=1, padx=(5, 12), pady=(4, 1), sticky="w")

        self.entry_aviso_emisor = ctk.CTkEntry(
            self.frame_formulario_aviso, placeholder_text="Ej. Dirección Académica",
            fg_color="white", border_color=self.COLOR_ENTRY_BORDER,
            text_color=self.COLOR_TEXT_INSIDE,
            placeholder_text_color=self.COLOR_PLACEHOLDER, font=fuente(11), height=30
        )
        self.entry_aviso_emisor.grid(row=3, column=0, padx=(12, 5), pady=3, sticky="ew")

        self.combo_aviso_destinatario = Dropdown(
            self.frame_formulario_aviso,
            values=["Todas las Academias", "Solo Coordinadores"],
            width=180, height=30, font=fuente(11), dropdown_font=fuente(11)
        )
        self.combo_aviso_destinatario.grid(row=3, column=1, padx=(5, 12), pady=3, sticky="ew")

        ctk.CTkLabel(
            self.frame_formulario_aviso, text="FECHA DEL EVENTO",
            font=fuente_etiqueta(9), text_color=self.COLOR_LABEL
        ).grid(row=4, column=0, columnspan=2, padx=12, pady=(4, 1), sticky="w")

        self.box_fecha = ctk.CTkFrame(self.frame_formulario_aviso, fg_color="transparent")
        self.box_fecha.grid(row=5, column=0, columnspan=2, padx=12, pady=3, sticky="ew")
        self.box_fecha.grid_columnconfigure(0, weight=1)

        self.entry_aviso_fecha = ctk.CTkEntry(
            self.box_fecha, fg_color="white", border_color=self.COLOR_ENTRY_BORDER,
            text_color=self.COLOR_TEXT_INSIDE, font=fuente_dato(10), height=30
        )
        self.entry_aviso_fecha.insert(0, self.fecha_seleccionada)
        self.entry_aviso_fecha.grid(row=0, column=0, padx=(0, 4), sticky="ew")

        self.btn_calendario_avisos = ctk.CTkButton(
            self.box_fecha, text="", image=icono("calendar", 16, "#FFFFFF"),
            width=34, height=30,
            fg_color=COLOR_SECUNDARIO, hover_color=COLOR_SECUNDARIO_HOVER,
            command=self.abrir_calendario_avisos_popup
        )
        self.btn_calendario_avisos.grid(row=0, column=1)

        ctk.CTkLabel(
            self.frame_formulario_aviso, text="CONTENIDO DEL AVISO",
            font=fuente_etiqueta(9), text_color=self.COLOR_LABEL
        ).grid(row=6, column=0, columnspan=2, padx=12, pady=(4, 1), sticky="w")

        self.entry_aviso_detalle = ctk.CTkEntry(
            self.frame_formulario_aviso, placeholder_text="Describe el aviso",
            fg_color="white", border_color=self.COLOR_ENTRY_BORDER,
            text_color=self.COLOR_TEXT_INSIDE,
            placeholder_text_color=self.COLOR_PLACEHOLDER, font=fuente(11), height=30
        )
        self.entry_aviso_detalle.grid(row=7, column=0, columnspan=2, padx=12, pady=3, sticky="ew")

        self.btn_guardar_aviso = ctk.CTkButton(
            self.frame_formulario_aviso, text="  Publicar aviso",
            image=icono("send", 14, "#FFFFFF"),
            compound="left",
            fg_color=COLOR_SECUNDARIO, hover_color=COLOR_SECUNDARIO_HOVER,
            font=fuente_titulo(10), height=32
        )
        self.btn_guardar_aviso.grid(row=8, column=0, padx=(12, 5), pady=(8, 10), sticky="ew")

        self.btn_cancelar_aviso = ctk.CTkButton(
            self.frame_formulario_aviso, text="Cancelar",
            fg_color="transparent", hover_color="#EAF4EC",
            border_width=0, border_color=COLOR_BORDE,
            text_color=COLOR_TEXTO_SUAVE, font=fuente(10, "bold"),
            height=32, command=self._cancelar_edicion_aviso
        )
        self.btn_cancelar_aviso.grid(row=8, column=1, padx=(5, 12), pady=(8, 10), sticky="ew")

        self.frame_formulario_aviso.grid_remove()

        # Búsqueda y filtros de avisos
        self.frame_filtros_avisos = ctk.CTkFrame(
            self.panel_avisos, fg_color="#F8FAF9", corner_radius=14,
            border_width=0, border_color="#E8EDEA"
        )
        self.frame_filtros_avisos.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 7))
        self.frame_filtros_avisos.grid_columnconfigure(0, weight=1)
        self.frame_filtros_avisos.grid_columnconfigure(1, weight=0)
        self.frame_filtros_avisos.grid_columnconfigure(2, weight=0)

        self.entry_busqueda_avisos = ctk.CTkEntry(
            self.frame_filtros_avisos,
            placeholder_text="Buscar aviso...",
            fg_color="white", border_color=COLOR_INPUT_BORDER,
            text_color=self.COLOR_TEXT_INSIDE,
            placeholder_text_color="#8A8F98", font=fuente(11), height=30
        )
        self.entry_busqueda_avisos.grid(
            row=0, column=0, columnspan=3, padx=9, pady=(8, 4), sticky="ew"
        )
        self.entry_busqueda_avisos.bind(
            "<KeyRelease>", lambda _evento: self._aplicar_filtros_avisos()
        )

        self.entry_fecha_evento_filtro = ctk.CTkEntry(
            self.frame_filtros_avisos,
            placeholder_text="Fecha evento (AAAA-MM-DD)",
            fg_color="white", border_color=COLOR_INPUT_BORDER,
            text_color=self.COLOR_TEXT_INSIDE,
            placeholder_text_color="#8A8F98", font=fuente_dato(10), height=27
        )
        self.entry_fecha_evento_filtro.grid(row=1, column=0, padx=(9, 4), pady=3, sticky="ew")
        self.entry_fecha_evento_filtro.bind(
            "<KeyRelease>", lambda _evento: self._aplicar_filtros_avisos()
        )

        self.btn_calendario_filtro_evento = ctk.CTkButton(
            self.frame_filtros_avisos, text="",
            image=icono("calendar", 13, COLOR_PRIMARIO),
            width=29, height=27,
            fg_color="#EAF4EC", hover_color="#D8EBDD",
            command=lambda: self._abrir_calendario_filtro(
                self.entry_fecha_evento_filtro, self._aplicar_filtros_avisos
            )
        )
        self.btn_calendario_filtro_evento.grid(row=1, column=1, padx=(0, 4), pady=3)

        self.combo_orden_avisos = Dropdown(
            self.frame_filtros_avisos, values=["Más reciente", "Más antiguo"],
            width=124, height=27, font=fuente(10), dropdown_font=fuente(10),
            command=lambda _valor: self._aplicar_filtros_avisos()
        )
        self.combo_orden_avisos.grid(row=1, column=2, padx=(0, 9), pady=3, sticky="e")

        self.combo_destinatario_filtro = Dropdown(
            self.frame_filtros_avisos,
            values=["Todos los destinatarios", "Todas las Academias", "Solo Coordinadores"],
            width=180, height=27, font=fuente(10), dropdown_font=fuente(10),
            command=lambda _valor: self._aplicar_filtros_avisos()
        )
        self.combo_destinatario_filtro.grid(
            row=2, column=0, columnspan=3, padx=9, pady=3, sticky="ew"
        )

        pie = ctk.CTkFrame(self.frame_filtros_avisos, fg_color="transparent")
        pie.grid(row=3, column=0, columnspan=3, padx=9, pady=(1, 8), sticky="ew")
        pie.grid_columnconfigure(0, weight=1)

        self.lbl_resumen_filtros_avisos = ctk.CTkLabel(
            pie, text="", font=fuente(10), text_color=COLOR_TEXTO_SUAVE, anchor="w"
        )
        self.lbl_resumen_filtros_avisos.grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            pie, text="  Limpiar", width=80, height=23,
            image=icono("x", 10, COLOR_PRIMARIO),
            compound="left",
            fg_color="transparent", hover_color="#EAF4EC",
            border_width=0, border_color="#D5E3D8",
            text_color=COLOR_PRIMARIO, font=fuente(10, "bold"),
            command=self.limpiar_filtros_avisos
        ).grid(row=0, column=1, sticky="e")

        # Listado de avisos con desplazamiento propio
        self.frame_avisos_lista = ctk.CTkFrame(self.panel_avisos, fg_color="transparent")
        self.frame_avisos_lista.grid(row=3, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.frame_avisos_lista.grid_rowconfigure(0, weight=1)
        self.frame_avisos_lista.grid_columnconfigure(0, weight=1)

        self.container_lista_avisos = ctk.CTkScrollableFrame(
            self.frame_avisos_lista, fg_color="transparent"
        )
        self.container_lista_avisos.grid(row=0, column=0, sticky="nsew")

    # ==================================================================
    # CONSTRUCCIÓN DE LA COLUMNA DE MATERIALES
    # ==================================================================
    def _crear_panel_materiales(self):
        self.panel_materiales = ctk.CTkFrame(self, fg_color="white", corner_radius=18)
        self.panel_materiales.grid(row=0, column=1, padx=(6, 0), pady=0, sticky="nsew")
        self.panel_materiales.grid_columnconfigure(0, weight=1)
        self.panel_materiales.grid_rowconfigure(3, weight=1)

        encabezado = ctk.CTkFrame(self.panel_materiales, fg_color="transparent")
        encabezado.grid(row=0, column=0, sticky="ew", padx=15, pady=(13, 4))
        encabezado.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            encabezado, text="RECURSOS", font=fuente_etiqueta(8),
            text_color=COLOR_SECUNDARIO
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            encabezado, text="  Materiales",
            image=icono("folder-open", 19, COLOR_SECUNDARIO),
            compound="left",
            font=fuente_titulo(17), text_color=COLOR_SECUNDARIO
        ).grid(row=1, column=0, sticky="w")

        self.lbl_contador_materiales = ctk.CTkLabel(
            encabezado, text="0",
            font=fuente_dato(10), text_color=COLOR_SECUNDARIO,
            fg_color="#F7EFE6", corner_radius=8, height=22, width=42
        )
        self.lbl_contador_materiales.grid(row=1, column=1, sticky="w", padx=(8, 0))

        self.btn_nuevo_material = ctk.CTkButton(
            encabezado, text="  Nuevo material", width=124, height=28,
            image=icono("plus", 14, "#FFFFFF"),
            compound="left",
            fg_color=COLOR_SECUNDARIO, hover_color=COLOR_SECUNDARIO_HOVER,
            font=fuente_titulo(10), command=self._alternar_formulario_material
        )
        self.btn_nuevo_material.grid(row=0, column=2, rowspan=2, sticky="e")

        ctk.CTkLabel(
            encabezado,
            text="Comparte recursos y archivos con la comunidad escolar.",
            font=fuente(11), text_color=COLOR_TEXTO_SUAVE
        ).grid(row=2, column=0, columnspan=3, sticky="w", pady=(2, 0))

        # Formulario plegable de materiales
        self.frame_formulario_material = ctk.CTkFrame(
            self.panel_materiales, fg_color="#FCF9F5", corner_radius=14,
            border_width=0, border_color="#F0E4D7"
        )
        self.frame_formulario_material.grid(row=1, column=0, sticky="ew", padx=12, pady=(5, 8))
        self.frame_formulario_material.grid_columnconfigure((0, 1), weight=1)

        self.lbl_form_material = ctk.CTkLabel(
            self.frame_formulario_material, text="  Añadir material",
            image=icono("folder-open", 16, COLOR_SECUNDARIO),
            compound="left",
            font=fuente_titulo(13), text_color=COLOR_SECUNDARIO
        )
        self.lbl_form_material.grid(row=0, column=0, columnspan=2, padx=12, pady=(10, 3), sticky="w")

        self.entry_mat_nombre = ctk.CTkEntry(
            self.frame_formulario_material, placeholder_text="Nombre del material",
            fg_color="white", border_color=self.COLOR_ENTRY_BORDER,
            text_color=self.COLOR_TEXT_INSIDE,
            placeholder_text_color=self.COLOR_PLACEHOLDER, font=fuente(11), height=30
        )
        self.entry_mat_nombre.grid(row=1, column=0, columnspan=2, padx=12, pady=3, sticky="ew")

        ctk.CTkLabel(
            self.frame_formulario_material, text="CATEGORÍA / ACADEMIA",
            font=fuente_etiqueta(9), text_color=self.COLOR_LABEL
        ).grid(row=2, column=0, columnspan=2, padx=12, pady=(4, 1), sticky="w")

        self.combo_mat_categoria = Dropdown(
            self.frame_formulario_material, values=["Todas las Academias"],
            width=180, height=30, font=fuente(11), dropdown_font=fuente(11)
        )
        self.combo_mat_categoria.grid(row=3, column=0, columnspan=2, padx=12, pady=3, sticky="ew")

        ctk.CTkLabel(
            self.frame_formulario_material, text="DESCRIPCIÓN",
            font=fuente_etiqueta(9), text_color=self.COLOR_LABEL
        ).grid(row=4, column=0, columnspan=2, padx=12, pady=(4, 1), sticky="w")

        self.entry_mat_descripcion = ctk.CTkEntry(
            self.frame_formulario_material, placeholder_text="Detalles del material",
            fg_color="white", border_color=self.COLOR_ENTRY_BORDER,
            text_color=self.COLOR_TEXT_INSIDE,
            placeholder_text_color=self.COLOR_PLACEHOLDER, font=fuente(11), height=30
        )
        self.entry_mat_descripcion.grid(row=5, column=0, columnspan=2, padx=12, pady=3, sticky="ew")

        ctk.CTkLabel(
            self.frame_formulario_material, text="ENLACE O ARCHIVO",
            font=fuente_etiqueta(9), text_color=self.COLOR_LABEL
        ).grid(row=6, column=0, columnspan=2, padx=12, pady=(4, 1), sticky="w")

        self.entry_mat_enlace = ctk.CTkEntry(
            self.frame_formulario_material, placeholder_text="http://... o ruta del archivo",
            fg_color="white", border_color=self.COLOR_ENTRY_BORDER,
            text_color=self.COLOR_TEXT_INSIDE,
            placeholder_text_color=self.COLOR_PLACEHOLDER, font=fuente(11), height=30
        )
        self.entry_mat_enlace.grid(row=7, column=0, columnspan=2, padx=12, pady=3, sticky="ew")

        self.btn_guardar_material = ctk.CTkButton(
            self.frame_formulario_material, text="  Guardar material",
            image=icono("save", 14, "#FFFFFF"),
            compound="left",
            fg_color=COLOR_SECUNDARIO, hover_color=COLOR_SECUNDARIO_HOVER,
            font=fuente_titulo(10), height=32
        )
        self.btn_guardar_material.grid(row=8, column=0, padx=(12, 5), pady=(8, 5), sticky="ew")

        self.btn_cancelar_material = ctk.CTkButton(
            self.frame_formulario_material, text="Cancelar",
            fg_color="transparent", hover_color="#F7EFE6",
            border_width=0, border_color=COLOR_BORDE,
            text_color=COLOR_TEXTO_SUAVE, font=fuente(10, "bold"),
            height=32, command=self._cancelar_edicion_material
        )
        self.btn_cancelar_material.grid(row=8, column=1, padx=(5, 12), pady=(8, 5), sticky="ew")

        # Carga múltiple de archivos (solo administrador)
        self.frame_archivos = ctk.CTkFrame(
            self.frame_formulario_material, fg_color="#F8FAF9", corner_radius=12,
            border_width=0, border_color=COLOR_BORDE
        )
        self.frame_archivos.grid(row=9, column=0, columnspan=2, padx=12, pady=(3, 10), sticky="ew")
        self.frame_archivos.grid_columnconfigure(0, weight=1)

        encabezado_archivos = ctk.CTkFrame(self.frame_archivos, fg_color="transparent")
        encabezado_archivos.grid(row=0, column=0, padx=10, pady=(8, 0), sticky="ew")
        encabezado_archivos.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            encabezado_archivos, text="  Subir archivos de material",
            image=icono("paperclip", 14, COLOR_SECUNDARIO),
            compound="left",
            font=fuente_titulo(11), text_color=COLOR_SECUNDARIO
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            encabezado_archivos,
            text="Selecciona varios archivos de cualquier carpeta (PDF, Word, imágenes, etc.).",
            font=fuente(10), text_color=COLOR_TEXTO_SUAVE
        ).grid(row=1, column=0, sticky="w")

        crear_badge(
            encabezado_archivos, "ADMINISTRADOR", color=COLOR_PRIMARIO, ancho=102
        ).grid(row=0, column=1, rowspan=2, padx=(8, 0), sticky="e")

        acciones_archivos = ctk.CTkFrame(self.frame_archivos, fg_color="transparent")
        acciones_archivos.grid(row=1, column=0, padx=10, pady=(7, 3), sticky="ew")
        acciones_archivos.grid_columnconfigure(1, weight=1)

        self.btn_seleccionar_archivos = ctk.CTkButton(
            acciones_archivos, text="  Seleccionar", width=118, height=28,
            image=icono("folder-open", 14, "#FFFFFF"),
            compound="left",
            fg_color=COLOR_SECUNDARIO, hover_color=COLOR_SECUNDARIO_HOVER,
            font=fuente(11, "bold"), command=self.seleccionar_archivos
        )
        self.btn_seleccionar_archivos.grid(row=0, column=0, sticky="w")

        self.lbl_resumen_archivos = ctk.CTkLabel(
            acciones_archivos, text="No has seleccionado archivos.",
            font=fuente(11), text_color=COLOR_TEXTO_SUAVE, anchor="w"
        )
        self.lbl_resumen_archivos.grid(row=0, column=1, padx=6, sticky="ew")

        self.btn_subir_archivos = ctk.CTkButton(
            acciones_archivos, text="  Subir", width=88, height=28,
            image=icono("upload", 13, "#FFFFFF"),
            compound="left",
            fg_color=COLOR_PRIMARIO, hover_color=COLOR_PRIMARIO_HOVER,
            font=fuente(11, "bold"), state="disabled"
        )
        self.btn_subir_archivos.grid(row=0, column=2, sticky="e")

        self.container_archivos_seleccionados = ctk.CTkFrame(
            self.frame_archivos, fg_color="transparent"
        )
        self.container_archivos_seleccionados.grid(
            row=2, column=0, padx=10, pady=(0, 8), sticky="ew"
        )

        self.frame_archivos.grid_remove()
        self.frame_formulario_material.grid_remove()

        # Búsqueda y filtros de materiales
        self.frame_filtros_materiales = ctk.CTkFrame(
            self.panel_materiales, fg_color="#FCF9F5", corner_radius=14,
            border_width=0, border_color="#F0E4D7"
        )
        self.frame_filtros_materiales.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 7))
        self.frame_filtros_materiales.grid_columnconfigure(0, weight=1)
        self.frame_filtros_materiales.grid_columnconfigure(1, weight=0)
        self.frame_filtros_materiales.grid_columnconfigure(2, weight=0)

        self.entry_busqueda_materiales = ctk.CTkEntry(
            self.frame_filtros_materiales,
            placeholder_text="Buscar material...",
            fg_color="white", border_color=COLOR_INPUT_BORDER,
            text_color=self.COLOR_TEXT_INSIDE,
            placeholder_text_color="#8A8F98", font=fuente(11), height=30
        )
        self.entry_busqueda_materiales.grid(
            row=0, column=0, columnspan=3, padx=9, pady=(8, 4), sticky="ew"
        )
        self.entry_busqueda_materiales.bind(
            "<KeyRelease>", lambda _evento: self._aplicar_filtros_materiales()
        )

        self.entry_fecha_publicacion_filtro = ctk.CTkEntry(
            self.frame_filtros_materiales,
            placeholder_text="Fecha publicación (AAAA-MM-DD)",
            fg_color="white", border_color=COLOR_INPUT_BORDER,
            text_color=self.COLOR_TEXT_INSIDE,
            placeholder_text_color="#8A8F98", font=fuente_dato(10), height=27
        )
        self.entry_fecha_publicacion_filtro.grid(
            row=1, column=0, padx=(9, 4), pady=3, sticky="ew"
        )
        self.entry_fecha_publicacion_filtro.bind(
            "<KeyRelease>", lambda _evento: self._aplicar_filtros_materiales()
        )

        self.btn_calendario_filtro_publicacion = ctk.CTkButton(
            self.frame_filtros_materiales, text="",
            image=icono("calendar", 13, COLOR_SECUNDARIO),
            width=29, height=27,
            fg_color="#F7EFE6", hover_color="#EEDDCB",
            command=lambda: self._abrir_calendario_filtro(
                self.entry_fecha_publicacion_filtro, self._aplicar_filtros_materiales
            )
        )
        self.btn_calendario_filtro_publicacion.grid(row=1, column=1, padx=(0, 4), pady=3)

        self.combo_orden_materiales = Dropdown(
            self.frame_filtros_materiales, values=["Más reciente", "Más antiguo"],
            width=124, height=27, font=fuente(10), dropdown_font=fuente(10),
            command=lambda _valor: self._aplicar_filtros_materiales()
        )
        self.combo_orden_materiales.grid(row=1, column=2, padx=(0, 9), pady=3, sticky="e")

        self.combo_academia_filtro_materiales = Dropdown(
            self.frame_filtros_materiales, values=["Todas las categorías"],
            width=180, height=27, font=fuente(10), dropdown_font=fuente(10),
            command=lambda _valor: self._aplicar_filtros_materiales()
        )
        self.combo_academia_filtro_materiales.grid(
            row=2, column=0, columnspan=3, padx=9, pady=3, sticky="ew"
        )

        pie = ctk.CTkFrame(self.frame_filtros_materiales, fg_color="transparent")
        pie.grid(row=3, column=0, columnspan=3, padx=9, pady=(1, 8), sticky="ew")
        pie.grid_columnconfigure(0, weight=1)

        self.lbl_resumen_filtros_materiales = ctk.CTkLabel(
            pie, text="", font=fuente(10), text_color=COLOR_TEXTO_SUAVE, anchor="w"
        )
        self.lbl_resumen_filtros_materiales.grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            pie, text="  Limpiar", width=80, height=23,
            image=icono("x", 10, COLOR_SECUNDARIO),
            compound="left",
            fg_color="transparent", hover_color="#F7EFE6",
            border_width=0, border_color="#EADAC9",
            text_color=COLOR_SECUNDARIO, font=fuente(10, "bold"),
            command=self.limpiar_filtros_materiales
        ).grid(row=0, column=1, sticky="e")

        # Listado de materiales con desplazamiento propio
        self.frame_materiales_lista = ctk.CTkFrame(self.panel_materiales, fg_color="transparent")
        self.frame_materiales_lista.grid(row=3, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.frame_materiales_lista.grid_rowconfigure(0, weight=1)
        self.frame_materiales_lista.grid_columnconfigure(0, weight=1)

        self.container_lista_materiales = ctk.CTkScrollableFrame(
            self.frame_materiales_lista, fg_color="transparent"
        )
        self.container_lista_materiales.grid(row=0, column=0, sticky="nsew")

    # ==================================================================
    # PERMISOS Y VISIBILIDAD
    # ==================================================================
    def configurar_modo_lectura(self, solo_lectura):
        """Oculta las herramientas de creación cuando el rol es Docente."""
        self._solo_lectura = bool(solo_lectura)

        if self._solo_lectura:
            self._ocultar_formulario_aviso()
            self._ocultar_formulario_material()
            self.btn_nuevo_aviso.grid_remove()
            self.btn_nuevo_material.grid_remove()
            self.frame_archivos.grid_remove()
        else:
            self.btn_nuevo_aviso.grid()
            self.btn_nuevo_material.grid()
            if self.puede_subir_archivos:
                self.frame_archivos.grid()

    def habilitar_carga_archivos(self, habilitado):
        """Muestra u oculta la sección de carga de archivos según el rol."""
        self.puede_subir_archivos = bool(habilitado)
        if self.puede_subir_archivos and not self._solo_lectura:
            self.frame_archivos.grid()
        else:
            self.frame_archivos.grid_remove()
            if not self.puede_subir_archivos:
                self.limpiar_archivos_seleccionados()

    # ==================================================================
    # FORMULARIOS DE AVISOS
    # ==================================================================
    def _alternar_formulario_aviso(self):
        if self._solo_lectura:
            return
        if self._form_aviso_visible:
            if self._en_edicion_aviso:
                self._cancelar_edicion_aviso()
            else:
                self.limpiar_formulario_aviso()
                self._ocultar_formulario_aviso()
        else:
            self._mostrar_formulario_aviso()

    def _mostrar_formulario_aviso(self):
        self.frame_formulario_aviso.grid()
        self.frame_filtros_avisos.grid_remove()
        self._form_aviso_visible = True
        self.btn_nuevo_aviso.configure(
            text="  Cerrar", image=icono("x", 14, "#FFFFFF")
        )

    def _ocultar_formulario_aviso(self):
        if not hasattr(self, "frame_formulario_aviso"):
            return
        self.frame_formulario_aviso.grid_remove()
        self.frame_filtros_avisos.grid()
        self._form_aviso_visible = False
        self.btn_nuevo_aviso.configure(
            text="  Nuevo aviso", image=icono("plus", 14, "#FFFFFF")
        )

    def _cancelar_edicion_aviso(self):
        if self._en_edicion_aviso and callable(self.on_cancelar_edicion_aviso):
            self.on_cancelar_edicion_aviso()
        else:
            self.limpiar_formulario_aviso()
            self._ocultar_formulario_aviso()

    def cargar_datos_edicion_aviso(self, aviso):
        """Muestra el formulario y precarga los datos de un aviso existente."""
        self._en_edicion_aviso = True
        self._mostrar_formulario_aviso()
        self.lbl_form_aviso.configure(
            text="  Editar aviso", image=icono("square-pen", 16, COLOR_PRIMARIO)
        )
        self.btn_guardar_aviso.configure(
            text="  Guardar cambios",
            image=icono("save", 14, "#FFFFFF"),
            fg_color=COLOR_PRIMARIO,
            hover_color=COLOR_PRIMARIO_HOVER
        )

        self._escribir_entry(self.entry_aviso_titulo, aviso.get('titulo') or "")
        self._escribir_entry(self.entry_aviso_emisor, aviso.get('emisor') or "")
        self._escribir_entry(self.entry_aviso_detalle, aviso.get('detalle') or "")

        fecha_evento = parse_fecha(aviso.get('fecha_evento'))
        if fecha_evento:
            self.fecha_seleccionada = fecha_evento.strftime("%Y-%m-%d")
            self._escribir_entry(self.entry_aviso_fecha, self.fecha_seleccionada)
        else:
            self._escribir_entry(self.entry_aviso_fecha, self.fecha_seleccionada)

        destinatario = aviso.get('destinatario') or "Todas las Academias"
        valores = list(self.combo_aviso_destinatario.cget("values"))
        if destinatario not in valores:
            valores.append(destinatario)
            self.combo_aviso_destinatario.configure(values=valores)
        self.combo_aviso_destinatario.set(destinatario)

        try:
            self.entry_aviso_titulo.focus_set()
        except Exception:
            pass

    def salir_modo_edicion_aviso(self):
        """Cierra el formulario y lo deja listo para una nueva publicación."""
        self._en_edicion_aviso = False
        self.lbl_form_aviso.configure(
            text="  Publicar aviso", image=icono("megaphone", 16, COLOR_PRIMARIO)
        )
        self.btn_guardar_aviso.configure(
            text="  Publicar aviso",
            image=icono("send", 14, "#FFFFFF"),
            fg_color=COLOR_SECUNDARIO,
            hover_color=COLOR_SECUNDARIO_HOVER
        )
        self.limpiar_formulario_aviso()
        self._ocultar_formulario_aviso()

    def limpiar_formulario_aviso(self):
        self._escribir_entry(self.entry_aviso_titulo, "")
        self._escribir_entry(self.entry_aviso_emisor, "")
        self._escribir_entry(self.entry_aviso_detalle, "")
        self.fecha_seleccionada = datetime.now().strftime("%Y-%m-%d")
        self._escribir_entry(self.entry_aviso_fecha, self.fecha_seleccionada)

    # ==================================================================
    # FORMULARIOS DE MATERIALES
    # ==================================================================
    def _alternar_formulario_material(self):
        if self._solo_lectura:
            return
        if self._form_material_visible:
            if self._en_edicion_material:
                self._cancelar_edicion_material()
            else:
                self.limpiar_formulario_material()
                self._ocultar_formulario_material()
        else:
            self._mostrar_formulario_material()

    def _mostrar_formulario_material(self):
        self.frame_formulario_material.grid()
        self.frame_filtros_materiales.grid_remove()
        self._form_material_visible = True
        self.btn_nuevo_material.configure(
            text="  Cerrar", image=icono("x", 14, "#FFFFFF")
        )

    def _ocultar_formulario_material(self):
        if not hasattr(self, "frame_formulario_material"):
            return
        self.frame_formulario_material.grid_remove()
        self.frame_filtros_materiales.grid()
        self._form_material_visible = False
        self.btn_nuevo_material.configure(
            text="  Nuevo material", image=icono("plus", 14, "#FFFFFF")
        )

    def _cancelar_edicion_material(self):
        if self._en_edicion_material and callable(self.on_cancelar_edicion_material):
            self.on_cancelar_edicion_material()
        else:
            self.limpiar_formulario_material()
            self._ocultar_formulario_material()

    def cargar_datos_edicion_material(self, material):
        """Muestra el formulario y precarga los datos de un material existente."""
        self._en_edicion_material = True
        self._mostrar_formulario_material()
        self.lbl_form_material.configure(
            text="  Editar material", image=icono("square-pen", 16, COLOR_SECUNDARIO)
        )
        self.btn_guardar_material.configure(
            text="  Guardar cambios",
            image=icono("save", 14, "#FFFFFF"),
            fg_color=COLOR_PRIMARIO,
            hover_color=COLOR_PRIMARIO_HOVER
        )

        self._escribir_entry(self.entry_mat_nombre, material.get('nombre') or "")
        self._escribir_entry(self.entry_mat_descripcion, material.get('descripcion') or "")
        self._escribir_entry(self.entry_mat_enlace, material.get('enlace') or "")

        categoria = material.get('categoria') or "Todas las Academias"
        valores = list(self.combo_mat_categoria.cget("values"))
        if categoria not in valores:
            valores.append(categoria)
            self.combo_mat_categoria.configure(values=valores)
        self.combo_mat_categoria.set(categoria)

        try:
            self.entry_mat_nombre.focus_set()
        except Exception:
            pass

    def salir_modo_edicion_material(self):
        """Cierra el formulario y lo deja listo para un nuevo material."""
        self._en_edicion_material = False
        self.lbl_form_material.configure(
            text="  Añadir material", image=icono("folder-open", 16, COLOR_SECUNDARIO)
        )
        self.btn_guardar_material.configure(
            text="  Guardar material",
            image=icono("save", 14, "#FFFFFF"),
            fg_color=COLOR_SECUNDARIO,
            hover_color=COLOR_SECUNDARIO_HOVER
        )
        self.limpiar_formulario_material()
        self._ocultar_formulario_material()

    def limpiar_formulario_material(self):
        self._escribir_entry(self.entry_mat_nombre, "")
        self._escribir_entry(self.entry_mat_descripcion, "")
        self._escribir_entry(self.entry_mat_enlace, "")

    # ==================================================================
    # CATÁLOGOS Y FILTROS
    # ==================================================================
    def actualizar_academias_dinamicas(self, lista_academias):
        """Refresca las academias dinámicas en los desplegables desde la BD."""
        self._academias = list(lista_academias or [])
        if not self._academias:
            return

        opciones_avisos = ["Todas las Academias", "Solo Coordinadores"] + self._academias
        actual = self.combo_aviso_destinatario.get()
        if actual not in opciones_avisos:
            opciones_avisos.append(actual)
        self.combo_aviso_destinatario.configure(values=opciones_avisos)
        self.combo_aviso_destinatario.set(actual)

        opciones_materiales = ["Todas las Academias"] + self._academias
        actual_mat = self.combo_mat_categoria.get()
        if actual_mat not in opciones_materiales:
            opciones_materiales.append(actual_mat)
        self.combo_mat_categoria.configure(values=opciones_materiales)
        self.combo_mat_categoria.set(actual_mat)

        opciones_filtro = (
            ["Todos los destinatarios", "Todas las Academias", "Solo Coordinadores"]
            + self._academias
        )
        actual_filtro = self.combo_destinatario_filtro.get()
        if actual_filtro not in opciones_filtro:
            opciones_filtro.append(actual_filtro)
        self.combo_destinatario_filtro.configure(values=opciones_filtro)
        self.combo_destinatario_filtro.set(actual_filtro)

    def limpiar_filtros_avisos(self):
        limpiar_entry(self.entry_busqueda_avisos)
        limpiar_entry(self.entry_fecha_evento_filtro)
        self.combo_orden_avisos.set("Más reciente")
        self.combo_destinatario_filtro.set("Todos los destinatarios")
        self._aplicar_filtros_avisos()

    def limpiar_filtros_materiales(self):
        limpiar_entry(self.entry_busqueda_materiales)
        limpiar_entry(self.entry_fecha_publicacion_filtro)
        self.combo_orden_materiales.set("Más reciente")
        self.combo_academia_filtro_materiales.set("Todas las categorías")
        self._aplicar_filtros_materiales()

    def _aplicar_filtros_avisos(self):
        if not hasattr(self, "combo_destinatario_filtro"):
            return

        consulta = self.entry_busqueda_avisos.get().strip()
        fecha_evento = self.entry_fecha_evento_filtro.get().strip()
        orden = self.combo_orden_avisos.get()
        destinatario = self.combo_destinatario_filtro.get()

        filtrados = []
        for aviso in self._avisos:
            if (
                destinatario not in ("Todos los destinatarios", "")
                and aviso.get('destinatario') != destinatario
            ):
                continue
            if not fecha_coincide(aviso.get('fecha_evento'), fecha_evento):
                continue
            if not coincide_busqueda(
                consulta,
                aviso.get('titulo'),
                aviso.get('emisor'),
                aviso.get('detalle'),
                aviso.get('destinatario'),
            ):
                continue
            filtrados.append(aviso)

        filtrados.sort(
            key=lambda a: parse_fecha(a.get('fecha_publicacion')) or datetime.min,
            reverse=(orden != "Más antiguo")
        )

        self._renderizar_avisos(filtrados)
        self._actualizar_contadores_avisos(len(filtrados))

    def _aplicar_filtros_materiales(self):
        if not hasattr(self, "combo_academia_filtro_materiales"):
            return

        consulta = self.entry_busqueda_materiales.get().strip()
        fecha_publicacion = self.entry_fecha_publicacion_filtro.get().strip()
        orden = self.combo_orden_materiales.get()
        categoria = self.combo_academia_filtro_materiales.get()

        filtrados = []
        for material in self._materiales:
            if (
                categoria not in ("Todas las categorías", "")
                and material.get('categoria') != categoria
            ):
                continue
            if not fecha_coincide(material.get('fecha_publicacion'), fecha_publicacion):
                continue
            if not coincide_busqueda(
                consulta,
                material.get('nombre'),
                material.get('descripcion'),
                material.get('enlace'),
                material.get('categoria'),
            ):
                continue
            filtrados.append(material)

        filtrados.sort(
            key=lambda m: parse_fecha(m.get('fecha_publicacion')) or datetime.min,
            reverse=(orden != "Más antiguo")
        )

        self._renderizar_materiales(filtrados)
        self._actualizar_contadores_materiales(len(filtrados))

    def _actualizar_contadores_avisos(self, mostrados):
        total = len(self._avisos)
        self.lbl_contador_avisos.configure(text=str(total))
        if mostrados == total:
            self.lbl_resumen_filtros_avisos.configure(text=f"{total} aviso{'s' if total != 1 else ''}.")
        else:
            self.lbl_resumen_filtros_avisos.configure(
                text=f"Mostrando {mostrados} de {total}."
            )

    def _actualizar_contadores_materiales(self, mostrados):
        total = len(self._materiales)
        self.lbl_contador_materiales.configure(text=str(total))
        if mostrados == total:
            self.lbl_resumen_filtros_materiales.configure(
                text=f"{total} material{'es' if total != 1 else ''}."
            )
        else:
            self.lbl_resumen_filtros_materiales.configure(
                text=f"Mostrando {mostrados} de {total}."
            )

    def _actualizar_opciones_filtro_avisos(self):
        base = ["Todos los destinatarios", "Todas las Academias", "Solo Coordinadores"]
        valores = base + self._academias
        for aviso in self._avisos:
            destinatario = aviso.get('destinatario')
            if destinatario and destinatario not in valores:
                valores.append(destinatario)
        actual = self.combo_destinatario_filtro.get()
        if actual not in valores:
            actual = "Todos los destinatarios"
        self.combo_destinatario_filtro.configure(values=valores)
        self.combo_destinatario_filtro.set(actual)

    def _actualizar_opciones_filtro_materiales(self):
        valores = ["Todas las categorías"]
        for material in self._materiales:
            categoria = material.get('categoria')
            if categoria and categoria not in valores:
                valores.append(categoria)
        actual = self.combo_academia_filtro_materiales.get()
        if actual not in valores:
            actual = "Todas las categorías"
        self.combo_academia_filtro_materiales.configure(values=valores)
        self.combo_academia_filtro_materiales.set(actual)

    # ==================================================================
    # CALENDARIO
    # ==================================================================
    def _abrir_popup_calendario(self, al_confirmar, fecha_inicial=None):
        if not HAS_CUSTOM_CALENDAR:
            messagebox.showinfo("Información", "El componente de calendario no está disponible.")
            return

        try:
            popup = ctk.CTkToplevel(self)
            popup.title("Seleccionar Fecha")
            popup.geometry("320x360")
            popup.resizable(False, False)
            popup.attributes("-topmost", True)
            try:
                popup.attributes("-toolwindow", True)
            except Exception:
                pass
            popup.transient(self.winfo_toplevel())

            raiz = self.winfo_toplevel()
            x = raiz.winfo_rootx() + (raiz.winfo_width() - 320) // 2
            y = raiz.winfo_rooty() + (raiz.winfo_height() - 360) // 2
            popup.geometry(f"320x360+{max(8, x)}+{max(8, y)}")

            cal_frame = ctk.CTkFrame(popup, fg_color="white")
            cal_frame.pack(expand=True, fill="both", padx=10, pady=10)

            cal = CustomCalendar(cal_frame)
            cal.pack(expand=True, fill="both")

            def confirmar_fecha():
                al_confirmar(cal.get_date())
                popup.destroy()

            ctk.CTkButton(
                popup, text="Confirmar Fecha", fg_color=COLOR_PRIMARIO,
                hover_color=COLOR_PRIMARIO_HOVER, command=confirmar_fecha
            ).pack(pady=10)

            cal.select_date(fecha_inicial or datetime.now().date())
            popup.after(100, lambda: (popup.lift(), popup.focus_force()))
        except Exception as e:
            print(f"Error abriendo calendario: {e}")

    def abrir_calendario_avisos_popup(self):
        def asignar(fecha_res):
            self.fecha_seleccionada = fecha_res.strftime("%Y-%m-%d")
            self._escribir_entry(self.entry_aviso_fecha, self.fecha_seleccionada)

        self._abrir_popup_calendario(asignar, parse_fecha(self.entry_aviso_fecha.get()))

    def _abrir_calendario_filtro(self, entry, al_cambiar=None):
        def asignar(fecha_res):
            self._escribir_entry(entry, fecha_res.strftime("%Y-%m-%d"))
            if callable(al_cambiar):
                al_cambiar()

        self._abrir_popup_calendario(asignar, parse_fecha(entry.get()))

    # ==================================================================
    # ARCHIVOS
    # ==================================================================
    def seleccionar_archivos(self):
        """Abre el explorador para elegir varios archivos de cualquier carpeta."""
        if not self.puede_subir_archivos:
            return

        seleccion = filedialog.askopenfilenames(
            title="Seleccionar archivos de material",
            filetypes=[
                ("Todos los archivos", "*.*"),
                ("Documentos PDF", "*.pdf"),
                ("Documentos de Word", "*.docx *.doc"),
                ("Hojas de cálculo", "*.xlsx *.xls *.csv"),
                ("Presentaciones", "*.pptx *.ppt"),
                ("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("Videos", "*.mp4 *.avi *.mkv *.mov"),
                ("Archivos comprimidos", "*.zip *.rar *.7z"),
            ],
        )
        if not seleccion:
            return

        existentes = {
            os.path.normcase(os.path.abspath(ruta))
            for ruta in self.archivos_seleccionados
        }
        for ruta in seleccion:
            ruta_absoluta = os.path.abspath(ruta)
            clave = os.path.normcase(ruta_absoluta)
            if clave in existentes:
                continue
            self.archivos_seleccionados.append(ruta_absoluta)
            existentes.add(clave)

        self._refrescar_archivos_seleccionados()

    def _refrescar_archivos_seleccionados(self):
        for widget in self.container_archivos_seleccionados.winfo_children():
            widget.destroy()

        total = len(self.archivos_seleccionados)
        if total:
            self.lbl_resumen_archivos.configure(
                text=f"{total} archivo{'s' if total != 1 else ''} seleccionado{'s' if total != 1 else ''}."
            )
            self.btn_subir_archivos.configure(state="normal")
        else:
            self.lbl_resumen_archivos.configure(text="No has seleccionado archivos.")
            self.btn_subir_archivos.configure(state="disabled")
            return

        for ruta in self.archivos_seleccionados:
            fila = ctk.CTkFrame(
                self.container_archivos_seleccionados,
                fg_color="white", corner_radius=10,
                border_width=0, border_color=COLOR_BORDE
            )
            fila.pack(fill="x", pady=2)

            ctk.CTkLabel(
                fila, text=f"  {os.path.basename(ruta)}",
                image=icono("file-text", 13, COLOR_SECUNDARIO),
                compound="left",
                font=fuente_dato(10), text_color=COLOR_TEXTO, anchor="w"
            ).pack(side="left", padx=(8, 5), pady=4)

            try:
                tamano = self._formatear_tamano(os.path.getsize(ruta))
            except OSError:
                tamano = "tamaño desconocido"

            ctk.CTkLabel(
                fila, text=tamano,
                font=fuente_dato(9), text_color=COLOR_TEXTO_SUAVE
            ).pack(side="left", pady=4)

            ctk.CTkButton(
                fila, text="", image=icono("x", 12, "#B03A2E"),
                width=28, height=22,
                fg_color="transparent", hover_color="#FDEDEC",
                border_width=0, border_color="#E6B0AA",
                command=lambda r=ruta: self.quitar_archivo(r)
            ).pack(side="right", padx=6, pady=3)

    @staticmethod
    def _formatear_tamano(cantidad_bytes):
        tamano = float(cantidad_bytes)
        for unidad in ("B", "KB", "MB", "GB"):
            if tamano < 1024 or unidad == "GB":
                return f"{tamano:.0f} {unidad}" if unidad == "B" else f"{tamano:.1f} {unidad}"
            tamano /= 1024
        return f"{tamano:.1f} GB"

    def quitar_archivo(self, ruta):
        clave = os.path.normcase(os.path.abspath(ruta))
        self.archivos_seleccionados = [
            actual
            for actual in self.archivos_seleccionados
            if os.path.normcase(os.path.abspath(actual)) != clave
        ]
        self._refrescar_archivos_seleccionados()

    def limpiar_archivos_seleccionados(self):
        self.archivos_seleccionados = []
        self._refrescar_archivos_seleccionados()

    def obtener_archivos_seleccionados(self):
        return list(self.archivos_seleccionados)

    # ==================================================================
    # DATOS DE LOS FORMULARIOS
    # ==================================================================
    def obtener_datos_avisos(self):
        fecha_ingresada = self.entry_aviso_fecha.get().strip() or self.fecha_seleccionada
        fecha = parse_fecha(fecha_ingresada)
        fecha_iso = fecha.strftime("%Y-%m-%d") if fecha else fecha_ingresada
        return {
            "titulo": self.entry_aviso_titulo.get().strip(),
            "emisor": self.entry_aviso_emisor.get().strip(),
            "destinatario": self.combo_aviso_destinatario.get(),
            "fecha_evento": fecha_iso,
            "fecha_hora": f"{fecha_iso} 12:00",
            "detalle": self.entry_aviso_detalle.get().strip()
        }

    def obtener_datos_materiales(self):
        return {
            "nombre": self.entry_mat_nombre.get().strip(),
            "categoria": self.combo_mat_categoria.get(),
            "descripcion": self.entry_mat_descripcion.get().strip(),
            "enlace": self.entry_mat_enlace.get().strip()
        }

    def limpiar_formularios(self):
        self.limpiar_formulario_aviso()
        self.limpiar_formulario_material()

    # ==================================================================
    # LISTADOS
    # ==================================================================
    def mostrar_cargando(self):
        """Esqueletos para avisos y materiales mientras llegan los datos."""
        for contenedor, tono in (
            (self.container_lista_avisos, "verde"),
            (self.container_lista_materiales, "bronce"),
        ):
            for widget in contenedor.winfo_children():
                widget.destroy()
            SkeletonLista(contenedor, filas=3, tono=tono, compacto=True)

    def mostrar_avisos(self, lista):
        self._avisos = list(lista or [])
        self._actualizar_opciones_filtro_avisos()
        self._aplicar_filtros_avisos()

    def mostrar_materiales(self, lista):
        self._materiales = list(lista or [])
        self._actualizar_opciones_filtro_materiales()
        self._aplicar_filtros_materiales()

    def _renderizar_avisos(self, lista):
        for widget in self.container_lista_avisos.winfo_children():
            widget.destroy()

        if not lista:
            mensaje = (
                "No hay avisos publicados."
                if not self._avisos
                else "No hay avisos que coincidan con la búsqueda o los filtros."
            )
            ctk.CTkLabel(
                self.container_lista_avisos, text=mensaje,
                font=fuente(11), text_color=COLOR_TEXTO_SUAVE
            ).pack(pady=20)
            return

        for aviso in lista:
            es_nuevo = es_reciente(aviso.get('fecha_publicacion'))
            paleta = paleta_tarjeta("verde")
            card = crear_tarjeta_tinte(self.container_lista_avisos, "verde")
            if es_nuevo:
                card.configure(border_color=COLOR_NUEVO)
            card.pack(fill="x", pady=4, padx=1)

            top_line = ctk.CTkFrame(card, fg_color="transparent")
            top_line.pack(fill="x", padx=10, pady=(8, 3))
            top_line.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                top_line, text="  " + (aviso.get('titulo') or "Aviso"),
                image=icono("megaphone", 14, paleta["acento"]),
                compound="left",
                font=fuente_titulo(12), text_color=COLOR_PRIMARIO,
                anchor="w", justify="left", wraplength=300
            ).grid(row=0, column=0, sticky="w")

            if es_nuevo:
                crear_badge(
                    top_line, "NUEVO", color=COLOR_NUEVO, ancho=56
                ).grid(row=0, column=1, padx=(5, 0), sticky="e")

            meta = ctk.CTkFrame(card, fg_color="transparent")
            meta.pack(fill="x", padx=10, pady=(0, 2))

            fecha_evento = formatear_fecha_hora(aviso.get('fecha_evento'), incluir_hora=False)
            ctk.CTkLabel(
                meta, text=f"  De: {aviso.get('emisor') or '—'}   |   Evento: {fecha_evento}",
                image=icono("user-round", 12, GRIS_OSCURO),
                compound="left",
                font=fuente(10), text_color=COLOR_TEXTO,
                anchor="w", justify="left", wraplength=330
            ).pack(anchor="w")

            ctk.CTkLabel(
                meta, text=f"  Para: {aviso.get('destinatario') or 'General'}",
                image=icono("users-round", 12, GRIS_OSCURO),
                compound="left",
                font=fuente(10), text_color=COLOR_TEXTO,
                anchor="w", justify="left", wraplength=330
            ).pack(anchor="w")

            ctk.CTkLabel(
                meta, text=f"  Publicado: {formatear_fecha_hora(aviso.get('fecha_publicacion'))}",
                image=icono("clock-3", 11, GRIS_OSCURO),
                compound="left",
                font=fuente_dato(9), text_color=COLOR_TEXTO_SUAVE, anchor="w"
            ).pack(anchor="w")

            ctk.CTkLabel(
                card, text=aviso.get('detalle') or "Sin contenido.",
                font=fuente(10), text_color=COLOR_TEXTO_SUAVE,
                anchor="w", justify="left", wraplength=330
            ).pack(anchor="w", padx=10, pady=(4, 4))

            if (self.puede_editar and self.on_editar_aviso) or (
                self.puede_eliminar and self.on_eliminar_aviso
            ):
                footer = ctk.CTkFrame(card, fg_color="transparent")
                footer.pack(fill="x", padx=10, pady=(0, 8))

                if self.puede_editar and self.on_editar_aviso:
                    crear_boton_editar(
                        footer, lambda a=aviso: self.on_editar_aviso(a)
                    ).pack(side="right", padx=(5, 0))

                if self.puede_eliminar and self.on_eliminar_aviso:
                    crear_boton_eliminar(
                        footer,
                        lambda aid=aviso.get('id_aviso'): self.on_eliminar_aviso(aid)
                    ).pack(side="right")

    @staticmethod
    def _texto_enlace(enlace):
        enlace = (enlace or "").strip()
        if not enlace:
            return "Sin enlace"

        def corto(texto, limite=20):
            return texto if len(texto) <= limite else texto[: limite - 1] + "…"

        if os.path.isfile(enlace):
            return f"Abrir archivo: {corto(os.path.basename(enlace))}"
        if os.path.isabs(enlace):
            return f"No encontrado: {corto(os.path.basename(enlace))}"
        return corto(enlace, 46)

    def abrir_enlace(self, enlace):
        """Abre un archivo local o un enlace web registrado en el material."""
        enlace = (enlace or "").strip()
        if not enlace:
            messagebox.showwarning("Sin enlace", "Este material no tiene un enlace registrado.")
            return

        if os.path.exists(enlace):
            try:
                if hasattr(os, "startfile"):
                    os.startfile(enlace)
                else:
                    webbrowser.open(f"file://{os.path.abspath(enlace)}")
            except Exception as e:
                messagebox.showerror("No se pudo abrir", f"No se pudo abrir el archivo:\n{e}")
            return

        if enlace.lower().startswith(("http://", "https://")):
            webbrowser.open(enlace)
            return

        messagebox.showwarning(
            "Archivo no disponible",
            "El archivo ya no se encuentra en la ruta registrada:\n\n" + enlace
        )

    def _renderizar_materiales(self, lista):
        for widget in self.container_lista_materiales.winfo_children():
            widget.destroy()

        if not lista:
            mensaje = (
                "No hay materiales disponibles."
                if not self._materiales
                else "No hay materiales que coincidan con la búsqueda o los filtros."
            )
            ctk.CTkLabel(
                self.container_lista_materiales, text=mensaje,
                font=fuente(11), text_color=COLOR_TEXTO_SUAVE
            ).pack(pady=20)
            return

        for mat in lista:
            es_nuevo = es_reciente(mat.get('fecha_publicacion'))
            paleta = paleta_tarjeta("bronce")
            card = crear_tarjeta_tinte(self.container_lista_materiales, "bronce")
            if es_nuevo:
                card.configure(border_color=COLOR_NUEVO)
            card.pack(fill="x", pady=4, padx=1)

            top_line = ctk.CTkFrame(card, fg_color="transparent")
            top_line.pack(fill="x", padx=10, pady=(8, 3))
            top_line.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                top_line, text="  " + (mat.get('nombre') or "Material"),
                image=icono("folder-open", 14, paleta["acento"]),
                compound="left",
                font=fuente_titulo(12), text_color=COLOR_SECUNDARIO,
                anchor="w", justify="left", wraplength=300
            ).grid(row=0, column=0, sticky="w")

            if es_nuevo:
                crear_badge(
                    top_line, "NUEVO", color=COLOR_NUEVO, ancho=56
                ).grid(row=0, column=1, padx=(5, 0), sticky="e")

            meta = ctk.CTkFrame(card, fg_color="transparent")
            meta.pack(fill="x", padx=10, pady=(0, 2))

            ctk.CTkLabel(
                meta, text=f"  {mat.get('categoria') or 'General'}",
                image=icono("tag", 12, paleta["acento"]),
                compound="left",
                font=fuente_etiqueta(9), text_color=COLOR_TEXTO,
                anchor="w", justify="left", wraplength=330
            ).pack(anchor="w")

            ctk.CTkLabel(
                meta, text=f"  Publicado: {formatear_fecha_hora(mat.get('fecha_publicacion'))}",
                image=icono("clock-3", 11, GRIS_OSCURO),
                compound="left",
                font=fuente_dato(9), text_color=COLOR_TEXTO_SUAVE, anchor="w"
            ).pack(anchor="w")

            ctk.CTkLabel(
                card, text=mat.get('descripcion') or "Sin descripción.",
                font=fuente(10), text_color=COLOR_TEXTO_SUAVE,
                anchor="w", justify="left", wraplength=330
            ).pack(anchor="w", padx=10, pady=(4, 2))

            enlace_material = mat.get('enlace')
            icono_enlace = "paperclip" if os.path.isfile(enlace_material or "") else "link"
            etiqueta_enlace = ctk.CTkLabel(
                card, text="  " + self._texto_enlace(enlace_material),
                image=icono(icono_enlace, 12, "#2B7BB9"),
                compound="left",
                font=fuente_dato(9, "underline"), text_color="#2B7BB9",
                cursor="hand2", anchor="w", justify="left", wraplength=250
            )
            etiqueta_enlace.pack(anchor="w", padx=10, pady=(0, 3))
            etiqueta_enlace.bind(
                "<Button-1>",
                lambda event, enlace=enlace_material: self.abrir_enlace(enlace)
            )

            if (self.puede_editar and self.on_editar_material) or (
                self.puede_eliminar and self.on_eliminar_material
            ):
                footer = ctk.CTkFrame(card, fg_color="transparent")
                footer.pack(fill="x", padx=10, pady=(0, 8))

                if self.puede_editar and self.on_editar_material:
                    crear_boton_editar(
                        footer, lambda m=mat: self.on_editar_material(m)
                    ).pack(side="right", padx=(5, 0))

                if self.puede_eliminar and self.on_eliminar_material:
                    crear_boton_eliminar(
                        footer,
                        lambda mid=mat.get('id_material'): self.on_eliminar_material(mid)
                    ).pack(side="right")

    # ==================================================================
    # UTILIDADES
    # ==================================================================
    @staticmethod
    def _escribir_entry(entry, texto):
        if texto:
            entry.delete(0, "end")
            entry.insert(0, texto)
        else:
            limpiar_entry(entry)

    def ir_a_avisos(self):
        """Muestra la parte superior de la lista de avisos más recientes."""
        try:
            self.container_lista_avisos.update_idletasks()
            self.container_lista_avisos._parent_canvas.yview_moveto(0)
        except Exception:
            pass

    def ir_a_materiales(self):
        """Muestra la parte superior de la lista de materiales más recientes."""
        try:
            self.container_lista_materiales.update_idletasks()
            self.container_lista_materiales._parent_canvas.yview_moveto(0)
        except Exception:
            pass
