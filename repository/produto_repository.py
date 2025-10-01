from database.connection import get_db_connection

def exists_by_codigo(codigo):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT codigo_item FROM Produtos WHERE codigo_item = ?", (codigo,))
        return cursor.fetchone() is not None

def find_grupo_estoque(codigo_produto):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT grupo_estoque FROM Produtos WHERE codigo_item = ?", (codigo_produto,))
        resultado = cursor.fetchone()
        return resultado[0] if resultado else None

def get_all_codigos():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT codigo_item FROM Produtos ORDER BY codigo_item")
        return [row[0] for row in cursor.fetchall()]