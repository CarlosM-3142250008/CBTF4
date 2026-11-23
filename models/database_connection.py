import psycopg
from psycopg.rows import dict_row
from models.config import db_config

class Database_connection:
    def __init__(self):
        self.config = db_config

    def get_connection(self):
        try:
            conexion = psycopg.connect(
                host=self.config.get('host', 'localhost'),
                user=self.config.get('user', 'postgres'),
                password=str(self.config.get('password', '')),
                dbname=self.config.get('database', 'CBTF'),
                port=self.config.get('port', 5432)
            )
            return conexion
        except Exception as e:
            print(f"--> Error al conectar con PostgreSQL: {e}")
            return None

    def ejecutar_consulta(self, query, params=()):
        conexion = self.get_connection()
        if not conexion:
            return None
        
        try:
            # dict_row devuelve los resultados como diccionario
            with conexion.cursor(row_factory=dict_row) as cursor:
                cursor.execute(query, params)
                resultados = cursor.fetchall()
                return resultados
        except Exception as e:
            print(f"--> Error al ejecutar consulta SQL: {e}")
            return None
        finally:
            if conexion:
                conexion.close()