import customtkinter as ctk

from views.typography import (
    fuente,
    fuente_dato,
    fuente_etiqueta,
    fuente_titulo,
)
from datetime import datetime
from tkinter import messagebox

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
    normalizar_texto,
    paleta_tarjeta,
    parse_fecha,
)
from views.time_picker import TimePicker


class ConvocatoriasView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        self.grid_columnconfigure(0, weight=0, minsize=360)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.COLOR_LABEL = "#222222"
        self.COLOR_ENTRY_BG = COLOR_INPUT_BG
        self.COLOR_ENTRY_BORDER = COLOR_INPUT_BORDER
        self.COLOR_TEXT_INSIDE = "#111111"
        self.COLOR_PLACEHOLDER = "#777777"

        self.fecha_seleccionada = datetime.now().strftime("%Y-%m-%d")

        # Permisos y callbacks administrados por el DashboardController.
        self.puede_eliminar = False
        self.puede_editar = False
        self.on_eliminar = None
        self.on_editar = None
        self.on_cancelar_edicion = None

        self._en_edicion = False
        self._convocatorias = []
        self._academias = []

        # ============================================================
        # PANEL IZQUIERDO: FORMULARIO DE CREACIÓN / EDICIÓN
        # ============================================================
        self.frame_form = ctk.CTkFrame(self, fg_color="white", corner_radius=18)
        self.frame_form.grid(row=0, column=0, padx=(0, 8), pady=0, sticky="nsew")

        header_form = ctk.CTkFrame(self.frame_form, fg_color="transparent")
        header_form.pack(fill="x", padx=20, pady=(8, 4))
        ctk.CTkLabel(
            header_form, text="PROGRAMACIÓN",
            font=fuente_etiqueta(8), text_color=COLOR_SECUNDARIO
        ).pack(anchor="w")
        self.lbl_titulo_form = ctk.CTkLabel(
            header_form,
            text="  Nueva Convocatoria",
            image=icono("calendar-days", 19, COLOR_PRIMARIO),
            compound="left",
            font=fuente_titulo(17),
            text_color=COLOR_PRIMARIO
        )
        self.lbl_titulo_form.pack(anchor="w")

        # Tipo de Sesión
        ctk.CTkLabel(
            self.frame_form, text="TIPO DE SESIÓN",
            font=fuente_etiqueta(9), text_color="#4B5563"
        ).pack(anchor="w", padx=20, pady=(2, 0))
        self.combo_tipo = Dropdown(
            self.frame_form, values=["Ordinaria", "Extraordinaria"],
            width=320, height=30, font=fuente(11), dropdown_font=fuente(11)
        )
        self.combo_tipo.pack(fill="x", padx=20, pady=(0, 5))

        # Catálogo de Academia / Destinatario (Dinámico)
        ctk.CTkLabel(
            self.frame_form, text="ACADEMIA / DESTINATARIO",
            font=fuente_etiqueta(9), text_color="#4B5563"
        ).pack(anchor="w", padx=20, pady=(2, 0))
        self.combo_academia = Dropdown(
            self.frame_form,
            values=["Cargando academias..."],
            width=320, height=30, font=fuente(11), dropdown_font=fuente(11)
        )
        self.combo_academia.pack(fill="x", padx=20, pady=(0, 5))

        # Fecha y Hora
        self.frame_fechas = ctk.CTkFrame(self.frame_form, fg_color="transparent")
        self.frame_fechas.pack(fill="x", padx=20, pady=(2, 4))
        self.frame_fechas.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            self.frame_fechas, text="FECHA DE LA SESIÓN",
            font=fuente_etiqueta(9), text_color="#4B5563"
        ).grid(row=0, column=0, sticky="w")
        self.box_fecha = ctk.CTkFrame(self.frame_fechas, fg_color="transparent")
        self.box_fecha.grid(row=1, column=0, padx=(0, 5), sticky="ew")
        self.box_fecha.grid_columnconfigure(0, weight=1)

        self.entry_fecha = ctk.CTkEntry(
            self.box_fecha,
            fg_color=self.COLOR_ENTRY_BG,
            border_color=self.COLOR_ENTRY_BORDER,
            text_color=self.COLOR_TEXT_INSIDE,
            font=fuente_dato(11)
        )
        self.entry_fecha.insert(0, self.fecha_seleccionada)
        self.entry_fecha.grid(row=0, column=0, padx=(0, 4), sticky="ew")

        self.btn_calendario_conv = ctk.CTkButton(
            self.box_fecha, text="", image=icono("calendar", 16, "#FFFFFF"),
            width=36, height=30,
            fg_color=COLOR_SECUNDARIO, hover_color=COLOR_SECUNDARIO_HOVER,
            command=self.abrir_calendario_conv_popup
        )
        self.btn_calendario_conv.grid(row=0, column=1)

        ctk.CTkLabel(
            self.frame_fechas, text="HORA (24 H)",
            font=fuente_etiqueta(9), text_color="#4B5563"
        ).grid(row=0, column=1, sticky="w")
        self.hora_picker = TimePicker(self.frame_fechas, initial="10:00")
        self.hora_picker.grid(row=1, column=1, padx=(5, 0), sticky="ew")

        # Documento Oficial / Acta (RF-13)
        ctk.CTkLabel(
            self.frame_form, text="DOCUMENTO OFICIAL / ACTA (OPCIONAL)",
            font=fuente_etiqueta(9), text_color="#4B5563"
        ).pack(anchor="w", padx=20, pady=(2, 0))
        self.entry_doc_oficial = ctk.CTkEntry(
            self.frame_form,
            placeholder_text="Ej. Acta_Sesion_Ordinaria_Nov.pdf",
            fg_color=self.COLOR_ENTRY_BG,
            border_color=self.COLOR_ENTRY_BORDER,
            text_color=self.COLOR_TEXT_INSIDE,
            placeholder_text_color=self.COLOR_PLACEHOLDER,
            font=fuente_dato(10)
        )
        self.entry_doc_oficial.pack(fill="x", padx=20, pady=(0, 4))

        ctk.CTkLabel(
            self.frame_form,
            text="  Recuerda: mínimo 72 horas de anticipación.",
            image=icono("triangle-alert", 14, COLOR_SECUNDARIO),
            compound="left",
            font=fuente(10, "italic"), text_color=COLOR_SECUNDARIO
        ).pack(anchor="w", padx=20, pady=(0, 3))

        # Orden del día
        ctk.CTkLabel(
            self.frame_form, text="ORDEN DEL DÍA",
            font=fuente_etiqueta(9), text_color="#4B5563"
        ).pack(anchor="w", padx=20, pady=(2, 0))
        self.txt_orden_dia = ctk.CTkTextbox(
            self.frame_form, height=64, corner_radius=12,
            fg_color=self.COLOR_ENTRY_BG,
            border_color=self.COLOR_ENTRY_BORDER,
            border_width=0,
            text_color=self.COLOR_TEXT_INSIDE,
            font=fuente(11)
        )
        self.txt_orden_dia.pack(fill="x", padx=20, pady=(0, 6))

        # Acciones en una sola fila: el botón de cancelar aparece a la derecha
        # solo durante la edición, sin empujar el botón principal fuera del panel.
        acciones_form = ctk.CTkFrame(self.frame_form, fg_color="transparent")
        acciones_form.pack(fill="x", padx=20, pady=(0, 8))
        acciones_form.grid_columnconfigure(0, weight=1)

        self.btn_guardar = ctk.CTkButton(
            acciones_form, text="  Emitir Convocatoria",
            image=icono("send", 16, "#FFFFFF"),
            compound="left",
            fg_color=COLOR_SECUNDARIO, hover_color=COLOR_SECUNDARIO_HOVER,
            font=fuente_titulo(12), height=38
        )
        self.btn_guardar.grid(row=0, column=0, sticky="ew")

        self.btn_cancelar_edicion = ctk.CTkButton(
            acciones_form, text="Cancelar", width=92,
            fg_color="transparent", hover_color="#F0F4F1",
            border_width=0, border_color=COLOR_BORDE,
            text_color=COLOR_TEXTO_SUAVE, font=fuente(10, "bold"),
            height=30, command=self._cancelar_edicion
        )
        self.btn_cancelar_edicion.grid(
            row=0, column=1, padx=(8, 0), sticky="ew"
        )
        self.btn_cancelar_edicion.grid_remove()

        # ============================================================
        # PANEL DERECHO: BÚSQUEDA, FILTROS E HISTORIAL
        # ============================================================
        self.frame_lista = ctk.CTkFrame(self, fg_color="white", corner_radius=18)
        self.frame_lista.grid(row=0, column=1, padx=(0, 0), pady=0, sticky="nsew")
        self.frame_lista.grid_rowconfigure(2, weight=1)
        self.frame_lista.grid_columnconfigure(0, weight=1)

        encabezado = ctk.CTkFrame(self.frame_lista, fg_color="transparent")
        encabezado.grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 6))
        encabezado.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            encabezado, text="HISTORIAL",
            font=fuente_etiqueta(8), text_color=COLOR_PRIMARIO
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            encabezado, text="  Convocatorias Programadas",
            image=icono("calendar-days", 18, COLOR_PRIMARIO),
            compound="left",
            font=fuente_titulo(17), text_color="#333333"
        ).grid(row=1, column=0, sticky="w")

        self.lbl_contador = ctk.CTkLabel(
            encabezado, text="",
            font=fuente_dato(10), text_color=COLOR_PRIMARIO,
            fg_color="#EAF4EC", corner_radius=8, height=22
        )
        self.lbl_contador.grid(row=1, column=1, sticky="e")

        # Barra de búsqueda y filtros
        self.frame_filtros = ctk.CTkFrame(
            self.frame_lista, fg_color="#F8FAF9", corner_radius=14,
            border_width=0, border_color="#E8EDEA"
        )
        self.frame_filtros.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 8))
        self.frame_filtros.grid_columnconfigure(0, weight=1)
        self.frame_filtros.grid_columnconfigure(1, weight=0)
        self.frame_filtros.grid_columnconfigure(2, weight=0)

        self.entry_busqueda = ctk.CTkEntry(
            self.frame_filtros,
            placeholder_text="Buscar por academia, tipo, orden o documento...",
            fg_color="white", border_color=COLOR_INPUT_BORDER,
            text_color=self.COLOR_TEXT_INSIDE,
            placeholder_text_color="#8A8F98",
            font=fuente(11), height=32
        )
        self.entry_busqueda.grid(row=0, column=0, columnspan=3, padx=10, pady=(9, 4), sticky="ew")
        self.entry_busqueda.bind("<KeyRelease>", lambda _evento: self._aplicar_filtros())

        # Fecha de evento + calendario
        self.entry_fecha_filtro = ctk.CTkEntry(
            self.frame_filtros,
            placeholder_text="Fecha evento (AAAA-MM-DD)",
            fg_color="white", border_color=COLOR_INPUT_BORDER,
            text_color=self.COLOR_TEXT_INSIDE,
            placeholder_text_color="#8A8F98",
            font=fuente_dato(10), height=28
        )
        self.entry_fecha_filtro.grid(row=1, column=0, padx=(10, 4), pady=3, sticky="ew")
        self.entry_fecha_filtro.bind("<KeyRelease>", lambda _evento: self._aplicar_filtros())

        self.btn_calendario_filtro = ctk.CTkButton(
            self.frame_filtros, text="", image=icono("calendar", 14, COLOR_PRIMARIO),
            width=30, height=28,
            fg_color="#EAF4EC", hover_color="#D8EBDD",
            command=lambda: self._abrir_calendario_filtro(self.entry_fecha_filtro)
        )
        self.btn_calendario_filtro.grid(row=1, column=1, padx=(0, 4), pady=3)

        self.combo_orden = Dropdown(
            self.frame_filtros, values=["Más reciente", "Más antiguo"],
            width=126, height=28, font=fuente(10), dropdown_font=fuente(10),
            command=lambda _valor: self._aplicar_filtros()
        )
        self.combo_orden.grid(row=1, column=2, padx=(0, 10), pady=3, sticky="e")

        self.combo_tipo_filtro = Dropdown(
            self.frame_filtros,
            values=["Todos los tipos", "Ordinaria", "Extraordinaria"],
            width=150, height=28, font=fuente(10), dropdown_font=fuente(10),
            command=lambda _valor: self._aplicar_filtros()
        )
        self.combo_tipo_filtro.grid(row=2, column=0, padx=(10, 4), pady=3, sticky="ew")

        self.combo_academia_filtro = Dropdown(
            self.frame_filtros, values=["Todas las academias"],
            width=150, height=28, font=fuente(10), dropdown_font=fuente(10),
            command=lambda _valor: self._aplicar_filtros()
        )
        self.combo_academia_filtro.grid(row=2, column=1, columnspan=2, padx=(0, 10), pady=3, sticky="ew")

        pie_filtros = ctk.CTkFrame(self.frame_filtros, fg_color="transparent")
        pie_filtros.grid(row=3, column=0, columnspan=3, padx=10, pady=(1, 8), sticky="ew")
        pie_filtros.grid_columnconfigure(0, weight=1)

        self.lbl_resumen_filtros = ctk.CTkLabel(
            pie_filtros, text="",
            font=fuente(10), text_color=COLOR_TEXTO_SUAVE, anchor="w"
        )
        self.lbl_resumen_filtros.grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            pie_filtros, text="  Limpiar filtros", width=104, height=24,
            image=icono("x", 11, COLOR_PRIMARIO),
            compound="left",
            fg_color="transparent", hover_color="#EAF4EC",
            border_width=0, border_color="#D5E3D8",
            text_color=COLOR_PRIMARIO, font=fuente(10, "bold"),
            command=self.limpiar_filtros
        ).grid(row=0, column=1, sticky="e")

        self.scroll_convocatorias = ctk.CTkScrollableFrame(
            self.frame_lista, fg_color="transparent"
        )
        self.scroll_convocatorias.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 12))

    # ------------------------------------------------------------------
    # Catálogos y filtros
    # ------------------------------------------------------------------
    def actualizar_opciones_academias(self, lista_academias):
        """Puebla los desplegables con las academias provenientes de la BD."""
        self._academias = list(lista_academias or [])
        if not self._academias:
            return

        academia_actual = self.combo_academia.get()
        if academia_actual not in self._academias:
            academia_actual = self._academias[0]
        self.combo_academia.configure(values=self._academias)
        self.combo_academia.set(academia_actual)

        opciones_filtro = ["Todas las academias"] + self._academias
        filtro_actual = self.combo_academia_filtro.get()
        self.combo_academia_filtro.configure(values=opciones_filtro)
        if filtro_actual not in opciones_filtro:
            filtro_actual = "Todas las academias"
        self.combo_academia_filtro.set(filtro_actual)

    def limpiar_filtros(self):
        limpiar_entry(self.entry_busqueda)
        limpiar_entry(self.entry_fecha_filtro)
        self.combo_orden.set("Más reciente")
        self.combo_tipo_filtro.set("Todos los tipos")
        self.combo_academia_filtro.set("Todas las academias")
        self._aplicar_filtros()

    def _aplicar_filtros(self):
        consulta = self.entry_busqueda.get().strip()
        fecha_evento = self.entry_fecha_filtro.get().strip()
        orden = self.combo_orden.get()
        tipo = self.combo_tipo_filtro.get()
        academia = self.combo_academia_filtro.get()

        filtradas = []
        for conv in self._convocatorias:
            if tipo not in ("Todos los tipos", "") and conv.get('tipo') != tipo:
                continue
            if academia not in ("Todas las academias", "") and conv.get('academia') != academia:
                continue
            if not fecha_coincide(conv.get('fecha_hora'), fecha_evento):
                continue
            if not coincide_busqueda(
                consulta,
                conv.get('academia'),
                conv.get('tipo'),
                conv.get('orden_dia'),
                conv.get('documento_oficial'),
            ):
                continue
            filtradas.append(conv)

        filtradas.sort(
            key=lambda c: parse_fecha(c.get('fecha_publicacion')) or datetime.min,
            reverse=(orden != "Más antiguo")
        )

        self._renderizar_convocatorias(filtradas)

        total = len(self._convocatorias)
        mostradas = len(filtradas)
        self.lbl_contador.configure(text=f"{mostradas} de {total}")
        if mostradas == total:
            self.lbl_resumen_filtros.configure(text="Mostrando todas las convocatorias.")
        else:
            self.lbl_resumen_filtros.configure(
                text=f"Filtros activos: {mostradas} coincidencia{'s' if mostradas != 1 else ''}."
            )

    def _renderizar_convocatorias(self, lista):
        for widget in self.scroll_convocatorias.winfo_children():
            widget.destroy()

        if not lista:
            mensaje = (
                "No hay convocatorias programadas."
                if not self._convocatorias
                else "No hay convocatorias que coincidan con la búsqueda o los filtros."
            )
            ctk.CTkLabel(
                self.scroll_convocatorias,
                text=mensaje,
                font=fuente(11),
                text_color=COLOR_TEXTO_SUAVE
            ).pack(pady=24)
            return

        for conv in lista:
            es_nuevo = es_reciente(conv.get('fecha_publicacion'))
            paleta = paleta_tarjeta("azul")
            card = crear_tarjeta_tinte(self.scroll_convocatorias, "azul")
            if es_nuevo:
                card.configure(border_color=COLOR_NUEVO)
            card.pack(fill="x", pady=5, padx=2)

            top_frame = ctk.CTkFrame(card, fg_color="transparent")
            top_frame.pack(fill="x", padx=12, pady=(10, 3))
            top_frame.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                top_frame,
                text="  " + (conv.get('academia') or "General"),
                image=icono("school", 15, paleta["acento"]),
                compound="left",
                font=fuente_titulo(13),
                text_color=COLOR_PRIMARIO,
                anchor="w",
                justify="left",
                wraplength=300
            ).grid(row=0, column=0, sticky="w")

            tipo = conv.get('tipo') or "—"
            color_tipo = COLOR_SECUNDARIO if tipo == "Extraordinaria" else "#6B7280"
            crear_badge(
                top_frame, tipo.upper(), color=color_tipo, ancho=105
            ).grid(row=0, column=1, padx=(8, 0), sticky="e")

            if es_nuevo:
                crear_badge(
                    top_frame, "NUEVO", color=COLOR_NUEVO, ancho=60
                ).grid(row=0, column=2, padx=(6, 0), sticky="e")

            meta = ctk.CTkFrame(card, fg_color="transparent")
            meta.pack(fill="x", padx=12, pady=(0, 2))

            ctk.CTkLabel(
                meta,
                text=f"  Sesión: {formatear_fecha_hora(conv.get('fecha_hora'))}",
                image=icono("calendar", 13, paleta["acento"]),
                compound="left",
                font=fuente_titulo(11),
                text_color=COLOR_TEXTO,
                anchor="w"
            ).pack(anchor="w")

            ctk.CTkLabel(
                meta,
                text=f"  Publicado: {formatear_fecha_hora(conv.get('fecha_publicacion'))}",
                image=icono("clock-3", 12, GRIS_OSCURO),
                compound="left",
                font=fuente_dato(9),
                text_color=COLOR_TEXTO_SUAVE,
                anchor="w"
            ).pack(anchor="w")

            if conv.get('documento_oficial'):
                ctk.CTkLabel(
                    card,
                    text=f"  Acta / Doc. oficial: {conv['documento_oficial']}",
                    image=icono("file-text", 13, "#2B7BB9"),
                    compound="left",
                    font=fuente_dato(10),
                    text_color="#2B7BB9",
                    anchor="w"
                ).pack(anchor="w", padx=12, pady=(3, 0))

            orden_limpio = str(conv.get('orden_dia') or "—").replace('\\n', '\n')
            ctk.CTkLabel(
                card,
                text=f"  Orden del día:\n{orden_limpio}",
                image=icono("list-filter", 13, GRIS_OSCURO),
                compound="left",
                font=fuente(11),
                text_color=COLOR_TEXTO_SUAVE,
                justify="left",
                anchor="w",
                wraplength=510
            ).pack(anchor="w", padx=12, pady=(4, 5))

            if (self.puede_editar and self.on_editar) or (self.puede_eliminar and self.on_eliminar):
                footer = ctk.CTkFrame(card, fg_color="transparent")
                footer.pack(fill="x", padx=12, pady=(0, 9))

                if self.puede_editar and self.on_editar:
                    crear_boton_editar(
                        footer,
                        lambda c=conv: self.on_editar(c)
                    ).pack(side="right", padx=(6, 0))

                if self.puede_eliminar and self.on_eliminar:
                    crear_boton_eliminar(
                        footer,
                        lambda cid=conv.get('id_convocatoria'): self.on_eliminar(cid)
                    ).pack(side="right")

    # ------------------------------------------------------------------
    # Modo edición
    # ------------------------------------------------------------------
    def cargar_datos_edicion(self, convocatoria):
        """Precarga el formulario con los datos de una convocatoria existente."""
        if not convocatoria:
            return

        self._en_edicion = True
        self.lbl_titulo_form.configure(
            text="  Editar Convocatoria",
            image=icono("square-pen", 18, COLOR_PRIMARIO),
        )
        self.btn_guardar.configure(
            text="  Guardar cambios",
            image=icono("save", 16, "#FFFFFF"),
            fg_color=COLOR_PRIMARIO,
            hover_color=COLOR_PRIMARIO_HOVER
        )
        self.btn_cancelar_edicion.grid()

        tipo = convocatoria.get('tipo')
        if tipo:
            self.combo_tipo.set(tipo)

        academia = convocatoria.get('academia')
        if academia:
            valores = list(self.combo_academia.cget("values"))
            if academia not in valores:
                valores.append(academia)
                self.combo_academia.configure(values=valores)
            self.combo_academia.set(academia)

        fecha_hora = parse_fecha(convocatoria.get('fecha_hora'))
        if fecha_hora:
            self.fecha_seleccionada = fecha_hora.strftime("%Y-%m-%d")
            self._escribir_entry(self.entry_fecha, self.fecha_seleccionada)
            self.hora_picker.set(fecha_hora.strftime("%H:%M"))
        else:
            self._escribir_entry(self.entry_fecha, self.fecha_seleccionada)
            self.hora_picker.set("10:00")

        self._escribir_entry(
            self.entry_doc_oficial,
            convocatoria.get('documento_oficial') or ""
        )

        self.txt_orden_dia.delete("1.0", "end")
        self.txt_orden_dia.insert("1.0", convocatoria.get('orden_dia') or "")

        try:
            self.entry_fecha.focus_set()
        except Exception:
            pass

    def salir_modo_edicion(self):
        """Restaura el formulario al estado de creación."""
        self._en_edicion = False
        self.lbl_titulo_form.configure(
            text="  Nueva Convocatoria",
            image=icono("calendar-days", 19, COLOR_PRIMARIO),
        )
        self.btn_guardar.configure(
            text="  Emitir Convocatoria",
            image=icono("send", 16, "#FFFFFF"),
            fg_color=COLOR_SECUNDARIO,
            hover_color=COLOR_SECUNDARIO_HOVER
        )
        self.btn_cancelar_edicion.grid_remove()
        self.limpiar_formulario()

    def _cancelar_edicion(self):
        if callable(self.on_cancelar_edicion):
            self.on_cancelar_edicion()
        else:
            self.salir_modo_edicion()

    @staticmethod
    def _escribir_entry(entry, texto):
        if texto:
            entry.delete(0, "end")
            entry.insert(0, texto)
        else:
            limpiar_entry(entry)

    # ------------------------------------------------------------------
    # Calendario
    # ------------------------------------------------------------------
    def _abrir_popup_calendario(self, al_confirmar, fecha_inicial=None):
        if not HAS_CUSTOM_CALENDAR:
            messagebox.showinfo("Información", "El componente de calendario no se encuentra disponible.")
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
            print(f"Error al abrir calendario: {e}")

    def abrir_calendario_conv_popup(self):
        def asignar(fecha_res):
            self.fecha_seleccionada = fecha_res.strftime("%Y-%m-%d")
            self._escribir_entry(self.entry_fecha, self.fecha_seleccionada)

        self._abrir_popup_calendario(asignar, parse_fecha(self.entry_fecha.get()))

    def _abrir_calendario_filtro(self, entry):
        def asignar(fecha_res):
            self._escribir_entry(entry, fecha_res.strftime("%Y-%m-%d"))
            self._aplicar_filtros()

        self._abrir_popup_calendario(asignar, parse_fecha(entry.get()))

    def desplazar_lista_al_inicio(self):
        """Coloca el historial en la parte superior para mostrar lo recién creado."""
        try:
            self.scroll_convocatorias.update_idletasks()
            self.scroll_convocatorias._parent_canvas.yview_moveto(0)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # API usada por el controlador
    # ------------------------------------------------------------------
    def mostrar_cargando(self):
        """Muestra esqueletos mientras llega el historial desde la BD."""
        for widget in self.scroll_convocatorias.winfo_children():
            widget.destroy()
        SkeletonLista(
            self.scroll_convocatorias, filas=3, tono="azul", compacto=True
        )

    def mostrar_convocatorias(self, lista):
        self._convocatorias = list(lista or [])
        self._aplicar_filtros()

    def obtener_datos_formulario(self):
        fecha_ingresada = self.entry_fecha.get().strip() or self.fecha_seleccionada
        fecha_parseada = parse_fecha(fecha_ingresada)
        fecha_normalizada = (
            fecha_parseada.strftime("%Y-%m-%d") if fecha_parseada else fecha_ingresada
        )
        hora_seleccionada = self.hora_picker.get()
        return {
            "tipo": self.combo_tipo.get(),
            "academia": self.combo_academia.get(),
            "fecha": fecha_normalizada,
            "hora": hora_seleccionada,
            "fecha_hora": f"{fecha_normalizada} {hora_seleccionada}",
            "orden": self.txt_orden_dia.get("1.0", "end-1c").strip(),
            "doc_oficial": self.entry_doc_oficial.get().strip()
        }

    def limpiar_formulario(self):
        self.combo_tipo.set("Ordinaria")
        self.fecha_seleccionada = datetime.now().strftime("%Y-%m-%d")
        self._escribir_entry(self.entry_fecha, self.fecha_seleccionada)
        self.hora_picker.set("10:00")
        self.txt_orden_dia.delete("1.0", "end")
        self._escribir_entry(self.entry_doc_oficial, "")
