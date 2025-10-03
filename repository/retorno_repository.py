# repository/retorno_repository.py
from database.connection import get_db_connection

def exists_by_numero_and_cnpj(numero_nota, cnpj_cliente):
    """Verifica se uma nota de retorno já existe para um cliente específico."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM NotasRetorno WHERE numero_nota = ? AND cnpj_cliente = ?", (numero_nota, cnpj_cliente))
        return cursor.fetchone() is not None

def salvar_retorno_completo(num_nota, cnpj_cliente, data, texto_ref, tipo_retorno, itens_retorno, vinculos):
    """Salva a nota de retorno, incluindo o tipo de retorno categorizado."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # QUERY ATUALIZADA para incluir a coluna tipo_retorno
        cursor.execute(
            """INSERT INTO NotasRetorno 
               (numero_nota, cnpj_cliente, data_emissao, texto_referencia, tipo_retorno) 
               VALUES (?, ?, ?, ?, ?)""", 
            (num_nota, cnpj_cliente, data, texto_ref, tipo_retorno)
        )
        id_nota_retorno = cursor.lastrowid

        # O resto da função continua o mesmo
        itens_retorno_ids = {}
        for item_data in itens_retorno:
            cursor.execute("INSERT INTO ItensRetorno (id_nota_retorno, codigo_produto, quantidade) VALUES (?, ?, ?)",
                           (id_nota_retorno, item_data['codigo'], item_data['quantidade']))
            itens_retorno_ids[item_data['codigo']] = cursor.lastrowid
        
        for vinculo in vinculos:
            id_garantia_original, codigo_produto, qtd_vinculada = vinculo['id_garantia_original'], vinculo['codigo_produto'], vinculo['qtd_vinculada']
            id_item_retorno = itens_retorno_ids.get(codigo_produto)
            if id_item_retorno:
                cursor.execute("INSERT INTO LinkRetornoGarantia (id_item_retorno, id_item_garantia_original, quantidade_vinculada) VALUES (?, ?, ?)",
                               (id_item_retorno, id_garantia_original, qtd_vinculada))
                cursor.execute("UPDATE ItensGarantia SET quantidade_retornada = 1, status_retorno = 'Retornado' WHERE id = ?",
                               (id_garantia_original,))