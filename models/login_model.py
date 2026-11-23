from models.database_connection import Database_connection

class LoginModel:
    def __init__(self):
        self.db = Database_connection()

    def verificar_credenciales(self, usuario, password):
        """Consulta obteniendo el nombre exacto del rol directamente desde la tabla de roles."""
        query = """
            SELECT u.id_usuario, u.nombre, u.ape_pat, u.ape_mat, u.id_rol, r.rol, u.usuario
            FROM "CBTF".usuarios u
            JOIN "CBTF".roles r ON u.id_rol = r.id_rol
            WHERE u.usuario = %s AND u.pass_hash = %s;
        """
        resultado = self.db.ejecutar_consulta(query, (usuario, password))

        if resultado and len(resultado) > 0:
            user_data = resultado[0]
            
            # Soporte para diccionario o tupla
            if isinstance(user_data, dict):
                id_usr = user_data.get('id_usuario')
                nom = user_data.get('nombre', '')
                ape = user_data.get('ape_pat', '')
                usr_name = user_data.get('usuario', '')
                id_rol = user_data.get('id_rol')
                rol_nombre = user_data.get('rol', 'Docente')
            else:
                id_usr = user_data[0]
                nom = user_data[1]
                ape = user_data[2]
                id_rol = user_data[4]
                rol_nombre = user_data[5]
                usr_name = user_data[6]

            nombre_completo = f"{nom} {ape}".strip()

            return {
                "id_usuario": id_usr,
                "nombre": nombre_completo,
                "usuario": usr_name,
                "id_rol": id_rol,
                "rol": rol_nombre,
                "ape_pat": ape
            }
        return None