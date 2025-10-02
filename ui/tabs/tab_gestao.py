# ui/tabs/tab_gestao.py
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from services.dashboard_service import DashboardService
from repository import garantia_repository, cliente_repository, produto_repository

class GestaoTab(ttk.Frame):
    def __init__(self, parent_notebook, main_app):
        super().__init__(parent_notebook, padding=(10))
        self.main_app = main_app # <--- ESTA É A LINHA QUE FALTAVA E CAUSA O ERRO
        self.service = DashboardService()
        self.current_view = None
        self._criar_widgets()

    def _criar_widgets(self):
        # Navegação + Filtros
        top_frame = ttk.Frame(self)
        top_frame.pack(fill=X, pady=(0, 5))
        self.btn_ver_tabela = ttk.Button(top_frame, text="Tabela", command=lambda: self._mostrar_view('tabela'))
        self.btn_ver_tabela.pack(side=LEFT, padx=(0,5))
        self.btn_ver_dashboard = ttk.Button(top_frame, text="Dashboard Geral", command=lambda: self._mostrar_view('dashboard'))
        self.btn_ver_dashboard.pack(side=LEFT, padx=5)
        self.btn_ver_ressarcimento = ttk.Button(top_frame, text="Dashboard Ressarcimento", command=lambda: self._mostrar_view('ressarcimento'))
        self.btn_ver_ressarcimento.pack(side=LEFT, padx=5)
        
        filtros_frame = ttk.LabelFrame(self, text="Filtros", padding=10)
        filtros_frame.pack(fill=X, pady=5)
        ttk.Label(filtros_frame, text="Ano:").pack(side=LEFT, padx=(5,2)); self.combo_ano = ttk.Combobox(filtros_frame, state="readonly", width=10); self.combo_ano.pack(side=LEFT, padx=(0,10))
        ttk.Label(filtros_frame, text="Mês:").pack(side=LEFT, padx=(5,2)); self.combo_mes = ttk.Combobox(filtros_frame, state="readonly", width=15, values=["Todos"] + list(self._mes_map().keys())); self.combo_mes.pack(side=LEFT, padx=(0,10))
        ttk.Label(filtros_frame, text="Cliente:").pack(side=LEFT, padx=(5,2)); self.combo_cliente = ttk.Combobox(filtros_frame, state="readonly", width=25); self.combo_cliente.pack(side=LEFT, padx=(0,10))
        ttk.Label(filtros_frame, text="Produto:").pack(side=LEFT, padx=(5,2)); self.combo_produto = ttk.Combobox(filtros_frame, state="readonly", width=20); self.combo_produto.pack(side=LEFT, padx=(0,10))
        ttk.Button(filtros_frame, text="Limpar", command=self._limpar_filtros, bootstyle="secondary").pack(side=RIGHT, padx=5)
        ttk.Button(filtros_frame, text="Filtrar", command=self.atualizar_visualizacao, bootstyle="primary").pack(side=RIGHT, padx=5)

        # Container para as views
        self.container = ttk.Frame(self)
        self.container.pack(fill=BOTH, expand=YES)
        self._criar_view_tabela(); self._criar_view_dashboard_geral(); self._criar_view_dashboard_ressarcimento()

    def carregar_dados_iniciais(self):
        self.carregar_filtros()
        self._mostrar_view('tabela')

    def carregar_filtros(self):
        self.combo_ano['values'] = ["Todos"] + garantia_repository.get_all_available_years()
        self.combo_cliente['values'] = ["Todos"] + cliente_repository.get_all_nomes()
        self.combo_produto['values'] = ["Todos"] + produto_repository.get_all_codigos()
        self._limpar_filtros()

    def _limpar_filtros(self):
        self.combo_ano.set("Todos"); self.combo_mes.set("Todos"); self.combo_cliente.set("Todos"); self.combo_produto.set("Todos")
        self.atualizar_visualizacao()

    def _mes_map(self):
        return {"Janeiro": "01", "Fevereiro": "02", "Março": "03", "Abril": "04", "Maio": "05", "Junho": "06", "Julho": "07", "Agosto": "08", "Setembro": "09", "Outubro": "10", "Novembro": "11", "Dezembro": "12"}

    def _get_filtros(self):
        ano = self.combo_ano.get(); mes_str = self.combo_mes.get(); cliente = self.combo_cliente.get(); produto = self.combo_produto.get()
        filtros = {}
        if ano != "Todos": filtros['ano'] = ano
        if mes_str != "Todos": filtros['mes'] = self._mes_map().get(mes_str)
        if cliente != "Todos": filtros['cliente'] = cliente
        if produto != "Todos": filtros['produto'] = produto
        return filtros

    def atualizar_visualizacao(self):
        filtros = self._get_filtros()
        if self.current_view == 'tabela': self._atualizar_tabela(filtros)
        elif self.current_view == 'dashboard': self._atualizar_dashboard_geral(filtros)
        elif self.current_view == 'ressarcimento': self._atualizar_dashboard_ressarcimento(filtros)
    
    def _mostrar_view(self, view_name):
        self.current_view = view_name
        self.frame_tabela.pack_forget(); self.frame_dashboard_geral.pack_forget(); self.frame_dashboard_ressarcimento.pack_forget()
        
        self.btn_ver_tabela.config(bootstyle="primary-outline"); self.btn_ver_dashboard.config(bootstyle="info-outline"); self.btn_ver_ressarcimento.config(bootstyle="info-outline")

        if view_name == 'tabela': self.frame_tabela.pack(fill=BOTH, expand=YES); self.btn_ver_tabela.config(bootstyle="success")
        elif view_name == 'dashboard': self.frame_dashboard_geral.pack(fill=BOTH, expand=YES); self.btn_ver_dashboard.config(bootstyle="success")
        elif view_name == 'ressarcimento': self.frame_dashboard_ressarcimento.pack(fill=BOTH, expand=YES); self.btn_ver_ressarcimento.config(bootstyle="success")
        
        self.atualizar_visualizacao()

    def _criar_view_tabela(self):
        self.frame_tabela = ttk.Frame(self.container)
        cols = ('id', 'data_lancamento', 'numero_nota', 'data_nota', 'cnpj', 'cliente', 'grupo_cliente', 'codigo_analise', 'codigo_produto', 'grupo_estoque', 'codigo_avaria', 'valor_item', 'status', 'procedente_improcedente', 'ressarcimento', 'numero_serie', 'fornecedor')
        self.tree_gestao = ttk.Treeview(self.frame_tabela, columns=cols, show='headings')
        headings = {'id': ('ID', 40), 'data_lancamento': ('Data Lanç', 90), 'numero_nota': ('Nº Nota', 80), 'data_nota': ('Data Nota', 90), 'cnpj': ('CNPJ', 110), 'cliente': ('Cliente', 200), 'grupo_cliente': ('Grupo Cliente', 100), 'codigo_analise': ('Cód. Análise', 90), 'codigo_produto': ('Cód. Produto', 90), 'grupo_estoque': ('Grupo Estoque', 110), 'codigo_avaria': ('Cód. Avaria', 80), 'valor_item': ('Valor', 80), 'status': ('Status', 110), 'procedente_improcedente': ('Procedência', 100), 'ressarcimento': ('Ressarcimento', 100), 'numero_serie': ('Nº Série', 80), 'fornecedor': ('Fornecedor', 120)}
        for col, (text, width) in headings.items():
            self.tree_gestao.heading(col, text=text)
            self.tree_gestao.column(col, width=width, anchor=CENTER)
        v_scroll = ttk.Scrollbar(self.frame_tabela, orient=VERTICAL, command=self.tree_gestao.yview); v_scroll.pack(side=RIGHT, fill=Y)
        h_scroll = ttk.Scrollbar(self.frame_tabela, orient=HORIZONTAL, command=self.tree_gestao.xview); h_scroll.pack(side=BOTTOM, fill=X)
        self.tree_gestao.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        self.tree_gestao.pack(fill=BOTH, expand=YES)
        
    def _atualizar_tabela(self, filtros):
        for i in self.tree_gestao.get_children(): self.tree_gestao.delete(i)
        dados = self.service.get_dados_completos_gestao(filtros)
        for item in dados:
            self.tree_gestao.insert('', END, values=tuple(item.get(key, '-') for key in self.tree_gestao['columns']))

    def _criar_view_dashboard_geral(self):
        self.frame_dashboard_geral = ttk.Frame(self.container)
        self.frame_dashboard_geral.columnconfigure(0, weight=1); self.frame_dashboard_geral.rowconfigure(0, weight=1)
        self.canvas_geral_frame = ttk.LabelFrame(self.frame_dashboard_geral, text="Distribuição de Status (Geral)", padding=15); self.canvas_geral_frame.grid(row=0, column=0, sticky="nsew", padx=(0,10))
        stats_frame = ttk.LabelFrame(self.frame_dashboard_geral, text="Resumo (Geral)", padding=15, width=350); stats_frame.grid(row=0, column=1, sticky="ns"); stats_frame.pack_propagate(False)
        self.lbl_proc_qtd = self._create_stat_label(stats_frame, "Procedentes", "#28a745", "Quantidade: -"); self.lbl_proc_val = self._create_stat_label(stats_frame, None, None, "Valor Total: R$ -", pad_bottom=15)
        self.lbl_impr_qtd = self._create_stat_label(stats_frame, "Improcedentes", "#dc3545", "Quantidade: -"); self.lbl_impr_val = self._create_stat_label(stats_frame, None, None, "Valor Total: R$ -", pad_bottom=15)
        self.lbl_pend_qtd = self._create_stat_label(stats_frame, "Pendentes", "#6c757d", "Quantidade: -"); self.lbl_pend_val = self._create_stat_label(stats_frame, None, None, "Valor Total: R$ -", pad_bottom=15)
        ttk.Separator(stats_frame, orient=HORIZONTAL).pack(fill=X, pady=10)
        self.lbl_total_qtd = self._create_stat_label(stats_frame, "Total Recebido", "#17a2b8", "Quantidade Total: -"); self.lbl_total_val = self._create_stat_label(stats_frame, None, None, "Valor Total: R$ -")
    
    def _atualizar_dashboard_geral(self, filtros):
        stats = self.service.get_estatisticas_gerais(filtros)
        proc_q, proc_v = stats['Procedente']['quantidade'], stats['Procedente']['valor_total']
        impr_q, impr_v = stats['Improcedente']['quantidade'], stats['Improcedente']['valor_total']
        pend_q, pend_v = stats['Pendente']['quantidade'], stats['Pendente']['valor_total']
        self.lbl_proc_qtd.config(text=f"Quantidade: {proc_q}"); self.lbl_proc_val.config(text=f"Valor Total: R$ {proc_v:.2f}")
        self.lbl_impr_qtd.config(text=f"Quantidade: {impr_q}"); self.lbl_impr_val.config(text=f"Valor Total: R$ {impr_v:.2f}")
        self.lbl_pend_qtd.config(text=f"Quantidade: {pend_q}"); self.lbl_pend_val.config(text=f"Valor Total: R$ {pend_v:.2f}")
        self.lbl_total_qtd.config(text=f"Quantidade Total: {proc_q + impr_q + pend_q}"); self.lbl_total_val.config(text=f"Valor Total: R$ {proc_v + impr_v + pend_v:.2f}")
        self._desenhar_grafico(self.canvas_geral_frame, [proc_q, impr_q, pend_q], ['Procedentes', 'Improcedentes', 'Pendentes'], ['#28a745', '#dc3545', '#6c757d'])

    def _criar_view_dashboard_ressarcimento(self):
        self.frame_dashboard_ressarcimento = ttk.Frame(self.container)
        self.frame_dashboard_ressarcimento.columnconfigure(0, weight=1); self.frame_dashboard_ressarcimento.rowconfigure(0, weight=1)
        self.canvas_ressarc_frame = ttk.LabelFrame(self.frame_dashboard_ressarcimento, text="Distribuição de Ressarcimentos (Valor)", padding=15); self.canvas_ressarc_frame.grid(row=0, column=0, sticky="nsew", padx=(0,10))
        stats_frame = ttk.LabelFrame(self.frame_dashboard_ressarcimento, text="Resumo (Ressarcimento)", padding=15, width=350); stats_frame.grid(row=0, column=1, sticky="ns"); stats_frame.pack_propagate(False)
        self.lbl_r_proc_qtd = self._create_stat_label(stats_frame, "Procedentes", "#28a745", "Quantidade: -"); self.lbl_r_proc_val = self._create_stat_label(stats_frame, None, None, "Valor Total: R$ -", pad_bottom=15)
        self.lbl_r_impr_qtd = self._create_stat_label(stats_frame, "Improcedentes", "#dc3545", "Quantidade: -"); self.lbl_r_impr_val = self._create_stat_label(stats_frame, None, None, "Valor Total: R$ -", pad_bottom=15)
        self.lbl_r_pend_qtd = self._create_stat_label(stats_frame, "Pendentes", "#6c757d", "Quantidade: -"); self.lbl_r_pend_val = self._create_stat_label(stats_frame, None, None, "Valor Potencial: R$ -", pad_bottom=15)
        ttk.Separator(stats_frame, orient=HORIZONTAL).pack(fill=X, pady=10)
        self.lbl_r_total_qtd = self._create_stat_label(stats_frame, "Total Ressarcimento", "#17a2b8", "Quantidade Total: -"); self.lbl_r_total_val = self._create_stat_label(stats_frame, None, None, "Valor Total: R$ -")

    def _atualizar_dashboard_ressarcimento(self, filtros):
        stats = self.service.get_estatisticas_ressarcimento(filtros)
        proc_q, proc_v = stats['Procedente']['quantidade'], stats['Procedente']['valor_total']
        impr_q, impr_v = stats['Improcedente']['quantidade'], stats['Improcedente']['valor_total']
        pend_q, pend_v = stats['Pendente']['quantidade'], stats['Pendente']['valor_total']
        self.lbl_r_proc_qtd.config(text=f"Quantidade: {proc_q}"); self.lbl_r_proc_val.config(text=f"Valor Total: R$ {proc_v:.2f}")
        self.lbl_r_impr_qtd.config(text=f"Quantidade: {impr_q}"); self.lbl_r_impr_val.config(text=f"Valor Total: R$ {impr_v:.2f}")
        self.lbl_r_pend_qtd.config(text=f"Quantidade: {pend_q}"); self.lbl_r_pend_val.config(text=f"Valor Potencial: R$ {pend_v:.2f}")
        self.lbl_r_total_qtd.config(text=f"Quantidade Total: {proc_q + pend_q}"); self.lbl_r_total_val.config(text=f"Valor Total: R$ {proc_v + impr_v + pend_v:.2f}")
        self._desenhar_grafico(self.canvas_ressarc_frame, [proc_v, impr_v, pend_v], ['Procedentes', 'Improcedentes', 'Pendentes'], ['#28a745', '#dc3545', '#6c757d'])

    def _create_stat_label(self, parent, title, color, text, pad_bottom=0):
        if title: ttk.Label(parent, text=title, font=("Helvetica", 12, "bold"), foreground=color).pack(anchor='w', pady=(0, 5))
        label = ttk.Label(parent, text=text)
        label.pack(anchor='w', padx=10, pady=(0, pad_bottom))
        return label

    def _desenhar_grafico(self, parent_frame, sizes, labels, colors):
        for widget in parent_frame.winfo_children(): widget.destroy()
        
        non_zero_data = [(size, label, color) for size, label, color in zip(sizes, labels, colors) if size > 0]
        if not non_zero_data:
            ttk.Label(parent_frame, text="Não há dados para exibir.").pack(pady=20, expand=YES)
            return

        sizes, labels, colors = zip(*non_zero_data)
        fig, ax = plt.subplots(figsize=(6, 6), dpi=100)
        
        fig.patch.set_facecolor(self.main_app.style.colors.bg)
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, 
               wedgeprops={'edgecolor': 'white'}, 
               textprops={'color': self.main_app.style.colors.fg})
        
        ax.axis('equal'); fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=YES)