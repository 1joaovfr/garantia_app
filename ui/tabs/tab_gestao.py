import tkinter as tk
from tkinter import ttk, filedialog
from datetime import datetime
import pandas as pd
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ttkbootstrap.dialogs import Messagebox
from services.dashboard_service import DashboardService
from repository import garantia_repository, cliente_repository

class AutocompleteEntry(ttk.Entry):
    def __init__(self, parent, autocomplete_list, **kwargs):
        super().__init__(parent, **kwargs)
        self.autocomplete_list = autocomplete_list
        self._popup = None
        self.var = self["textvariable"]
        if not self.var:
            self.var = self["textvariable"] = tk.StringVar()
        self.var.trace('w', self._on_text_changed)
        self.bind("<Up>", self._move_selection)
        self.bind("<Down>", self._move_selection)
        self.bind("<Return>", self._confirm_selection)
    def _create_popup(self):
        self._popup = tk.Toplevel(self.winfo_toplevel())
        self._popup.overrideredirect(True)
        self._listbox = tk.Listbox(self._popup, exportselection=False, font=('Helvetica', 10), background="#f0f0f0")
        self._listbox.pack(fill=tk.BOTH, expand=True)
        self._listbox.bind("<<ListboxSelect>>", self._on_listbox_select)
        self._listbox.bind("<ButtonRelease-1>", self._on_listbox_select)
        self._popup.winfo_toplevel().bind("<Button-1>", self._on_click_outside, add="+")
    def _position_popup(self):
        if self._popup:
            x = self.winfo_rootx()
            y = self.winfo_rooty() + self.winfo_height()
            width = self.winfo_width()
            list_height = min(self._listbox.size() * 20, 100)
            self._popup.geometry(f"{width}x{list_height}+{x}+{y}")
    def _on_text_changed(self, *args):
        text = self.var.get()
        if not text: self._hide_popup(); return
        suggestions = [item for item in self.autocomplete_list if item.lower().startswith(text.lower())]
        if suggestions:
            if not self._popup or not self._popup.winfo_exists(): self._create_popup()
            self._listbox.delete(0, tk.END)
            for item in suggestions: self._listbox.insert(tk.END, item)
            self._position_popup(); self._popup.lift()
        else:
            self._hide_popup()
    def _move_selection(self, event):
        if not self._popup or not self._popup.winfo_exists(): return
        current_selection = self._listbox.curselection(); current_index = current_selection[0] if current_selection else -1
        new_index = current_index
        if event.keysym == 'Down': new_index = min(current_index + 1, self._listbox.size() - 1)
        elif event.keysym == 'Up': new_index = max(current_index - 1, 0)
        if new_index >= 0 and new_index != current_index:
            self._listbox.selection_clear(0, tk.END); self._listbox.selection_set(new_index)
            self._listbox.activate(new_index); self._listbox.see(new_index)
    def _confirm_selection(self, event):
        if not self._popup or not self._popup.winfo_exists(): return "break"
        if self._listbox.curselection(): self._on_listbox_select(event)
        elif self._listbox.index(tk.ACTIVE) >= 0:
            self._listbox.selection_set(tk.ACTIVE); self._on_listbox_select(event)
        return "break"
    def _on_listbox_select(self, event):
        if not self._popup or not self._popup.winfo_exists(): return
        selections = self._listbox.curselection()
        if not selections: return
        value = self._listbox.get(selections[0]); self.var.set(value)
        self.icursor(tk.END); self._hide_popup()
    def _on_click_outside(self, event):
        if self._popup and self._popup.winfo_exists():
            if event.widget != self and event.widget.master != self._popup: self._hide_popup()
    def _hide_popup(self):
        if self._popup and self._popup.winfo_exists():
            self._popup.winfo_toplevel().unbind("<Button-1>"); self._popup.destroy(); self._popup = None

class GestaoTab(ttk.Frame):
    def __init__(self, parent_notebook, main_app):
        super().__init__(parent_notebook)
        self.main_app = main_app
        self.service = DashboardService()
        self.current_view = None
        self.lista_grupos = [] 
        self._create_widgets()

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=BOTH, expand=YES)
        top_frame = ttk.Frame(main_frame); top_frame.pack(fill=X, pady=(0, 5))
        self.btn_ver_tabela = ttk.Button(top_frame, text="Tabela", command=lambda: self._mostrar_view('tabela')); self.btn_ver_tabela.pack(side=LEFT, padx=(0,5))
        self.btn_ver_dashboard = ttk.Button(top_frame, text="Dashboard Geral", command=lambda: self._mostrar_view('dashboard')); self.btn_ver_dashboard.pack(side=LEFT, padx=5)
        self.btn_ver_ressarcimento = ttk.Button(top_frame, text="Dashboard Ressarcimento", command=lambda: self._mostrar_view('ressarcimento')); self.btn_ver_ressarcimento.pack(side=LEFT, padx=5)
        self.filtros_frame = ttk.LabelFrame(main_frame, text="Filtros", padding=10)
        ttk.Label(self.filtros_frame, text="Ano:").pack(side=LEFT, padx=(5,2))
        self.combo_ano = ttk.Combobox(self.filtros_frame, state="readonly", width=10); self.combo_ano.pack(side=LEFT, padx=(0,10))
        ttk.Label(self.filtros_frame, text="Mês:").pack(side=LEFT, padx=(5,2))
        self.combo_mes = ttk.Combobox(self.filtros_frame, state="readonly", width=15, values=["Todos"] + list(self._mes_map().keys())); self.combo_mes.pack(side=LEFT, padx=(0,10))
        ttk.Label(self.filtros_frame, text="Grupo do Cliente:").pack(side=LEFT, padx=(5,2))
        self.entry_grupo = AutocompleteEntry(self.filtros_frame, self.lista_grupos, width=25); self.entry_grupo.pack(side=LEFT, padx=(0,10))
        ttk.Button(self.filtros_frame, text="Limpar", command=self._limpar_filtros, bootstyle="secondary").pack(side=RIGHT, padx=5)
        ttk.Button(self.filtros_frame, text="Filtrar", command=self.atualizar_visualizacao, bootstyle="primary").pack(side=RIGHT, padx=5)
        self.container = ttk.Frame(main_frame); self.container.pack(fill=BOTH, expand=YES)
        self._criar_view_tabela(); self._criar_view_dashboard_geral(); self._criar_view_dashboard_ressarcimento()

    def _exportar_para_excel(self):
        dados_atuais = self.service.get_dados_completos_gestao()
        if not dados_atuais:
            Messagebox.show_warning("Não há dados na tabela para exportar.", "Tabela Vazia"); return
        df = pd.DataFrame(dados_atuais)
        mapeamento_cabecalhos = {key: val[0] for key, val in self.headings.items()}
        df.rename(columns=mapeamento_cabecalhos, inplace=True)
        try:
            hoje = datetime.now().strftime('%Y-%m-%d')
            caminho_arquivo = filedialog.asksaveasfilename(
                title="Salvar como arquivo Excel", defaultextension=".xlsx",
                filetypes=[("Arquivos Excel", "*.xlsx"), ("Todos os arquivos", "*.*")],
                initialfile=f"relatorio_garantias_{hoje}.xlsx"
            )
            if caminho_arquivo:
                df.to_excel(caminho_arquivo, index=False)
                Messagebox.show_info("Sucesso!", f"Os dados foram exportados com sucesso para:\n{caminho_arquivo}")
        except Exception as e:
            Messagebox.showerror("Erro na Exportação", f"Ocorreu um erro ao salvar o arquivo:\n{e}")

    def _mostrar_view(self, view_name):
        self.current_view = view_name
        self.frame_tabela.pack_forget(); self.frame_dashboard_geral.pack_forget(); self.frame_dashboard_ressarcimento.pack_forget()
        if view_name == 'tabela':
            self.filtros_frame.pack_forget()
        else:
            self.filtros_frame.pack(fill=X, pady=5, before=self.container)
        self.btn_ver_tabela.config(bootstyle="primary-outline"); self.btn_ver_dashboard.config(bootstyle="info-outline"); self.btn_ver_ressarcimento.config(bootstyle="info-outline")
        if view_name == 'tabela': self.frame_tabela.pack(fill=BOTH, expand=YES); self.btn_ver_tabela.config(bootstyle="success")
        elif view_name == 'dashboard': self.frame_dashboard_geral.pack(fill=BOTH, expand=YES); self.btn_ver_dashboard.config(bootstyle="success")
        elif view_name == 'ressarcimento': self.frame_dashboard_ressarcimento.pack(fill=BOTH, expand=YES); self.btn_ver_ressarcimento.config(bootstyle="success")
        self.atualizar_visualizacao()
    
    def _criar_view_tabela(self):
        self.frame_tabela = ttk.Frame(self.container)
        tabela_container = ttk.Frame(self.frame_tabela); tabela_container.pack(fill=BOTH, expand=YES)
        cols = ('id', 'data_lancamento', 'numero_nota', 'data_nota', 'cnpj', 'cliente', 'grupo_cliente', 'cidade', 'estado', 'regioes', 'codigo_analise', 'codigo_produto', 'grupo_estoque', 'codigo_avaria', 'descricao_tecnica', 'valor_item', 'status', 'procedente_improcedente', 'ressarcimento', 'numero_serie', 'fornecedor', 'notas_retorno')
        self.tree_gestao = ttk.Treeview(tabela_container, columns=cols, show='headings')
        self.headings = {
            'id': ('ID', 40), 'data_lancamento': ('Data de Lançamento', 120), 'numero_nota': ('Número da Nota', 100),
            'data_nota': ('Data da Nota', 100), 'cnpj': ('CNPJ do Cliente', 120), 'cliente': ('Nome do Cliente', 200),
            'grupo_cliente': ('Grupo do Cliente', 120), 'cidade': ('Cidade', 120), 'estado': ('Estado', 50),
            'regioes': ('Região', 100), 'codigo_analise': ('Código de Análise', 100),
            'codigo_produto': ('Código do Produto', 120), 'grupo_estoque': ('Grupo de Estoque', 120),
            'codigo_avaria': ('Código de Avaria', 100), 'descricao_tecnica': ('Descrição Técnica', 200),
            'valor_item': ('Valor do Produto', 100), 'status': ('Status', 110),
            'procedente_improcedente': ('Procedência', 100), 'ressarcimento': ('Ressarcimento', 100),
            'numero_serie': ('Número de Série', 100), 'fornecedor': ('Fornecedor', 120),
            'notas_retorno': ('Nota(s) de Retorno', 120)
        }
        for col, (text, width) in self.headings.items():
            self.tree_gestao.heading(col, text=text); self.tree_gestao.column(col, width=width, anchor=CENTER)
        v_scroll = ttk.Scrollbar(tabela_container, orient=VERTICAL, command=self.tree_gestao.yview); v_scroll.pack(side=RIGHT, fill=Y)
        h_scroll = ttk.Scrollbar(tabela_container, orient=HORIZONTAL, command=self.tree_gestao.xview); h_scroll.pack(side=BOTTOM, fill=X)
        self.tree_gestao.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        self.tree_gestao.pack(fill=BOTH, expand=YES)
        acoes_frame = ttk.Frame(self.frame_tabela); acoes_frame.pack(fill=X, pady=(10, 0))
        self.btn_exportar_excel = ttk.Button(acoes_frame, text="Extrair para Excel", command=self._exportar_para_excel, bootstyle="success")
        self.btn_exportar_excel.pack(side=RIGHT)

    def carregar_dados_iniciais(self):
        self.carregar_filtros(); self._mostrar_view('tabela')
    
    def carregar_filtros(self):
        self.combo_ano['values'] = ["Todos"] + garantia_repository.get_all_available_years()
        self.lista_grupos = cliente_repository.get_all_grupos()
        self.entry_grupo.autocomplete_list = self.lista_grupos
        self._limpar_filtros()

    def _limpar_filtros(self):
        self.combo_ano.set("Todos"); self.combo_mes.set("Todos")
        self.entry_grupo.delete(0, END); self.atualizar_visualizacao()

    ## --- FUNÇÃO QUE FALTAVA --- ##
    def _mes_map(self):
        return {"Janeiro": "01", "Fevereiro": "02", "Março": "03", "Abril": "04", "Maio": "05", "Junho": "06", "Julho": "07", "Agosto": "08", "Setembro": "09", "Outubro": "10", "Novembro": "11", "Dezembro": "12"}

    def _get_filtros(self):
        filtros = {}
        if self.combo_ano.get() != "Todos": filtros['ano'] = self.combo_ano.get()
        if self.combo_mes.get() != "Todos": filtros['mes'] = self._mes_map().get(self.combo_mes.get())
        if self.entry_grupo.get() != "": filtros['grupo'] = self.entry_grupo.get()
        return filtros

    def atualizar_visualizacao(self):
        if self.current_view == 'tabela': self._atualizar_tabela({})
        else:
            filtros = self._get_filtros()
            if self.current_view == 'dashboard': self._atualizar_dashboard_geral(filtros)
            elif self.current_view == 'ressarcimento': self._atualizar_dashboard_ressarcimento(filtros)
    
    def _atualizar_tabela(self, filtros):
        for i in self.tree_gestao.get_children(): self.tree_gestao.delete(i)
        dados = self.service.get_dados_completos_gestao() # A tabela não usa filtros
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
        label = ttk.Label(parent, text=text); label.pack(anchor='w', padx=10, pady=(0, pad_bottom))
        return label

    def _desenhar_grafico(self, parent_frame, sizes, labels, colors):
        for widget in parent_frame.winfo_children(): widget.destroy()
        non_zero_data = [(size, label, color) for size, label, color in zip(sizes, labels, colors) if size > 0]
        if not non_zero_data:
            ttk.Label(parent_frame, text="Não há dados para exibir.").pack(pady=20, expand=YES); return
        sizes, labels, colors = zip(*non_zero_data)
        fig, ax = plt.subplots(figsize=(6, 6), dpi=100)
        fig.patch.set_facecolor(self.main_app.style.colors.bg)
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, wedgeprops={'edgecolor': 'white'}, textprops={'color': self.main_app.style.colors.fg})
        ax.axis('equal'); fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas.draw(); canvas.get_tk_widget().pack(expand=YES)

        acoes_frame = ttk.Frame(self.frame_tabela)
        acoes_frame.pack(fill=X, pady=(10, 0))
        self.btn_exportar_excel = ttk.Button(acoes_frame, text="Extrair para Excel", command=self._exportar_para_excel, bootstyle="success")
        self.btn_exportar_excel.pack(side=RIGHT)

    def atualizar_visualizacao(self):
        if self.current_view == 'tabela':
            self._atualizar_tabela({})
        else:
            filtros = self._get_filtros()
            if self.current_view == 'dashboard': self._atualizar_dashboard_geral(filtros)
            elif self.current_view == 'ressarcimento': self._atualizar_dashboard_ressarcimento(filtros)

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