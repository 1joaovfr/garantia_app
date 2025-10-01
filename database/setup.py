# database/setup.py
import sqlite3
from config import DB_NAME

def criar_banco_de_dados():
    """Cria a estrutura inicial do banco de dados com a nova estrutura da tabela Clientes."""
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            print(f"Banco de dados '{DB_NAME}' conectado com sucesso.")

            # Tabela 1: Empresas (Mantenha o conteúdo original)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Empresas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo_empresa TEXT NOT NULL UNIQUE,
                    nome TEXT
                )
            ''')

            # Tabela 2: Clientes (Com a nova estrutura definitiva)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Clientes (
                    cnpj TEXT PRIMARY KEY,
                    codigo_cliente TEXT,
                    cliente TEXT,
                    cidade TEXT,
                    estado TEXT,
                    regioes TEXT,
                    grupo_cliente TEXT
                )
            ''')

            # Tabela 3: Produtos (Mantenha o conteúdo original)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Produtos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo_item TEXT NOT NULL UNIQUE,
                    descricao TEXT,
                    grupo_estoque TEXT
                )
            ''')

            # Tabela 4: Códigos de Avaria (Mantenha o conteúdo original)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS CodigosAvaria (
                    codigo_avaria TEXT PRIMARY KEY,
                    descricao_tecnica TEXT,
                    classificacao TEXT,
                    grupo_relacionado TEXT
                )
            ''')
            
            # Tabela 5: Notas Fiscais (Mantenha o conteúdo original)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS NotasFiscais (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_nota TEXT NOT NULL,
                    data_nota TEXT NOT NULL,
                    cnpj_cliente TEXT,
                    data_lancamento TEXT,
                    FOREIGN KEY (cnpj_cliente) REFERENCES Clientes (cnpj)
                )
            ''')

            # Tabela 6: Itens da Garantia (Mantenha o conteúdo original)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ItensGarantia (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_nota_fiscal INTEGER,
                    codigo_produto TEXT,
                    valor_item REAL,
                    status TEXT DEFAULT 'Pendente de Análise',
                    codigo_analise TEXT,
                    numero_serie TEXT,
                    codigo_avaria TEXT,
                    descricao_avaria TEXT,
                    procedente_improcedente TEXT,
                    produzido_revenda TEXT,
                    fornecedor TEXT,
                    ressarcimento TEXT,
                    FOREIGN KEY (id_nota_fiscal) REFERENCES NotasFiscais (id) ON DELETE CASCADE,
                    FOREIGN KEY (codigo_produto) REFERENCES Produtos (codigo_item),
                    -- ALTERADO DE 'REFERENCES CodigosAvaria (codigo)'
                    FOREIGN KEY (codigo_avaria) REFERENCES CodigosAvaria (codigo_avaria)
                )
            ''')

            conn.commit()
            print("Estrutura do banco de dados verificada/criada com sucesso!")

    except sqlite3.Error as e:
        print(f"Ocorreu um erro com o banco de dados: {e}")

if __name__ == "__main__":
    criar_banco_de_dados()