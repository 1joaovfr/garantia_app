from database.connection import get_db_connection

def find_itens_pendentes():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT ig.id, ig.codigo_analise, nf.numero_nota, nf.data_nota,
                   c.cliente, ig.codigo_produto, ig.ressarcimento -- ALTERADO AQUI
            FROM ItensGarantia ig
            JOIN NotasFiscais nf ON ig.id_nota_fiscal = nf.id
            JOIN Clientes c ON nf.cnpj_cliente = c.cnpj
            WHERE ig.status = 'Pendente de Análise' ORDER BY nf.data_nota
        """
        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]

def find_by_filters(filtros):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT ig.id, nf.numero_nota, nf.data_nota, c.cnpj, c.cliente, -- ALTERADO AQUI
                   ig.codigo_analise, ig.codigo_produto, ig.status, 
                   ig.procedente_improcedente, ig.valor_item, ig.ressarcimento
            FROM ItensGarantia ig
            JOIN NotasFiscais nf ON ig.id_nota_fiscal = nf.id
            JOIN Clientes c ON nf.cnpj_cliente = c.cnpj
        """
        condicoes, parametros = [], []
        if filtros['cnpj']:
            condicoes.append("c.cnpj LIKE ?")
            parametros.append(f"%{filtros['cnpj']}%")
        if filtros['razao_social']:
            # Alterado de 'nome_cliente' para 'cliente'
            condicoes.append("c.cliente LIKE ?")
            parametros.append(f"%{filtros['razao_social']}%")
        if filtros['numero_nota']:
            condicoes.append("nf.numero_nota LIKE ?")
            parametros.append(f"%{filtros['numero_nota']}%")
        if filtros['status'] and filtros['status'] != 'Todos':
            condicoes.append("ig.status = ?")
            parametros.append(filtros['status'])
        
        if condicoes: query += " WHERE " + " AND ".join(condicoes)
        query += " ORDER BY nf.data_nota DESC, nf.numero_nota"
        
        cursor.execute(query, parametros)
        return [dict(row) for row in cursor.fetchall()]

def find_complete_details_by_id(id_item):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ItensGarantia WHERE id = ?", (id_item,))
        item = cursor.fetchone()
        return dict(item) if item else None

def get_last_codigo_analise(letra_mes):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT codigo_analise FROM ItensGarantia WHERE codigo_analise LIKE ? ORDER BY codigo_analise DESC LIMIT 1",
            (f"{letra_mes}%",)
        )
        ultimo_codigo = cursor.fetchone()
        return ultimo_codigo[0] if ultimo_codigo else None

def get_all_available_years():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT DISTINCT STRFTIME('%Y', data_lancamento) FROM NotasFiscais WHERE data_lancamento IS NOT NULL ORDER BY 1 DESC"
        cursor.execute(query)
        return [row[0] for row in cursor.fetchall()]

def find_all_complete_data_for_gestao(filtros={}):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        ## ALTERADO: A consulta SQL foi atualizada para incluir as novas colunas
        base_query = """
            SELECT 
                ig.id, nf.data_lancamento, nf.numero_nota, nf.data_nota,
                c.cnpj, c.cliente, c.grupo_cliente, 
                c.cidade, c.estado, c.regioes, -- ADICIONADAS colunas de Cliente
                ig.codigo_analise, ig.codigo_produto, p.grupo_estoque, 
                ig.codigo_avaria, 
                ca.descricao_tecnica, -- ADICIONADA coluna de CodigosAvaria
                ig.valor_item, ig.status, ig.procedente_improcedente, 
                ig.ressarcimento, ig.numero_serie, ig.fornecedor
            FROM ItensGarantia AS ig
            LEFT JOIN NotasFiscais AS nf ON ig.id_nota_fiscal = nf.id
            LEFT JOIN Clientes AS c ON nf.cnpj_cliente = c.cnpj
            LEFT JOIN Produtos AS p ON ig.codigo_produto = p.codigo_item
            -- ADICIONADO: Novo JOIN para buscar a descrição da avaria
            LEFT JOIN CodigosAvaria AS ca ON ig.codigo_avaria = ca.codigo_avaria
        """
        # A query para a tabela não usa mais filtros, então não adicionamos WHERE
        base_query += " ORDER BY nf.data_lancamento DESC, ig.id DESC"
        
        cursor.execute(base_query)
        return [dict(row) for row in cursor.fetchall()]
def get_stats(filtros={}):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        base_from = "FROM ItensGarantia ig JOIN NotasFiscais nf ON ig.id_nota_fiscal = nf.id LEFT JOIN Clientes c ON nf.cnpj_cliente = c.cnpj"
        
        condicoes, params = [], []
        if filtros.get('ano'): condicoes.append("STRFTIME('%Y', nf.data_lancamento) = ?"); params.append(filtros['ano'])
        if filtros.get('mes'): condicoes.append("STRFTIME('%m', nf.data_lancamento) = ?"); params.append(filtros['mes'])
        # REMOVIDO: filtro de cliente e produto
        # ADICIONADO: filtro de grupo
        if filtros.get('grupo'): condicoes.append("c.grupo_cliente = ?"); params.append(filtros['grupo'])
        
        where_sql = " AND ".join(condicoes) if condicoes else "1=1"
        
        query = f"""
            SELECT 'Procedente' as c, COUNT(ig.id) as q, SUM(ig.valor_item) as v {base_from} WHERE ig.procedente_improcedente = 'Procedente' AND {where_sql}
            UNION ALL SELECT 'Improcedente' as c, COUNT(ig.id) as q, SUM(ig.valor_item) as v {base_from} WHERE ig.procedente_improcedente = 'Improcedente' AND {where_sql}
            UNION ALL SELECT 'Pendente' as c, COUNT(ig.id) as q, SUM(ig.valor_item) as v {base_from} WHERE ig.status = 'Pendente de Análise' AND {where_sql}
        """
        cursor.execute(query, params * 3)
        return cursor.fetchall()

def get_ressarcimento_stats(filtros={}):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        base_from = "FROM ItensGarantia ig JOIN NotasFiscais nf ON ig.id_nota_fiscal = nf.id LEFT JOIN Clientes c ON nf.cnpj_cliente = c.cnpj"
        
        condicoes, params = ["ig.ressarcimento IS NOT NULL", "CAST(ig.ressarcimento AS REAL) > 0"], []
        if filtros.get('ano'): condicoes.append("STRFTIME('%Y', nf.data_lancamento) = ?"); params.append(filtros['ano'])
        if filtros.get('mes'): condicoes.append("STRFTIME('%m', nf.data_lancamento) = ?"); params.append(filtros['mes'])
        # REMOVIDO: filtro de cliente e produto
        # ADICIONADO: filtro de grupo
        if filtros.get('grupo'): condicoes.append("c.grupo_cliente = ?"); params.append(filtros['grupo'])
        
        where_sql = " WHERE " + " AND ".join(condicoes)
        query = f"""
            SELECT
                SUM(CASE WHEN ig.procedente_improcedente = 'Procedente' THEN CAST(ig.ressarcimento AS REAL) ELSE 0 END) as valor_p,
                COUNT(CASE WHEN ig.procedente_improcedente = 'Procedente' AND CAST(ig.ressarcimento AS REAL) > 0 THEN ig.id END) as qtd_p,
                SUM(CASE WHEN ig.procedente_improcedente = 'Improcedente' THEN CAST(ig.ressarcimento AS REAL) ELSE 0 END) as valor_i,
                COUNT(CASE WHEN ig.procedente_improcedente = 'Improcedente' THEN ig.id END) as qtd_i,
                SUM(CASE WHEN ig.status = 'Pendente de Análise' THEN CAST(ig.ressarcimento AS REAL) ELSE 0 END) as valor_pend,
                COUNT(CASE WHEN ig.status = 'Pendente de Análise' THEN ig.id END) as qtd_pend
            {base_from} {where_sql}
        """
        cursor.execute(query, params)
        return cursor.fetchone()

def save_nota_e_itens(cnpj, numero_nota, data_nota, data_lancamento, itens_com_codigo):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO NotasFiscais (numero_nota, data_nota, cnpj_cliente, data_lancamento) VALUES (?, ?, ?, ?)", (numero_nota, data_nota, cnpj, data_lancamento))
        id_nota_fiscal = cursor.lastrowid
        
        for item in itens_com_codigo:
            for i in range(item['quantidade']):
                codigo_final = f"{item['codigo_analise'][:-3]}{int(item['codigo_analise'][-3:]) + i:03d}" if not item['e_tucho'] else item['codigo_analise']
                sql_insert = "INSERT INTO ItensGarantia (id_nota_fiscal, codigo_produto, valor_item, codigo_analise, ressarcimento) VALUES (?, ?, ?, ?, ?)"
                params = (id_nota_fiscal, item['codigo'], item['valor'], codigo_final, item.get('ressarcimento'))
                cursor.execute(sql_insert, params)

def save_analise(id_item, dados_analise):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = """
            UPDATE ItensGarantia SET status = 'Analisado', codigo_analise = ?, numero_serie = ?,
            codigo_avaria = ?, descricao_avaria = ?, procedente_improcedente = ?,
            produzido_revenda = ?, fornecedor = ? WHERE id = ?
        """
        params = (
            dados_analise['codigo_analise'], dados_analise['numero_serie'], 
            dados_analise['codigo_avaria'], dados_analise['descricao_avaria'], 
            dados_analise['procedente_improcedente'], dados_analise['produzido_revenda'], 
            dados_analise['fornecedor'], id_item
        )
        cursor.execute(query, params)

def delete_by_ids(lista_ids):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        placeholders_ids = ','.join('?' for _ in lista_ids)
        
        query_select_nf = f"SELECT DISTINCT id_nota_fiscal FROM ItensGarantia WHERE id IN ({placeholders_ids})"
        cursor.execute(query_select_nf, lista_ids)
        notas_fiscais_afetadas = {row[0] for row in cursor.fetchall()}
        
        query_delete_itens = f"DELETE FROM ItensGarantia WHERE id IN ({placeholders_ids})"
        cursor.execute(query_delete_itens, lista_ids)
        
        for id_nota in notas_fiscais_afetadas:
            cursor.execute("SELECT COUNT(*) FROM ItensGarantia WHERE id_nota_fiscal = ?", (id_nota,))
            if cursor.fetchone()[0] == 0:
                cursor.execute("DELETE FROM NotasFiscais WHERE id = ?", (id_nota,))