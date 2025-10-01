import tkinter as tk
from tkinter import ttk, END
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from services.garantia_service import GarantiaService
from repository import cliente_repository, produto_repository, empresa_repository

class LancamentoTab(ttk.Frame):
    def __init__(self, parent_notebook, main_app):
        super().__init__(parent_notebook, padding=(10))
        self.main_app = main_app
        self.service = GarantiaService()
        self.itens_nota = []
        self._criar_widgets()

    def _criar_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=BOTH, expand=YES)
        ttk.Label(main_frame, text="Lançamento de Nota Fiscal", font=("Helvetica", 16, "bold")).pack(pady=(0, 20), anchor="w")

        # Dados da Nota
        dados_nota_frame = ttk.LabelFrame(main_frame, text="Dados do Cliente e Nota Fiscal", padding=15)
        dados_nota_frame.pack(fill=X, pady=(0, 10))
        dados_nota_frame.columnconfigure((1, 3), weight=1)
        
        ttk.Label(dados_nota_frame, text="Empresa:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.empresa_combo = ttk.Combobox(dados_nota_frame, state="readonly")
        self.empresa_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(dados_nota_frame, text="CNPJ:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.cnpj_entry = ttk.Entry(dados_nota_frame)
        self.cnpj_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.cnpj_entry.bind("<FocusOut>", self._buscar_cliente)
        self.cnpj_entry.bind("<Return>", self._buscar_cliente)
        
        ttk.Label(dados_nota_frame, text="Nome Cliente:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.razao_social_entry = ttk.Entry(dados_nota_frame, state="readonly")
        self.razao_social_entry.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

        ttk.Label(dados_nota_frame, text="Nº da Nota:").grid(row=0, column=2, padx=(20, 5), pady=5, sticky="w")
        self.num_nota_entry = ttk.Entry(dados_nota_frame)
        self.num_nota_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        
        ttk.Label(dados_nota_frame, text="Data da Nota:").grid(row=1, column=2, padx=(20, 5), pady=5, sticky="w")
        self.data_nota_entry = ttkb.DateEntry(dados_nota_frame, bootstyle="primary", dateformat="%d/%m/%Y")
        self.data_nota_entry.grid(row=1, column=3, padx=5, pady=5, sticky="ew")

        # Adicionar Itens
        add_item_frame = ttk.LabelFrame(main_frame, text="Adicionar Itens à Nota", padding=15)
        add_item_frame.pack(fill=X, pady=10)
        ttk.Label(add_item_frame, text="Cód. Item:").pack(side=LEFT, padx=(0, 5))
        self.item_entry = ttk.Entry(add_item_frame, width=15); self.item_entry.pack(side=LEFT, fill=X, expand=YES, padx=5)
        ttk.Label(add_item_frame, text="Quantidade:").pack(side=LEFT, padx=(15, 5))
        self.qtd_entry = ttk.Entry(add_item_frame, width=8); self.qtd_entry.pack(side=LEFT, fill=X, expand=YES, padx=5)
        ttk.Label(add_item_frame, text="Valor Unitário:").pack(side=LEFT, padx=(15, 5))
        self.valor_entry = ttk.Entry(add_item_frame, width=10); self.valor_entry.pack(side=LEFT, fill=X, expand=YES, padx=5)
        
        self.ressarc_check_var = tk.BooleanVar()
        ttk.Checkbutton(add_item_frame, text="Ressarcimento?", variable=self.ressarc_check_var, command=self._toggle_ressarcimento_entry, bootstyle="primary").pack(side=LEFT, padx=(20, 5))
        self.ressarc_label = ttk.Label(add_item_frame, text="Valor Ressarc:")
        self.ressarc_entry = ttk.Entry(add_item_frame, width=10)
        ttk.Button(add_item_frame, text="Adicionar Item", command=self._adicionar_item_lista, bootstyle="success").pack(side=RIGHT, padx=(20, 0))

        # Treeview Itens
        lista_itens_frame = ttk.LabelFrame(main_frame, text="Itens da Nota", padding=15)
        lista_itens_frame.pack(fill=BOTH, expand=YES, pady=10)
        self.tree_lancamento = ttk.Treeview(lista_itens_frame, columns=("codigo", "quantidade", "valor_unit", "ressarcimento"), show="headings")
        self.tree_lancamento.heading("codigo", text="Código do Item"); self.tree_lancamento.column("codigo", anchor=CENTER, width=120)
        self.tree_lancamento.heading("quantidade", text="Quantidade"); self.tree_lancamento.column("quantidade", anchor=CENTER, width=80)
        self.tree_lancamento.heading("valor_unit", text="Valor Unitário"); self.tree_lancamento.column("valor_unit", anchor=CENTER, width=100)
        self.tree_lancamento.heading("ressarcimento", text="Ressarcimento"); self.tree_lancamento.column("ressarcimento", anchor=CENTER, width=100)
        self.tree_lancamento.pack(side=LEFT, fill=BOTH, expand=YES)
        
        # Botões Ações
        acoes_frame = ttk.Frame(main_frame)
        acoes_frame.pack(fill=X, pady=(10, 0))
        ttk.Button(acoes_frame, text="Guardar Nota Fiscal", command=self._salvar_nota_fiscal, bootstyle="primary").pack(side=RIGHT, padx=5)
        ttk.Button(acoes_frame, text="Limpar Campos", command=self._limpar_tela, bootstyle="secondary-outline").pack(side=RIGHT, padx=5)

    def carregar_dados_iniciais(self):
        empresas = empresa_repository.get_all_codigos()
        self.empresa_combo['values'] = empresas
        if empresas: self.empresa_combo.set(empresas[0])

    def _buscar_cliente(self, event=None):
        cnpj = self.cnpj_entry.get().strip()
        if not cnpj: return
        cliente = cliente_repository.find_by_cnpj(cnpj)
        # Alterado de 'nome_cliente' para 'cliente'
        nome = cliente['cliente'] if cliente else "CNPJ não encontrado!"
        self.razao_social_entry.config(state="normal")
        self.razao_social_entry.delete(0, END)
        self.razao_social_entry.insert(0, nome)
        self.razao_social_entry.config(state="readonly")

    def _toggle_ressarcimento_entry(self):
        if self.ressarc_check_var.get():
            self.ressarc_label.pack(side=LEFT, padx=(15, 5))
            self.ressarc_entry.pack(side=LEFT, fill=X, expand=YES, padx=5)
        else:
            self.ressarc_label.pack_forget()
            self.ressarc_entry.pack_forget()
            self.ressarc_entry.delete(0, END)

    def _adicionar_item_lista(self):
        codigo, qtd_str, valor_str = self.item_entry.get().strip(), self.qtd_entry.get().strip(), self.valor_entry.get().strip().replace(',', '.')
        if not all([codigo, qtd_str, valor_str]):
            Messagebox.show_error("Preencha todos os campos do item.", "Erro de Validação"); return
        if not produto_repository.exists_by_codigo(codigo):
            Messagebox.show_error(f"O código de item '{codigo}' não foi encontrado.", "Item Inválido"); return
        try:
            qtd, valor = int(qtd_str), float(valor_str)
            ressarcimento, ressarcimento_str = None, "-"
            if self.ressarc_check_var.get():
                ressarc_val_str = self.ressarc_entry.get().strip().replace(',', '.')
                if not ressarc_val_str:
                    Messagebox.show_error("O valor de ressarcimento deve ser preenchido.", "Erro de Validação"); return
                ressarcimento = float(ressarc_val_str)
                ressarcimento_str = f"R$ {ressarcimento:.2f}"
            
            self.tree_lancamento.insert("", END, values=(codigo, qtd, f"R$ {valor:.2f}", ressarcimento_str))
            self.itens_nota.append({"codigo": codigo, "quantidade": qtd, "valor": valor, "ressarcimento": ressarcimento})
            self.item_entry.delete(0, END); self.qtd_entry.delete(0, END); self.valor_entry.delete(0, END)
            self.ressarc_entry.delete(0, END); self.ressarc_check_var.set(False); self._toggle_ressarcimento_entry()
            self.item_entry.focus()
        except ValueError:
            Messagebox.show_error("Quantidade e Valores devem ser números.", "Erro de Validação"); return

    def _salvar_nota_fiscal(self):
        cnpj = self.cnpj_entry.get().strip()
        numero_nota = self.num_nota_entry.get().strip()
        data_nota = self.data_nota_entry.get_date().strftime('%Y-%m-%d')
        
        sucesso, mensagem = self.service.registrar_nova_nota(cnpj, numero_nota, data_nota, self.itens_nota)
        
        if sucesso:
            Messagebox.show_info(mensagem, "Sucesso")
            self._limpar_tela()
            self.main_app.notificar_atualizacao()
        else:
            Messagebox.show_error(mensagem, "Erro ao Guardar")
            
    def _limpar_tela(self):
        self.cnpj_entry.delete(0, END); self.num_nota_entry.delete(0, END)
        self.razao_social_entry.config(state="normal"); self.razao_social_entry.delete(0, END); self.razao_social_entry.config(state="readonly")
        for i in self.tree_lancamento.get_children(): self.tree_lancamento.delete(i)
        self.itens_nota.clear()
        self.ressarc_entry.delete(0, END); self.ressarc_check_var.set(False); self._toggle_ressarcimento_entry()
        self.cnpj_entry.focus()