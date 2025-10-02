# ui/tabs/tab_analise.py
import tkinter as tk
from tkinter import ttk, END
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from datetime import datetime
from repository import garantia_repository, codigo_avaria_repository
from services.garantia_service import GarantiaService

class AnaliseTab(ttk.Frame):
    def __init__(self, parent_notebook, main_app):
        super().__init__(parent_notebook, padding=(10))
        self.main_app = main_app
        self.service = GarantiaService()
        self.id_item_selecionado = None
        self.codigos_avaria_map = {}
        self._create_widgets()

    def _create_widgets(self):
        # Lista de itens pendentes
        lista_frame = ttk.LabelFrame(self, text="Itens Pendentes de Análise", padding=15)
        lista_frame.pack(fill=X, pady=(0, 10))

        # Adicionada a coluna 'qtd'
        cols = ("id", "analise", "nota", "cliente", "produto", "qtd", "data", "ressarcimento")
        self.tree_analise = ttk.Treeview(lista_frame, columns=cols, show="headings", height=12)
        
        self.tree_analise.heading("id", text="ID"); self.tree_analise.column("id", width=50, anchor=CENTER)
        self.tree_analise.heading("analise", text="Cód. Análise"); self.tree_analise.column("analise", width=100, anchor=CENTER)
        self.tree_analise.heading("nota", text="Nº Nota"); self.tree_analise.column("nota", width=80, anchor=CENTER)
        self.tree_analise.heading("cliente", text="Cliente"); self.tree_analise.column("cliente", width=250)
        self.tree_analise.heading("produto", text="Cód. Produto"); self.tree_analise.column("produto", width=120, anchor=CENTER)
        self.tree_analise.heading("qtd", text="Qtd."); self.tree_analise.column("qtd", width=50, anchor=CENTER) # Nova coluna
        self.tree_analise.heading("data", text="Data Nota"); self.tree_analise.column("data", width=100, anchor=CENTER)
        self.tree_analise.heading("ressarcimento", text="Ressarcimento"); self.tree_analise.column("ressarcimento", width=100, anchor=CENTER)
        
        self.tree_analise.pack(side=LEFT, fill=BOTH, expand=YES)
        v_scroll = ttk.Scrollbar(lista_frame, orient=VERTICAL, command=self.tree_analise.yview)
        v_scroll.pack(side=RIGHT, fill=Y)
        self.tree_analise.configure(yscrollcommand=v_scroll.set)
        self.tree_analise.bind("<<TreeviewSelect>>", self._on_item_select)

        # Formulário de análise
        self.form_frame = ttk.LabelFrame(self, text="Formulário de Análise", padding=15)
        self.form_frame.pack(fill=BOTH, expand=YES)
        self.form_frame.columnconfigure((1, 3), weight=1)
        
        ttk.Label(self.form_frame, text="Cód. Análise:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.analise_cod_entry = ttk.Entry(self.form_frame, state="readonly"); self.analise_cod_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(self.form_frame, text="Nº de Série:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.analise_serie_entry = ttk.Entry(self.form_frame); self.analise_serie_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        
        ttk.Label(self.form_frame, text="Cód. Avaria:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.analise_avaria_combo = ttk.Combobox(self.form_frame, state="readonly"); self.analise_avaria_combo.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.analise_avaria_combo.bind("<<ComboboxSelected>>", self._atualizar_status_procedencia)
        
        self.analise_status_label = ttk.Label(self.form_frame, text="Status: -", font=("Helvetica", 10, "bold")); self.analise_status_label.grid(row=1, column=2, columnspan=2, padx=5, pady=5, sticky="w")
        
        ttk.Label(self.form_frame, text="Descrição Avaria:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.analise_desc_avaria_entry = ttk.Entry(self.form_frame, state="readonly"); self.analise_desc_avaria_entry.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="ew")
        
        ttk.Label(self.form_frame, text="Origem:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.analise_origem_combo = ttk.Combobox(self.form_frame, state="readonly", values=["Produzido", "Revenda"]); self.analise_origem_combo.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(self.form_frame, text="Fornecedor:").grid(row=3, column=2, padx=5, pady=5, sticky="w")
        self.analise_fornecedor_entry = ttk.Entry(self.form_frame); self.analise_fornecedor_entry.grid(row=3, column=3, padx=5, pady=5, sticky="ew")
        
        ttk.Button(self.form_frame, text="Guardar Análise", command=self._salvar_analise, bootstyle="primary").grid(row=4, column=3, padx=5, pady=20, sticky="e")
        self._set_form_state("disabled")

    def carregar_dados_iniciais(self):
        self.codigos_avaria_map = codigo_avaria_repository.get_all()
        self.analise_avaria_combo['values'] = list(self.codigos_avaria_map.keys())
        self.carregar_itens_pendentes()

    def carregar_itens_pendentes(self):
        for i in self.tree_analise.get_children(): self.tree_analise.delete(i)
        
        itens = garantia_repository.find_itens_pendentes()
        for item in itens:
            data_formatada = datetime.strptime(item['data_nota'], '%Y-%m-%d').strftime('%d/%m/%Y')
            ressarcimento_str = f"R$ {float(item['ressarcimento']):.2f}" if item.get('ressarcimento') and str(item['ressarcimento']).replace('.','',1).isdigit() else "-"
            
            self.tree_analise.insert("", END, values=(
                item['id'], 
                item['codigo_analise'], 
                item['numero_nota'], 
                item['cliente'], 
                item['codigo_produto'],
                item['quantidade'], # <-- Valor da nova coluna
                data_formatada, 
                ressarcimento_str
            ))

    def _on_item_select(self, event=None):
        selecionado = self.tree_analise.focus()
        if not selecionado: return
        self._limpar_form()
        item = self.tree_analise.item(selecionado, "values")
        self.id_item_selecionado = item[0]
        
        self.analise_cod_entry.config(state="normal"); self.analise_cod_entry.delete(0, END); self.analise_cod_entry.insert(0, item[1]); self.analise_cod_entry.config(state="readonly")
        self.form_frame.config(text=f"Formulário de Análise - Item ID: {self.id_item_selecionado}")
        self._set_form_state("normal")

    def _atualizar_status_procedencia(self, event=None):
        cod_avaria = self.analise_avaria_combo.get()
        info = self.codigos_avaria_map.get(cod_avaria, {})
        classificacao = info.get('classificacao', '-')
        
        self.analise_desc_avaria_entry.config(state="normal"); self.analise_desc_avaria_entry.delete(0, END); self.analise_desc_avaria_entry.insert(0, info.get('descricao', '')); self.analise_desc_avaria_entry.config(state="readonly")
        
        style = "default"
        if classificacao == "Procedente": style = "success"
        elif classificacao == "Improcedente": style = "danger"
        self.analise_status_label.config(text=f"Status: {classificacao}", bootstyle=style)

    def _salvar_analise(self):
        if not self.id_item_selecionado: return
        campos = {'Nº de Série': self.analise_serie_entry.get(), 'Cód. Avaria': self.analise_avaria_combo.get(), 'Origem': self.analise_origem_combo.get(), 'Fornecedor': self.analise_fornecedor_entry.get()}
        for nome, valor in campos.items():
            if not valor.strip():
                Messagebox.showerror(f"O campo '{nome}' é obrigatório.", "Erro de Validação"); return
        
        cod_avaria = campos['Cód. Avaria']
        dados = {
            'codigo_analise': self.analise_cod_entry.get(), 'numero_serie': campos['Nº de Série'], 'codigo_avaria': cod_avaria, 
            'descricao_avaria': self.analise_desc_avaria_entry.get(), 
            'procedente_improcedente': self.codigos_avaria_map.get(cod_avaria, {}).get('classificacao'), 
            'produzido_revenda': campos['Origem'], 'fornecedor': campos['Fornecedor']
        }
        
        sucesso, msg = self.service.salvar_analise(self.id_item_selecionado, dados)
        if sucesso:
            Messagebox.showinfo(msg, "Sucesso")
            self._limpar_form()
            self.main_app.notificar_atualizacao()
        else:
            Messagebox.showerror(msg, "Erro")

    def _set_form_state(self, state):
        for widget in self.form_frame.winfo_children():
            try:
                if isinstance(widget, (ttk.Entry, ttk.Combobox, ttk.Button)):
                    widget.config(state=state)
                if isinstance(widget, ttk.Entry) and widget in [self.analise_cod_entry, self.analise_desc_avaria_entry]:
                    widget.config(state="readonly" if state == "normal" else "disabled")
            except tk.TclError: pass

    def _limpar_form(self):
        self.id_item_selecionado = None
        self.form_frame.config(text="Formulário de Análise")
        self.analise_cod_entry.config(state="normal"); self.analise_cod_entry.delete(0, END); self.analise_cod_entry.config(state="readonly")
        for entry in [self.analise_serie_entry, self.analise_fornecedor_entry]: entry.delete(0, END)
        self.analise_desc_avaria_entry.config(state="normal"); self.analise_desc_avaria_entry.delete(0, END); self.analise_desc_avaria_entry.config(state="readonly")
        for combo in [self.analise_avaria_combo, self.analise_origem_combo]: combo.set('')
        self.analise_status_label.config(text="Status: -", bootstyle="default")
        self._set_form_state("disabled")