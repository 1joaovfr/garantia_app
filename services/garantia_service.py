from datetime import datetime
from repository import garantia_repository, produto_repository, cliente_repository

class GarantiaService:
    def registrar_nova_nota(self, cnpj, numero_nota, data_nota, itens):
        if not cliente_repository.find_by_cnpj(cnpj):
            return False, "CNPJ inválido ou não registrado."
        if not numero_nota.strip():
            return False, "O campo 'Nº da Nota' é obrigatório."
        if not itens:
            return False, "Adicione pelo menos um item à nota."

        data_lancamento = datetime.now().strftime('%Y-%m-%d')
        letra_mes = chr(64 + int(data_lancamento.split('-')[1]))
        
        ultimo_codigo = garantia_repository.get_last_codigo_analise(letra_mes)
        proximo_numero = int(ultimo_codigo[1:]) + 1 if ultimo_codigo else 1
        
        itens_com_codigo = []
        for item in itens:
            grupo_estoque = produto_repository.find_grupo_estoque(item['codigo'])
            item['e_tucho'] = (grupo_estoque == 'TUCHOS HIDRAULICOS')
            item['codigo_analise'] = f"{letra_mes}{proximo_numero:03d}"
            
            if not item['e_tucho']:
                proximo_numero += item['quantidade']
            else:
                proximo_numero += 1
            
            itens_com_codigo.append(item)
            
        try:
            garantia_repository.save_nota_e_itens(cnpj, numero_nota, data_nota, data_lancamento, itens_com_codigo)
            return True, "Nota fiscal e itens salvos com sucesso!"
        except Exception as e:
            return False, f"Erro ao salvar nota fiscal: {e}"

    def salvar_analise(self, id_item, dados_analise):
        try:
            garantia_repository.save_analise(id_item, dados_analise)
            return True, "Análise salva com sucesso!"
        except Exception as e:
            return False, f"Erro ao salvar análise: {e}"

    def excluir_itens(self, lista_ids):
        if not lista_ids:
            return True, "Nenhum item selecionado para exclusão."
        try:
            garantia_repository.delete_by_ids(lista_ids)
            quantidade = len(lista_ids)
            s_ou_n = "item" if quantidade == 1 else "itens"
            return True, f"{quantidade} {s_ou_n} excluído(s) com sucesso."
        except Exception as e:
            return False, f"Erro ao excluir itens: {e}"