# repository/cliente_repository.py
from database.connection import get_db_connection

def find_by_cnpj(cnpj):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Clientes WHERE cnpj = ?", (cnpj,))
        cliente = cursor.fetchone()
        return dict(cliente) if cliente else None

def get_all_nomes():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT cliente FROM Clientes ORDER BY cliente")
        return [row[0] for row in cursor.fetchall()]

def get_all_grupos():
    """Busca todos os nomes de grupos de clientes únicos."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Adiciona um filtro para não retornar valores nulos ou vazios
        cursor.execute("SELECT DISTINCT grupo_cliente FROM Clientes WHERE grupo_cliente IS NOT NULL AND grupo_cliente != '' ORDER BY grupo_cliente")
        return [row[0] for row in cursor.fetchall()]