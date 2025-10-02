# gerador_de_testes.py
import sqlite3
import random
import string
from datetime import datetime, timedelta
from config import DB_NAME

# --- CONFIGURAÇÕES DO GERADOR ---
NUMERO_DE_NOTAS_FISCAIS = 50
MAX_ITENS_POR_NOTA = 8
FORNECEDORES_EXEMPLO = ['Fornecedor A', 'Indústrias Delta', 'Componentes Brasil', 'Peças Premium', 'Tech Parts SA']
# ---------------------------------

def buscar_dados_base(cursor):
    """Busca os dados mestre (clientes, produtos, avarias) que servirão de base para a geração."""
    cursor.execute("SELECT cnpj FROM Clientes")
    clientes = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT codigo_item FROM Produtos")
    produtos = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT codigo_avaria FROM CodigosAvaria WHERE classificacao = 'Procedente'")
    avarias_procedentes = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT codigo_avaria FROM CodigosAvaria WHERE classificacao = 'Improcedente'")
    avarias_improcedentes = [row[0] for row in cursor.fetchall()]
    
    if not all([clientes, produtos, avarias_procedentes, avarias_improcedentes]):
        print("\nERRO: Uma ou mais tabelas base (Clientes, Produtos, CodigosAvaria) estão vazias.")
        print("Por favor, rode o script 'seed.py' primeiro para popular os dados mestre.")
        return None
        
    return {
        "clientes": clientes,
        "produtos": produtos,
        "avarias_procedentes": avarias_procedentes,
        "avarias_improcedentes": avarias_improcedentes
    }

def limpar_dados_antigos(cursor):
    """Apaga os dados transacionais antigos para evitar duplicatas."""
    print("Limpando dados transacionais antigos (Notas Fiscais e Itens de Garantia)...")
    cursor.execute("DELETE FROM LinkRetornoGarantia")
    cursor.execute("DELETE FROM ItensRetorno")
    cursor.execute("DELETE FROM NotasRetorno")
    cursor.execute("DELETE FROM ItensGarantia")
    cursor.execute("DELETE FROM NotasFiscais")
    print("Limpeza concluída.")

def gerar_dados_teste():
    """Função principal que gera e insere os dados de teste."""
    
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            
            limpar_dados_antigos(conn)

            dados_base = buscar_dados_base(cursor)
            if not dados_base:
                return

            print(f"\nGerando {NUMERO_DE_NOTAS_FISCAIS} notas fiscais de garantia com dados aleatórios...")
            
            contadores_analise = {}

            for i in range(NUMERO_DE_NOTAS_FISCAIS):
                hoje = datetime.now()
                data_inicio_periodo = hoje - timedelta(days=730)
                dias_totais_periodo = (hoje - data_inicio_periodo).days
                dias_aleatorios_nota = random.randint(0, dias_totais_periodo)
                data_nota_obj = data_inicio_periodo + timedelta(days=dias_aleatorios_nota)
                
                data_lancamento_obj = data_nota_obj + timedelta(days=random.randint(1, 30))
                if data_lancamento_obj > hoje:
                    data_lancamento_obj = hoje
                
                data_nota_str = data_nota_obj.strftime('%Y-%m-%d')
                data_lancamento_str = data_lancamento_obj.strftime('%Y-%m-%d')
                
                cliente_cnpj = random.choice(dados_base["clientes"])
                numero_nota = f"{i+1:04d}"
                
                cursor.execute("INSERT INTO NotasFiscais (numero_nota, data_nota, cnpj_cliente, data_lancamento) VALUES (?, ?, ?, ?)",
                               (numero_nota, data_nota_str, cliente_cnpj, data_lancamento_str))
                id_nota_fiscal = cursor.lastrowid
                
                num_itens = random.randint(1, MAX_ITENS_POR_NOTA)
                for _ in range(num_itens):
                    codigo_produto = random.choice(dados_base["produtos"])
                    valor_item = round(random.uniform(20.50, 899.90), 2)
                    tipo_item = random.choices(["pendente", "procedente", "improcedente"], weights=[0.5, 0.3, 0.2], k=1)[0]
                    
                    status_db = 'Pendente de Análise'
                    dados_analise = { 'numero_serie': None, 'codigo_avaria': None, 'descricao_avaria': None, 'procedente_improcedente': None, 'produzido_revenda': None, 'fornecedor': None }

                    ## --- LÓGICA CORRIGIDA: CÓDIGO DE ANÁLISE GERADO PARA TODOS OS ITENS --- ##
                    mes_lancamento = data_lancamento_obj.month
                    letra_mes = chr(64 + mes_lancamento)
                    contador_atual = contadores_analise.get(letra_mes, 0) + 1
                    contadores_analise[letra_mes] = contador_atual
                    codigo_analise_gerado = f"{letra_mes}{contador_atual:03d}"
                    ## --- FIM DA CORREÇÃO --- ##

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
                        INSERT INTO ItensGarantia (
                            id_nota_fiscal, codigo_produto, valor_item, status,
                            codigo_analise, numero_serie, codigo_avaria, descricao_avaria,
                            procedente_improcedente, produzido_revenda, fornecedor, ressarcimento
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        id_nota_fiscal, codigo_produto, valor_item, status_db,
                        codigo_analise_gerado, # <- Usa a variável gerada para TODOS
                        dados_analise['numero_serie'],
                        dados_analise['codigo_avaria'], dados_analise['descricao_avaria'],
                        dados_analise['procedente_improcedente'], dados_analise['produzido_revenda'],
                        dados_analise['fornecedor'], ressarcimento
                    ))

            conn.commit()
            print("\nDados de teste gerados com sucesso!")

    except sqlite3.Error as e:
        print(f"\nOcorreu um erro de banco de dados: {e}")
    except Exception as e:
        print(f"\nOcorreu um erro inesperado: {e}")

if __name__ == "__main__":
    print("Este script irá apagar TODAS as notas fiscais e itens de garantia existentes")
    print("para gerar um novo conjunto de dados de teste.")
    resposta = input("Deseja continuar? (s/n): ")
    if resposta.lower() == 's':
        gerar_dados_teste()
    else:
        print("Operação cancelada.")