import sqlite3
from contextlib import contextmanager
from config import DB_NAME

@contextmanager
def get_db_connection():
    """
    Fornece uma conexão com o banco de dados gerenciada por contexto.
    Garante que a conexão seja confirmada (commit) em caso de sucesso
    e revertida (rollback) em caso de erro, e sempre fechada.
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row  # Retorna resultados como dicionários
        yield conn
        conn.commit()
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        print(f"Erro no banco de dados: {e}")
        raise  # Re-lança a exceção para ser tratada pelas camadas superiores
    finally:
        if conn:
            conn.close()