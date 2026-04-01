import customtkinter as ctk
from tkinter import ttk, messagebox
from typing import List
from datetime import datetime

from app.models.pedido import Pedido
from app.models.pedido_item import PedidoItem
from app.services.pedido_service import PedidoService
from app.services.produto_service import ProdutoService

class PedidosView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.pedido_service = PedidoService()
        self.produto_service = ProdutoService()
        self.current_pedido_id = None
        self.current_itens: List[PedidoItem] = []
        
        # === Layout Principal ===
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # === Header ===
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.title_label = ctk.CTkLabel(header_frame, text="Gerenciamento de Pedidos", font=("Roboto", 20, "bold"))
        self.title_label.pack(side="left", padx=10, pady=10)
        
        self.btn_novo = ctk.CTkButton(header_frame, text="Novo Pedido", command=self._novo_pedido)
        self.btn_novo.pack(side="right", padx=10, pady=10)
        
        # === Body (Container) ===
        self.body_container = ctk.CTkFrame(self, fg_color="transparent")
        self.body_container.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.body_container.grid_columnconfigure(0, weight=1)
        self.body_container.grid_rowconfigure(0, weight=1)
        
        self.view_lista = ctk.CTkFrame(self.body_container, fg_color="transparent")
        self.view_form = ctk.CTkFrame(self.body_container, fg_color="transparent")
        
        self._setup_lista_view()
        self._setup_form_view()
        
        self._show_lista()
        self._carregar_pedidos()

    def _show_lista(self):
        self.view_form.grid_forget()
        self.view_lista.grid(row=0, column=0, sticky="nsew")
        self.btn_novo.configure(state="normal")
        self.title_label.configure(text="Gerenciamento de Pedidos")

    def _show_form(self, editando=False):
        self.view_lista.grid_forget()
        self.view_form.grid(row=0, column=0, sticky="nsew")
        self.btn_novo.configure(state="disabled")
        self.title_label.configure(text="Editar Pedido" if editando else "Novo Pedido")

    def _aplicar_mascara_data(self, event):
        entry = event.widget
        digits = "".join(ch for ch in entry.get() if ch.isdigit())[:8]
        partes = []
        if len(digits) >= 2:
            partes.append(digits[:2])
        elif digits:
            partes.append(digits)
        if len(digits) >= 4:
            partes.append(digits[2:4])
        elif len(digits) > 2:
            partes.append(digits[2:])
        if len(digits) > 4:
            partes.append(digits[4:])
        novo = "/".join(partes)
        entry.delete(0, "end")
        entry.insert(0, novo)

    def _aplicar_mascara_decimal(self, event):
        entry = event.widget
        bruto = entry.get()
        digitos = "".join(ch for ch in bruto if ch.isdigit())
        tem_virgula = "," in bruto
        if not digitos:
            sanitizado = ""
        else:
            if tem_virgula:
                parte_int, parte_dec = bruto.split(",", 1)
                int_digits = "".join(ch for ch in parte_int if ch.isdigit()) or "0"
                dec_all = "".join(ch for ch in parte_dec if ch.isdigit())

                # Permite digitação contínua no final: 1,000 -> 10,00 -> 100,00
                if len(dec_all) > 2:
                    int_digits = int_digits + dec_all[:-2]
                    dec_digits = dec_all[-2:]
                else:
                    dec_digits = dec_all.ljust(2, "0")
            else:
                int_digits = digitos
                dec_digits = "00"

            int_norm = str(int(int_digits))
            grupos = []
            while int_norm:
                grupos.insert(0, int_norm[-3:])
                int_norm = int_norm[:-3]
            sanitizado = f"{'.'.join(grupos)},{dec_digits}"
        entry.delete(0, "end")
        entry.insert(0, sanitizado)

    def _aplicar_mascara_inteiro(self, event):
        entry = event.widget
        sanitizado = "".join(ch for ch in entry.get() if ch.isdigit())
        entry.delete(0, "end")
        entry.insert(0, sanitizado)

    def _normalizar_data_para_ui(self, valor: str) -> str:
        data_txt = (valor or "").strip()
        if not data_txt:
            return ""
        for formato in ("%d/%m/%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(data_txt, formato).strftime("%d/%m/%Y")
            except ValueError:
                continue
        return data_txt

    def _normalizar_numero_para_float(self, valor: str) -> str:
        numero_txt = valor.strip().replace(" ", "")
        if not numero_txt:
            return ""
        if "," in numero_txt:
            return numero_txt.replace(".", "").replace(",", ".")
        return numero_txt

    def _formatar_moeda_ui(self, valor: float) -> str:
        return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def _validar_data(self, valor: str, campo: str, obrigatorio: bool = False) -> str:
        data_txt = valor.strip()
        if not data_txt:
            if obrigatorio:
                raise ValueError(f"O campo {campo} é obrigatório.")
            return ""

        try:
            data_obj = datetime.strptime(data_txt, "%d/%m/%Y")
        except ValueError as exc:
            raise ValueError(f"O campo {campo} deve estar no formato DD/MM/AAAA.") from exc
        return data_obj.strftime("%d/%m/%Y")

    def _parse_float_campo(self, valor: str, campo: str, obrigatorio: bool = False, minimo: float | None = None) -> float:
        numero_txt = self._normalizar_numero_para_float(valor)
        if not numero_txt:
            if obrigatorio:
                raise ValueError(f"O campo {campo} é obrigatório.")
            return 0.0

        try:
            numero = float(numero_txt)
        except ValueError as exc:
            raise ValueError(f"O campo {campo} deve ser numérico.") from exc

        if minimo is not None and numero < minimo:
            raise ValueError(f"O campo {campo} não pode ser menor que {minimo}.")
        return numero

    def _setup_lista_view(self):
        self.view_lista.grid_columnconfigure(0, weight=1)
        self.view_lista.grid_rowconfigure(1, weight=1)
        
        # Filtros
        filter_frame = ctk.CTkFrame(self.view_lista)
        filter_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(filter_frame, text="Cliente:").pack(side="left", padx=5)
        self.filtro_cliente = ctk.CTkEntry(filter_frame, width=200)
        self.filtro_cliente.pack(side="left", padx=5)
        
        ctk.CTkLabel(filter_frame, text="Status Pag.:").pack(side="left", padx=5)
        self.filtro_status = ctk.CTkOptionMenu(filter_frame, values=["Todos", "Pendente", "Recebido"])
        self.filtro_status.pack(side="left", padx=5)
        
        self.btn_buscar = ctk.CTkButton(filter_frame, text="Buscar", command=self._carregar_pedidos, width=100)
        self.btn_buscar.pack(side="left", padx=10)
        
        # Treeview
        tree_frame = ctk.CTkFrame(self.view_lista)
        tree_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2b2b2b", foreground="white", rowheight=25, fieldbackground="#2b2b2b", borderwidth=0)
        style.map('Treeview', background=[('selected', '#1f538d')])
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat")
        
        columns = ("id", "cliente", "data", "entrega", "valor_total", "responsavel")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("cliente", text="Cliente")
        self.tree.heading("data", text="Data Pedido")
        self.tree.heading("entrega", text="Data Entrega")
        self.tree.heading("valor_total", text="Valor Total")
        self.tree.heading("responsavel", text="Responsável")
        
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("cliente", width=200)
        self.tree.column("data", width=100, anchor="center")
        self.tree.column("entrega", width=100, anchor="center")
        self.tree.column("valor_total", width=100, anchor="e")
        self.tree.column("responsavel", width=150)
        
        self.tree.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.bind("<Double-1>", self._editar_pedido)

    def _setup_form_view(self):
        self.view_form.grid_columnconfigure((0, 1), weight=1)
        
        # --- Seção Dados Gerais ---
        frame_gerais = ctk.CTkFrame(self.view_form)
        frame_gerais.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(frame_gerais, text="Nome do Cliente:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_nome_cliente = ctk.CTkEntry(frame_gerais, width=300, placeholder_text="Texto")
        self.entry_nome_cliente.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ctk.CTkLabel(frame_gerais, text="Data Pedido:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_data_pedido = ctk.CTkEntry(frame_gerais, width=150, placeholder_text="DD/MM/AAAA")
        self.entry_data_pedido.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.entry_data_pedido.bind("<KeyRelease>", self._aplicar_mascara_data)
        
        ctk.CTkLabel(frame_gerais, text="Data Entrega:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.entry_data_entrega = ctk.CTkEntry(frame_gerais, width=150, placeholder_text="DD/MM/AAAA")
        self.entry_data_entrega.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        self.entry_data_entrega.bind("<KeyRelease>", self._aplicar_mascara_data)
        
        ctk.CTkLabel(frame_gerais, text="Responsável:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.entry_responsavel = ctk.CTkEntry(frame_gerais, width=200, placeholder_text="Texto")
        self.entry_responsavel.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        # --- Seção Pagamentos ---
        frame_pag = ctk.CTkFrame(self.view_form)
        frame_pag.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        # Pagamento Inicial
        ctk.CTkLabel(frame_pag, text="SINAL (Pagamento Inicial)", font=("Roboto", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=5)
        
        ctk.CTkLabel(frame_pag, text="Valor R$:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_pag_ini_valor = ctk.CTkEntry(frame_pag, width=100, placeholder_text="0,00")
        self.entry_pag_ini_valor.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        ctk.CTkLabel(frame_pag, text="Data:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.entry_pag_ini_data = ctk.CTkEntry(frame_pag, width=100, placeholder_text="DD/MM/AAAA")
        self.entry_pag_ini_data.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        self.entry_pag_ini_data.bind("<KeyRelease>", self._aplicar_mascara_data)
        
        ctk.CTkLabel(frame_pag, text="Forma:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.cb_pag_ini_forma = ctk.CTkComboBox(frame_pag, values=["Dinheiro", "PIX", "Cartão Crédito", "Cartão Débito"], width=150)
        self.cb_pag_ini_forma.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        ctk.CTkLabel(frame_pag, text="Status:").grid(row=2, column=2, padx=5, pady=5, sticky="e")
        self.cb_pag_ini_status = ctk.CTkComboBox(frame_pag, values=["Pendente", "Recebido"], width=100)
        self.cb_pag_ini_status.grid(row=2, column=3, padx=5, pady=5, sticky="w")
        
        # Pagamento Final
        ctk.CTkLabel(frame_pag, text="RESTANTE (Pagamento Final)", font=("Roboto", 14, "bold")).grid(row=0, column=4, columnspan=2, pady=5)
        
        ctk.CTkLabel(frame_pag, text="Valor R$:").grid(row=1, column=4, padx=5, pady=5, sticky="e")
        self.entry_pag_fin_valor = ctk.CTkEntry(frame_pag, width=100, placeholder_text="0,00")
        self.entry_pag_fin_valor.grid(row=1, column=5, padx=5, pady=5, sticky="w")
        
        ctk.CTkLabel(frame_pag, text="Data:").grid(row=1, column=6, padx=5, pady=5, sticky="e")
        self.entry_pag_fin_data = ctk.CTkEntry(frame_pag, width=100, placeholder_text="DD/MM/AAAA")
        self.entry_pag_fin_data.grid(row=1, column=7, padx=5, pady=5, sticky="w")
        self.entry_pag_fin_data.bind("<KeyRelease>", self._aplicar_mascara_data)
        
        ctk.CTkLabel(frame_pag, text="Forma:").grid(row=2, column=4, padx=5, pady=5, sticky="e")
        self.cb_pag_fin_forma = ctk.CTkComboBox(frame_pag, values=["Dinheiro", "PIX", "Cartão Crédito", "Cartão Débito"], width=150)
        self.cb_pag_fin_forma.grid(row=2, column=5, padx=5, pady=5, sticky="w")
        
        ctk.CTkLabel(frame_pag, text="Status:").grid(row=2, column=6, padx=5, pady=5, sticky="e")
        self.cb_pag_fin_status = ctk.CTkComboBox(frame_pag, values=["Pendente", "Recebido"], width=100)
        self.cb_pag_fin_status.grid(row=2, column=7, padx=5, pady=5, sticky="w")
        
        # --- Seção Itens ---
        frame_itens = ctk.CTkFrame(self.view_form)
        frame_itens.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.view_form.grid_rowconfigure(2, weight=1)
        
        lbl_itens = ctk.CTkLabel(frame_itens, text="Itens do Pedido", font=("Roboto", 14, "bold"))
        lbl_itens.pack(anchor="w", padx=5, pady=5)
        
        add_item_frame = ctk.CTkFrame(frame_itens, fg_color="transparent")
        add_item_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(add_item_frame, text="Produto:").pack(side="left", padx=5)
        self.cb_add_produto = ctk.CTkComboBox(add_item_frame, values=[], width=250)
        self.cb_add_produto.pack(side="left", padx=5)
        
        ctk.CTkLabel(add_item_frame, text="Qtd:").pack(side="left", padx=5)
        self.entry_add_qtd = ctk.CTkEntry(add_item_frame, width=60, placeholder_text="0")
        self.entry_add_qtd.pack(side="left", padx=5)
        self.entry_add_qtd.bind("<KeyRelease>", self._aplicar_mascara_inteiro)
        
        btn_add_item = ctk.CTkButton(add_item_frame, text="Adicionar Item", command=self._add_item, width=120)
        btn_add_item.pack(side="left", padx=10)
        
        btn_del_item = ctk.CTkButton(add_item_frame, text="Remover Selecionado", command=self._remover_item, width=150, fg_color="#c93434", hover_color="#942626")
        btn_del_item.pack(side="left", padx=10)
        
        self.tree_itens = ttk.Treeview(frame_itens, columns=("id", "produto", "qtd", "preco", "subtotal"), show="headings", height=5)
        self.tree_itens.heading("id", text="ID Prod")
        self.tree_itens.heading("produto", text="Produto")
        self.tree_itens.heading("qtd", text="Quantidade")
        self.tree_itens.heading("preco", text="Preço Unit. (Snapshot)")
        self.tree_itens.heading("subtotal", text="Subtotal")
        
        self.tree_itens.column("id", width=50, anchor="center")
        self.tree_itens.column("produto", width=250)
        self.tree_itens.column("qtd", width=80, anchor="center")
        self.tree_itens.column("preco", width=120, anchor="e")
        self.tree_itens.column("subtotal", width=120, anchor="e")
        
        self.tree_itens.pack(fill="both", expand=True, padx=5, pady=5)
        
        # --- Total ---
        self.lbl_total = ctk.CTkLabel(frame_itens, text="Total: R$ 0.00", font=("Roboto", 16, "bold"))
        self.lbl_total.pack(side="right", padx=10, pady=10)
        
        # --- Ações ---
        frame_acoes = ctk.CTkFrame(self.view_form, fg_color="transparent")
        frame_acoes.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="e")
        
        self.btn_salvar = ctk.CTkButton(frame_acoes, text="Salvar", command=self._salvar)
        self.btn_salvar.pack(side="right", padx=5)
        
        self.btn_excluir = ctk.CTkButton(frame_acoes, text="Excluir", fg_color="#c93434", hover_color="#942626", command=self._excluir)
        self.btn_excluir.pack(side="right", padx=5)
        
        self.btn_cancelar = ctk.CTkButton(frame_acoes, text="Cancelar", fg_color="gray", hover_color="#555555", command=self._cancelar)
        self.btn_cancelar.pack(side="right", padx=5)
        
        self._carregar_combos()

    def _carregar_combos(self):
        produtos = self.produto_service.listar()
        self.cb_add_produto.configure(values=[f"{p.id} - {p.nome}" for p in produtos])

    def _carregar_pedidos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        cliente = self.filtro_cliente.get()
        status = self.filtro_status.get()
        
        pedidos = self.pedido_service.listar(cliente_nome=cliente, status_pagamento=status)
        for p in pedidos:
            self.tree.insert("", "end", values=(
                p.id, p.cliente_nome, p.data_pedido, p.data_entrega,
                f"R$ {self._formatar_moeda_ui(p.valor_total)}", p.responsavel
            ))

    def _atualizar_lista_itens(self):
        for item in self.tree_itens.get_children():
            self.tree_itens.delete(item)
            
        total = 0.0
        for i, item in enumerate(self.current_itens):
            self.tree_itens.insert("", "end", iid=str(i), values=(
                item.produto_id,
                item.produto_nome,
                item.quantidade,
                f"R$ {self._formatar_moeda_ui(item.preco_unitario_snapshot)}",
                f"R$ {self._formatar_moeda_ui(item.valor_item)}"
            ))
            total += item.valor_item
            
        self.lbl_total.configure(text=f"Total: R$ {self._formatar_moeda_ui(total)}")

    def _add_item(self):
        prod_str = self.cb_add_produto.get()
        qtd_str = self.entry_add_qtd.get().strip()
        
        if not prod_str or not qtd_str:
            messagebox.showwarning("Aviso", "Selecione um produto e informe a quantidade.")
            return
            
        try:
            prod_id = int(prod_str.split(" - ")[0])
            produto = self.produto_service.get_by_id(prod_id)
            if not produto:
                return
                
            qtd = int(qtd_str)
            if qtd <= 0:
                messagebox.showwarning("Aviso", "A quantidade deve ser maior que zero.")
                return
                
            item = PedidoItem(
                produto_id=produto.id,
                quantidade=qtd,
                preco_unitario_snapshot=produto.preco_venda_unitario, # Snapshot set on add
                valor_item=produto.preco_venda_unitario * qtd,
                produto_nome=produto.nome
            )
            
            # Check se ja existe e soma qtd
            existente = next((i for i in self.current_itens if i.produto_id == item.produto_id), None)
            if existente:
                existente.quantidade += qtd
                existente.valor_item = existente.quantidade * existente.preco_unitario_snapshot
            else:
                self.current_itens.append(item)
                
            self.entry_add_qtd.delete(0, 'end')
            self._atualizar_lista_itens()
            
        except ValueError:
            messagebox.showwarning("Aviso", "Quantidade inválida. Informe apenas números inteiros.")

    def _remover_item(self):
        selected = self.tree_itens.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um item para remover.")
            return
            
        idx = int(selected[0])
        del self.current_itens[idx]
        self._atualizar_lista_itens()

    def _novo_pedido(self):
        self.current_pedido_id = None
        self.current_itens = []
        
        self.entry_nome_cliente.delete(0, 'end')
        self.entry_data_pedido.delete(0, 'end')
        self.entry_data_pedido.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.entry_data_entrega.delete(0, 'end')
        self.entry_responsavel.delete(0, 'end')
        
        self.entry_pag_ini_valor.delete(0, 'end')
        self.entry_pag_ini_valor.insert(0, "0,00")
        self.entry_pag_ini_data.delete(0, 'end')
        self.cb_pag_ini_forma.set("PIX")
        self.cb_pag_ini_status.set("Pendente")
        
        self.entry_pag_fin_valor.delete(0, 'end')
        self.entry_pag_fin_valor.insert(0, "0,00")
        self.entry_pag_fin_data.delete(0, 'end')
        self.cb_pag_fin_forma.set("PIX")
        self.cb_pag_fin_status.set("Pendente")
        
        self.btn_excluir.configure(state="disabled")
        
        self._atualizar_lista_itens()
        self._show_form(editando=False)

    def _editar_pedido(self, event):
        selected = self.tree.selection()
        if not selected:
            return
            
        item = self.tree.item(selected[0])
        ped_id = int(item['values'][0])
        
        pedido = self.pedido_service.get_by_id(ped_id)
        if not pedido:
            return
            
        self._novo_pedido() # Limpa
        
        self.current_pedido_id = pedido.id
        self.current_itens = pedido.itens
        
        self.entry_nome_cliente.delete(0, 'end')
        self.entry_nome_cliente.insert(0, pedido.cliente_nome or "")
                
        self.entry_data_pedido.delete(0, 'end')
        self.entry_data_pedido.insert(0, self._normalizar_data_para_ui(pedido.data_pedido or ""))
        
        self.entry_data_entrega.delete(0, 'end')
        self.entry_data_entrega.insert(0, self._normalizar_data_para_ui(pedido.data_entrega or ""))
        
        self.entry_responsavel.delete(0, 'end')
        self.entry_responsavel.insert(0, pedido.responsavel or "")
        
        self.entry_pag_ini_valor.delete(0, 'end')
        self.entry_pag_ini_valor.insert(0, self._formatar_moeda_ui(pedido.pag_inicial_valor or 0.0))
        self.entry_pag_ini_data.delete(0, 'end')
        self.entry_pag_ini_data.insert(0, self._normalizar_data_para_ui(pedido.pag_inicial_data or ""))
        self.cb_pag_ini_forma.set(pedido.pag_inicial_forma)
        self.cb_pag_ini_status.set(pedido.pag_inicial_status)
        
        self.entry_pag_fin_valor.delete(0, 'end')
        self.entry_pag_fin_valor.insert(0, self._formatar_moeda_ui(pedido.pag_final_valor or 0.0))
        self.entry_pag_fin_data.delete(0, 'end')
        self.entry_pag_fin_data.insert(0, self._normalizar_data_para_ui(pedido.pag_final_data or ""))
        self.cb_pag_fin_forma.set(pedido.pag_final_forma)
        self.cb_pag_fin_status.set(pedido.pag_final_status)
        
        self.btn_excluir.configure(state="normal")
        self._atualizar_lista_itens()
        self._show_form(editando=True)

    def _salvar(self):
        nome_cliente = self.entry_nome_cliente.get().strip()
        if not nome_cliente:
            messagebox.showwarning("Aviso", "Informe o nome do cliente.")
            return

        if not self.current_itens:
            messagebox.showwarning("Aviso", "Adicione ao menos um item ao pedido.")
            return
            
        try:
            data_pedido = self._validar_data(self.entry_data_pedido.get(), "Data do Pedido", obrigatorio=True)
            data_entrega = self._validar_data(self.entry_data_entrega.get(), "Data de Entrega")
            pag_inicial_data = self._validar_data(self.entry_pag_ini_data.get(), "Data do Pagamento Inicial")
            pag_final_data = self._validar_data(self.entry_pag_fin_data.get(), "Data do Pagamento Final")

            if data_entrega and datetime.strptime(data_entrega, "%d/%m/%Y") < datetime.strptime(data_pedido, "%d/%m/%Y"):
                raise ValueError("A Data de Entrega não pode ser menor que a Data do Pedido.")

            responsavel = self.entry_responsavel.get().strip()
            if not responsavel:
                raise ValueError("O campo Responsável é obrigatório.")

            pag_inicial_valor = self._parse_float_campo(self.entry_pag_ini_valor.get(), "Valor do Pagamento Inicial", minimo=0.0)
            pag_final_valor = self._parse_float_campo(self.entry_pag_fin_valor.get(), "Valor do Pagamento Final", minimo=0.0)

            pag_ini_forma = self.cb_pag_ini_forma.get().strip()
            pag_ini_status = self.cb_pag_ini_status.get().strip()
            pag_fin_forma = self.cb_pag_fin_forma.get().strip()
            pag_fin_status = self.cb_pag_fin_status.get().strip()

            if not pag_ini_forma or not pag_ini_status or not pag_fin_forma or not pag_fin_status:
                raise ValueError("Preencha forma e status dos pagamentos.")
            
            ped = Pedido(
                id=self.current_pedido_id,
                cliente_nome=nome_cliente,
                data_pedido=data_pedido,
                data_entrega=data_entrega,
                valor_total=0.0, # Service recalcula
                pag_inicial_valor=pag_inicial_valor,
                pag_inicial_data=pag_inicial_data,
                pag_inicial_forma=pag_ini_forma,
                pag_inicial_status=pag_ini_status,
                pag_final_valor=pag_final_valor,
                pag_final_data=pag_final_data,
                pag_final_forma=pag_fin_forma,
                pag_final_status=pag_fin_status,
                responsavel=responsavel
            )
            ped.itens = self.current_itens
            
            self.pedido_service.salvar(ped)
            messagebox.showinfo("Sucesso", "Pedido salvo com sucesso!")
            self._carregar_pedidos()
            self._show_lista()
            
        except ValueError as e:
            messagebox.showerror("Erro", f"Valor inválido: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _excluir(self):
        if not self.current_pedido_id:
            return
            
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir este pedido?"):
            try:
                self.pedido_service.excluir(self.current_pedido_id)
                messagebox.showinfo("Sucesso", "Pedido excluído com sucesso!")
                self._carregar_pedidos()
                self._show_lista()
            except Exception as e:
                messagebox.showerror("Erro", str(e))

    def _cancelar(self):
        self._show_lista()
