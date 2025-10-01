from database.connection import get_db_connection

def get_all_codigos():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT codigo_empresa FROM Empresas ORDER BY codigo_empresa")
        return [row[0] for row in cursor.fetchall()]