# ui/tabs/tab_retorno.py
import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from services.retorno_service import RetornoService

class RetornoTab(ttk.Frame):
    def __init__(self, parent_notebook, main_app):
        super().__init__(parent_notebook, padding=15)
        self.main_app = main_app
        self.service = RetornoService()
        self.itens_retorno_digitados = []
        self._create_widgets()

    def _create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=BOTH, expand=YES)

        input_frame = ttk.LabelFrame(main_frame, text="1. Dados da Nota de Retorno", padding=15, width=550)
        input_frame.pack_propagate(False)
        input_frame.pack(side=LEFT, fill=Y, padx=(0, 10))
        
        ttk.Label(input_frame, text="Número da Nota de Retorno:").pack(anchor=W)
        self.num_nota_retorno_entry = ttk.Entry(input_frame)
        self.num_nota_retorno_entry.pack(fill=X, pady=(0, 10))
        ttk.Label(input_frame, text="Dados Adicionais (Referência):").pack(anchor=W)
        self.ref_text = tk.Text(input_frame, height=4)
        self.ref_text.pack(fill=X, pady=(0, 15))
        item_frame = ttk.LabelFrame(input_frame, text="Itens da Nota", padding=10)
        item_frame.pack(fill=BOTH, pady=10, expand=True)
        item_frame.columnconfigure(1, weight=1)
        item_frame.rowconfigure(2, weight=1)
        ttk.Label(item_frame, text="Cód. Produto:").grid(row=0, column=0, sticky="w", padx=(0, 5), pady=2)
        self.item_codigo_entry = ttk.Entry(item_frame)
        self.item_codigo_entry.grid(row=0, column=1, columnspan=2, sticky="ew", pady=2)
        ttk.Label(item_frame, text="Quantidade:").grid(row=1, column=0, sticky="w", padx=(0, 5), pady=2)
        self.item_qtd_entry = ttk.Entry(item_frame)
        self.item_qtd_entry.grid(row=1, column=1, sticky="ew", pady=2, padx=(0,5))
        add_button = ttk.Button(item_frame, text="Adicionar", command=self._adicionar_item_retorno, bootstyle="outline")
        add_button.grid(row=1, column=2, pady=2)
        tree_frame_left = ttk.Frame(item_frame)
        tree_frame_left.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=(10,0))
        scrollbar_left = ttk.Scrollbar(tree_frame_left, orient=VERTICAL)
        self.itens_retorno_tree = ttk.Treeview(tree_frame_left, columns=("codigo", "qtd"), show="headings", height=5, yscrollcommand=scrollbar_left.set)
        scrollbar_left.config(command=self.itens_retorno_tree.yview)
        scrollbar_left.pack(side=RIGHT, fill=Y)
        self.itens_retorno_tree.pack(side=LEFT, fill=BOTH, expand=YES)
        self.itens_retorno_tree.heading("codigo", text="Cód. Produto")
        self.itens_retorno_tree.heading("qtd", text="Quantidade")
        self.itens_retorno_tree.column("codigo", anchor=CENTER)
        self.itens_retorno_tree.column("qtd", anchor=CENTER)
        ttk.Button(input_frame, text="Buscar Origens", command=self._processar_e_vincular, bootstyle="primary").pack(side=BOTTOM, fill=X, ipady=5, pady=(10,0))
        linking_frame = ttk.LabelFrame(main_frame, text="2. Distribuição e Vínculo de Itens", padding=15)
        linking_frame.pack(side=LEFT, fill=BOTH, expand=YES)
        tree_frame_right = ttk.Frame(linking_frame)
        tree_frame_right.pack(fill=BOTH, expand=YES, pady=5)
        scrollbar_right = ttk.Scrollbar(tree_frame_right, orient=VERTICAL)
        self.origem_tree = ttk.Treeview(tree_frame_right, columns=("id", "nf_origem", "codigo", "qtd_pendente", "qtd_a_retornar"), show="headings", yscrollcommand=scrollbar_right.set)
        scrollbar_right.config(command=self.origem_tree.yview)
        scrollbar_right.pack(side=RIGHT, fill=Y)
        self.origem_tree.pack(side=LEFT, fill=BOTH, expand=YES)
        self.origem_tree.heading("id", text="ID Garantia"); self.origem_tree.column("id", width=80, anchor=CENTER)
        self.origem_tree.heading("nf_origem", text="NF Origem"); self.origem_tree.column("nf_origem", width=80, anchor=CENTER)
        self.origem_tree.heading("codigo", text="Cód. Produto"); self.origem_tree.column("codigo", width=120, anchor=CENTER)
        self.origem_tree.heading("qtd_pendente", text="Qtd. Pendente"); self.origem_tree.column("qtd_pendente", width=100, anchor=CENTER)
        self.origem_tree.heading("qtd_a_retornar", text="Qtd. a Retornar"); self.origem_tree.column("qtd_a_retornar", width=120, anchor=CENTER)
        self.origem_tree.bind("<<TreeviewSelect>>", self._on_origem_select)
        ttk.Separator(linking_frame, orient=HORIZONTAL).pack(fill=X, pady=(5, 10))
        bottom_controls_frame = ttk.Frame(linking_frame)
        bottom_controls_frame.pack(fill=X)
        bottom_controls_frame.columnconfigure((0, 1), weight=1)
        qty_edit_frame = ttk.LabelFrame(bottom_controls_frame, text="Ações para Item Selecionado", padding=10)
        qty_edit_frame.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        qty_edit_frame.columnconfigure(1, weight=1)
        ttk.Label(qty_edit_frame, text="Quantidade:").grid(row=0, column=0, padx=(0,5), pady=5)
        self.qty_to_return_entry = ttk.Entry(qty_edit_frame, width=10, state=DISABLED)
        self.qty_to_return_entry.grid(row=0, column=1, padx=5, pady=5, sticky=EW)
        self.set_qty_button = ttk.Button(qty_edit_frame, text="Definir", state=DISABLED, command=self._definir_quantidade_retorno)
        self.set_qty_button.grid(row=0, column=2, padx=5, pady=5)
        summary_frame = ttk.LabelFrame(bottom_controls_frame, text="Resumo da Vinculação", padding=10)
        summary_frame.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        summary_frame.columnconfigure(1, weight=1)
        default_font_name = self.main_app.style.lookup('TLabel', 'font')
        font_tamanho = 10
        ttk.Label(summary_frame, text="Total na NF Retorno:").grid(row=0, column=0, sticky=W)
        self.total_retorno_label = ttk.Label(summary_frame, text="0", anchor=E, font=(default_font_name, font_tamanho))
        self.total_retorno_label.grid(row=0, column=1, sticky=EW, padx=5)
        ttk.Label(summary_frame, text="Total Vinculado:").grid(row=1, column=0, sticky=W)
        
        ## --- CORRIGIDO: Removido o parâmetro 'font="bold"' duplicado --- ##
        self.total_vinculado_label = ttk.Label(summary_frame, text="0", anchor=E, font=(default_font_name, font_tamanho, "bold"))
        self.total_vinculado_label.grid(row=1, column=1, sticky=EW, padx=5)
        
        self.save_button = ttk.Button(linking_frame, text="Salvar Vínculos e Finalizar Retorno", state=DISABLED, command=self._salvar_vinculos)
        self.save_button.pack(side=BOTTOM, fill=X, ipady=5, pady=(15,0))

    def _processar_e_vincular(self):
        for i in self.origem_tree.get_children(): self.origem_tree.delete(i)
        
        texto_ref = self.ref_text.get("1.0", END)
        itens_origem, mensagem = self.service.buscar_origens(texto_ref)
        
        if not itens_origem:
            messagebox.showwarning("Busca de Origens", mensagem)
            return

        for item in itens_origem:
            self.origem_tree.insert("", END, values=(item['id'], item['numero_nota'], item['codigo_produto'], item['qtd_pendente'], 0))
        
        self.save_button.config(state=NORMAL)
        self._atualizar_totais()
        messagebox.showinfo("Busca de Origens", mensagem)

    def _salvar_vinculos(self):
        num_nota = self.num_nota_retorno_entry.get()
        texto_ref = self.ref_text.get("1.0", END)
        itens_retorno = self.itens_retorno_digitados
        
        vinculos = []
        for item_id in self.origem_tree.get_children():
            valores = self.origem_tree.item(item_id, 'values')
            qtd_vinculada = int(valores[4])
            if qtd_vinculada > 0:
                vinculos.append({
                    'id_garantia_original': int(valores[0]),
                    'codigo_produto': valores[2],
                    'qtd_vinculada': qtd_vinculada
                })
        
        sucesso, mensagem = self.service.salvar_novo_retorno(num_nota, texto_ref, itens_retorno, vinculos)

        if sucesso:
            messagebox.showinfo("Sucesso", mensagem)
            self._resetar_tela()
            # Notifica a aplicação principal para atualizar outras abas
            self.main_app.notificar_atualizacao()
        else:
            messagebox.showerror("Erro ao Salvar", mensagem)

    # O resto dos métodos são auxiliares da UI e podem ser copiados do protótipo
    # _adicionar_item_retorno, _on_origem_select, _definir_quantidade_retorno, _atualizar_totais, _resetar_tela
    def _adicionar_item_retorno(self):
        codigo = self.item_codigo_entry.get().strip(); qtd_str = self.item_qtd_entry.get().strip()
        if not codigo or not qtd_str or not qtd_str.isdigit(): messagebox.showerror("Erro", "Código e quantidade numérica são obrigatórios."); return
        self.itens_retorno_digitados.append({'codigo': codigo, 'quantidade': int(qtd_str)})
        self.itens_retorno_tree.insert("", END, values=(codigo, int(qtd_str)))
        self.item_codigo_entry.delete(0, END); self.item_qtd_entry.delete(0, END); self.item_codigo_entry.focus(); self._atualizar_totais()
    def _on_origem_select(self, event):
        if not self.origem_tree.selection():
            self.qty_to_return_entry.config(state=DISABLED); self.set_qty_button.config(state=DISABLED); return
        self.qty_to_return_entry.config(state=NORMAL); self.set_qty_button.config(state=NORMAL)
        selected_item = self.origem_tree.selection()[0]; current_values = self.origem_tree.item(selected_item, 'values')
        self.qty_to_return_entry.delete(0, END); self.qty_to_return_entry.insert(0, current_values[4])
    def _definir_quantidade_retorno(self):
        if not self.origem_tree.selection(): return
        selected_item_id = self.origem_tree.selection()[0]; valores = self.origem_tree.item(selected_item_id, 'values'); codigo_produto_selecionado = valores[2]; qtd_pendente = int(valores[3])
        try:
            nova_qtd = int(self.qty_to_return_entry.get())
            if nova_qtd < 0: raise ValueError("Quantidade não pode ser negativa")
            if nova_qtd > qtd_pendente: messagebox.showwarning("Aviso", f"A quantidade a retornar ({nova_qtd}) não pode ser maior que a pendente ({qtd_pendente})."); return
        except ValueError: messagebox.showerror("Erro", "Insira um número válido."); return
        total_disponivel_nf = sum(item['quantidade'] for item in self.itens_retorno_digitados if item['codigo'] == codigo_produto_selecionado)
        total_ja_vinculado_outras_linhas = 0
        for item_id in self.origem_tree.get_children():
            if item_id == selected_item_id: continue
            valores_linha = self.origem_tree.item(item_id, 'values'); codigo_produto_linha = valores_linha[2]
            if codigo_produto_linha == codigo_produto_selecionado: total_ja_vinculado_outras_linhas += int(valores_linha[4])
        if (total_ja_vinculado_outras_linhas + nova_qtd) > total_disponivel_nf:
            messagebox.showerror("Erro de Validação", f"Limite para o produto '{codigo_produto_selecionado}' excedido!\n\n- NF de Retorno contém: {total_disponivel_nf} unidade(s)\n- Você já vinculou: {total_ja_vinculado_outras_linhas} unidade(s) em outras linhas\n- Você está tentando vincular mais: {nova_qtd} unidade(s)\n\nO total ({total_ja_vinculado_outras_linhas + nova_qtd}) não pode ultrapassar {total_disponivel_nf}."); return
        novos_valores = list(valores); novos_valores[4] = nova_qtd
        self.origem_tree.item(selected_item_id, values=novos_valores); self._atualizar_totais()
    def _atualizar_totais(self):
        total_retorno = sum(item['quantidade'] for item in self.itens_retorno_digitados); self.total_retorno_label.config(text=f"{total_retorno}")
        total_vinculado = sum(int(self.origem_tree.item(item_id, 'values')[4]) for item_id in self.origem_tree.get_children()); self.total_vinculado_label.config(text=f"{total_vinculado}")
        if total_retorno != total_vinculado or total_retorno == 0: self.total_vinculado_label.config(bootstyle="danger")
        else: self.total_vinculado_label.config(bootstyle="success")
    def _resetar_tela(self):
        self.num_nota_retorno_entry.delete(0, END); self.ref_text.delete("1.0", END)
        for i in self.itens_retorno_tree.get_children(): self.itens_retorno_tree.delete(i)
        for i in self.origem_tree.get_children(): self.origem_tree.delete(i)
        self.itens_retorno_digitados.clear()
        self.qty_to_return_entry.delete(0, END); self.qty_to_return_entry.config(state=DISABLED)
        self.set_qty_button.config(state=DISABLED); self.save_button.config(state=DISABLED)
        self._atualizar_totais()