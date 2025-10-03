import tkinter as tk
from tkinter import ttk, messagebox, END
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from services.retorno_service import RetornoService
from repository import cliente_repository

class RetornoTab(ttk.Frame):
    def __init__(self, parent_notebook, main_app):
        super().__init__(parent_notebook)
        self.main_app = main_app
        self.service = RetornoService()
        self.itens_retorno_digitados = {}
        self.selected_item_ids = {}
        self._create_widgets()

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding=10); main_frame.pack(fill=BOTH, expand=YES)
        main_frame.rowconfigure(0, weight=1); main_frame.columnconfigure(0, weight=2); main_frame.columnconfigure(1, weight=3)

        input_frame = ttk.LabelFrame(main_frame, text="1. Dados da Nota de Retorno", padding=15)
        input_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        input_frame.columnconfigure(0, weight=1); input_frame.rowconfigure(2, weight=1)
        
        general_data_frame = ttk.LabelFrame(input_frame, text="Dados Gerais")
        general_data_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        general_data_frame.columnconfigure(1, weight=1)
        ttk.Label(general_data_frame, text="CNPJ do Cliente:").grid(row=0, column=0, padx=5, pady=5, sticky="w") # PADRONIZADO
        self.cnpj_entry = ttk.Entry(general_data_frame); self.cnpj_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.cnpj_entry.bind("<FocusOut>", self._buscar_cliente); self.cnpj_entry.bind("<Return>", self._buscar_cliente)
        ttk.Label(general_data_frame, text="Nome do Cliente:").grid(row=1, column=0, padx=5, pady=5, sticky="w") # PADRONIZADO
        self.nome_cliente_entry = ttk.Entry(general_data_frame, state="readonly"); self.nome_cliente_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(general_data_frame, text="Número da Nota de Retorno:").grid(row=2, column=0, padx=5, pady=5, sticky="w") # PADRONIZADO
        self.num_nota_retorno_entry = ttk.Entry(general_data_frame); self.num_nota_retorno_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        ref_frame = ttk.LabelFrame(input_frame, text="Dados Adicionais (Referência)"); ref_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self.ref_text = tk.Text(ref_frame, height=3); self.ref_text.pack(fill=X, expand=YES, padx=5, pady=5)

        item_frame = ttk.LabelFrame(input_frame, text="Itens da Nota", padding=10); item_frame.grid(row=2, column=0, sticky="nsew")
        item_frame.columnconfigure(1, weight=1); item_frame.rowconfigure(2, weight=1)
        ttk.Label(item_frame, text="Código do Produto:").grid(row=0, column=0, sticky="w", padx=(0, 5), pady=2) # PADRONIZADO
        self.item_codigo_entry = ttk.Entry(item_frame); self.item_codigo_entry.grid(row=0, column=1, columnspan=2, sticky="ew", pady=2)
        ttk.Label(item_frame, text="Quantidade:").grid(row=1, column=0, sticky="w", padx=(0, 5), pady=2) # PADRONIZADO
        self.item_qtd_entry = ttk.Entry(item_frame); self.item_qtd_entry.grid(row=1, column=1, sticky="ew", pady=2, padx=(0,5))
        ttk.Button(item_frame, text="Adicionar", command=self._adicionar_item_retorno, bootstyle="outline").grid(row=1, column=2, pady=2)
        
        tree_frame_left = ttk.Frame(item_frame); tree_frame_left.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=(10,0))
        scrollbar_left = ttk.Scrollbar(tree_frame_left, orient=VERTICAL)
        self.itens_retorno_tree = ttk.Treeview(tree_frame_left, columns=("codigo", "qtd"), show="headings", height=5, yscrollcommand=scrollbar_left.set)
        scrollbar_left.config(command=self.itens_retorno_tree.yview); scrollbar_left.pack(side=RIGHT, fill=Y); self.itens_retorno_tree.pack(side=LEFT, fill=BOTH, expand=YES)
        self.itens_retorno_tree.heading("codigo", text="Código do Produto"); self.itens_retorno_tree.column("codigo", anchor=CENTER) # PADRONIZADO
        self.itens_retorno_tree.heading("qtd", text="Quantidade"); self.itens_retorno_tree.column("qtd", anchor=CENTER) # PADRONIZADO

        ttk.Button(input_frame, text="Buscar Origens", command=self._processar_e_vincular, bootstyle="primary").grid(row=3, column=0, sticky="ew", ipady=5, pady=(10,0))
        
        linking_frame = ttk.LabelFrame(main_frame, text="2. Seleção de Peças para Devolução", padding=15); linking_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        ttk.Label(linking_frame, text="Clique em uma linha para selecionar/desselecionar as peças para retorno.").pack(anchor=W)
        
        tree_frame_right = ttk.Frame(linking_frame); tree_frame_right.pack(fill=BOTH, expand=YES, pady=5)
        scrollbar_right = ttk.Scrollbar(tree_frame_right, orient=VERTICAL)
        self.origem_tree = ttk.Treeview(tree_frame_right, columns=("nf_origem", "codigo", "procedencia"), show="headings", selectmode="none", yscrollcommand=scrollbar_right.set)
        scrollbar_right.config(command=self.origem_tree.yview); scrollbar_right.pack(side=RIGHT, fill=Y); self.origem_tree.pack(side=LEFT, fill=BOTH, expand=YES)
        self.origem_tree.heading("nf_origem", text="Nota Fiscal de Origem"); self.origem_tree.column("nf_origem", width=120, anchor=CENTER) # PADRONIZADO
        self.origem_tree.heading("codigo", text="Código do Produto"); self.origem_tree.column("codigo", width=150) # PADRONIZADO
        self.origem_tree.heading("procedencia", text="Procedência"); self.origem_tree.column("procedencia", width=120, anchor=CENTER)
        self.origem_tree.tag_configure('selecionado', background='lightblue', foreground='black')
        self.origem_tree.bind("<Button-1>", self._on_row_toggle)
        
        summary_frame = ttk.LabelFrame(linking_frame, text="Resumo da Vinculação", padding=10); summary_frame.pack(fill=X, pady=10)
        summary_frame.columnconfigure(1, weight=1)
        default_font_name = self.main_app.style.lookup('TLabel', 'font'); font_tamanho = 10
        ttk.Label(summary_frame, text="Total na NF Retorno:").grid(row=0, column=0, sticky=W)
        self.total_retorno_label = ttk.Label(summary_frame, text="0", anchor=E, font=(default_font_name, font_tamanho)); self.total_retorno_label.grid(row=0, column=1, sticky=EW, padx=5)
        ttk.Label(summary_frame, text="Total de Peças Selecionadas:").grid(row=1, column=0, sticky=W)
        self.total_vinculado_label = ttk.Label(summary_frame, text="0", font=(default_font_name, font_tamanho, "bold"), anchor=E); self.total_vinculado_label.grid(row=1, column=1, sticky=EW, padx=5)
        self.save_button = ttk.Button(linking_frame, text="Salvar Vínculos e Finalizar Retorno", state=DISABLED, command=self._salvar_vinculos); self.save_button.pack(side=BOTTOM, fill=X, ipady=5, pady=(15,0))

    def _on_row_toggle(self, event):
        row_id = self.origem_tree.identify_row(event.y)
        if not row_id: return
        is_selected = not self.selected_item_ids.get(row_id, False)
        self.selected_item_ids[row_id] = is_selected
        self.origem_tree.item(row_id, tags=('selecionado',) if is_selected else ())
        self._atualizar_totais()

    def _buscar_cliente(self, event=None):
        cnpj = self.cnpj_entry.get().strip()
        if not cnpj: return
        cliente_data = cliente_repository.find_by_cnpj(cnpj)
        nome = cliente_data['cliente'] if cliente_data else "CNPJ não encontrado!"
        self.nome_cliente_entry.config(state="normal")
        self.nome_cliente_entry.delete(0, END)
        self.nome_cliente_entry.insert(0, nome)
        self.nome_cliente_entry.config(state="readonly")

    def _processar_e_vincular(self):
        self._resetar_painel_direito()
        cnpj = self.cnpj_entry.get().strip()
        texto_ref = self.ref_text.get("1.0", END)
        itens_origem, mensagem = self.service.buscar_origens(texto_ref, cnpj)
        if not itens_origem:
            messagebox.showwarning("Busca de Origens", mensagem)
            return
        
        for item in itens_origem:
            self.origem_tree.insert("", END, 
                iid=item['id'], 
                values=(
                    item['numero_nota'], 
                    item['codigo_produto'],
                    item['procedente_improcedente'] or '-'
                )
            )
            self.selected_item_ids[str(item['id'])] = False
        
        self.save_button.config(state=NORMAL)
        self._atualizar_totais()
        messagebox.showinfo("Busca de Origens", mensagem)

    def _adicionar_item_retorno(self):
        codigo = self.item_codigo_entry.get().strip()
        qtd_str = self.item_qtd_entry.get().strip()
        if not (codigo and qtd_str and qtd_str.isdigit()):
            messagebox.showerror("Erro", "Código e quantidade numérica são obrigatórios.")
            return
        qtd = int(qtd_str)
        self.itens_retorno_digitados[codigo] = self.itens_retorno_digitados.get(codigo, 0) + qtd
        self._atualizar_tree_itens_retorno()
        self.item_codigo_entry.delete(0, END)
        self.item_qtd_entry.delete(0, END)
        self.item_codigo_entry.focus()
        self._atualizar_totais()

    def _atualizar_tree_itens_retorno(self):
        for i in self.itens_retorno_tree.get_children():
            self.itens_retorno_tree.delete(i)
        for codigo, qtd in self.itens_retorno_digitados.items():
            self.itens_retorno_tree.insert("", END, values=(codigo, qtd))

    def _atualizar_totais(self, event=None):
        total_retorno = sum(self.itens_retorno_digitados.values())
        self.total_retorno_label.config(text=f"{total_retorno}")
        total_vinculado = sum(1 for selected in self.selected_item_ids.values() if selected)
        self.total_vinculado_label.config(text=f"{total_vinculado}")
        if total_retorno != total_vinculado or total_retorno == 0:
            self.total_vinculado_label.config(bootstyle="danger")
        else:
            self.total_vinculado_label.config(bootstyle="success")

    def _salvar_vinculos(self):
        total_retorno = sum(self.itens_retorno_digitados.values())
        total_vinculado = sum(1 for selected in self.selected_item_ids.values() if selected)
        if total_retorno != total_vinculado:
            messagebox.showerror("Erro de Validação", "O total de peças selecionadas não bate com o total de itens da nota de retorno.")
            return
        
        totais_vinculados_por_prod = {}
        for item_id, is_selected in self.selected_item_ids.items():
            if is_selected:
                valores = self.origem_tree.item(item_id, 'values')
                codigo_prod = valores[1]
                totais_vinculados_por_prod[codigo_prod] = totais_vinculados_por_prod.get(codigo_prod, 0) + 1
        
        if self.itens_retorno_digitados != totais_vinculados_por_prod:
             messagebox.showerror("Erro de Validação", "A contagem de peças selecionadas por produto não bate com os totais da nota de retorno.")
             return

        vinculos = []
        for item_id, is_selected in self.selected_item_ids.items():
            if is_selected:
                valores = self.origem_tree.item(item_id, 'values')
                vinculos.append({'id_garantia_original': int(item_id), 'codigo_produto': valores[1], 'qtd_vinculada': 1})
        
        itens_retorno_lista = [{'codigo': k, 'quantidade': v} for k, v in self.itens_retorno_digitados.items()]
        num_nota = self.num_nota_retorno_entry.get().strip()
        cnpj = self.cnpj_entry.get().strip()
        texto_ref = self.ref_text.get("1.0", END)
        sucesso, mensagem = self.service.salvar_novo_retorno(num_nota, cnpj, texto_ref, itens_retorno_lista, vinculos)

        if sucesso:
            messagebox.showinfo("Sucesso", mensagem)
            self._resetar_tela()
            self.main_app.notificar_atualizacao()
        else:
            messagebox.showerror("Erro ao Salvar", mensagem)

    def _resetar_painel_direito(self):
        for i in self.origem_tree.get_children():
            self.origem_tree.delete(i)
        self.selected_item_ids.clear()
        self.save_button.config(state=DISABLED)
        self._atualizar_totais()

    def _resetar_tela(self):
        self.cnpj_entry.delete(0, END)
        self.nome_cliente_entry.config(state="normal")
        self.nome_cliente_entry.delete(0, END)
        self.nome_cliente_entry.config(state="readonly")
        self.num_nota_retorno_entry.delete(0, END)
        self.ref_text.delete("1.0", END)
        for i in self.itens_retorno_tree.get_children():
            self.itens_retorno_tree.delete(i)
        self.itens_retorno_digitados.clear()
        self._resetar_painel_direito()