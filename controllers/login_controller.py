import queue
import threading
from tkinter import messagebox

from models.login_model import LoginModel
from views.dashboard_view import DashboardView
from controllers.dashboard_controller import DashboardController


class LoginController:
    """Coordina el login sin bloquear el hilo de la interfaz.

    La consulta a PostgreSQL se ejecuta en un hilo aparte. El hilo de la
    interfaz solo revisa una cola cada 60 ms, de modo que el spinner sigue
    girando con fluidez mientras se valida la credencial.
    """

    def __init__(self, view):
        self.view = view
        self.model = LoginModel()

        self._validando = False
        self._cola = None
        self._sondeo_id = None
        self._dashboard_view = None
        self._dashboard_controller = None

        # Vincular el botón de inicio de sesión al método procesar_login
        self.view.btn_login.configure(command=self.procesar_login)

        # Permitir iniciar sesión al presionar la tecla Enter
        self.view.bind("<Return>", lambda event: self.procesar_login())

    def procesar_login(self):
        if self._validando:
            return

        usuario = self.view.entry_usuario.get().strip()
        password = self.view.entry_password.get().strip()

        if not usuario or not password:
            self.view.mostrar_error_auth(
                "Ingresa tu usuario y contraseña para continuar."
            )
            return

        self._validando = True
        self._cola = queue.Queue()
        self.view.mostrar_carga()

        hilo = threading.Thread(
            target=self._validar_en_segundo_plano,
            args=(usuario, password),
            daemon=True,
        )
        hilo.start()

        self._sondeo_id = self.view.after(60, self._revisar_resultado)

    def _validar_en_segundo_plano(self, usuario, password):
        """Trabajo de red/BD fuera del hilo de Tkinter."""
        try:
            datos = self.model.verificar_credenciales(usuario, password)
            if datos:
                self._cola.put(("ok", datos))
            else:
                self._cola.put(("invalido", None))
        except Exception as error:
            self._cola.put(("error", str(error)))

    def _revisar_resultado(self):
        self._sondeo_id = None
        if not self._validando or not self.view.winfo_exists():
            return

        try:
            estado, datos = self._cola.get_nowait()
        except queue.Empty:
            self._sondeo_id = self.view.after(60, self._revisar_resultado)
            return

        self._validando = False

        if estado == "ok":
            self.view.ocultar_carga()
            self._abrir_dashboard(datos)
            return

        self.view.ocultar_carga()

        if estado == "invalido":
            self.view.mostrar_error_auth(
                "Usuario o contraseña incorrectos. Verifica tus datos."
            )
            self.view.entry_password.delete(0, "end")
            self.view.entry_password.focus_set()
        else:
            self.view.mostrar_error_auth(
                "No se pudo conectar con el servidor. Revisa la conexión e intenta de nuevo."
            )

    def _abrir_dashboard(self, usuario_db):
        """Abre el panel como ventana secundaria y oculta el login."""
        dashboard_view = None

        try:
            dashboard_view = DashboardView(master=self.view)
            self._dashboard_controller = DashboardController(
                dashboard_view,
                usuario_db,
                on_logout=self._volver_al_login,
            )
            self._dashboard_view = dashboard_view

            # El panel ya está construido: recién aquí se oculta el login
            # para evitar un parpadeo a escritorio vacío.
            self.view.withdraw()
            dashboard_view.after(80, self._presentar_dashboard)
        except Exception as error:
            self._dashboard_view = None
            self._dashboard_controller = None
            try:
                if dashboard_view is not None and dashboard_view.winfo_exists():
                    dashboard_view.destroy()
            except Exception:
                pass
            self.view.deiconify()
            self.view.lift()
            messagebox.showerror(
                "Error al abrir el panel",
                f"No se pudo iniciar el panel principal.\n\n{error}",
            )

    def _presentar_dashboard(self):
        """Trae el panel al frente una vez que la raíz quedó oculta."""
        vista = self._dashboard_view
        if vista is None:
            return
        try:
            if not vista.winfo_exists():
                return
            vista.deiconify()
            vista.lift()
            vista.focus_force()
        except Exception:
            pass

    def _volver_al_login(self):
        """Cierra el panel y restaura la pantalla de acceso sin terminar la app."""
        self._dashboard_view = None
        self._dashboard_controller = None
        self._validando = False

        try:
            self.view.ocultar_carga()
            self.view.entry_password.delete(0, "end")
            self.view.limpiar_error()
            self.view.deiconify()
            self.view.lift()
            self.view.focus_force()
            self.view.after(80, self.view.enfocar_entrada)
        except Exception:
            pass
