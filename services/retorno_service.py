# services/retorno_service.py
import re
from datetime import datetime
from repository import retorno_repository, garantia_repository

class RetornoService:
    def _determinar_tipo_retorno(self, texto_ref):
        """Analisa o texto de referência e retorna a categoria correspondente."""
        texto = texto_ref.lower()

        if "retorno de improcedencia" in texto:
            return "Garantia Improcedente"
        elif "retorno de garantia" in texto:
            return "Garantia Procedente"
        elif "retorno de itens de giro" in texto:
            return "Itens de Giro"
        elif "tratativa de crédito" in texto or "abatimento em crédito" in texto:
            return "Tratativa de Crédito"
        else:
            return "Não Especificado"

    def parse_referencia(self, texto):
        """Usa regex para extrair APENAS os números das NFs do texto de referência de forma mais flexível."""
        
        ## --- LÓGICA DE BUSCA ATUALIZADA E MAIS FLEXÍVEL --- ##
        # Este novo padrão aceita todas as variações que você listou:
        # NF-e, NF-es, NF, NFs, NFS, Nota, Notas
        padrao = r"ref\.\s+a(?:s)?\s+(?:NF-e[s]?|NF[Ss]?|Nota[s]?)\s*([\d,\s]+)"
        match = re.search(padrao, texto, re.IGNORECASE)
        
        if match:
            numeros_str = match.group(1)
            return [num.strip() for num in numeros_str.split(',')]
        
        return []

    def buscar_origens(self, texto_ref, cnpj):
        """Processa o texto de referência e busca os itens de garantia correspondentes."""
        
        if not cnpj:
            return None, "Por favor, informe primeiro o CNPJ do cliente."
            
        nfs_origem_numeros = self.parse_referencia(texto_ref)
        
        if not nfs_origem_numeros:
            return None, "Nenhuma referência a NF de origem válida (ex: ref. a NF-e 123) foi encontrada no texto."
        
        itens_origem = garantia_repository.find_itens_pendentes_de_retorno_por_nfs(nfs_origem_numeros, cnpj)
        
        if not itens_origem:
            return None, f"Nenhum item analisado e pendente foi encontrado para as NFs ({', '.join(nfs_origem_numeros)}) deste cliente."
            
        return itens_origem, f"Itens encontrados para as NFs: {', '.join(nfs_origem_numeros)}"

    def salvar_novo_retorno(self, num_nota, cnpj, texto_ref, itens_retorno, vinculos):
        if not num_nota: return False, "O número da nota de retorno é obrigatório."
        if not cnpj: return False, "O CNPJ do cliente é obrigatório."
        
        if retorno_repository.exists_by_numero_and_cnpj(num_nota, cnpj):
            return False, f"O número de nota de retorno '{num_nota}' já foi lançado para este cliente."
        
        # Validações de totais por produto
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
            tipo_retorno = self._determinar_tipo_retorno(texto_ref)
            data_hoje = datetime.now().strftime('%Y-%m-%d')
            retorno_repository.salvar_retorno_completo(num_nota, cnpj, data_hoje, texto_ref, tipo_retorno, itens_retorno, vinculos)
            return True, "Nota de retorno e vínculos salvos com sucesso!"
        except Exception as e:
            return False, f"Erro ao salvar no banco de dados: {e}"