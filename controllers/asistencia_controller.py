from tkinter import messagebox
from models.asistencia_model import AsistenciaModel

class AsistenciaController:
    def __init__(self, view):
        self.view = view
        self.model = AsistenciaModel()

        # Vincular botones a las funciones correspondientes
        self.view.btn_buscar.configure(command=self.cargar_profesores)
        self.view.btn_guardar_asistencia.configure(command=self.guardar_asistencia)

    def cargar_profesores(self):
        self.view.mostrar_cargando()
        self.view.after(80, self._cargar_profesores_ahora)

    def _cargar_profesores_ahora(self):
        try:
            if not self.view.winfo_exists():
                return
        except Exception:
            return
        profesores = self.model.obtener_docentes()
        self.view.cargar_datos(profesores)

    def guardar_asistencia(self):
        datos = self.view.obtener_datos_para_guardar()
        
        if not datos or not datos.get('registros'):
            messagebox.showwarning("Atención", "No hay docentes en la lista para registrar asistencia.")
            return

        guardados = 0
        for prof_id, info in datos['registros'].items():
            exito = self.model.guardar_asistencia(
                id_sesion=datos['id_clase'],
                id_usuario=prof_id,
                fecha=datos['fecha'],
                estatus=info['estado'],
                momento=datos['momento'],
                minutos_retardo=info['minutos'],
                motivo_justificacion=info['motivo']
            )
            if exito:
                guardados += 1

        if guardados > 0:
            messagebox.showinfo("Éxito", f"Se registraron {guardados} asistencias correctamente en la base de datos.")
        else:
            messagebox.showerror("Error", "No se pudo guardar la asistencia en la base de datos. Revisa la consola para ver el detalle.")