import os
import customtkinter as ctk
from PIL import Image, ImageOps
from datetime import datetime

from views.icons import VERDE, icono
from views.typography import fuente

class AvisosView(ctk.CTk):
    def __init__(self, parent_container):
        # Recibimos el contenedor principal para insertar esta vista
        self.parent = parent_container
        
        # Configuración de la ventana (se usa como contenedor)
        self.title("Avisos y Documentos")
        
        # Paleta de colores consistente con el proyecto
        self.COLOR_BG = "#F4F6F8"
        self.COLOR_CARD = "white"
        self.COLOR_ACCENT = "#A3723E"

        # Contenedor principal para la vista
        self.main_frame = ctk.CTkFrame(self.parent, fg_color=self.COLOR_BG, corner_radius=0)
        self.main_frame.pack(fill="both", expand=True, padx=0, pady=0)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Header
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="white", height=65, corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew")

        self.lbl_titulo_header = ctk.CTkLabel(
            self.header_frame,
            text="  Gestión de Avisos y Documentos",
            image=icono("megaphone", 19, VERDE),
            compound="left",
            font=fuente(20, "bold"),
            text_color="#222222"
        )
        self.lbl_titulo_header.pack(side="left", padx=25, pady=15)

        # Área de Contenido
        self.scroll_content = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.scroll_content.grid(row=1, column=0, sticky="nsew", padx=20, pady=15)
        self.scroll_content.grid_columnconfigure((0, 1), weight=1)

        # Sección de Formulario (Superior)
        self.frame_formulario = ctk.CTkFrame(self.scroll_content, fg_color=self.COLOR_CARD, corner_radius=10, border_width=0, border_color="#E0E0E0")
        self.frame_formulario.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(self.frame_formulario, text="Registrar Nuevo Aviso", font=fuente(15, "bold"), text_color="#333333").pack(pady=(10, 5))
        
        # Grid para campos del formulario
        self.grid_form = ctk.CTkGrid(self.frame_formulario)
        self.grid_form.grid_columnconfigure((0, 1), weight=1)

        self.entry_titulo = ctk.CTkEntry(self.grid_form, placeholder_text="Título del aviso")
        self.entry_titulo.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.entry_emisor = ctk.CTkEntry(self.grid_form, placeholder_text="Emisor (ej. Dirección)")
        self.entry_emisor.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.entry_fecha = ctk.CTkEntry(self.grid_form, placeholder_text="Fecha (DD-MM-YYYY)")
        self.entry_fecha.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        self.entry_detalle = ctk.CTkEntry(self.grid_form, placeholder_text="Detalle del aviso")
        self.entry_detalle.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.entry_categoria = ctk.CTkEntry(self.grid_form, placeholder_text="Categoría (ej. Administrativo)")
        self.entry_categoria.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

        self.btn_guardar = ctk.CTkButton(self.grid_form, text="PUBLICAR AVISO", font=fuente(13, "bold"), fg_color=self.COLOR_ACCENT, hover_color="#8B5E34")
        self.btn_guardar.grid(row=3, column=0, columnspan=2, padx=5, pady=15, sticky="ew")

        # Sección de Lista (Inferior)
        self.frame_lista = ctk.CTkFrame(self.scroll_content, fg_color=self.COLOR_CARD, corner_radius=10)
        self.frame_lista.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(self.frame_lista, text="Avisos Publicados", font=fuente(15, "bold"), text_color="#333333").pack(anchor="w", padx=15, pady=(10, 5))
        
        self.container_lista_avisos = ctk.CTkFrame(self.frame_lista, fg_color="transparent")
        self.container_lista_avisos.pack(fill="x", padx=15, pady=(0, 15))

    def obtener_datos_formulario(self):
        return {
            "titulo": self.entry_titulo.get().strip(),
            "emisor": self.entry_emisor.get().strip(),
            "fecha": self.entry_fecha.get().strip(),
            "detalle": self.entry_detalle.get().strip(),
            "categoria": self.entry_categoria.get().strip() or "General"
        }

    def limpiar_formulario(self):
        self.entry_titulo.delete(0, 'end')
        self.entry_emisor.delete(0, 'end')
        self.entry_fecha.delete(0, 'end')
        self.entry_detalle.delete(0, 'end')
        self.entry_categoria.delete(0, 'end')

    def mostrar_avisos(self, lista):
        # Limpiar lista existente
        for widget in self.container_lista_avisos.winfo_children():
            widget.destroy()

        # Obtener fecha de hoy para el badge
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")

        for aviso in lista:
            item_frame = ctk.CTkFrame(self.container_lista_avisos, fg_color="#F8F9FA", corner_radius=6)
            item_frame.pack(fill="x", pady=5)

            # Título y Categoría
            top_line = ctk.CTkFrame(item_frame, fg_color="transparent")
            top_line.pack(fill="x", padx=10, pady=(6, 0))

            ctk.CTkLabel(top_line, text=f"{aviso['titulo']}", font=fuente(13, "bold"), text_color="#1D6F23").pack(side="left")
            
            # Lógica del badge NUEVO para Avisos
            # El modelo devuelve fecha_evento como fecha_hora
            es_nuevo = False
            fecha_aviso = aviso.get('fecha_hora', 'N/A')
            if fecha_aviso and fecha_hoy in fecha_aviso:
                es_nuevo = True

            ctk.CTkLabel(top_line, text=f"[{aviso['categoria']}]", font=fuente(11), text_color="gray").pack(side="right")
            
            if es_nuevo:
                lbl_nuevo = ctk.CTkLabel(top_line, text="NUEVO", font=fuente(11, "bold"), text_color="white", fg_color="#0078D7", corner_radius=4)
                lbl_nuevo.pack(side="right", padx=(5, 0))

            # Detalles
            lbl_det = ctk.CTkLabel(item_frame, text=f"De: {aviso['emisor']} | Fecha: {fecha_aviso}", font=fuente(12), text_color="#555555")
            lbl_det.pack(anchor="w", padx=10)

            lbl_desc = ctk.CTkLabel(item_frame, text=aviso['detalle'], font=fuente(12), text_color="#666666", wraplength=800)
            lbl_desc.pack(anchor="w", padx=10, pady=(0, 6))
