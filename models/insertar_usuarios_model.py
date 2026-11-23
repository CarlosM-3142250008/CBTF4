from models.database_connection import Database_connection

class UsuarioGestionModel:
    def __init__(self):
        self.db = Database_connection()

    def obtener_roles(self):
        query = 'SELECT id_rol, rol FROM "CBTF".roles ORDER BY id_rol ASC;'
        return self.db.ejecutar_consulta(query) or []

    def obtener_todos_los_usuarios(self):
        """Consulta todos los usuarios registrados con el nombre de su rol."""
        query = """
            SELECT u.id_usuario, u.nombre, u.ape_pat, u.ape_mat, u.usuario, r.rol
            FROM "CBTF".usuarios u
            JOIN "CBTF".roles r ON u.id_rol = r.id_rol
            ORDER BY u.id_usuario DESC;
        """
        return self.db.ejecutar_consulta(query) or []

    def existe_nombre_usuario(self, usuario_str):
        query = 'SELECT id_usuario FROM "CBTF".usuarios WHERE usuario = %s;'
        res = self.db.ejecutar_consulta(query, (usuario_str,))
        return len(res) > 0 if res else False

    def registrar_usuario(self, nombre, ape_pat, ape_mat, usuario, pass_hash, id_rol):
        query_max_id = 'SELECT COALESCE(MAX(id_usuario), 0) + 1 AS next_id FROM "CBTF".usuarios;'
        res_id = self.db.ejecutar_consulta(query_max_id)
        next_id = res_id[0]['next_id'] if res_id else 1

        query_insert = """
            INSERT INTO "CBTF".usuarios (id_usuario, id_rol, nombre, ape_pat, ape_mat, pass_hash, usuario)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        conexion = self.db.get_connection()
        if not conexion:
            return False
        try:
            with conexion.cursor() as cursor:
                cursor.execute(query_insert, (next_id, id_rol, nombre, ape_pat, ape_mat, pass_hash, usuario))
                conexion.commit()
                return True
        except Exception as e:
            print(f"Error registrando usuario: {e}")
            return False
        finally:
            conexion.close()

    def eliminar_usuario(self, id_usuario):
        """Elimina un usuario por su ID. Devuelve True si se eliminó al menos un registro."""
        query_delete = 'DELETE FROM "CBTF".usuarios WHERE id_usuario = %s;'
        conexion = self.db.get_connection()
        if not conexion:
            return False
        try:
            with conexion.cursor() as cursor:
                cursor.execute(query_delete, (id_usuario,))
                eliminados = cursor.rowcount
                conexion.commit()
                return eliminados > 0
        except Exception as e:
            print(f"Error eliminando usuario: {e}")
            if conexion:
                conexion.rollback()
            return False
        finally:
            if conexion:
                conexion.close()