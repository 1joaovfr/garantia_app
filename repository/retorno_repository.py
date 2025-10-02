from database.connection import get_db_connection

def salvar_retorno_completo(num_nota, data, texto_ref, itens_retorno, vinculos):
    """Salva a nota de retorno, seus itens, os vínculos e atualiza as garantias originais em uma única transação."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Salva a Nota de Retorno
        cursor.execute("INSERT INTO NotasRetorno (numero_nota, data_emissao, texto_referencia) VALUES (?, ?, ?)", 
                       (num_nota, data, texto_ref))
        id_nota_retorno = cursor.lastrowid

        # 2. Salva os Itens do Retorno e mapeia seus IDs
        itens_retorno_ids = {}
        for item_data in itens_retorno:
            cursor.execute("INSERT INTO ItensRetorno (id_nota_retorno, codigo_produto, quantidade) VALUES (?, ?, ?)",
                           (id_nota_retorno, item_data['codigo'], item_data['quantidade']))
            # Guarda o ID do item recém-criado, associado ao seu código de produto
            itens_retorno_ids[item_data['codigo']] = cursor.lastrowid
        
        # 3. Salva os Vínculos e atualiza as garantias originais
        for vinculo in vinculos:
            id_garantia_original = vinculo['id_garantia_original']
            codigo_produto = vinculo['codigo_produto']
            qtd_vinculada = vinculo['qtd_vinculada']
            
            id_item_retorno = itens_retorno_ids.get(codigo_produto)
            if id_item_retorno:
                cursor.execute("INSERT INTO LinkRetornoGarantia (id_item_retorno, id_item_garantia_original, quantidade_vinculada) VALUES (?, ?, ?)",
                               (id_item_retorno, id_garantia_original, qtd_vinculada))
                cursor.execute("UPDATE ItensGarantia SET quantidade_retornada = quantidade_retornada + ? WHERE id = ?",
                               (qtd_vinculada, id_garantia_original))

        # 4. Atualiza o status final dos itens de garantia (pós-vinculação)
        cursor.execute("UPDATE ItensGarantia SET status_retorno = 'Totalmente Retornado' WHERE quantidade_retornada >= quantidade")
        cursor.execute("UPDATE ItensGarantia SET status_retorno = 'Parcialmente Retornado' WHERE quantidade_retornada > 0 AND quantidade_retornada < quantidade")