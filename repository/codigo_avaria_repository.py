from database.connection import get_db_connection

def get_all():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT codigo, descricao_tecnica, classificacao FROM CodigosAvaria ORDER BY codigo")
        rows = cursor.fetchall()
        return {row['codigo']: {'descricao': row['descricao_tecnica'], 'classificacao': row['classificacao']} for row in rows}