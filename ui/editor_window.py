import tkinter as tk
from tkinter import ttk, END
import ttkbootstrap as ttkb
from ttkbootstrap.dialogs import Messagebox
from repository import garantia_repository, codigo_avaria_repository
from services.garantia_service import GarantiaService

class EditorWindow(tk.Toplevel):
    def __init__(self, parent_app, id_item):
        super().__init__(parent_app)
        self.parent_app = parent_app
        self.id_item = id_item
        self.codigos_avaria_map = codigo_avaria_repository.get_all()
        self.service = GarantiaService()

        self.title(f"Editar Item de Garantia - ID: {id_item}")
        self.geometry("700x350")
        self.transient(parent_app)
        self.grab_set()

        self._criar_widgets()
        self._carregar_dados_item()

    def _criar_widgets(self):
        form_frame = ttk.LabelFrame(self, text="Dados da Análise", padding=15)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        form_frame.columnconfigure((1, 3), weight=1)

        ttk.Label(form_frame, text="Cód. Análise:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.cod_entry = ttk.Entry(form_frame, state="readonly"); self.cod_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(form_frame, text="Nº de Série:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.serie_entry = ttk.Entry(form_frame); self.serie_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        
        ttk.Label(form_frame, text="Cód. Avaria:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.avaria_combo = ttk.Combobox(form_frame, state="readonly", values=list(self.codigos_avaria_map.keys()))
        self.avaria_combo.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.avaria_combo.bind("<<ComboboxSelected>>", self._atualizar_status)
        
        self.status_label = ttk.Label(form_frame, text="Status: -", font=("Helvetica", 10, "bold"))
        self.status_label.grid(row=1, column=2, columnspan=2, padx=5, pady=5, sticky="w")
        
        ttk.Label(form_frame, text="Descrição Avaria:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.desc_avaria_entry = ttk.Entry(form_frame, state="readonly")
        self.desc_avaria_entry.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="ew")
        
        ttk.Label(form_frame, text="Origem:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.origem_combo = ttk.Combobox(form_frame, state="readonly", values=["Produzido", "Revenda"])
        self.origem_combo.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(form_frame, text="Fornecedor:").grid(row=3, column=2, padx=5, pady=5, sticky="w")
        self.fornecedor_entry = ttk.Entry(form_frame)
        self.fornecedor_entry.grid(row=3, column=3, padx=5, pady=5, sticky="ew")

        save_btn = ttk.Button(form_frame, text="Salvar Alterações", command=self._salvar_edicao, bootstyle="primary")
        save_btn.grid(row=4, column=3, padx=5, pady=20, sticky="e")

    def _carregar_dados_item(self):
        item_data = garantia_repository.find_complete_details_by_id(self.id_item)
        if not item_data:
            Messagebox.show_error("Não foi possível carregar os dados do item.", "Erro")
            self.destroy()
            return
            
        self.cod_entry.config(state="normal"); self.cod_entry.delete(0, END); self.cod_entry.insert(0, item_data.get('codigo_analise', '')); self.cod_entry.config(state="readonly")
        self.serie_entry.insert(0, item_data.get('numero_serie', ''))
        self.avaria_combo.set(item_data.get('codigo_avaria', ''))
        self.origem_combo.set(item_data.get('produzido_revenda', ''))
        self.fornecedor_entry.insert(0, item_data.get('fornecedor', ''))
        self._atualizar_status()

    def _atualizar_status(self, event=None):
        cod_avaria = self.avaria_combo.get()
        info = self.codigos_avaria_map.get(cod_avaria, {})
        classificacao = info.get('classificacao', '-')
        
        self.desc_avaria_entry.config(state="normal"); self.desc_avaria_entry.delete(0, END); self.desc_avaria_entry.insert(0, info.get('descricao', '')); self.desc_avaria_entry.config(state="readonly")
        
        style = "default"
        if classificacao == "Procedente": style = "success"
        elif classificacao == "Improcedente": style = "danger"
        self.status_label.config(text=f"Status: {classificacao}", bootstyle=style)

    def _salvar_edicao(self):
        cod_avaria = self.avaria_combo.get()
        dados = {
            'codigo_analise': self.cod_entry.get(), 'numero_serie': self.serie_entry.get(),
            'codigo_avaria': cod_avaria, 'descricao_avaria': self.desc_avaria_entry.get(),
            'procedente_improcedente': self.codigos_avaria_map.get(cod_avaria, {}).get('classificacao'),
            'produzido_revenda': self.origem_combo.get(), 'fornecedor': self.fornecedor_entry.get()
        }
        
        sucesso, msg = self.service.salvar_analise(self.id_item, dados)
        if sucesso: 
            Messagebox.show_info("Alterações salvas com sucesso!", "Sucesso")
            self.parent_app.notificar_atualizacao()
            self.destroy()
        else: 
            Messagebox.show_error(msg, "Erro ao Salvar")