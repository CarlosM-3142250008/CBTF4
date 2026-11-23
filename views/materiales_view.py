import os
import customtkinter as ctk
from PIL import Image, ImageOps
from datetime import datetime

from views.icons import BRONCE, icono
from views.typography import fuente

class MaterialesView(ctk.CTk):
    def __init__(self, parent_container):
        self.parent = parent_container
        
        # Configuración de la ventana
        self.title("Gestión de Materiales")
        self.COLOR_BG = "#F4F6F8"
        self.COLOR_CARD = "white"
        self.COLOR_ACCENT = "#A3723E"

        # Contenedor principal
        self.main_frame = ctk.CTkFrame(self.parent, fg_color=self.COLOR_BG, corner_radius=0)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Header
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="white", height=65, corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew")

        self.lbl_titulo_header = ctk.CTkLabel(
            self.header_frame,
            text="  Repositorio de Materiales",
            image=icono("folder-open", 19, BRONCE),
            compound="left",
            font=fuente(20, "bold"),
            text_color="#222222"
        )
        self.lbl_titulo_header.pack(side="left", padx=25, pady=15)

        # Área de Contenido
        self.scroll_content = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.scroll_content.grid(row=1, column=0, sticky="nsew", padx=20, pady=15)
        self.scroll_content.grid_columnconfigure((0, 1), weight=1)

        # Sección de Formulario
        self.frame_formulario = ctk.CTkFrame(self.scroll_content, fg_color=self.COLOR_CARD, corner_radius=10, border_width=0, border_color="#E0E0E0")
        self.frame_formulario.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(self.frame_formulario, text="Añadir Nuevo Recurso", font=fuente(15, "bold"), text_color="#333333").pack(pady=(10, 5))
        
        self.grid_form = ctk.CTkGrid(self.frame_formulario)
        self.grid_form.grid_columnconfigure((0, 1), weight=1)

        self.entry_nombre = ctk.CTkEntry(self.grid_form, placeholder_text="Nombre del material")
        self.entry_nombre.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.entry_categoria = ctk.CTkEntry(self.grid_form, placeholder_text="Categoría")
        self.entry_categoria.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.entry_descripcion = ctk.CTkEntry(self.grid_form, placeholder_text="Descripción breve")
        self.entry_descripcion.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        self.entry_enlace = ctk.CTkEntry(self.grid_form, placeholder_text="URL / Enlace de acceso")
        self.entry_enlace.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.btn_guardar = ctk.CTkButton(self.grid_form, text="GUARDAR MATERIAL", font=fuente(13, "bold"), fg_color=self.COLOR_ACCENT, hover_color="#8B5E34")
        self.btn_guardar.grid(row=2, column=0, columnspan=2, padx=5, pady=15, sticky="ew")

        # Sección de Lista
        self.frame_lista = ctk.CTkFrame(self.scroll_content, fg_color=self.COLOR_CARD, corner_radius=10)
        self.frame_lista.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(self.frame_lista, text="Materiales Disponibles", font=fuente(15, "bold"), text_color="#333333").pack(anchor="w", padx=15, pady=(10, 5))
        
        self.container_lista_materiales = ctk.CTkFrame(self.frame_lista, fg_color="transparent")
        self.container_lista_materiales.pack(fill="x", padx=15, pady=(0, 15))

    def obtener_datos_formulario(self):
        return {
            "nombre": self.entry_nombre.get().strip(),
            "categoria": self.entry_categoria.get().strip(),
            "descripcion": self.entry_descripcion.get().strip(),
            "enlace": self.entry_enlace.get().strip()
        }

    def limpiar_formulario(self):
        self.entry_nombre.delete(0, 'end')
        self.entry_categoria.delete(0, 'end')
        self.entry_descripcion.delete(0, 'end')
        self.entry_enlace.delete(0, 'end')

    def mostrar_materiales(self, lista):
        for widget in self.container_lista_materiales.winfo_children():
            widget.destroy()

        # Obtener fecha de hoy para el badge
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")

        for mat in lista:
            item_frame = ctk.CTkFrame(self.container_lista_materiales, fg_color="#F8F9FA", corner_radius=6)
            item_frame.pack(fill="x", pady=5)

            top_line = ctk.CTkFrame(item_frame, fg_color="transparent")
            top_line.pack(fill="x", padx=10, pady=(6, 0))

            ctk.CTkLabel(top_line, text=f"{mat['nombre']}", font=fuente(13, "bold"), text_color="#1D6F23").pack(side="left")
            
            # Lógica del badge NUEVO para Materiales
            # El modelo devuelve fecha_registro como fecha_hora
            es_nuevo = False
            fecha_mat = mat.get('fecha_hora', 'N/A')
            if fecha_mat and fecha_hoy in fecha_mat:
                es_nuevo = True

            ctk.CTkLabel(top_line, text=f"[{mat['categoria']}]", font=fuente(11), text_color="gray").pack(side="right")
            
            if es_nuevo:
                lbl_nuevo = ctk.CTkLabel(top_line, text="NUEVO", font=fuente(11, "bold"), text_color="white", fg_color="#0078D7", corner_radius=4)
                lbl_nuevo.pack(side="right", padx=(5, 0))

            lbl_desc = ctk.CTkLabel(item_frame, text=f"Descripción: {mat['descripcion']}", font=fuente(12), text_color="#555555")
            lbl_desc.pack(anchor="w", padx=10)

            lbl_enlace = ctk.CTkLabel(
                item_frame,
                text=f"  {mat['enlace']}",
                image=icono("link", 12, "#2B7BB9"),
                compound="left",
                font=fuente(12, "underline"),
                text_color="#2B7BB9",
                cursor="hand2",
            )
            lbl_enlace.pack(anchor="w", padx=10, pady=(0, 6))
            
            # Simular apertura de enlace (opcional, pero bueno para la funcionalidad)
            lbl_enlace.bind("<Button-1>", lambda e: print(f"Abriendo enlace: {mat['enlace']}"))
