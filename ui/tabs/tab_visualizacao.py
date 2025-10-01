import tkinter as tk
from tkinter import ttk, END
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from datetime import datetime
from repository import garantia_repository
from services.garantia_service import GarantiaService
from ui.editor_window import EditorWindow

class VisualizacaoTab(ttk.Frame):
    def __init__(self, parent_notebook, main_app):
        super().__init__(parent_notebook, padding=(10))
        self.main_app = main_app
        self.service = GarantiaService()
        self._criar_widgets()

    def _criar_widgets(self):
        # Filtros
        filtros_frame = ttk.LabelFrame(self, text="Filtros de Pesquisa", padding=15)
        filtros_frame.pack(fill=X, pady=(0, 10))
        filtros_frame.columnconfigure((1, 3), weight=1)
        ttk.Label(filtros_frame, text="CNPJ:").grid(row=0, column=0, padx=5, pady=5, sticky="w"); self.filtro_cnpj = ttk.Entry(filtros_frame); self.filtro_cnpj.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(filtros_frame, text="Nome Cliente:").grid(row=0, column=2, padx=(15, 5), pady=5, sticky="w"); self.filtro_razao = ttk.Entry(filtros_frame); self.filtro_razao.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        ttk.Label(filtros_frame, text="Nº Nota:").grid(row=1, column=0, padx=5, pady=5, sticky="w"); self.filtro_nota = ttk.Entry(filtros_frame); self.filtro_nota.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(filtros_frame, text="Status:").grid(row=1, column=2, padx=(15, 5), pady=5, sticky="w"); self.filtro_status = ttk.Combobox(filtros_frame, state="readonly", values=["Todos", "Pendente de Análise", "Analisado"]); self.filtro_status.grid(row=1, column=3, padx=5, pady=5, sticky="ew"); self.filtro_status.set("Todos")
        btn_frame = ttk.Frame(filtros_frame); btn_frame.grid(row=0, column=4, rowspan=2, padx=(20, 5), sticky="e")
        ttk.Button(btn_frame, text="Filtrar", command=self.aplicar_filtros, bootstyle="primary").pack(fill=X, pady=2, ipady=4)
        ttk.Button(btn_frame, text="Limpar", command=self._limpar_filtros, bootstyle="secondary").pack(fill=X, pady=2, ipady=4)

        # Treeview
        lista_geral_frame = ttk.LabelFrame(self, text="Registros de Garantia", padding=15)
        lista_geral_frame.pack(fill=BOTH, expand=YES)
        cols = ("id", "nota", "data", "cnpj", "cliente", "analise", "produto", "valor", "status", "procedencia", "ressarcimento")
        self.tree = ttk.Treeview(lista_geral_frame, columns=cols, show="headings", selectmode="extended")
        headings = {"id": ("ID", 40), "nota": ("Nº Nota", 80), "data": ("Data", 80), "cnpj": ("CNPJ", 110), "cliente": ("Cliente", 180), "analise": ("Cód. Análise", 100), "produto": ("Cód. Produto", 100), "valor": ("Valor", 80), "status": ("Status", 120), "procedencia": ("Procedência", 100), "ressarcimento": ("Ressarcimento", 100)}
        for col, (text, width) in headings.items(): self.tree.heading(col, text=text); self.tree.column(col, width=width, anchor=CENTER)
        v_scroll = ttk.Scrollbar(lista_geral_frame, orient=VERTICAL, command=self.tree.yview); v_scroll.pack(side=RIGHT, fill=Y)
        h_scroll = ttk.Scrollbar(lista_geral_frame, orient=HORIZONTAL, command=self.tree.xview); h_scroll.pack(side=BOTTOM, fill=X)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        self.tree.pack(fill=BOTH, expand=YES)

        # Botões
        acoes_frame = ttk.Frame(self); acoes_frame.pack(fill=X, pady=(10, 0))
        ttk.Button(acoes_frame, text="Excluir Selecionado(s)", command=self._excluir_itens, bootstyle="danger").pack(side=RIGHT, padx=5)
        ttk.Button(acoes_frame, text="Editar Selecionado", command=self._editar_item, bootstyle="info").pack(side=RIGHT, padx=5)

    def carregar_dados_iniciais(self):
        self.aplicar_filtros()

    def aplicar_filtros(self):
            filtros = {'cnpj': self.filtro_cnpj.get(), 'razao_social': self.filtro_razao.get(), 'numero_nota': self.filtro_nota.get(), 'status': self.filtro_status.get()}
            for i in self.tree.get_children(): self.tree.delete(i)
            resultados = garantia_repository.find_by_filters(filtros)
            for item in resultados:
                data = datetime.strptime(item['data_nota'], '%Y-%m-%d').strftime('%d/%m/%Y')
                valor = f"R$ {item['valor_item']:.2f}" if item['valor_item'] is not None else '-'
                ressarc = f"R$ {float(item['ressarcimento']):.2f}" if item.get('ressarcimento') and item['ressarcimento'].replace('.','',1).isdigit() else "-"
                # Alterado de item['nome_cliente'] para item['cliente']
                self.tree.insert("", END, values=(item['id'], item['numero_nota'], data, item['cnpj'], item['cliente'], item['codigo_analise'] or '-', item['codigo_produto'], valor, item['status'], item['procedente_improcedente'] or '-', ressarc))

    def _limpar_filtros(self):
        self.filtro_cnpj.delete(0, END); self.filtro_razao.delete(0, END); self.filtro_nota.delete(0, END); self.filtro_status.set("Todos")
        self.aplicar_filtros()

    def _excluir_itens(self):
        selecionados = self.tree.selection()
        if not selecionados:
            Messagebox.show_warning("Nenhum item selecionado.", "Aviso"); return
        ids = [self.tree.item(item, "values")[0] for item in selecionados]
        if Messagebox.yesno(f"Tem certeza que deseja excluir os {len(ids)} itens selecionados?", "Confirmação de Exclusão") == "Yes":
            sucesso, msg = self.service.excluir_itens(ids)
            if sucesso:
                Messagebox.show_info(msg, "Sucesso")
                self.main_app.notificar_atualizacao()
            else:
                Messagebox.show_error(msg, "Erro")

    def _editar_item(self):
        selecionados = self.tree.selection()
        if not selecionados or len(selecionados) > 1:
            Messagebox.show_warning("Selecione apenas um item para editar.", "Aviso"); return
        item_values = self.tree.item(selecionados[0], "values")
        if item_values[8] == 'Pendente de Análise':
            Messagebox.show_warning("Não é possível editar um item que ainda não foi analisado.", "Ação Inválida"); return
        EditorWindow(self.main_app, item_values[0])