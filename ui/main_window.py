# ui/main_window.py
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttkb
import matplotlib.pyplot as plt
from .tabs.tab_lancamento import LancamentoTab
from .tabs.tab_analise import AnaliseTab
from .tabs.tab_visualizacao import VisualizacaoTab
from .tabs.tab_gestao import GestaoTab
from .tabs.tab_retorno import RetornoTab # <-- 1. IMPORTAR A NOVA ABA

class App(ttkb.Window):
    def __init__(self, title="Sistema de Gestão de Garantias", size=(1300, 800), **kwargs):
        super().__init__(title=title, size=size, **kwargs)
        self.minsize(size[0], size[1])

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.lancamento_tab = LancamentoTab(notebook, self)
        self.analise_tab = AnaliseTab(notebook, self)
        self.visualizacao_tab = VisualizacaoTab(notebook, self)
        self.gestao_tab = GestaoTab(notebook, self)
        self.retorno_tab = RetornoTab(notebook, self) # <-- 2. CRIAR A INSTÂNCIA DA NOVA ABA

        notebook.add(self.lancamento_tab, text='  Lançamento de Garantia  ')
        notebook.add(self.analise_tab, text='  Análise de Garantia  ')
        notebook.add(self.retorno_tab, text='  Lançamento de Retorno  ') # <-- 3. ADICIONAR AO NOTEBOOK
        notebook.add(self.visualizacao_tab, text='  Visualizar Garantias  ')
        notebook.add(self.gestao_tab, text='  Gestão de Dados  ')

        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self._carregar_dados_iniciais()

    def _on_closing(self):
        plt.close('all')
        self.destroy()

    def _carregar_dados_iniciais(self):
        # O carregamento inicial agora chama métodos específicos de cada aba
        self.lancamento_tab.carregar_dados_iniciais()
        self.analise_tab.carregar_dados_iniciais()
        self.visualizacao_tab.carregar_dados_iniciais()
        self.gestao_tab.carregar_dados_iniciais()
        # A nova aba não precisa de um carregamento inicial de dados

    def notificar_atualizacao(self):
        """Notifica todas as abas que uma atualização de dados ocorreu."""
        print("Notificando abas para atualização...")
        self.analise_tab.carregar_itens_pendentes()
        self.visualizacao_tab.aplicar_filtros()
        self.gestao_tab.carregar_filtros()
        self.gestao_tab.atualizar_visualizacao()