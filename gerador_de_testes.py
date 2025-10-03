import sqlite3
import random
import string
from datetime import datetime, timedelta
from config import DB_NAME

NUMERO_DE_NOTAS_FISCAIS = 20
MAX_TIPOS_DE_ITEM_POR_NOTA = 5
MAX_QTD_POR_TIPO_ITEM = 8 
FORNECEDORES_EXEMPLO = ['Fornecedor A', 'Indústrias Delta', 'Componentes Brasil', 'Peças Premium', 'Tech Parts SA']

def buscar_dados_base(cursor):
    cursor.execute("SELECT cnpj FROM Clientes")
    clientes = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT codigo_item FROM Produtos")
    produtos = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT codigo_avaria FROM CodigosAvaria WHERE classificacao = 'Procedente'")
    avarias_procedentes = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT codigo_avaria FROM CodigosAvaria WHERE classificacao = 'Improcedente'")
    avarias_improcedentes = [row[0] for row in cursor.fetchall()]
    if not all([clientes, produtos, avarias_procedentes, avarias_improcedentes]):
        print("\nERRO: Tabelas base (Clientes, Produtos, CodigosAvaria) estão vazias.")
        print("Execute 'seed.py' primeiro.")
        return None
    return {"clientes": clientes, "produtos": produtos, "avarias_procedentes": avarias_procedentes, "avarias_improcedentes": avarias_improcedentes}

def limpar_dados_antigos(cursor):
    print("Limpando dados transacionais antigos...")
    cursor.execute("DELETE FROM LinkRetornoGarantia"); cursor.execute("DELETE FROM ItensRetorno"); cursor.execute("DELETE FROM NotasRetorno")
    cursor.execute("DELETE FROM ItensGarantia"); cursor.execute("DELETE FROM NotasFiscais")
    print("Limpeza concluída.")

def gerar_dados_teste():
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            limpar_dados_antigos(cursor)
            dados_base = buscar_dados_base(cursor)
            if not dados_base: return

            print(f"\nGerando {NUMERO_DE_NOTAS_FISCAIS} notas fiscais de garantia...")
            contadores_analise = {}

            for i in range(NUMERO_DE_NOTAS_FISCAIS):
                hoje = datetime.now()
                data_inicio_periodo = hoje - timedelta(days=730)
                dias_aleatorios_nota = random.randint(0, (hoje - data_inicio_periodo).days)
                data_nota_obj = data_inicio_periodo + timedelta(days=dias_aleatorios_nota)
                data_lancamento_obj = data_nota_obj + timedelta(days=random.randint(1, 30))
                if data_lancamento_obj > hoje: data_lancamento_obj = hoje
                data_nota_str = data_nota_obj.strftime('%Y-%m-%d')
                data_lancamento_str = data_lancamento_obj.strftime('%Y-%m-%d')
                
                cliente_cnpj = random.choice(dados_base["clientes"])
                numero_nota = str(random.randint(10000, 99999))
                
                cursor.execute("INSERT INTO NotasFiscais (numero_nota, data_nota, cnpj_cliente, data_lancamento) VALUES (?, ?, ?, ?)",
                               (numero_nota, data_nota_str, cliente_cnpj, data_lancamento_str))
                id_nota_fiscal = cursor.lastrowid
                
                num_tipos_de_item = random.randint(1, MAX_TIPOS_DE_ITEM_POR_NOTA)
                for _ in range(num_tipos_de_item):
                    quantidade_real = random.randint(1, MAX_QTD_POR_TIPO_ITEM)
                    codigo_produto = random.choice(dados_base["produtos"])
                    
                    for _ in range(quantidade_real):
                        valor_item = round(random.uniform(20.50, 899.90), 2)
                        tipo_item = random.choices(["pendente", "procedente", "improcedente"], weights=[0.5, 0.3, 0.2], k=1)[0]
                        
                        status_db = 'Pendente de Análise'
                        dados_analise = { 'numero_serie': None, 'codigo_avaria': None, 'descricao_avaria': None, 'procedente_improcedente': None, 'produzido_revenda': None, 'fornecedor': None }
                        
                        mes_lancamento = data_lancamento_obj.month
                        letra_mes = chr(64 + mes_lancamento)
                        contador_atual = contadores_analise.get(letra_mes, 0) + 1
                        contadores_analise[letra_mes] = contador_atual
                        codigo_analise_gerado = f"{letra_mes}{contador_atual:03d}"

                        if tipo_item in ['procedente', 'improcedente']:
                            status_db = 'Analisado'
                            dados_analise['procedente_improcedente'] = tipo_item.capitalize()
                            dados_analise['codigo_avaria'] = random.choice(dados_base["avarias_procedentes"]) if tipo_item == 'procedente' else random.choice(dados_base["avarias_improcedentes"])
                            dados_analise['numero_serie'] = ''.join(random.choices(string.digits, k=13))
                            dados_analise['fornecedor'] = random.choice(FORNECEDORES_EXEMPLO)
                            dados_analise['produzido_revenda'] = random.choice(['Produzido', 'Revenda'])
                        
                        ressarcimento = None
                        if status_db == 'Analisado' and random.choice([True, False]):
                            ressarcimento = round(valor_item * random.uniform(0.8, 1.0), 2)
                        
                        cursor.execute("""
                            INSERT INTO ItensGarantia (id_nota_fiscal, codigo_produto, valor_item, status, codigo_analise, numero_serie, codigo_avaria, descricao_avaria, procedente_improcedente, produzido_revenda, fornecedor, ressarcimento) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                            (id_nota_fiscal, codigo_produto, valor_item, status_db, codigo_analise_gerado, dados_analise['numero_serie'], dados_analise['codigo_avaria'], dados_analise['descricao_avaria'], dados_analise['procedente_improcedente'], dados_analise['produzido_revenda'], dados_analise['fornecedor'], ressarcimento)
                        )
            conn.commit()
            print("\nDados de teste (linha por item) gerados com sucesso!")

    except sqlite3.Error as e:
        print(f"\nOcorreu um erro de banco de dados: {e}")
    except Exception as e:
        print(f"\nOcorreu um erro inesperado: {e}")

if __name__ == "__main__":
    resposta = input("Este script irá apagar todos os dados transacionais para gerar novos. Deseja continuar? (s/n): ")
    if resposta.lower() == 's':
        gerar_dados_teste()
    else:
        print("Operação cancelada.")