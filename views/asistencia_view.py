import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

from views.dropdown import Dropdown
from views.icons import VERDE, icono
from views.skeleton import SkeletonTabla
from views.typography import (
    fuente,
    fuente_dato,
    fuente_etiqueta,
    fuente_titulo,
)
from views.ui_utils import crear_tarjeta_tinte

try:
    from views.custom_calendar import CustomCalendar
    HAS_CUSTOM_CALENDAR = True
except ImportError:
    try:
        from custom_calendar import CustomCalendar
        HAS_CUSTOM_CALENDAR = True
    except ImportError:
        HAS_CUSTOM_CALENDAR = False


class AsistenciaView(ctk.CTkFrame):
    def __init__(self, parent_container):
        super().__init__(parent_container, fg_color="transparent")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.COLOR_LABEL = "#222222"
        self.COLOR_ENTRY_BG = "#F0F4F1"
        self.COLOR_ENTRY_BORDER = "#CCCCCC"
        self.COLOR_TEXT_INSIDE = "#111111"

        # --- PANEL SUPERIOR: FILTROS Y MOMENTO ---
        self.frame_filtros = ctk.CTkFrame(self, fg_color="white", corner_radius=18)
        self.frame_filtros.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.frame_filtros.grid_columnconfigure((0, 1, 2), weight=1)

        header_filtros = ctk.CTkFrame(self.frame_filtros, fg_color="transparent")
        header_filtros.grid(row=0, column=0, columnspan=3, padx=15, pady=(12, 4), sticky="ew")
        ctk.CTkLabel(
            header_filtros, text="PASE DE LISTA",
            font=fuente_etiqueta(8), text_color="#1D6F23"
        ).pack(anchor="w")
        ctk.CTkLabel(
            header_filtros, text="  Control de Asistencia",
            image=icono("clipboard-check", 19, VERDE),
            compound="left",
            font=fuente_titulo(17), text_color="#1F2937"
        ).pack(anchor="w")
        ctk.CTkLabel(
            header_filtros, text="Selecciona la sesión y el momento del registro.",
            font=fuente(10), text_color="#6B7280"
        ).pack(anchor="w")

        # Seleccionar Sesión
        ctk.CTkLabel(
            self.frame_filtros, text="SESIÓN DE ACADEMIA",
            font=fuente_etiqueta(9), text_color=self.COLOR_LABEL
        ).grid(row=1, column=0, padx=15, pady=(8, 2), sticky="w")
        self.combo_sesion = Dropdown(
            self.frame_filtros,
            values=["Sesión 1 - Programación", "Sesión 2 - Matemáticas", "Consejo Técnico General"],
            width=220, height=32, font=fuente(11), dropdown_font=fuente(11)
        )
        self.combo_sesion.grid(row=2, column=0, padx=15, pady=(0, 10), sticky="ew")

        # Seleccionar Momento de la Sesión (RF-09)
        ctk.CTkLabel(
            self.frame_filtros, text="MOMENTO DEL REGISTRO",
            font=fuente_etiqueta(9), text_color=self.COLOR_LABEL
        ).grid(row=1, column=1, padx=15, pady=(8, 2), sticky="w")
        self.combo_momento = Dropdown(
            self.frame_filtros,
            values=["Inicio de Sesión", "Mitad de Sesión", "Final de Sesión"],
            width=220, height=32, font=fuente(11), dropdown_font=fuente(11)
        )
        self.combo_momento.grid(row=2, column=1, padx=15, pady=(0, 10), sticky="ew")

        # Fecha de la Sesión
        ctk.CTkLabel(
            self.frame_filtros, text="FECHA DE LA SESIÓN",
            font=fuente_etiqueta(9), text_color=self.COLOR_LABEL
        ).grid(row=1, column=2, padx=15, pady=(8, 2), sticky="w")
        self.frame_fecha = ctk.CTkFrame(self.frame_filtros, fg_color="transparent")
        self.frame_fecha.grid(row=2, column=2, padx=15, pady=(0, 10), sticky="ew")
        self.frame_fecha.grid_columnconfigure(0, weight=1)

        self.entry_fecha = ctk.CTkEntry(
            self.frame_fecha, fg_color=self.COLOR_ENTRY_BG,
            border_color=self.COLOR_ENTRY_BORDER, text_color=self.COLOR_TEXT_INSIDE,
            font=fuente_dato(11)
        )
        self.entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_fecha.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        self.btn_abrir_calendario = ctk.CTkButton(
            self.frame_fecha, text="", image=icono("calendar", 16, "#FFFFFF"),
            width=38,
            fg_color="#A3723E", hover_color="#8B5E34", command=self.abrir_calendario_popup
        )
        self.btn_abrir_calendario.grid(row=0, column=1)

        # Botón Cargar Lista
        self.btn_buscar = ctk.CTkButton(
            self.frame_filtros, text="  Cargar pase de lista",
            image=icono("search", 16, "#FFFFFF"),
            compound="left",
            font=fuente_titulo(12),
            fg_color="#1D6F23", hover_color="#15531A"
        )
        self.btn_buscar.grid(row=3, column=0, columnspan=3, padx=15, pady=(0, 12), sticky="ew")

        # --- LISTA DE DOCENTES ---
        self.scroll_contenido = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_contenido.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.scroll_contenido.grid_columnconfigure(0, weight=1)

        self.frame_lista_profesores = ctk.CTkFrame(self.scroll_contenido, fg_color="white", corner_radius=14)
        self.frame_lista_profesores.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.frame_lista_profesores.grid_columnconfigure(0, weight=1)

        # Botón Guardar
        self.btn_guardar_asistencia = ctk.CTkButton(
            self, text="  Guardar asistencia de la sesión",
            image=icono("save", 16, "#FFFFFF"),
            compound="left",
            fg_color="#A3723E", hover_color="#8B5E34",
            font=fuente_titulo(12), height=42
        )
        self.btn_guardar_asistencia.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.dict_widgets_estado = {}

    def abrir_calendario_popup(self):
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
                fecha_res = cal.get_date()
                self.entry_fecha.delete(0, 'end')
                self.entry_fecha.insert(0, fecha_res.strftime("%Y-%m-%d"))
                popup.destroy()

            ctk.CTkButton(
                popup, text="Confirmar Fecha", fg_color="#1D6F23",
                font=fuente_titulo(11), command=confirmar_fecha
            ).pack(pady=10)
            cal.select_date(datetime.now().date())
        except Exception as e:
            print(f"Error abriendo calendario: {e}")

    def mostrar_cargando(self):
        """Filas fantasma mientras el pase de lista llega desde la BD."""
        for widget in self.frame_lista_profesores.winfo_children():
            widget.destroy()
        SkeletonTabla(self.frame_lista_profesores, filas=5, tono="azul")

    def cargar_datos(self, lista_profesores=None):
        for widget in self.frame_lista_profesores.winfo_children():
            widget.destroy()

        self.dict_widgets_estado.clear()

        if not lista_profesores:
            ctk.CTkLabel(
                self.frame_lista_profesores,
                text="Haz clic en “CARGAR PASE DE LISTA” para desplegar los docentes.",
                font=fuente(11), text_color="#6B7280"
            ).pack(pady=25)
            return

        header = ctk.CTkFrame(self.frame_lista_profesores, fg_color="#EAECEE", corner_radius=10)
        header.pack(fill="x", padx=10, pady=(10, 5))
        header.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(header, text="DOCENTE", font=fuente_etiqueta(9), text_color="#333333").grid(row=0, column=0, padx=15, pady=6, sticky="w")
        ctk.CTkLabel(header, text="ESTATUS / DETALLES", font=fuente_etiqueta(9), text_color="#333333").grid(row=0, column=1, padx=15, pady=6, sticky="e")

        for prof in lista_profesores:
            item = crear_tarjeta_tinte(self.frame_lista_profesores, "azul")
            item.pack(fill="x", padx=10, pady=4)
            item.grid_columnconfigure(0, weight=1)

            lbl_nombre = ctk.CTkLabel(
                item,
                text=f"  {prof['nombre']}",
                image=icono("user-round", 14, "#2B7BB9"),
                compound="left",
                font=fuente_titulo(12),
                text_color="#2C3E50",
            )
            lbl_nombre.grid(row=0, column=0, padx=15, pady=10, sticky="w")

            cont_derecho = ctk.CTkFrame(item, fg_color="transparent")
            cont_derecho.grid(row=0, column=1, padx=15, pady=6, sticky="e")

            # Estatus
            seg_button = ctk.CTkSegmentedButton(
                cont_derecho,
                values=["Presente", "Ausente", "Retardo", "Justificado"],
                # `fg_color` pinta las esquinas internas de los segmentos; si
                # se deja el gris por defecto aparece una línea entre ellos.
                fg_color="#F8F9FA",
                selected_color="#8FBF9A",
                selected_hover_color="#7BB389",
                unselected_color="#E3E5E8",
                unselected_hover_color="#D6D9DD",
                text_color="#1F2937",
                border_width=0,
                corner_radius=10,
                height=32,
                font=fuente(10),
            )
            seg_button.set("Presente")
            seg_button.pack(side="left", padx=5)

            # Campo para minutos de retardo (RF-10)
            ctk.CTkLabel(
                cont_derecho, text="MIN", font=fuente_etiqueta(8),
                text_color="#6B7280"
            ).pack(side="left", padx=(8, 2))
            entry_minutos = ctk.CTkEntry(
                cont_derecho, width=56, placeholder_text="0",
                fg_color=self.COLOR_ENTRY_BG, text_color="black", font=fuente_dato(10)
            )
            entry_minutos.insert(0, "0")
            entry_minutos.pack(side="left", padx=2)

            # Campo de justificación (RF-11, RF-12). Selector discreto: el
            # bronce se reserva para acciones, no para campos de filtro.
            combo_motivo = Dropdown(
                cont_derecho, width=164, height=30,
                values=["Sin motivo", "Cita en el ISSSTE", "Comisión del plantel"],
                font=fuente(10), dropdown_font=fuente(10)
            )
            combo_motivo.pack(side="left", padx=2)

            self.dict_widgets_estado[prof['id']] = {
                "estatus": seg_button,
                "minutos": entry_minutos,
                "motivo": combo_motivo
            }

    def obtener_datos_para_guardar(self):
        sesion_texto = self.combo_sesion.get()
        fecha = self.entry_fecha.get().strip()
        momento_texto = self.combo_momento.get()

        if not fecha:
            messagebox.showwarning("Atención", "Por favor ingresa o selecciona una fecha válida.")
            return None

        id_sesion = 1
        if "2" in sesion_texto:
            id_sesion = 2

        registros = {}
        for prof_id, dict_w in self.dict_widgets_estado.items():
            min_val = 0
            try:
                min_val = int(dict_w["minutos"].get().strip())
            except ValueError:
                min_val = 0

            registros[prof_id] = {
                "estado": dict_w["estatus"].get(),
                "minutos": min_val,
                "motivo": dict_w["motivo"].get()
            }

        return {
            "id_clase": id_sesion,
            "fecha": fecha,
            "momento": momento_texto,
            "registros": registros
        }