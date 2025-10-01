from database.connection import get_db_connection

def get_all():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Alterado de 'SELECT codigo, ...' para 'SELECT codigo_avaria, ...'
        cursor.execute("SELECT codigo_avaria, descricao_tecnica, classificacao FROM CodigosAvaria ORDER BY codigo_avaria")
        rows = cursor.fetchall()
        # Alterado de row['codigo'] para row['codigo_avaria']
        return {row['codigo_avaria']: {'descricao': row['descricao_tecnica'], 'classificacao': row['classificacao']} for row in rows}