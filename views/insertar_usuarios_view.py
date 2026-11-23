"""Gestión de usuarios: alta de cuentas y directorio del sistema."""

import customtkinter as ctk

from views.dropdown import Dropdown
from views.icons import GRIS_OSCURO, VERDE, icono
from views.skeleton import SkeletonLista
from views.typography import (
    fuente,
    fuente_dato,
    fuente_etiqueta,
    fuente_titulo,
)
from views.ui_utils import (
    COLOR_TEXTO,
    COLOR_TEXTO_SUAVE,
    crear_boton_eliminar,
    crear_tarjeta_tinte,
    paleta_tarjeta,
)


COLOR_ROL = {
    "Jefe de Academia": ("#F6EEE3", "#8A5A2E"),
    "Coordinador de Academia": ("#EAF2F9", "#2B6C9E"),
    "Docente": ("#EFF3F1", "#4B5563"),
}


class UsuariosView(ctk.CTkFrame):
    def __init__(self, parent_container):
        super().__init__(parent_container, fg_color="transparent")

        # Ambas columnas crecen por igual; el alto lo define el contenido,
        # no un peso vertical que empuje el formulario al centro.
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=1)

        # colores
        self.COLOR_LABEL = "#222222"
        self.COLOR_ENTRY_BG = "#F0F4F1"
        self.COLOR_ENTRY_BORDER = "#CCCCCC"
        self.COLOR_TEXT_INSIDE = "#111111"
        self.COLOR_PLACEHOLDER = "#777777"

        # Permisos de administrador (los controla el DashboardController)
        self.puede_eliminar = False
        self.on_eliminar_usuario = None

        # Cuenta con la sesión activa: nunca debe mostrar la opción de eliminarse.
        self.id_usuario_actual = None
        self.usuario_actual = None

        self._crear_formulario()
        self._crear_directorio()

    # ------------------------------------------------------------------
    # Panel izquierdo: alta de usuario
    # ------------------------------------------------------------------
    def _crear_formulario(self):
        paleta = paleta_tarjeta("bronce")
        self.frame_form = ctk.CTkFrame(self, fg_color="white", corner_radius=18)
        self.frame_form.grid(row=0, column=0, padx=(0, 8), pady=0, sticky="new")

        header_form = ctk.CTkFrame(self.frame_form, fg_color="transparent")
        header_form.pack(fill="x", padx=20, pady=(16, 8))
        ctk.CTkLabel(
            header_form,
            text="ALTA DE USUARIO",
            font=fuente_etiqueta(8),
            text_color=paleta["acento"],
        ).pack(anchor="w")
        ctk.CTkLabel(
            header_form,
            text="  Registrar Nuevo Usuario",
            image=icono("user-plus", 19, VERDE),
            compound="left",
            font=fuente_titulo(17),
            text_color=VERDE,
        ).pack(anchor="w", pady=(1, 0))
        ctk.CTkLabel(
            header_form,
            text="Completa los datos para crear una cuenta.",
            font=fuente(10),
            text_color=COLOR_TEXTO_SUAVE,
        ).pack(anchor="w")

        cuerpo = ctk.CTkFrame(self.frame_form, fg_color="transparent")
        cuerpo.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        campos = ctk.CTkFrame(cuerpo, fg_color="transparent")
        campos.pack(fill="x", pady=(4, 0))
        campos.grid_columnconfigure((0, 1), weight=1, uniform="campo")

        def etiqueta(texto, fila, columna):
            margen = (0, 6) if columna == 0 else (6, 0)
            ctk.CTkLabel(
                campos,
                text=texto,
                font=fuente_etiqueta(9),
                text_color="#4B5563",
            ).grid(row=fila, column=columna, sticky="w", padx=margen, pady=(10, 1))

        def margen(columna):
            return (0, 6) if columna == 0 else (6, 0)

        def campo(placeholder, fila, columna, tipo=None, show=None):
            etiqueta(tipo or placeholder, fila, columna)
            entrada = ctk.CTkEntry(
                campos,
                placeholder_text=placeholder,
                show=show or "",
                fg_color=self.COLOR_ENTRY_BG,
                border_color=self.COLOR_ENTRY_BORDER,
                text_color=self.COLOR_TEXT_INSIDE,
                placeholder_text_color=self.COLOR_PLACEHOLDER,
                font=fuente_dato(11) if "usuario" in (tipo or "").lower() else fuente(11),
            )
            entrada.grid(
                row=fila + 1,
                column=columna,
                sticky="ew",
                padx=margen(columna),
                pady=(0, 2),
            )
            return entrada

        self.entry_nombre = campo("Ej. María", 0, 0, "NOMBRE(S)")
        self.entry_ape_pat = campo("Ej. López", 0, 1, "APELLIDO PATERNO")
        self.entry_ape_mat = campo("Ej. Gómez", 2, 0, "APELLIDO MATERNO")
        self.entry_usuario = campo("Ej. mlopez", 2, 1, "USUARIO")
        self.entry_password = campo("••••••••", 4, 0, "CONTRASEÑA", show="•")

        etiqueta("ROL DEL USUARIO", 4, 1)
        self.combo_rol = Dropdown(
            campos,
            values=["Docente", "Coordinador de Academia", "Jefe de Academia"],
            width=200,
            height=30,
            font=fuente(11),
            dropdown_font=fuente(11),
        )
        self.combo_rol.grid(
            row=5,
            column=1,
            sticky="ew",
            padx=margen(1),
            pady=(0, 2),
        )

        # Pie del formulario: nota de roles y acción principal.
        pie = ctk.CTkFrame(cuerpo, fg_color="transparent")
        pie.pack(fill="x", side="bottom", pady=(16, 0))

        ctk.CTkFrame(pie, height=1, fg_color=paleta["borde"]).pack(
            fill="x", pady=(0, 10)
        )
        ctk.CTkLabel(
            pie,
            text="  El rol asignado define los módulos a los que podrá acceder la cuenta.",
            image=icono("lock-keyhole", 14, paleta["acento"]),
            compound="left",
            font=fuente(10),
            text_color=paleta["acento"],
            anchor="w",
            justify="left",
            wraplength=450,
        ).pack(anchor="w", pady=(0, 10))

        self.btn_guardar = ctk.CTkButton(
            pie,
            text="  Crear usuario",
            image=icono("plus", 16, "#FFFFFF"),
            compound="left",
            fg_color=paleta["acento"],
            hover_color="#865C30",
            text_color="white",
            font=fuente_titulo(12),
            height=40,
        )
        self.btn_guardar.pack(fill="x")

    # ------------------------------------------------------------------
    # Panel derecho: directorio
    # ------------------------------------------------------------------
    def _crear_directorio(self):
        paleta = paleta_tarjeta("verde")
        self.frame_lista = ctk.CTkFrame(self, fg_color="white", corner_radius=18)
        self.frame_lista.grid(row=0, column=1, padx=(8, 0), pady=0, sticky="nsew")

        header_lista = ctk.CTkFrame(self.frame_lista, fg_color="transparent")
        header_lista.pack(fill="x", padx=20, pady=(16, 8))
        ctk.CTkLabel(
            header_lista,
            text="DIRECTORIO",
            font=fuente_etiqueta(8),
            text_color=paleta["acento"],
        ).pack(anchor="w")
        ctk.CTkLabel(
            header_lista,
            text="  Usuarios Registrados",
            image=icono("users-round", 19, paleta["acento"]),
            compound="left",
            font=fuente_titulo(17),
            text_color=COLOR_TEXTO,
        ).pack(anchor="w", pady=(1, 0))
        ctk.CTkLabel(
            header_lista,
            text="Consulta las cuentas y sus permisos.",
            font=fuente(10),
            text_color=COLOR_TEXTO_SUAVE,
        ).pack(anchor="w")

        self.scroll_usuarios = ctk.CTkScrollableFrame(
            self.frame_lista, fg_color="transparent"
        )
        self.scroll_usuarios.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # El esqueleto se muestra hasta que el controlador entrega los datos.
        self.mostrar_cargando()

    # ------------------------------------------------------------------
    # API usada por el controlador
    # ------------------------------------------------------------------
    def obtener_datos_formulario(self):
        return {
            "nombre": self.entry_nombre.get().strip(),
            "ape_pat": self.entry_ape_pat.get().strip(),
            "ape_mat": self.entry_ape_mat.get().strip(),
            "usuario": self.entry_usuario.get().strip(),
            "password": self.entry_password.get().strip(),
            "rol": self.combo_rol.get(),
        }

    def limpiar_formulario(self):
        self.entry_nombre.delete(0, "end")
        self.entry_ape_pat.delete(0, "end")
        self.entry_ape_mat.delete(0, "end")
        self.entry_usuario.delete(0, "end")
        self.entry_password.delete(0, "end")

    def mostrar_cargando(self):
        """Dibuja el esqueleto de carga del directorio."""
        for widget in self.scroll_usuarios.winfo_children():
            widget.destroy()
        SkeletonLista(
            self.scroll_usuarios, filas=4, tono="verde", compacto=True
        )

    def _es_cuenta_actual(self, usuario):
        """Determina si el registro corresponde a la sesión activa."""
        id_actual = self.id_usuario_actual
        if id_actual is not None:
            try:
                if int(usuario.get("id_usuario")) == int(id_actual):
                    return True
            except (TypeError, ValueError):
                pass

        nombre_actual = (self.usuario_actual or "").strip().casefold()
        nombre_registro = (usuario.get("usuario") or "").strip().casefold()
        return bool(nombre_actual and nombre_registro == nombre_actual)

    def mostrar_usuarios(self, lista):
        for widget in self.scroll_usuarios.winfo_children():
            widget.destroy()

        if not lista:
            ctk.CTkLabel(
                self.scroll_usuarios,
                text="No hay usuarios registrados.",
                font=fuente(11),
                text_color=COLOR_TEXTO_SUAVE,
            ).pack(pady=20)
            return

        for usuario in lista:
            self._crear_tarjeta_usuario(usuario)

    def _crear_tarjeta_usuario(self, usuario):
        es_cuenta_actual = self._es_cuenta_actual(usuario)
        card = crear_tarjeta_tinte(self.scroll_usuarios, "verde")
        card.pack(fill="x", pady=4, padx=2)
        card.grid_columnconfigure(2, weight=1)

        # Riel de acento: cada cuenta tiene su propio cuerpo visual.
        ctk.CTkFrame(
            card,
            width=3,
            height=1,
            corner_radius=2,
            fg_color=VERDE if es_cuenta_actual else "#BBD6C0",
        ).grid(row=0, column=0, rowspan=3, sticky="ns", padx=(10, 0), pady=10)

        # Avatar con inicial del usuario.
        inicial = (usuario.get("nombre") or "?").strip()[:1].upper() or "?"
        ctk.CTkLabel(
            card,
            text=inicial,
            width=34,
            height=34,
            corner_radius=17,
            fg_color="#EAF4EC",
            text_color=VERDE,
            font=fuente_titulo(13),
        ).grid(row=0, column=1, rowspan=2, sticky="w", padx=(10, 8), pady=(10, 0))

        nombre_completo = (
            f"{usuario['nombre']} {usuario['ape_pat']} {usuario['ape_mat'] or ''}"
        ).strip()
        ctk.CTkLabel(
            card,
            text=nombre_completo,
            font=fuente_titulo(13),
            text_color="#1B4D26",
            anchor="w",
        ).grid(row=0, column=2, columnspan=2, sticky="w", pady=(10, 0))

        rol = usuario.get("rol") or "Docente"
        fondo_rol, texto_rol = COLOR_ROL.get(rol, ("#EFF3F1", "#4B5563"))

        ctk.CTkLabel(
            card,
            text=f"  @{usuario['usuario']}   ·   ID {usuario['id_usuario']}",
            image=icono("user-round", 12, GRIS_OSCURO),
            compound="left",
            font=fuente_dato(10),
            text_color=COLOR_TEXTO_SUAVE,
            anchor="w",
        ).grid(row=1, column=2, columnspan=2, sticky="w", pady=(0, 2))

        footer = ctk.CTkFrame(card, fg_color="transparent")
        footer.grid(row=2, column=1, columnspan=3, sticky="ew", padx=(0, 12), pady=(2, 8))

        ctk.CTkLabel(
            footer,
            text=f" {rol} ",
            font=fuente_etiqueta(9),
            text_color=texto_rol,
            fg_color=fondo_rol,
            corner_radius=6,
            height=20,
        ).pack(side="left")

        if es_cuenta_actual:
            ctk.CTkLabel(
                footer,
                text="  Tu cuenta (sesión activa)",
                image=icono("circle-check", 13, VERDE),
                compound="left",
                font=fuente_etiqueta(9),
                text_color=VERDE,
            ).pack(side="left", padx=(6, 0))

        # La cuenta propia nunca muestra el botón de eliminar.
        if self.puede_eliminar and self.on_eliminar_usuario and not es_cuenta_actual:
            crear_boton_eliminar(
                footer,
                lambda uid=usuario["id_usuario"]: self.on_eliminar_usuario(uid),
            ).pack(side="right")
