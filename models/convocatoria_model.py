from models.database_connection import Database_connection

class ConvocatoriaModel:
    def __init__(self):
        self.db = Database_connection()

    def obtener_lista_academias(self):
        """Devuelve los nombres de todas las academias registradas en PostgreSQL."""
        query = 'SELECT nombre_academia FROM "CBTF".academias ORDER BY id_academia ASC;'
        res = self.db.ejecutar_consulta(query) or []
        return [r['nombre_academia'] for r in res]

    def obtener_academias_con_id(self):
        """Devuelve id y nombre de las academias para mapear los desplegables."""
        query = 'SELECT id_academia, nombre_academia FROM "CBTF".academias ORDER BY id_academia ASC;'
        return self.db.ejecutar_consulta(query) or []

    def obtener_id_academia_por_nombre(self, nombre_academia):
        query = 'SELECT id_academia FROM "CBTF".academias WHERE nombre_academia = %s;'
        res = self.db.ejecutar_consulta(query, (nombre_academia,))
        return res[0]['id_academia'] if res else 1

    def obtener_id_academia_opcional(self, nombre_academia):
        """Devuelve el id de la academia o None si no es una academia válida."""
        query = 'SELECT id_academia FROM "CBTF".academias WHERE nombre_academia = %s;'
        res = self.db.ejecutar_consulta(query, (nombre_academia,))
        return res[0]['id_academia'] if res else None

    def obtener_convocatorias(self):
        """Historial completo ordenado por fecha de publicación (más reciente primero)."""
        query = """
            SELECT c.id_convocatoria, c.tipo_sesion AS tipo, a.nombre_academia AS academia,
                   c.fecha_hora_inicio AS fecha_hora, c.fecha_publicacion,
                   c.orden_dia, c.documento_oficial
            FROM "CBTF".convocatorias c
            JOIN "CBTF".academias a ON c.id_academia = a.id_academia
            ORDER BY c.fecha_publicacion DESC, c.id_convocatoria DESC;
        """
        return self.db.ejecutar_consulta(query) or []

    def crear_convocatoria(self, tipo_sesion, id_academia, fecha_hora_inicio, orden_dia, documento_oficial=""):
        conexion = self.db.get_connection()
        if not conexion:
            return False

        try:
            with conexion.cursor() as cursor:
                query_max_id = 'SELECT COALESCE(MAX(id_convocatoria), 0) + 1 AS next_id FROM "CBTF".convocatorias;'
                cursor.execute(query_max_id)
                res_max = cursor.fetchone()
                next_id = res_max['next_id'] if isinstance(res_max, dict) else res_max[0]

                query_insert = """
                    INSERT INTO "CBTF".convocatorias
                        (id_convocatoria, tipo_sesion, id_academia, fecha_hora_inicio,
                         orden_dia, documento_oficial, fecha_publicacion)
                    VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP);
                """
                cursor.execute(query_insert, (next_id, tipo_sesion, id_academia, fecha_hora_inicio, orden_dia, documento_oficial))
                conexion.commit()
                return True
        except Exception as e:
            print(f"--> Error al insertar convocatoria: {e}")
            if conexion:
                conexion.rollback()
            return False
        finally:
            if conexion:
                conexion.close()

    def actualizar_convocatoria(self, id_convocatoria, tipo_sesion, id_academia,
                                fecha_hora_inicio, orden_dia, documento_oficial=""):
        """Actualiza una convocatoria existente conservando su fecha de publicación."""
        conexion = self.db.get_connection()
        if not conexion:
            return False

        try:
            with conexion.cursor() as cursor:
                query_update = """
                    UPDATE "CBTF".convocatorias
                    SET tipo_sesion = %s,
                        id_academia = %s,
                        fecha_hora_inicio = %s,
                        orden_dia = %s,
                        documento_oficial = %s
                    WHERE id_convocatoria = %s;
                """
                cursor.execute(
                    query_update,
                    (tipo_sesion, id_academia, fecha_hora_inicio, orden_dia,
                     documento_oficial, id_convocatoria)
                )
                actualizados = cursor.rowcount
                conexion.commit()
                return actualizados > 0
        except Exception as e:
            print(f"--> Error al actualizar convocatoria: {e}")
            if conexion:
                conexion.rollback()
            return False
        finally:
            if conexion:
                conexion.close()

    def eliminar_convocatoria(self, id_convocatoria):
        conexion = self.db.get_connection()
        if not conexion:
            return False
        try:
            with conexion.cursor() as cursor:
                cursor.execute('DELETE FROM "CBTF".convocatorias WHERE id_convocatoria = %s', (id_convocatoria,))
                conexion.commit()
                return True
        except Exception as e:
            print(f"--> Error al eliminar convocatoria: {e}")
            if conexion:
                conexion.rollback()
            return False
        finally:
            if conexion:
                conexion.close()
