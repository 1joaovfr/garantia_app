# seed.py
import pandas as pd
import sqlite3
from pathlib import Path
from config import DB_NAME

# Define o caminho para a pasta com os dados e para o banco de dados
SEED_DATA_DIR = Path(__file__).parent / "seed"
DB_PATH = Path(__file__).parent / DB_NAME

def popular_empresas(cursor):
    """Lê Companies.xlsx e popula a tabela Empresas."""
    excel_path = SEED_DATA_DIR / "Companies.xlsx"
    if not excel_path.exists():
        print(f"AVISO: Arquivo não encontrado: {excel_path}")
        return

    df = pd.read_excel(excel_path)
    
    # --- IMPORTANTE: AJUSTE OS NOMES DAS COLUNAS AQUI ---
    # Verifique se os nomes das colunas no seu Excel correspondem aos da esquerda.
    # Se forem diferentes, altere-os. Ex: {'Código da Empresa': 'codigo_empresa'}
    mapeamento_colunas = {
        'codigo_empresa': 'codigo_empresa',
        'empresa': 'nome'
    }
    df.rename(columns=mapeamento_colunas, inplace=True)
    
    # Converte o dataframe para uma lista de tuplas para inserção no DB
    dados_para_inserir = [tuple(row) for row in df[['codigo_empresa', 'nome']].to_numpy()]
    
    # O comando INSERT OR IGNORE evita erros se a empresa já existir (pela chave única)
    cursor.executemany(
        "INSERT OR IGNORE INTO Empresas (codigo_empresa, nome) VALUES (?, ?)",
        dados_para_inserir
    )
    print(f"-> {len(dados_para_inserir)} registros de empresas processados.")

def popular_clientes(cursor):
    """Lê Clients.xlsx e popula a tabela Clientes."""
    excel_path = SEED_DATA_DIR / "Clients.xlsx"
    if not excel_path.exists():
        print(f"AVISO: Arquivo não encontrado: {excel_path}")
        return

    df = pd.read_excel(excel_path)
    
    # --- IMPORTANTE: AJUSTE OS NOMES DAS COLUNAS AQUI ---
    mapeamento_colunas = {
        'cnpj': 'cnpj',
        'codigo_cliente': 'codigo_cliente',
        'cliente': 'cliente',
        'cidade': 'cidade',
        'estado': 'estado',
        'regioes': 'regioes',
        'grupo_cliente': 'grupo_cliente'
    }
    df.rename(columns=mapeamento_colunas, inplace=True)
    
    # --- LINHA ALTERADA AQUI ---
    # Garante que o CNPJ seja lido como texto e remove espaços em branco
    # no início ou no fim, mas MANTÉM a formatação interna.
    df['cnpj'] = df['cnpj'].astype(str).str.strip()
    
    colunas_db = ['cnpj', 'codigo_cliente', 'cliente', 'cidade', 'estado', 'regioes', 'grupo_cliente']
    dados_para_inserir = [tuple(row) for row in df[colunas_db].to_numpy()]

    cursor.executemany(
        "INSERT OR IGNORE INTO Clientes (cnpj, codigo_cliente, cliente, cidade, estado, regioes, grupo_cliente) VALUES (?, ?, ?, ?, ?, ?, ?)",
        dados_para_inserir
    )
    print(f"-> {len(dados_para_inserir)} registros de clientes processados.")

def popular_produtos(cursor):
    """Lê Products.xlsx e popula a tabela Produtos."""
    excel_path = SEED_DATA_DIR / "Products.xlsx"
    if not excel_path.exists():
        print(f"AVISO: Arquivo não encontrado: {excel_path}")
        return
        
    df = pd.read_excel(excel_path)

    # --- IMPORTANTE: AJUSTE OS NOMES DAS COLUNAS AQUI ---
    mapeamento_colunas = {
        'codigo_item': 'codigo_item',
        'descricao': 'descricao',
        'grupo_estoque': 'grupo_estoque'
    }
    df.rename(columns=mapeamento_colunas, inplace=True)

    dados_para_inserir = [tuple(row) for row in df[['codigo_item', 'descricao', 'grupo_estoque']].to_numpy()]

    cursor.executemany(
        "INSERT OR IGNORE INTO Produtos (codigo_item, descricao, grupo_estoque) VALUES (?, ?, ?)",
        dados_para_inserir
    )
    print(f"-> {len(dados_para_inserir)} registros de produtos processados.")

def popular_codigos_avaria(cursor):
    """Lê Malfunction.xlsx e popula a tabela CodigosAvaria."""
    excel_path = SEED_DATA_DIR / "Malfunction.xlsx"
    if not excel_path.exists():
        print(f"AVISO: Arquivo não encontrado: {excel_path}")
        return
        
    df = pd.read_excel(excel_path)

    # --- IMPORTANTE: AJUSTE OS NOMES DAS COLUNAS AQUI ---
    mapeamento_colunas = {
        'codigo_avaria': 'codigo_avaria',
        'descricao_tecnica': 'descricao_tecnica',
        'classificacao': 'classificacao',
        'grupo_relacionado': 'grupo_relacionado'
    }
    df.rename(columns=mapeamento_colunas, inplace=True)

    colunas_db = ['codigo_avaria', 'descricao_tecnica', 'classificacao', 'grupo_relacionado']
    dados_para_inserir = [tuple(row) for row in df[colunas_db].to_numpy()]

    cursor.executemany(
        "INSERT OR IGNORE INTO CodigosAvaria (codigo_avaria, descricao_tecnica, classificacao, grupo_relacionado) VALUES (?, ?, ?, ?)",
        dados_para_inserir
    )
    print(f"-> {len(dados_para_inserir)} registros de códigos de avaria processados.")


def popular_banco_de_dados():
    """Função principal que orquestra a população de todas as tabelas."""
    print("Iniciando a população do banco de dados...")
    
    if not DB_PATH.exists():
        print(f"ERRO: Banco de dados '{DB_NAME}' não encontrado.")
        print("Execute o arquivo 'main.py' primeiro para criar o banco de dados.")
        return

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            popular_empresas(cursor)
            popular_clientes(cursor)
            popular_produtos(cursor)
            popular_codigos_avaria(cursor)
            
            conn.commit()
        
        print("\nPopulação do banco de dados concluída com sucesso!")

    except Exception as e:
        print(f"\nOcorreu um erro durante a população do banco de dados: {e}")

if __name__ == "__main__":
    # Garante que o usuário queira executar a ação
    resposta = input("Este script irá inserir dados no seu banco de dados. Deseja continuar? (s/n): ")
    if resposta.lower() == 's':
        popular_banco_de_dados()
    else:
        print("Operação cancelada.")