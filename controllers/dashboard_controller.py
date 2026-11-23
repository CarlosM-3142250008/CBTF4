from tkinter import messagebox
from models.dashboard_model import DashboardModel
from views.convocatorias_view import ConvocatoriasView
from views.avisos_materiales_view import AvisosMaterialesView
from views.asistencia_view import AsistenciaView
from views.insertar_usuarios_view import UsuariosView
from controllers.convocatorias_controller import ConvocatoriasController
from controllers.avisos_materiales_controller import AvisosMaterialesController
from controllers.asistencia_controller import AsistenciaController
from controllers.insertar_usuarios_controller import UsuariosController


class DashboardController:
    def __init__(self, view, usuario_datos, on_logout=None):
        self.view = view
        self.usuario = usuario_datos
        self.on_logout = on_logout
        self.model = DashboardModel()

        # Obtención precisa del id_rol y del rol desde la base de datos
        self.id_rol = self.usuario.get('id_rol', 3)
        
        # Mapeo por defecto si el texto viniera vacío (1: Jefe de Academia, 2: Coordinador de Academia, 3: Docente)
        mapa_roles = {1: "Jefe de Academia", 2: "Coordinador de Academia", 3: "Docente"}
        self.rol = self.usuario.get('rol') or mapa_roles.get(self.id_rol, "Docente")

        # El administrador del sistema es el Jefe de Academia (rol 1).
        # Se acepta también el nombre "Administrador" por si el rol se renombra en la BD.
        self.es_administrador = (
            self.id_rol == 1
            or str(self.rol).strip().lower() in ("administrador", "jefe de academia")
        )

        # Configurar información del usuario logueado en el encabezado
        nombre_usr = f"{self.usuario.get('nombre', '')}".strip()
        self.view.actualizar_usuario_header(nombre_usr, self.rol)

        # Cargar datos iniciales del Panel Principal
        self.cargar_datos_panel_principal()

        # Instanciar vistas secundarias (Submódulos)
        self.vista_convocatorias = ConvocatoriasView(self.view.main_container)
        self.vista_avisos_mat = AvisosMaterialesView(self.view.main_container)
        self.vista_asistencia = AsistenciaView(self.view.main_container)
        self.vista_usuarios = UsuariosView(self.view.main_container)

        # Instanciar controladores de cada submódulo
        self.controller_convocatorias = ConvocatoriasController(
            self.vista_convocatorias,
            es_admin=self.es_administrador
        )
        self.controller_avisos_mat = AvisosMaterialesController(
            self.vista_avisos_mat,
            self.usuario.get('id_usuario', 1),
            es_admin=self.es_administrador
        )
        self.controller_asistencia = AsistenciaController(self.vista_asistencia)
        self.controller_usuarios = UsuariosController(
            self.vista_usuarios,
            es_admin=self.es_administrador,
            id_usuario_actual=self.usuario.get('id_usuario'),
            usuario_actual=self.usuario.get('usuario')
        )

        # Aplicar restricciones en la barra lateral y en las subvistas según el rol real
        self.view.aplicar_restricciones_sidebar(
            self.rol, es_jefe=self.es_administrador
        )
        self.ajustar_subvistas_segun_rol()

        # Enlazar eventos de los botones de la barra lateral
        self.view.btn_nav_dashboard.configure(command=self.mostrar_dashboard)
        self.view.btn_nav_convocatorias.configure(command=self.mostrar_convocatorias)
        self.view.btn_nav_materiales.configure(command=self.mostrar_avisos_materiales)
        self.view.btn_nav_asistencia.configure(command=self.mostrar_asistencia)

        if hasattr(self.view, 'btn_nav_usuarios') and self.view.btn_nav_usuarios:
            self.view.btn_nav_usuarios.configure(command=self.mostrar_usuarios)

        self.view.btn_logout.configure(command=self.cerrar_sesion)
        self.view.sidebar.establecer_accion_logo(self.mostrar_dashboard)
        self.view.marcar_nav("dashboard")

    def es_docente(self):
        """Verifica si el usuario actual es Docente por ID (3) o por nombre."""
        return self.id_rol == 3 or str(self.rol).strip().lower() == "docente"

    def ajustar_subvistas_segun_rol(self):
        """Oculta paneles de creación/edición en los módulos únicamente si el rol es Docente."""
        if self.es_docente():
            # Ocultar formulario de creación en Convocatorias y expandir la lista
            if hasattr(self.vista_convocatorias, "frame_form"):
                self.vista_convocatorias.frame_form.grid_forget()
                self.vista_convocatorias.frame_lista.grid(
                    row=0, column=0, columnspan=2, sticky="nsew"
                )

            # En Avisos y Materiales se ocultan los formularios y botones de alta,
            # conservando las dos columnas de consulta.
            if hasattr(self.vista_avisos_mat, "configurar_modo_lectura"):
                self.vista_avisos_mat.configurar_modo_lectura(True)
            elif hasattr(self.vista_avisos_mat, "frame_formularios"):
                self.vista_avisos_mat.frame_formularios.grid_forget()
        else:
            if hasattr(self.vista_avisos_mat, "configurar_modo_lectura"):
                self.vista_avisos_mat.configurar_modo_lectura(False)

    def cargar_datos_panel_principal(self):
        """Dibuja los esqueletos y actualiza el panel al siguiente ciclo."""
        self.view.mostrar_cargando_panel()
        self.view.after(90, self._cargar_datos_panel_principal)

    def _cargar_datos_panel_principal(self):
        try:
            if not self.view.winfo_exists():
                return
        except Exception:
            return

        kpis = self.model.obtener_kpis()
        convocatorias = self.model.obtener_convocatorias_recientes()
        avisos = self.model.obtener_avisos_recientes()

        self.view.actualizar_kpis(kpis)
        self.view.mostrar_convocatorias(convocatorias)
        self.view.mostrar_avisos(avisos)

    def mostrar_dashboard(self):
        """Regresa al panel principal ocultando cualquier submódulo activo."""
        self.view.marcar_nav("dashboard")
        self.view.mostrar_pantalla_dashboard()
        self.cargar_datos_panel_principal()
        try:
            self.view.scroll_content._parent_canvas.yview_moveto(0)
        except Exception:
            pass

    def mostrar_convocatorias(self):
        self.view.marcar_nav("convocatorias")
        self.view.actualizar_titulo_header("Gestión de Convocatorias", "calendar-days")
        self.controller_convocatorias.cargar_convocatorias()
        self.view.cambiar_vista_modulo(self.vista_convocatorias)
        self.vista_convocatorias.after_idle(self.vista_convocatorias.desplazar_lista_al_inicio)

    def mostrar_avisos_materiales(self):
        self.view.marcar_nav("materiales")
        self.view.actualizar_titulo_header("Avisos y Recursos Materiales", "folder-open")
        self.controller_avisos_mat.cargar_datos()
        self.view.cambiar_vista_modulo(self.vista_avisos_mat)
        self.vista_avisos_mat.after_idle(self.vista_avisos_mat.ir_a_avisos)

    def mostrar_asistencia(self):
        """Módulo exclusivo del Jefe de Academia (rol 1)."""
        if not self.es_administrador:
            messagebox.showwarning(
                "Acceso Restringido",
                "El Control de Asistencia está reservado para el Jefe de Academia.",
            )
            return

        self.view.marcar_nav("asistencia")
        self.view.actualizar_titulo_header(
            "Registro y Control de Asistencias", "clipboard-check"
        )
        self.controller_asistencia.cargar_profesores()
        self.view.cambiar_vista_modulo(self.vista_asistencia)

    def mostrar_usuarios(self):
        """Bloquea el módulo únicamente para Docentes. Permite paso a Jefe y Coordinador."""
        if self.es_docente():
            messagebox.showwarning("Acceso Restringido", "Los docentes no cuentan con permisos para gestionar usuarios.")
            return

        self.view.actualizar_titulo_header(
            "Administración de Usuarios del Sistema", "users-round"
        )
        self.view.marcar_nav("usuarios")
        self.controller_usuarios.cargar_usuarios()
        self.view.cambiar_vista_modulo(self.vista_usuarios)

    def cerrar_sesion(self):
        confirmar = messagebox.askyesno(
            "Cerrar sesión",
            "¿Deseas cerrar tu sesión?\n\nVolverás a la pantalla de acceso.",
            parent=self.view,
        )
        if not confirmar:
            return

        callback = self.on_logout
        try:
            self.view.destroy()
        finally:
            if callable(callback):
                callback()