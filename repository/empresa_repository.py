from database.connection import get_db_connection

def get_all_as_dict():
    """Busca todas as empresas e retorna um dicionário no formato {codigo: nome}."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT codigo_empresa, nome FROM Empresas ORDER BY codigo_empresa")
        # Cria um dicionário a partir do resultado da query
        return {row['codigo_empresa']: row['nome'] for row in cursor.fetchall()}