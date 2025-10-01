from datetime import datetime
from repository import garantia_repository

class DashboardService:
    def _formatar_item_tabela(self, item):
        item_formatado = dict(item)
        for key in ['data_lancamento', 'data_nota']:
            if item_formatado.get(key):
                item_formatado[key] = datetime.strptime(item_formatado[key], '%Y-%m-%d').strftime('%d/%m/%Y')
        
        if item_formatado.get('valor_item') is not None:
            item_formatado['valor_item'] = f"R$ {item_formatado['valor_item']:.2f}"
        
        if item_formatado.get('ressarcimento'):
            try:
                item_formatado['ressarcimento'] = f"R$ {float(item_formatado['ressarcimento']):.2f}"
            except (ValueError, TypeError):
                item_formatado['ressarcimento'] = "-"
        
        return {k: (v if v is not None else '-') for k, v in item_formatado.items()}

    def get_dados_completos_gestao(self, filtros={}):
        dados = garantia_repository.find_all_complete_data_for_gestao(filtros)
        return [self._formatar_item_tabela(item) for item in dados]

    def get_estatisticas_gerais(self, filtros={}):
        resultados = garantia_repository.get_stats(filtros)
        estatisticas = {
            'Procedente': {'quantidade': 0, 'valor_total': 0},
            'Improcedente': {'quantidade': 0, 'valor_total': 0},
            'Pendente': {'quantidade': 0, 'valor_total': 0}
        }
        for row in resultados:
            cat = row['c']
            if cat in estatisticas:
                estatisticas[cat]['quantidade'] = row['q'] or 0
                estatisticas[cat]['valor_total'] = row['v'] or 0
        return estatisticas

    def get_estatisticas_ressarcimento(self, filtros={}):
        row = garantia_repository.get_ressarcimento_stats(filtros)
        if row:
            return {
                'Procedente': {'quantidade': row['qtd_p'] or 0, 'valor_total': row['valor_p'] or 0},
                'Improcedente': {'quantidade': row['qtd_i'] or 0, 'valor_total': row['valor_i'] or 0},
                'Pendente': {'quantidade': row['qtd_pend'] or 0, 'valor_total': row['valor_pend'] or 0}
            }
        return {'Procedente': {'quantidade': 0, 'valor_total': 0}, 'Improcedente': {'quantidade': 0, 'valor_total': 0}, 'Pendente': {'quantidade': 0, 'valor_total': 0}}