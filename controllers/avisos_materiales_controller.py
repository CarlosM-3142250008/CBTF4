import os
import shutil
from datetime import datetime
from tkinter import messagebox

from models.avisos_materiales_model import AvisosMaterialesModel
from models.convocatoria_model import ConvocatoriaModel
from views.ui_utils import parse_fecha


# Carpeta local donde se conservan los archivos subidos desde el equipo.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARPETA_ARCHIVOS = os.path.join(BASE_DIR, "archivos_materiales")


class AvisosMaterialesController:
    def __init__(self, view, id_usuario=1, es_admin=False):
        self.view = view
        self.id_usuario = id_usuario
        self.es_admin = bool(es_admin)
        self.model = AvisosMaterialesModel()
        self.conv_model = ConvocatoriaModel()
        self.mapa_academias = {}

        self.aviso_en_edicion = None
        self.material_en_edicion = None

        # La vista dibuja las acciones administrativas únicamente para el administrador.
        self.view.puede_eliminar = self.es_admin
        self.view.puede_editar = self.es_admin
        self.view.on_eliminar_aviso = self.eliminar_aviso
        self.view.on_eliminar_material = self.eliminar_material
        self.view.on_editar_aviso = self.preparar_edicion_aviso
        self.view.on_editar_material = self.preparar_edicion_material
        self.view.on_cancelar_edicion_aviso = self.cancelar_edicion_aviso
        self.view.on_cancelar_edicion_material = self.cancelar_edicion_material

        # La carga de archivos también está reservada al administrador
        self.view.habilitar_carga_archivos(self.es_admin)
        self.view.btn_subir_archivos.configure(command=self.subir_archivos)

        self.view.btn_guardar_aviso.configure(command=self.guardar_aviso)
        self.view.btn_guardar_material.configure(command=self.guardar_material)

    def cargar_datos(self):
        """Dibuja los esqueletos y luego carga avisos y materiales."""
        self.view.mostrar_cargando()
        self.view.after(80, self._cargar_datos_ahora)

    def _cargar_datos_ahora(self):
        try:
            if not self.view.winfo_exists():
                return
        except Exception:
            return

        # Catálogo de academias con su id para guardar el destinatario real
        academias = self.conv_model.obtener_academias_con_id()
        self.mapa_academias = {
            a['nombre_academia']: a['id_academia'] for a in academias
        }
        self.view.actualizar_academias_dinamicas(list(self.mapa_academias.keys()))

        # Avisos y materiales ordenados por fecha de publicación
        avisos = self.model.obtener_avisos()
        materiales = self.model.obtener_materiales()
        self.view.mostrar_avisos(avisos)
        self.view.mostrar_materiales(materiales)

    # ------------------------------------------------------------------
    # Avisos
    # ------------------------------------------------------------------
    def guardar_aviso(self):
        datos = self.view.obtener_datos_avisos()
        if not datos['titulo'] or not datos['emisor'] or not datos['detalle']:
            messagebox.showwarning("Campos vacíos", "Por favor completa los campos del aviso.")
            return

        fecha_evento = parse_fecha(datos.get('fecha_evento'))
        if not fecha_evento:
            messagebox.showwarning(
                "Fecha inválida",
                "La fecha del evento debe tener el formato AAAA-MM-DD."
            )
            return

        id_destinatario = self.mapa_academias.get(datos['destinatario'])

        if self.aviso_en_edicion is not None:
            exito = self.model.actualizar_aviso(
                id_aviso=self.aviso_en_edicion['id_aviso'],
                titulo=datos['titulo'],
                emisor=datos['emisor'],
                fecha_evento=fecha_evento.date(),
                contenido=datos['detalle'],
                id_academia_destinatario=id_destinatario,
                destinatario_texto=datos['destinatario']
            )
            titulo_exito = "Aviso actualizado"
            mensaje_exito = "El aviso se actualizó correctamente."
            mensaje_error = "No se pudo actualizar el aviso. Revisa la consola para ver el detalle."
        else:
            exito = self.model.crear_aviso(
                datos['titulo'],
                datos['emisor'],
                fecha_evento.strftime("%Y-%m-%d"),
                datos['detalle'],
                id_usuario=self.id_usuario,
                id_academia_destinatario=id_destinatario,
                destinatario_texto=datos['destinatario']
            )
            titulo_exito = "Éxito"
            mensaje_exito = "Aviso publicado correctamente."
            mensaje_error = "No se pudo publicar el aviso. Revisa la consola para ver el detalle."

        if exito:
            messagebox.showinfo(titulo_exito, mensaje_exito)
            self.aviso_en_edicion = None
            self.view.salir_modo_edicion_aviso()
            self.cargar_datos()
            self.view.ir_a_avisos()
        else:
            messagebox.showerror("Error", mensaje_error)

    def preparar_edicion_aviso(self, aviso):
        """Precarga el formulario con un aviso existente (solo administrador)."""
        if not self.es_admin:
            messagebox.showwarning(
                "Acceso restringido",
                "Solo el administrador puede editar avisos."
            )
            return

        if not isinstance(aviso, dict) or 'id_aviso' not in aviso:
            messagebox.showerror("Error", "No se pudieron obtener los datos del aviso.")
            return

        self.aviso_en_edicion = dict(aviso)
        self.view.cargar_datos_edicion_aviso(aviso)

    def cancelar_edicion_aviso(self):
        self.aviso_en_edicion = None
        self.view.salir_modo_edicion_aviso()

    # ------------------------------------------------------------------
    # Materiales
    # ------------------------------------------------------------------
    def guardar_material(self):
        datos = self.view.obtener_datos_materiales()
        if not datos['nombre'] or not datos['enlace']:
            messagebox.showwarning(
                "Campos vacíos",
                "Por favor ingresa al menos el nombre y el enlace del material."
            )
            return

        id_destinatario = self.mapa_academias.get(datos['categoria'])

        if self.material_en_edicion is not None:
            exito = self.model.actualizar_material(
                id_material=self.material_en_edicion['id_material'],
                nombre=datos['nombre'],
                id_catalogo=self.material_en_edicion.get('id_catalogo', 1),
                descripcion=datos['descripcion'],
                enlace=datos['enlace'],
                id_academia_destinatario=id_destinatario
            )
            titulo_exito = "Material actualizado"
            mensaje_exito = "El material se actualizó correctamente."
            mensaje_error = "No se pudo actualizar el material. Revisa la consola para ver el detalle."
        else:
            exito = self.model.crear_material(
                datos['nombre'],
                1,
                datos['descripcion'],
                datos['enlace'],
                id_usuario=self.id_usuario,
                id_academia_destinatario=id_destinatario
            )
            titulo_exito = "Éxito"
            mensaje_exito = "Material guardado correctamente."
            mensaje_error = "No se pudo guardar el material. Revisa la consola para ver el detalle."

        if exito:
            messagebox.showinfo(titulo_exito, mensaje_exito)
            self.material_en_edicion = None
            self.view.salir_modo_edicion_material()
            self.cargar_datos()
            self.view.ir_a_materiales()
        else:
            messagebox.showerror("Error", mensaje_error)

    def preparar_edicion_material(self, material):
        """Precarga el formulario con un material existente (solo administrador)."""
        if not self.es_admin:
            messagebox.showwarning(
                "Acceso restringido",
                "Solo el administrador puede editar materiales."
            )
            return

        if not isinstance(material, dict) or 'id_material' not in material:
            messagebox.showerror("Error", "No se pudieron obtener los datos del material.")
            return

        self.material_en_edicion = dict(material)
        self.view.cargar_datos_edicion_material(material)

    def cancelar_edicion_material(self):
        self.material_en_edicion = None
        self.view.salir_modo_edicion_material()

    # ------------------------------------------------------------------
    # Carga y eliminación de archivos
    # ------------------------------------------------------------------
    def subir_archivos(self):
        """Copia y registra varios archivos elegidos desde cualquier carpeta."""
        if not self.es_admin:
            messagebox.showwarning(
                "Acceso restringido",
                "Solo el administrador puede subir archivos de material."
            )
            return

        archivos = self.view.obtener_archivos_seleccionados()
        if not archivos:
            messagebox.showwarning(
                "Sin archivos",
                "Selecciona al menos un archivo antes de subirlo."
            )
            return

        categoria = self.view.combo_mat_categoria.get()
        id_destinatario = self.mapa_academias.get(categoria)

        preparados = []
        errores = []
        for ruta in archivos:
            try:
                if not os.path.isfile(ruta):
                    errores.append(f"{os.path.basename(ruta)}: ya no existe en esa ruta")
                    continue
                destino = self._copiar_archivo(ruta)
                preparados.append((
                    os.path.basename(ruta),
                    "Archivo cargado desde el equipo.",
                    destino
                ))
            except Exception as e:
                errores.append(f"{os.path.basename(ruta)}: {e}")

        if not preparados:
            detalle = "\n".join(errores[:5]) if errores else "No se pudo copiar ningún archivo."
            messagebox.showerror("Error al subir", "No se pudo subir ningún archivo.\n\n" + detalle)
            return

        insertados = self.model.crear_materiales(
            preparados,
            id_usuario=self.id_usuario,
            id_academia_destinatario=id_destinatario
        )

        if insertados != len(preparados):
            # Evitar archivos huérfanos si la transacción en la BD falló.
            for _, _, destino in preparados:
                self._borrar_archivo_subido(destino)
            messagebox.showerror(
                "Error",
                "No se pudieron registrar los archivos en la base de datos."
            )
            return

        self.view.limpiar_archivos_seleccionados()
        self.cargar_datos()
        self.view.ir_a_materiales()

        mensaje = f"Se subieron {insertados} archivo{'s' if insertados != 1 else ''} correctamente."
        if errores:
            mensaje += "\n\nNo se pudieron subir:\n" + "\n".join(errores[:5])
        messagebox.showinfo("Archivos subidos", mensaje)

    def _copiar_archivo(self, ruta_origen):
        """Copia un archivo a la carpeta local de materiales con nombre único."""
        os.makedirs(CARPETA_ARCHIVOS, exist_ok=True)

        nombre_original = os.path.basename(ruta_origen)
        tallo, extension = os.path.splitext(nombre_original)
        tallo_seguro = "".join(
            caracter for caracter in tallo if caracter not in '<>:"/\\|?*'
        ).strip() or "archivo"
        tallo_seguro = tallo_seguro[:80]

        marca = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        base = f"{marca}_{tallo_seguro}"
        destino = os.path.join(CARPETA_ARCHIVOS, f"{base}{extension}")
        contador = 1
        while os.path.exists(destino):
            destino = os.path.join(CARPETA_ARCHIVOS, f"{base}_{contador}{extension}")
            contador += 1

        shutil.copy2(ruta_origen, destino)
        return destino

    @staticmethod
    def _esta_en_carpeta_archivos(ruta):
        try:
            ruta_abs = os.path.abspath(ruta)
            carpeta_abs = os.path.abspath(CARPETA_ARCHIVOS)
            return os.path.commonpath([ruta_abs, carpeta_abs]) == carpeta_abs
        except (TypeError, ValueError):
            return False

    def _borrar_archivo_subido(self, ruta):
        """Borra únicamente archivos que viven dentro de la carpeta de materiales."""
        if not ruta or not self._esta_en_carpeta_archivos(ruta):
            return
        try:
            if os.path.isfile(ruta):
                os.remove(ruta)
        except OSError as e:
            print(f"--> No se pudo borrar el archivo {ruta}: {e}")

    def eliminar_aviso(self, id_aviso):
        """Elimina un aviso. Solo disponible para el administrador."""
        if not self.es_admin:
            messagebox.showwarning(
                "Acceso restringido",
                "Solo el administrador puede eliminar avisos."
            )
            return

        if not messagebox.askyesno(
            "Eliminar aviso",
            "¿Deseas eliminar este aviso?\n\nEsta acción no se puede deshacer."
        ):
            return

        if self.model.eliminar_aviso(id_aviso):
            if self.aviso_en_edicion and self.aviso_en_edicion.get('id_aviso') == id_aviso:
                self.cancelar_edicion_aviso()
            messagebox.showinfo("Aviso eliminado", "El aviso se eliminó correctamente.")
            self.cargar_datos()
        else:
            messagebox.showerror(
                "Error",
                "No se pudo eliminar el aviso. Revisa la consola para ver el detalle."
            )

    def eliminar_material(self, id_material):
        """Elimina un material. Solo disponible para el administrador."""
        if not self.es_admin:
            messagebox.showwarning(
                "Acceso restringido",
                "Solo el administrador puede eliminar materiales."
            )
            return

        if not messagebox.askyesno(
            "Eliminar material",
            "¿Deseas eliminar este material?\n\nEsta acción no se puede deshacer."
        ):
            return

        material = self.model.obtener_material(id_material)

        if self.model.eliminar_material(id_material):
            if self.material_en_edicion and self.material_en_edicion.get('id_material') == id_material:
                self.cancelar_edicion_material()
            if material:
                self._borrar_archivo_subido(material.get('enlace'))
            messagebox.showinfo("Material eliminado", "El material se eliminó correctamente.")
            self.cargar_datos()
        else:
            messagebox.showerror(
                "Error",
                "No se pudo eliminar el material. Revisa la consola para ver el detalle."
            )
