import os
import math
import customtkinter as ctk
from PIL import Image, ImageOps

from views.icons import icono
from views.loading_spinner import OverlayCarga
from views.typography import (
    fuente,
    fuente_display,
    fuente_etiqueta,
    fuente_titulo,
)


class LoginView(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de la ventana principal
        self.title("CBTF No. 4 - Sistema de Acceso")
        self.geometry("960x560")
        self.resizable(False, False)

        # Centrar ventana
        self.center_window(960, 560)

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
                    # Si no hay ImageTk, intentamos la forma directa
                    self.iconphoto(img_pil)
        except Exception:
            # Si falla la carga del icono, dejamos que la ventana use el default para no interrumpir la ejecución
            pass

        # Paleta de colores refinada
        self.COLOR_BG_RIGHT = "#15241A"      # Verde muy oscuro profundo
        self.COLOR_CARD_BG = "#213629"       # Verde contenedor tipo tarjeta
        self.COLOR_ACCENT = "#C48A4C"        # Tono dorado/marrón cálido acentuado
        self.COLOR_ACCENT_HOVER = "#D99B56"  # Hover dorado
        self.COLOR_TEXT_MAIN = "#FFFFFF"
        self.COLOR_TEXT_MUTED = "#A0B0A5"
        self.COLOR_BORDER_FOCUS = "#E0AE72"  # Borde en foco
        self.COLOR_INPUT_BG = "#18271E"      # Fondo de los campos en reposo
        self.COLOR_INPUT_FOCUS = "#3A2C1D"   # Fondo cálido del campo en uso

        # Configuración de cuadrícula (50% izquierda / 50% derecha)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1, minsize=480)
        self.grid_columnconfigure(1, weight=1, minsize=480)

        # Panel Izquierdo (Imagen limpia original)
        self.frame_left = ctk.CTkFrame(self, corner_radius=0, fg_color="#121212")
        self.frame_left.grid(row=0, column=0, sticky="nsew")
        self.crear_imagen_entrada()

        # Panel Derecho (Formulario)
        self.frame_right = ctk.CTkFrame(self, corner_radius=0, fg_color=self.COLOR_BG_RIGHT)
        self.frame_right.grid(row=0, column=1, sticky="nsew")

        # Tarjeta del Formulario
        self.card_frame = ctk.CTkFrame(
            self.frame_right,
            fg_color=self.COLOR_CARD_BG,
            corner_radius=26,
            border_width=0,
            border_color="#385743",
            width=360,
            height=470
        )
        
        # Posición inicial para una entrada breve y sobria.
        self.card_frame.place(relx=0.535, rely=0.515, anchor="center")

        # Contenido del formulario
        self.construir_formulario()

        # La animación arranca después del primer pintado para evitar saltos.
        self.after(80, self.animar_entrada_lateral)

        # El campo de usuario recibe el foco al abrir para que el estado
        # activo se vea de inmediato y se pueda escribir sin dar clic.
        self.after(240, self.enfocar_entrada)

    def center_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        try:
            escala = self._get_window_scaling()
        except Exception:
            escala = 1.0
        escala = escala or 1.0
        # `CTk.geometry` escala el tamaño, pero no las coordenadas x/y.
        ancho_fisico = round(width * escala)
        alto_fisico = round(height * escala)
        x = max(0, (screen_width - ancho_fisico) // 2)
        y = max(0, (screen_height - alto_fisico) // 2 - 30)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def crear_imagen_entrada(self):
        """Carga y ajusta la imagen de entrada original sin bordes ni efectos de brillo."""
        try:
            ruta_entrada = os.path.join(self.base_dir, "assets", "entrada.jpeg")
            if not os.path.exists(ruta_entrada):
                raise FileNotFoundError("Archivo de imagen no encontrado")

            img_pil = Image.open(ruta_entrada)
            img_fit = ImageOps.fit(img_pil, (480, 560), Image.Resampling.LANCZOS)

            self.entrada_img = ctk.CTkImage(
                light_image=img_fit,
                dark_image=img_fit,
                size=(480, 560)
            )

            lbl_entrada = ctk.CTkLabel(
                self.frame_left,
                image=self.entrada_img,
                text="",
                fg_color="transparent"
            )
            lbl_entrada.place(x=0, y=0, relwidth=1.0, relheight=1.0)

        except Exception as error:
            lbl_fallback = ctk.CTkLabel(
                self.frame_left,
                text="CBTF No. 4\nTerritorio Verde",
                font=fuente_display(22, "bold"),
                text_color="#537A5C"
            )
            lbl_fallback.place(relx=0.5, rely=0.5, anchor="center")

    def construir_formulario(self):
        self.form_inner = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        self.form_inner.pack(fill="both", expand=True, padx=25, pady=25)

        # Logo
        self.crear_logo()

        # Overline institucional: jerarquía editorial sobre el saludo.
        ctk.CTkLabel(
            self.form_inner,
            text="SISTEMA ACADÉMICO",
            font=fuente_etiqueta(8),
            text_color=self.COLOR_ACCENT,
        ).pack(pady=(0, 4))

        # Título
        self.lbl_titulo = ctk.CTkLabel(
            self.form_inner,
            text="¡Bienvenido!",
            font=fuente_display(26, "bold"),
            text_color=self.COLOR_TEXT_MAIN
        )
        self.lbl_titulo.pack(pady=(0, 2))

        self.lbl_subtitulo = ctk.CTkLabel(
            self.form_inner,
            text="Inicia sesión para continuar",
            font=fuente(11),
            text_color=self.COLOR_TEXT_MUTED
        )
        self.lbl_subtitulo.pack(pady=(0, 14))

        # Campo Usuario
        self.entry_usuario = ctk.CTkEntry(
            self.form_inner,
            placeholder_text="Usuario o Correo",
            width=290,
            height=44,
            corner_radius=14,
            fg_color="#18271E",
            text_color="white",
            placeholder_text_color="#6F8877",
            border_width=0,
            border_color="#2E4837",
            font=fuente(12)
        )
        self.entry_usuario.pack(pady=7)
        self.setup_focus_effects(self.entry_usuario)
        self.entry_usuario.bind(
            "<KeyRelease>", lambda event: self.limpiar_error(), add="+"
        )

        # Contenedor para el campo de Contraseña y el Botón de ver contraseña (para alinearlos horizontalmente)
        password_container = ctk.CTkFrame(self.form_inner, fg_color="transparent")
        password_container.pack(pady=7)

        # Campo Contraseña (ajustado ligeramente más corto para dar espacio al botón de ver)
        self.entry_password = ctk.CTkEntry(
            password_container,
            placeholder_text="Contraseña",
            show="•",
            width=238,
            height=44,
            corner_radius=14,
            fg_color="#18271E",
            text_color="white",
            placeholder_text_color="#6F8877",
            border_width=0,
            border_color="#2E4837",
            font=fuente(12)
        )
        self.entry_password.pack(side="left", padx=(0, 6))
        self.setup_focus_effects(self.entry_password)
        self.entry_password.bind(
            "<KeyRelease>", lambda event: self.limpiar_error(), add="+"
        )

        # Botón para mostrar contraseña al mantener presionado
        self._ojo_normal = icono("eye", 18, self.COLOR_TEXT_MUTED)
        self._ojo_activo = icono("eye", 18, self.COLOR_ACCENT)
        self.btn_ver_password = ctk.CTkButton(
            password_container,
            text="",
            image=self._ojo_normal,
            width=44,
            height=44,
            corner_radius=14,
            fg_color="#18271E",
            hover_color="#2E4837",
            text_color=self.COLOR_TEXT_MUTED,
        )
        self.btn_ver_password.pack(side="left")

        # Vincular eventos de presionar y soltar el ratón para mostrar/ocultar contraseña
        self.btn_ver_password.bind("<ButtonPress-1>", self.mostrar_password)
        self.btn_ver_password.bind("<ButtonRelease-1>", self.ocultar_password)

        # Olvidé contraseña
        self.lbl_olvide = ctk.CTkLabel(
            self.form_inner,
            text="¿Olvidaste tu contraseña?",
            font=fuente(11, "underline"),
            text_color=self.COLOR_TEXT_MUTED,
            cursor="hand2"
        )
        self.lbl_olvide.pack(pady=(3, 12))
        self.lbl_olvide.bind("<Enter>", lambda e: self.lbl_olvide.configure(text_color=self.COLOR_ACCENT))
        self.lbl_olvide.bind("<Leave>", lambda e: self.lbl_olvide.configure(text_color=self.COLOR_TEXT_MUTED))
        self.lbl_olvide.bind("<Button-1>", self.abrir_aviso_recuperacion)

        # Botón Login
        self.btn_login = ctk.CTkButton(
            self.form_inner,
            text="  Iniciar sesión",
            image=icono("log-in", 16, "#FFFFFF"),
            compound="left",
            width=290,
            height=46,
            corner_radius=14,
            fg_color=self.COLOR_ACCENT,
            hover_color=self.COLOR_ACCENT_HOVER,
            text_color="#FFFFFF",
            font=fuente_titulo(12),
            cursor="hand2"
        )
        self.btn_login.pack(pady=(0, 6))

        # Los errores se muestran dentro de la tarjeta, sin messageboxes.
        # La etiqueta solo se empaqueta cuando hay un mensaje real.
        self.lbl_error = ctk.CTkLabel(
            self.form_inner,
            text="",
            image=icono("triangle-alert", 13, "#F2B8B5"),
            compound="left",
            font=fuente(10),
            text_color="#F2B8B5",
            wraplength=290,
            justify="center",
        )

        # Overlay con spinner: se crea al final para quedar sobre el formulario.
        self.overlay_carga = OverlayCarga(
            self.card_frame,
            color_fondo=self.COLOR_CARD_BG,
            color_pista="#2E4A39",
            color_arco=self.COLOR_ACCENT,
            texto="Validando credenciales",
            subtitulo="Verificando tus datos de acceso",
        )

    # ------------------------------------------------------------------
    # Estado de validación
    # ------------------------------------------------------------------
    def mostrar_carga(self):
        """Cubre el formulario con el spinner mientras se valida."""
        self.limpiar_error()
        self.btn_login.configure(state="disabled")
        self.overlay_carga.iniciar()

    def ocultar_carga(self):
        self.overlay_carga.detener()
        self.btn_login.configure(state="normal")

    def mostrar_error_auth(self, mensaje):
        """Error inline sobrio, sin interrumpir con ventanas modales."""
        self.lbl_error.configure(text=f"  {mensaje}")
        if not self.lbl_error.winfo_manager():
            self.lbl_error.pack(pady=(6, 0))

    def limpiar_error(self):
        if self.lbl_error.cget("text"):
            self.lbl_error.configure(text="")
        if self.lbl_error.winfo_manager():
            self.lbl_error.pack_forget()

    def mostrar_password(self, event):
        """Muestra la contraseña mientras el botón esté presionado."""
        self.entry_password.configure(show="")
        self.btn_ver_password.configure(image=self._ojo_activo)

    def ocultar_password(self, event):
        """Vuelve a ocultar la contraseña al soltar el botón."""
        self.entry_password.configure(show="•")
        self.btn_ver_password.configure(image=self._ojo_normal)

    def crear_logo(self):
        try:
            ruta_logo = os.path.join(self.base_dir, "assets", "logo_CBTF.png")
            if not os.path.exists(ruta_logo):
                raise FileNotFoundError("Logo no encontrado")

            img_pil = Image.open(ruta_logo)
            self.logo_img = ctk.CTkImage(
                light_image=img_pil,
                dark_image=img_pil,
                size=(92, 92)
            )
            lbl_logo = ctk.CTkLabel(self.form_inner, image=self.logo_img, text="")
            lbl_logo.pack(pady=(0, 4))
        except Exception:
            lbl_logo = ctk.CTkLabel(
                self.form_inner,
                text="  CBTF No. 4",
                image=icono("trees", 22, self.COLOR_ACCENT),
                compound="left",
                font=fuente_display(19, "bold"),
                text_color=self.COLOR_ACCENT
            )
            lbl_logo.pack(pady=(0, 15))

    def setup_focus_effects(self, entry_widget):
        """Marca con claridad el campo que está en uso.

        El borde solo se dibuja cuando el campo tiene el foco; además el
        relleno pasa a un tono cálido para que el contraste contra los
        demás campos se note incluso de reojo.
        """

        def on_focus_in(event):
            entry_widget.configure(
                border_width=2,
                border_color=self.COLOR_BORDER_FOCUS,
                fg_color=self.COLOR_INPUT_FOCUS,
                placeholder_text_color="#D8C8B2",
            )

        def on_focus_out(event):
            entry_widget.configure(
                border_width=0,
                border_color="#2E4837",
                fg_color=self.COLOR_INPUT_BG,
                placeholder_text_color="#6F8877",
            )

        entry_widget.bind("<FocusIn>", on_focus_in)
        entry_widget.bind("<FocusOut>", on_focus_out)

    def enfocar_entrada(self):
        """Enfoca usuario al abrir y contraseña al volver desde el panel."""
        try:
            if self.entry_usuario.get().strip():
                self.entry_password.focus_set()
            else:
                self.entry_usuario.focus_set()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Aviso de recuperación de contraseña
    # ------------------------------------------------------------------
    def abrir_aviso_recuperacion(self, evento=None):
        existente = getattr(self, "_popup_recuperacion", None)
        if existente is not None and existente.winfo_exists():
            existente.lift()
            existente.focus_force()
            return "break"

        popup = ctk.CTkToplevel(self)
        popup.title("Recuperar contraseña")
        popup.resizable(False, False)
        popup.configure(fg_color=self.COLOR_BG_RIGHT)
        popup.transient(self)
        popup.attributes("-topmost", True)
        try:
            popup.attributes("-toolwindow", True)
        except Exception:
            pass

        ancho, alto = 430, 244
        self.update_idletasks()
        try:
            escala = self._get_window_scaling() or 1.0
        except Exception:
            escala = 1.0
        ancho_fisico = round(ancho * escala)
        alto_fisico = round(alto * escala)
        x = self.winfo_rootx() + (self.winfo_width() - ancho_fisico) // 2
        y = self.winfo_rooty() + (self.winfo_height() - alto_fisico) // 2
        popup.geometry(
            f"{ancho}x{alto}+{max(0, x)}+{max(0, y)}"
        )

        tarjeta = ctk.CTkFrame(
            popup,
            fg_color=self.COLOR_CARD_BG,
            corner_radius=22,
            border_width=1,
            border_color="#385743",
        )
        tarjeta.pack(fill="both", expand=True, padx=12, pady=12)

        ctk.CTkLabel(
            tarjeta,
            text="",
            image=icono("lock-keyhole", 24, self.COLOR_ACCENT),
        ).pack(pady=(18, 7))

        ctk.CTkLabel(
            tarjeta,
            text="Recuperar contraseña",
            font=fuente_display(17, "bold"),
            text_color=self.COLOR_TEXT_MAIN,
        ).pack()

        ctk.CTkLabel(
            tarjeta,
            text=(
                "Contactate con el/la jefe de academia\n"
                "para reestablecer tu contrasena"
            ),
            font=fuente(11),
            text_color=self.COLOR_TEXT_MUTED,
            wraplength=352,
            justify="center",
        ).pack(padx=20, pady=(8, 16))

        def cerrar():
            self._popup_recuperacion = None
            try:
                popup.grab_release()
            except Exception:
                pass
            popup.destroy()
            self.after(40, self.enfocar_entrada)

        btn_entendido = ctk.CTkButton(
            tarjeta,
            text="Entendido",
            width=132,
            height=38,
            corner_radius=12,
            fg_color=self.COLOR_ACCENT,
            hover_color=self.COLOR_ACCENT_HOVER,
            text_color="#1B2A1F",
            font=fuente_titulo(11),
            command=cerrar,
        )
        btn_entendido.pack(pady=(0, 16))

        popup.protocol("WM_DELETE_WINDOW", cerrar)
        popup.bind("<Escape>", lambda event: cerrar())
        self._popup_recuperacion = popup

        def presentar():
            if not popup.winfo_exists():
                return
            popup.grab_set()
            popup.lift()
            popup.focus_force()
            btn_entendido.focus_set()

        popup.after(80, presentar)
        return "break"

    def animar_entrada_lateral(self):
        """Entrada breve: la tarjeta se asienta desde la derecha y abajo."""
        start_x, start_y = 0.535, 0.515
        target_x, target_y = 0.5, 0.5
        steps = 24

        def step(i):
            if i > steps:
                return
            progress = i / steps
            eased = 1 - math.pow(1 - progress, 3)
            current_x = start_x + (target_x - start_x) * eased
            current_y = start_y + (target_y - start_y) * eased

            self.card_frame.place(relx=current_x, rely=current_y, anchor="center")
            if i < steps:
                self.after(16, lambda: step(i + 1))
            else:
                self.card_frame.place(relx=target_x, rely=target_y, anchor="center")

        step(1)


if __name__ == "__main__":
    app = LoginView()
    app.mainloop()