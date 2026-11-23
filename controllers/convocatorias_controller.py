from datetime import datetime
from tkinter import messagebox

from models.convocatoria_model import ConvocatoriaModel


class ConvocatoriasController:
    def __init__(self, view, es_admin=False):
        self.view = view
        self.model = ConvocatoriaModel()
        self.es_admin = bool(es_admin)
        self.id_convocatoria_edicion = None

        # La vista dibuja las acciones administrativas únicamente para el administrador.
        self.view.puede_eliminar = self.es_admin
        self.view.puede_editar = self.es_admin
        self.view.on_eliminar = self.eliminar_convocatoria
        self.view.on_editar = self.preparar_edicion
        self.view.on_cancelar_edicion = self.cancelar_edicion

        self.view.btn_guardar.configure(command=self.guardar_convocatoria)

    def cargar_convocatorias(self):
        """Muestra el esqueleto y consulta el historial sin bloquear el dibujo."""
        self.view.mostrar_cargando()
        self.view.after(80, self._cargar_convocatorias_ahora)

    def _cargar_convocatorias_ahora(self):
        try:
            if not self.view.winfo_exists():
                return
        except Exception:
            return

        academias = self.model.obtener_lista_academias()
        self.view.actualizar_opciones_academias(academias)

        lista = self.model.obtener_convocatorias()
        self.view.mostrar_convocatorias(lista)

    def _validar_formulario(self, datos):
        if not datos['orden'] or not datos['fecha'] or not datos['hora']:
            messagebox.showwarning(
                "Campos vacíos",
                "Por favor completa la fecha, hora y el orden del día."
            )
            return False

        try:
            datetime.strptime(f"{datos['fecha']} {datos['hora']}", "%Y-%m-%d %H:%M")
        except ValueError:
            messagebox.showwarning(
                "Formato inválido",
                "La fecha debe tener el formato AAAA-MM-DD y la hora HH:MM (24 horas)."
            )
            return False
        return True

    def guardar_convocatoria(self):
        datos = self.view.obtener_datos_formulario()
        if not self._validar_formulario(datos):
            return

        id_academia = self.model.obtener_id_academia_por_nombre(datos['academia'])
        timestamp_inicio = f"{datos['fecha']} {datos['hora']}:00"

        if self.id_convocatoria_edicion is not None:
            exito = self.model.actualizar_convocatoria(
                id_convocatoria=self.id_convocatoria_edicion,
                tipo_sesion=datos['tipo'],
                id_academia=id_academia,
                fecha_hora_inicio=timestamp_inicio,
                orden_dia=datos['orden'],
                documento_oficial=datos['doc_oficial']
            )
            mensaje_exito = "La convocatoria se actualizó correctamente."
            titulo_exito = "Convocatoria actualizada"
            mensaje_error = "No se pudo actualizar la convocatoria en la base de datos."
        else:
            exito = self.model.crear_convocatoria(
                tipo_sesion=datos['tipo'],
                id_academia=id_academia,
                fecha_hora_inicio=timestamp_inicio,
                orden_dia=datos['orden'],
                documento_oficial=datos['doc_oficial']
            )
            mensaje_exito = "¡Convocatoria emitida correctamente!"
            titulo_exito = "Éxito"
            mensaje_error = "No se pudo registrar la convocatoria en la base de datos."

        if exito:
            messagebox.showinfo(titulo_exito, mensaje_exito)
            self.id_convocatoria_edicion = None
            self.view.salir_modo_edicion()
            self.cargar_convocatorias()
            self.view.desplazar_lista_al_inicio()
        else:
            messagebox.showerror("Error de guardado", mensaje_error)

    def preparar_edicion(self, convocatoria):
        """Precarga el formulario con una convocatoria existente (solo administrador)."""
        if not self.es_admin:
            messagebox.showwarning(
                "Acceso restringido",
                "Solo el administrador puede editar convocatorias."
            )
            return

        try:
            id_convocatoria = convocatoria['id_convocatoria']
        except (KeyError, TypeError):
            messagebox.showerror("Error", "No se pudieron obtener los datos de la convocatoria.")
            return

        self.id_convocatoria_edicion = id_convocatoria
        self.view.cargar_datos_edicion(convocatoria)

    def cancelar_edicion(self):
        self.id_convocatoria_edicion = None
        self.view.salir_modo_edicion()

    def eliminar_convocatoria(self, id_convocatoria):
        """Elimina una convocatoria. Solo disponible para el administrador."""
        if not self.es_admin:
            messagebox.showwarning(
                "Acceso restringido",
                "Solo el administrador puede eliminar convocatorias."
            )
            return

        if not messagebox.askyesno(
            "Eliminar convocatoria",
            "¿Deseas eliminar esta convocatoria?\n\nEsta acción no se puede deshacer."
        ):
            return

        if self.model.eliminar_convocatoria(id_convocatoria):
            if self.id_convocatoria_edicion == id_convocatoria:
                self.cancelar_edicion()
            messagebox.showinfo("Convocatoria eliminada", "La convocatoria se eliminó correctamente.")
            self.cargar_convocatorias()
        else:
            messagebox.showerror(
                "Error",
                "No se pudo eliminar la convocatoria. Revisa la consola para ver el detalle."
            )
