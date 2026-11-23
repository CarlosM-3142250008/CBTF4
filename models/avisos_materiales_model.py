from models.database_connection import Database_connection

class AvisosMaterialesModel:
    def __init__(self):
        self.db = Database_connection()

    def obtener_avisos(self):
        """Avisos ordenados por fecha de publicación (más reciente primero)."""
        query = """
            SELECT a.id_aviso, a.titulo, a.emisor,
                   a.fecha_evento, a.contenido AS detalle, a.fecha_publicacion,
                   COALESCE(ac.nombre_academia, a.destinatario_texto, 'General') AS destinatario
            FROM "CBTF".avisos a
            LEFT JOIN "CBTF".academias ac ON a.id_academia_destinatario = ac.id_academia
            ORDER BY a.fecha_publicacion DESC, a.id_aviso DESC;
        """
        return self.db.ejecutar_consulta(query) or []

    def obtener_materiales(self):
        """Materiales ordenados por fecha de publicación (más reciente primero)."""
        query = """
            SELECT m.id_material, m.nombre, m.id_catalogo,
                   COALESCE(ac.nombre_academia, c.nombre_catalogo, 'General') AS categoria,
                   m.descripcion, m.enlace, m.fecha_registro AS fecha_publicacion,
                   m.id_academia_destinatario
            FROM "CBTF".materiales m
            LEFT JOIN "CBTF".catalogo c ON m.id_catalogo = c.id_catalogo
            LEFT JOIN "CBTF".academias ac ON m.id_academia_destinatario = ac.id_academia
            ORDER BY m.fecha_registro DESC, m.id_material DESC;
        """
        return self.db.ejecutar_consulta(query) or []

    def crear_aviso(self, titulo, emisor, fecha_evento, contenido, id_usuario=1,
                    id_academia_destinatario=None, destinatario_texto=None):
        conexion = self.db.get_connection()
        if not conexion:
            return False
        try:
            with conexion.cursor() as cursor:
                query_max_id = 'SELECT COALESCE(MAX(id_aviso), 0) + 1 AS next_id FROM "CBTF".avisos;'
                cursor.execute(query_max_id)
                res_max = cursor.fetchone()
                next_id = res_max['next_id'] if isinstance(res_max, dict) else res_max[0]

                query = """
                    INSERT INTO "CBTF".avisos
                        (id_aviso, titulo, emisor, fecha_evento, contenido, id_usuario,
                         fecha_publicacion, id_academia_destinatario, destinatario_texto)
                    VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s, %s);
                """
                cursor.execute(query, (next_id, titulo, emisor, fecha_evento, contenido,
                                       id_usuario, id_academia_destinatario, destinatario_texto))
                conexion.commit()
                return True
        except Exception as e:
            print(f"--> Error al insertar aviso: {e}")
            if conexion:
                conexion.rollback()
            return False
        finally:
            if conexion:
                conexion.close()

    def crear_material(self, nombre, id_catalogo, descripcion, enlace, id_usuario=1, id_academia_destinatario=None):
        conexion = self.db.get_connection()
        if not conexion:
            return False
        try:
            with conexion.cursor() as cursor:
                query_max_id = 'SELECT COALESCE(MAX(id_material), 0) + 1 AS next_id FROM "CBTF".materiales;'
                cursor.execute(query_max_id)
                res_max = cursor.fetchone()
                next_id = res_max['next_id'] if isinstance(res_max, dict) else res_max[0]

                query = """
                    INSERT INTO "CBTF".materiales
                        (id_material, nombre, id_catalogo, descripcion, enlace, id_usuario,
                         fecha_registro, id_academia_destinatario)
                    VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s);
                """
                cursor.execute(query, (next_id, nombre, id_catalogo, descripcion, enlace,
                                       id_usuario, id_academia_destinatario))
                conexion.commit()
                return True
        except Exception as e:
            print(f"--> Error al insertar material: {e}")
            if conexion:
                conexion.rollback()
            return False
        finally:
            if conexion:
                conexion.close()

    def crear_materiales(self, lista_materiales, id_usuario=1, id_academia_destinatario=None,
                         id_catalogo=1):
        """Inserta varios materiales en una sola transacción.

        Cada elemento de `lista_materiales` debe ser una tupla
        (nombre, descripcion, enlace). Devuelve la cantidad insertada o 0 si falla.
        """
        if not lista_materiales:
            return 0

        conexion = self.db.get_connection()
        if not conexion:
            return 0
        try:
            with conexion.cursor() as cursor:
                query_max_id = 'SELECT COALESCE(MAX(id_material), 0) AS max_id FROM "CBTF".materiales;'
                cursor.execute(query_max_id)
                res_max = cursor.fetchone()
                max_id = res_max['max_id'] if isinstance(res_max, dict) else res_max[0]

                query = """
                    INSERT INTO "CBTF".materiales
                        (id_material, nombre, id_catalogo, descripcion, enlace, id_usuario,
                         fecha_registro, id_academia_destinatario)
                    VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s);
                """
                for indice, (nombre, descripcion, enlace) in enumerate(lista_materiales, start=1):
                    cursor.execute(
                        query,
                        (max_id + indice, nombre, id_catalogo, descripcion, enlace,
                         id_usuario, id_academia_destinatario)
                    )
                conexion.commit()
                return len(lista_materiales)
        except Exception as e:
            print(f"--> Error al insertar materiales: {e}")
            if conexion:
                conexion.rollback()
            return 0
        finally:
            if conexion:
                conexion.close()

    def actualizar_aviso(self, id_aviso, titulo, emisor, fecha_evento, contenido,
                         id_academia_destinatario=None, destinatario_texto=None):
        """Actualiza un aviso sin modificar su fecha original de publicación."""
        conexion = self.db.get_connection()
        if not conexion:
            return False
        try:
            with conexion.cursor() as cursor:
                query = """
                    UPDATE "CBTF".avisos
                    SET titulo = %s,
                        emisor = %s,
                        fecha_evento = %s,
                        contenido = %s,
                        id_academia_destinatario = %s,
                        destinatario_texto = %s
                    WHERE id_aviso = %s;
                """
                cursor.execute(
                    query,
                    (titulo, emisor, fecha_evento, contenido,
                     id_academia_destinatario, destinatario_texto, id_aviso)
                )
                actualizados = cursor.rowcount
                conexion.commit()
                return actualizados > 0
        except Exception as e:
            print(f"--> Error al actualizar aviso: {e}")
            if conexion:
                conexion.rollback()
            return False
        finally:
            if conexion:
                conexion.close()

    def actualizar_material(self, id_material, nombre, id_catalogo, descripcion,
                            enlace, id_academia_destinatario=None):
        """Actualiza un material conservando su autor y fecha de registro."""
        conexion = self.db.get_connection()
        if not conexion:
            return False
        try:
            with conexion.cursor() as cursor:
                query = """
                    UPDATE "CBTF".materiales
                    SET nombre = %s,
                        id_catalogo = %s,
                        descripcion = %s,
                        enlace = %s,
                        id_academia_destinatario = %s
                    WHERE id_material = %s;
                """
                cursor.execute(
                    query,
                    (nombre, id_catalogo, descripcion, enlace,
                     id_academia_destinatario, id_material)
                )
                actualizados = cursor.rowcount
                conexion.commit()
                return actualizados > 0
        except Exception as e:
            print(f"--> Error al actualizar material: {e}")
            if conexion:
                conexion.rollback()
            return False
        finally:
            if conexion:
                conexion.close()

    def obtener_material(self, id_material):
        """Devuelve los datos basicos de un material por su ID."""
        query = """
            SELECT id_material, nombre, enlace
            FROM "CBTF".materiales
            WHERE id_material = %s;
        """
        resultado = self.db.ejecutar_consulta(query, (id_material,))
        return resultado[0] if resultado else None

    def eliminar_aviso(self, id_aviso):
        conexion = self.db.get_connection()
        if not conexion:
            return False
        try:
            with conexion.cursor() as cursor:
                cursor.execute('DELETE FROM "CBTF".avisos WHERE id_aviso = %s', (id_aviso,))
                conexion.commit()
                return True
        except Exception as e:
            print(f"--> Error al eliminar aviso: {e}")
            if conexion:
                conexion.rollback()
            return False
        finally:
            if conexion:
                conexion.close()

    def eliminar_material(self, id_material):
        conexion = self.db.get_connection()
        if not conexion:
            return False
        try:
            with conexion.cursor() as cursor:
                cursor.execute('DELETE FROM "CBTF".materiales WHERE id_material = %s', (id_material,))
                conexion.commit()
                return True
        except Exception as e:
            print(f"--> Error al eliminar material: {e}")
            if conexion:
                conexion.rollback()
            return False
        finally:
            if conexion:
                conexion.close()
