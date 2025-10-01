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
        cursor.execute("SELECT DISTINCT nome_cliente FROM Clientes ORDER BY nome_cliente")
        return [row[0] for row in cursor.fetchall()]