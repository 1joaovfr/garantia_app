import sqlite3
from config import DB_NAME

def criar_banco_de_dados():
    """
    Cria a estrutura COMPLETA e FINAL do banco de dados do zero.
    Este script contém o esquema para todos os módulos (Garantia e Retorno).
    """
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            print("Conectado ao banco de dados. Criando tabelas se não existirem...")

            # Tabela 1: Empresas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Empresas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo_empresa TEXT NOT NULL UNIQUE,
                    nome TEXT
                )
            ''')
            print("- Tabela 'Empresas' verificada/criada.")

            # Tabela 2: Clientes
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
            print("- Tabela 'Clientes' verificada/criada.")

            # Tabela 3: Produtos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Produtos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo_item TEXT NOT NULL UNIQUE,
                    descricao TEXT,
                    grupo_estoque TEXT
                )
            ''')
            print("- Tabela 'Produtos' verificada/criada.")

            # Tabela 4: Códigos de Avaria
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS CodigosAvaria (
                    codigo_avaria TEXT PRIMARY KEY,
                    descricao_tecnica TEXT,
                    classificacao TEXT,
                    grupo_relacionado TEXT
                )
            ''')
            print("- Tabela 'CodigosAvaria' verificada/criada.")

            # Tabela 5: Notas Fiscais de Garantia
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS NotasFiscais (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_nota TEXT NOT NULL,
                    data_nota TEXT NOT NULL,
                    cnpj_cliente TEXT,
                    data_lancamento TEXT,
                    FOREIGN KEY (cnpj_cliente) REFERENCES Clientes (cnpj),
                    UNIQUE (numero_nota, cnpj_cliente)
                )
            ''')
            print("- Tabela 'NotasFiscais' verificada/criada.")

            # Tabela 6: Itens da Garantia (LÓGICA CORRIGIDA: SEM COLUNA 'quantidade')
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
                    status_retorno TEXT DEFAULT 'Aguardando',
                    quantidade_retornada INTEGER DEFAULT 0, -- Esta coluna será 0 (não retornado) ou 1 (retornado)
                    FOREIGN KEY (id_nota_fiscal) REFERENCES NotasFiscais (id) ON DELETE CASCADE,
                    FOREIGN KEY (codigo_produto) REFERENCES Produtos (codigo_item),
                    FOREIGN KEY (codigo_avaria) REFERENCES CodigosAvaria (codigo_avaria)
                )
            ''')
            print("- Tabela 'ItensGarantia' verificada/criada.")
            
            # Tabela 7: Notas Fiscais de Retorno
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS NotasRetorno (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_nota TEXT NOT NULL,
                    cnpj_cliente TEXT,
                    data_emissao TEXT,
                    tipo_retorno TEXT,
                    texto_referencia TEXT,
                    FOREIGN KEY (cnpj_cliente) REFERENCES Clientes (cnpj),
                    UNIQUE (numero_nota, cnpj_cliente)
                )
            ''')
            print("- Tabela 'NotasRetorno' verificada/criada.")

            # Tabela 8: Itens das Notas de Retorno
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ItensRetorno (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_nota_retorno INTEGER,
                    codigo_produto TEXT,
                    quantidade INTEGER,
                    FOREIGN KEY (id_nota_retorno) REFERENCES NotasRetorno (id)
                )
            ''')
            print("- Tabela 'ItensRetorno' verificada/criada.")

            # Tabela 9: Tabela de Ligação entre Retorno e Garantia Original
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS LinkRetornoGarantia (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_item_retorno INTEGER,
                    id_item_garantia_original INTEGER,
                    quantidade_vinculada INTEGER,
                    FOREIGN KEY (id_item_retorno) REFERENCES ItensRetorno (id),
                    FOREIGN KEY (id_item_garantia_original) REFERENCES ItensGarantia (id)
                )
            ''')
            print("- Tabela 'LinkRetornoGarantia' verificada/criada.")

            conn.commit()
            print("\nEstrutura completa do banco de dados criada/verificada com sucesso!")

    except sqlite3.Error as e:
        print(f"Ocorreu um erro ao criar o banco de dados: {e}")

if __name__ == "__main__":
    criar_banco_de_dados()