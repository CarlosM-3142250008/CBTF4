from models.database_connection import Database_connection

class AsistenciaModel:
    def __init__(self):
        self.db = Database_connection()

    def obtener_docentes(self):
        query = """
            SELECT id_usuario AS id, CONCAT(nombre, ' ', ape_pat) AS nombre
            FROM "CBTF".usuarios
            ORDER BY id_usuario ASC;
        """
        return self.db.ejecutar_consulta(query) or []

    def guardar_asistencia(self, id_sesion, id_usuario, fecha, estatus, momento="Inicio", minutos_retardo=0, motivo_justificacion=""):
        conexion = self.db.get_connection()
        if not conexion:
            print("--> Error: No hay conexión a la base de datos.")
            return False

        try:
            with conexion.cursor() as cursor:
                # 1. Verificar si ya existe el registro para esa sesión, ese usuario Y ese momento específico
                query_check = """
                    SELECT id_asistencia 
                    FROM "CBTF".asistencias 
                    WHERE id_sesion = %s AND id_usuario = %s AND momento = %s;
                """
                cursor.execute(query_check, (id_sesion, id_usuario, momento))
                resultado = cursor.fetchone()

                if resultado:
                    # 2. Actualizar la asistencia del momento correspondiente si ya existía
                    id_asist = resultado['id_asistencia'] if isinstance(resultado, dict) else resultado[0]
                    query_update = """
                        UPDATE "CBTF".asistencias 
                        SET estatus = %s, fecha = %s, minutos_retardo = %s, motivo_justificacion = %s
                        WHERE id_asistencia = %s;
                    """
                    cursor.execute(query_update, (estatus, fecha, minutos_retardo, motivo_justificacion, id_asist))
                else:
                    # 3. Si es un nuevo momento, generar un id_asistencia no nulo e insertar
                    query_max_id = 'SELECT COALESCE(MAX(id_asistencia), 0) + 1 AS next_id FROM "CBTF".asistencias;'
                    cursor.execute(query_max_id)
                    res_max = cursor.fetchone()
                    next_id = res_max['next_id'] if isinstance(res_max, dict) else res_max[0]

                    query_insert = """
                        INSERT INTO "CBTF".asistencias (id_asistencia, id_sesion, id_usuario, fecha, estatus, momento, minutos_retardo, motivo_justificacion)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                    """
                    cursor.execute(query_insert, (next_id, id_sesion, id_usuario, fecha, estatus, momento, minutos_retardo, motivo_justificacion))

                conexion.commit()
                print(f"--> Asistencia guardada con éxito en BD para usuario {id_usuario} ({estatus} - {momento})")
                return True
        except Exception as e:
            print(f"--> Error grave al guardar asistencia en BD: {e}")
            if conexion:
                conexion.rollback()
            return False
        finally:
            if conexion:
                conexion.close()