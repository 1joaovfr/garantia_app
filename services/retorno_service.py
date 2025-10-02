# services/retorno_service.py
import re
from datetime import datetime
from repository import retorno_repository, garantia_repository

class RetornoService:
    def parse_referencia(self, texto):
        """Usa regex para extrair APENAS os números das NFs do texto de referência."""
        
        # Este padrão procura por 'NF-e', 'NF-es' ou 'Notas' e captura o grupo de números seguinte.
        padrao = r"(?:NF-es|NF-e|Notas)\s*([\d,\s]+)"
        match = re.search(padrao, texto, re.IGNORECASE)
        
        if match:
            numeros_str = match.group(1)
            # Limpa e retorna uma lista de strings de números (ex: ['1', '2', '17'])
            return [num.strip() for num in numeros_str.split(',')]
        
        return []

    def buscar_origens(self, texto_ref):
        """Processa o texto de referência e busca os itens de garantia correspondentes."""
        
        nfs_origem_numeros = self.parse_referencia(texto_ref)
        
        if not nfs_origem_numeros:
            return None, "Nenhuma referência a NF de origem válida (ex: NF-e 123) foi encontrada no texto."
        
        itens_origem = garantia_repository.find_itens_pendentes_de_retorno_por_nfs(nfs_origem_numeros)
        
        if not itens_origem:
            ## --- MENSAGEM DE ERRO MELHORADA --- ##
            return None, f"Nenhum item ANALISADO e pendente de retorno foi encontrado para as NFs: {', '.join(nfs_origem_numeros)}"
            
        return itens_origem, f"Itens analisados encontrados para as NFs: {', '.join(nfs_origem_numeros)}"
    # O restante do arquivo (função salvar_novo_retorno) permanece o mesmo
    def salvar_novo_retorno(self, num_nota, texto_ref, itens_retorno, vinculos):
        if not num_nota: return False, "O número da nota de retorno é obrigatório."
        if not itens_retorno: return False, "A nota de retorno deve conter pelo menos um item."
        if not vinculos: return False, "Nenhum item de origem foi vinculado."
        
        totais_nf_retorno = {}
        for item in itens_retorno:
            totais_nf_retorno[item['codigo']] = totais_nf_retorno.get(item['codigo'], 0) + item['quantidade']
        totais_vinculados = {}
        for v in vinculos:
            totais_vinculados[v['codigo_produto']] = totais_vinculados.get(v['codigo_produto'], 0) + v['qtd_vinculada']
        for codigo, qtd in totais_vinculados.items():
            if qtd > totais_nf_retorno.get(codigo, 0):
                return False, f"A quantidade vinculada para o produto '{codigo}' ({qtd}) é maior que a da NF de retorno ({totais_nf_retorno.get(codigo, 0)})."
        if sum(totais_nf_retorno.values()) != sum(totais_vinculados.values()):
            return False, "O total geral de itens vinculados não bate com o total da nota de retorno."
        try:
            data_hoje = datetime.now().strftime('%Y-%m-%d')
            retorno_repository.salvar_retorno_completo(num_nota, data_hoje, texto_ref, itens_retorno, vinculos)
            return True, "Nota de retorno e vínculos salvos com sucesso!"
        except Exception as e:
            return False, f"Erro ao salvar no banco de dados: {e}"