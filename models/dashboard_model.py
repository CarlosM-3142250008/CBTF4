from models.database_connection import Database_connection
class DashboardModel:
    def __init__(self):
        self.db = Database_connection()

    def obtener_kpis(self):
        """Calcula y obtiene los valores para las 3 tarjetas de KPIs."""
        # 1. Próxima sesión/convocatoria (solo fechas futuras)
        query_sesion = """
            SELECT fecha_hora_inicio 
            FROM "CBTF".convocatorias 
            WHERE fecha_hora_inicio >= CURRENT_TIMESTAMP
            ORDER BY fecha_hora_inicio ASC 
            LIMIT 1;
        """
        res_sesion = self.db.ejecutar_consulta(query_sesion)
        proxima_sesion = res_sesion[0]['fecha_hora_inicio'] if res_sesion else None

        # 2. Total de avisos y materiales registrados
        query_avisos = 'SELECT COUNT(*) as total FROM "CBTF".avisos;'
        query_materiales = 'SELECT COUNT(*) as total FROM "CBTF".materiales;'
        res_av = self.db.ejecutar_consulta(query_avisos)
        res_mat = self.db.ejecutar_consulta(query_materiales)
        
        total_avisos = res_av[0]['total'] if res_av else 0
        total_mat = res_mat[0]['total'] if res_mat else 0
        total_pendientes = total_avisos + total_mat

        # 3. Puntualidad / Asistencia promedio general
        query_asistencia = 'SELECT estatus FROM "CBTF".asistencias;'
        res_asist = self.db.ejecutar_consulta(query_asistencia)
        if res_asist:
            presentes = sum(1 for a in res_asist if a['estatus'] == 'Presente')
            porcentaje = f"{int((presentes / len(res_asist)) * 100)}%"
        else:
            porcentaje = "100%"

        return {
            "proxima_sesion": proxima_sesion,
            "avisos_pendientes": total_pendientes,
            "porcentaje_asistencia": porcentaje
        }

    def obtener_convocatorias_recientes(self):
        """Obtiene las convocatorias ordenadas por fecha de publicación."""
        query = """
            SELECT c.id_convocatoria, c.tipo_sesion AS tipo, a.nombre_academia AS academia,
                   c.fecha_hora_inicio AS fecha_hora, c.fecha_publicacion, c.orden_dia
            FROM "CBTF".convocatorias c
            JOIN "CBTF".academias a ON c.id_academia = a.id_academia
            ORDER BY c.fecha_publicacion DESC, c.id_convocatoria DESC;
        """
        return self.db.ejecutar_consulta(query) or []

    def obtener_avisos_recientes(self):
        """Obtiene los avisos ordenados por fecha de publicación."""
        query = """
            SELECT a.id_aviso, a.titulo, a.emisor, a.fecha_evento,
                   a.fecha_publicacion, a.contenido AS detalle
            FROM "CBTF".avisos a
            ORDER BY a.fecha_publicacion DESC, a.id_aviso DESC;
        """
        return self.db.ejecutar_consulta(query) or []