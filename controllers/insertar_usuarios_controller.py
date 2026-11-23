from tkinter import messagebox
from models.insertar_usuarios_model import UsuarioGestionModel

class UsuariosController:
    def __init__(self, view, es_admin=False, id_usuario_actual=None, usuario_actual=None):
        self.view = view
        self.model = UsuarioGestionModel()
        self.es_admin = bool(es_admin)
        self.id_usuario_actual = id_usuario_actual
        self.usuario_actual = usuario_actual

        # Mapeo simple de nombres de rol a ID de la BD
        self.roles_map = {
            "Jefe de Academia": 1,
            "Coordinador de Academia": 2,
            "Docente": 3
        }

        # La vista solo dibuja el botón de eliminar si el usuario es administrador.
        # El controlador vuelve a validar el permiso antes de borrar.
        self.view.puede_eliminar = self.es_admin
        self.view.id_usuario_actual = self.id_usuario_actual
        self.view.usuario_actual = self.usuario_actual
        self.view.on_eliminar_usuario = self.eliminar_usuario

        self.view.btn_guardar.configure(command=self.guardar_usuario)

    def cargar_usuarios(self):
        self.view.mostrar_cargando()
        self.view.after(80, self._cargar_usuarios_ahora)

    def _cargar_usuarios_ahora(self):
        try:
            if not self.view.winfo_exists():
                return
        except Exception:
            return
        lista = self.model.obtener_todos_los_usuarios()
        self.view.mostrar_usuarios(lista)

    def guardar_usuario(self):
        datos = self.view.obtener_datos_formulario()

        if not datos['nombre'] or not datos['ape_pat'] or not datos['usuario'] or not datos['password']:
            messagebox.showwarning("Campos vacíos", "Por favor completa Nombre, Apellido Paterno, Usuario y Contraseña.")
            return

        if self.model.existe_nombre_usuario(datos['usuario']):
            messagebox.showerror("Usuario duplicado", f"El nombre de usuario '{datos['usuario']}' ya existe.")
            return

        id_rol = self.roles_map.get(datos['rol'], 3)

        exito = self.model.registrar_usuario(
            nombre=datos['nombre'],
            ape_pat=datos['ape_pat'],
            ape_mat=datos['ape_mat'],
            usuario=datos['usuario'],
            pass_hash=datos['password'],
            id_rol=id_rol
        )

        if exito:
            messagebox.showinfo("Éxito", f"¡Usuario '{datos['usuario']}' registrado correctamente!")
            self.view.limpiar_formulario()
            self.cargar_usuarios()
        else:
            messagebox.showerror("Error", "No se pudo registrar el usuario en la base de datos.")

    def _es_usuario_actual(self, id_usuario):
        """Compara el ID recibido con la cuenta que tiene la sesión activa."""
        if self.id_usuario_actual is None:
            return False
        try:
            return int(id_usuario) == int(self.id_usuario_actual)
        except (TypeError, ValueError):
            return False

    def eliminar_usuario(self, id_usuario):
        """Elimina un usuario. Solo disponible para el administrador."""
        if not self.es_admin:
            messagebox.showwarning(
                "Acceso restringido",
                "Solo el administrador puede eliminar usuarios."
            )
            return

        if self._es_usuario_actual(id_usuario):
            messagebox.showwarning(
                "Acción no permitida",
                "No puedes eliminar tu propio usuario mientras tienes la sesión iniciada."
            )
            return

        if not messagebox.askyesno(
            "Eliminar usuario",
            "¿Deseas eliminar este usuario?\n\nEsta acción no se puede deshacer."
        ):
            return

        if self.model.eliminar_usuario(id_usuario):
            messagebox.showinfo("Usuario eliminado", "El usuario se eliminó correctamente.")
            self.cargar_usuarios()
        else:
            messagebox.showerror(
                "Error",
                "No se pudo eliminar el usuario. Revisa la consola para ver el detalle."
            )
