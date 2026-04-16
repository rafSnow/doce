import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from typing import List, Dict
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

from app.models.insumo import Insumo
from app.models.produto import Produto
from app.models.produto_insumo import ProdutoInsumo
from app.services.produto_service import ProdutoService
from app.services.insumo_service import InsumoService

class ProdutosView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.prod_service = ProdutoService()
        self.insumo_service = InsumoService()
        
        self.current_produto_id = None
        self.current_insumos_list: List[ProdutoInsumo] = []
        self.matriz_insumos: Dict[int, Insumo] = {}  # id -> Insumo (cache para cálculos rápidos)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # === Header ===
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.title_label = ctk.CTkLabel(header_frame, text="Gerenciamento de Produtos", font=("Roboto", 20, "bold"))
        self.title_label.pack(side="left", padx=10, pady=10)

        self.btn_exportar = ctk.CTkButton(header_frame, text="Exportar Excel", command=self._on_exportar_excel)
        self.btn_exportar.pack(side="right", padx=(0, 10), pady=10)
        
        self.btn_novo = ctk.CTkButton(header_frame, text="Novo Produto", command=self._on_novo)
        self.btn_novo.pack(side="right", padx=10, pady=10)

        # === Body Container ===
        self.body_container = ctk.CTkFrame(self, fg_color="transparent")
        self.body_container.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.body_container.grid_columnconfigure(0, weight=1)
        self.body_container.grid_rowconfigure(0, weight=1)

        self.view_lista = ctk.CTkFrame(self.body_container, fg_color="transparent")
        self.view_form = ctk.CTkFrame(self.body_container, fg_color="transparent")

        self._build_table()
        self._build_form_sidebar()
        
        self._show_lista()
        self._carregar_dados()

    def _show_lista(self):
        self.view_form.grid_forget()
        self.view_lista.grid(row=0, column=0, sticky="nsew")
        self.btn_novo.configure(state="normal")
        self.title_label.configure(text="Gerenciamento de Produtos")

    def _show_form(self, editando=False):
        self.view_lista.grid_forget()
        self.view_form.grid(row=0, column=0, sticky="nsew")
        self.btn_novo.configure(state="disabled")
        self.title_label.configure(text="Editar Produto" if editando else "Novo Produto")

    def _formatar_numero_br(self, valor: float, casas: int = 2) -> str:
        base = f"{valor:,.{casas}f}"
        return base.replace(",", "X").replace(".", ",").replace("X", ".")

    def _parse_float_campo(self, valor: str, campo: str, obrigatorio: bool = True, minimo: float | None = None) -> float:
        numero_txt = valor.strip().replace(",", ".")
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

    def _aplicar_mascara_decimal(self, event):
        entry = event.widget
        raw = entry.get().replace(",", ".")
        resultado = []
        tem_ponto = False
        for ch in raw:
            if ch.isdigit():
                resultado.append(ch)
            elif ch == "." and not tem_ponto:
                resultado.append(ch)
                tem_ponto = True
        sanitizado = "".join(resultado)
        if "." in sanitizado:
            inteiro, decimal = sanitizado.split(".", 1)
            sanitizado = f"{inteiro}.{decimal[:2]}"
        entry.delete(0, "end")
        entry.insert(0, sanitizado)

    def _aplicar_mascara_inteiro(self, event):
        entry = event.widget
        sanitizado = "".join(ch for ch in entry.get() if ch.isdigit())
        entry.delete(0, "end")
        entry.insert(0, sanitizado)

    def _build_table(self):
        self.view_lista.grid_columnconfigure(0, weight=1)
        self.view_lista.grid_rowconfigure(1, weight=1)
        
        # Filtros
        filter_frame = ctk.CTkFrame(self.view_lista)
        filter_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.entry_busca = ctk.CTkEntry(filter_frame, placeholder_text="Buscar por nome...", width=300)
        self.entry_busca.pack(side="left", padx=10)
        self.entry_busca.bind("<KeyRelease>", lambda e: self._carregar_dados())

        table_frame = ctk.CTkFrame(self.view_lista)
        table_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2b2b2b", foreground="white", rowheight=25, fieldbackground="#2b2b2b", borderwidth=0)
        style.map('Treeview', background=[('selected', '#1f538d')])
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat")
        style.map("Treeview.Heading", background=[('active', '#3b3b3b')])

        columns = ("id", "nome", "rendimento", "custo", "comissao", "preco")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="Treeview")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("nome", text="Nome")
        self.tree.heading("rendimento", text="Rendimento")
        self.tree.heading("custo", text="Custo Unita. (R$)")
        self.tree.heading("comissao", text="Markup (%)")
        self.tree.heading("preco", text="Preço Venda (R$)")
        
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("nome", width=180, anchor="w")
        self.tree.column("rendimento", width=90, anchor="center")
        self.tree.column("custo", width=110, anchor="center")
        self.tree.column("comissao", width=90, anchor="center")
        self.tree.column("preco", width=110, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(fill="both", expand=True, side="left")
        scrollbar.pack(fill="y", side="right")

        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Button-3>", self._show_context_menu)
        
        self.context_menu = tk.Menu(self, tearoff=0, bg="#2b2b2b", fg="white")
        self.context_menu.add_command(label="Editar", command=self._on_editar_selecionado)
        self.context_menu.add_command(label="Duplicar", command=self._on_duplicar_selecionado)
        self.context_menu.add_command(label="Excluir", command=self._on_excluir_selecionado)

    def _build_form_sidebar(self):
        self.form_frame = ctk.CTkFrame(self.view_form)
        self.form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        inner_form = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        inner_form.pack(expand=True, padx=20, pady=20)
        inner_form.grid_columnconfigure(0, weight=1)
        inner_form.grid_columnconfigure(1, weight=1)
        
        # --- Seção Dados Base ---
        ctk.CTkLabel(inner_form, text="Dados do Produto", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, pady=10, sticky="w")

        ctk.CTkLabel(inner_form, text="Nome").grid(row=1, column=0, padx=10, pady=(5, 2), sticky="w")
        self.entry_nome = ctk.CTkEntry(inner_form, placeholder_text="Texto", width=300)
        self.entry_nome.grid(row=2, column=0, columnspan=2, padx=10, pady=(0, 8), sticky="ew")

        ctk.CTkLabel(inner_form, text="Rendimento").grid(row=3, column=0, padx=10, pady=(5, 2), sticky="w")
        ctk.CTkLabel(inner_form, text="Markup (%)").grid(row=3, column=1, padx=10, pady=(5, 2), sticky="w")
        self.entry_rendimento = ctk.CTkEntry(inner_form, placeholder_text="Numero")
        self.entry_rendimento.grid(row=4, column=0, padx=10, pady=(0, 8), sticky="ew")
        self.entry_rendimento.bind("<KeyRelease>", self._aplicar_mascara_inteiro)
        self.entry_markup = ctk.CTkEntry(inner_form, placeholder_text="Numero")
        self.entry_markup.grid(row=4, column=1, padx=10, pady=(0, 8), sticky="ew")
        self.entry_markup.bind("<KeyRelease>", self._aplicar_mascara_decimal)

        self.entry_rendimento.bind("<KeyRelease>", lambda e: (self._aplicar_mascara_inteiro(e), self._atualizar_calculos_label()))
        self.entry_markup.bind("<KeyRelease>", lambda e: (self._aplicar_mascara_decimal(e), self._atualizar_calculos_label()))

        # --- Seção Insumos ---
        ctk.CTkLabel(inner_form, text="Insumos (Ficha Tecnica)", font=ctk.CTkFont(weight="bold")).grid(row=5, column=0, columnspan=2, pady=(15, 5), sticky="w")
        
        frame_add_insumo = ctk.CTkFrame(inner_form, fg_color="transparent")
        frame_add_insumo.grid(row=6, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        frame_add_insumo.grid_columnconfigure(0, weight=1)
        frame_add_insumo.grid_columnconfigure(1, weight=1)
        frame_add_insumo.grid_columnconfigure(2, weight=0)
        
        ctk.CTkLabel(frame_add_insumo, text="Insumo").grid(row=0, column=0, padx=(0, 6), pady=(0, 2), sticky="w")
        ctk.CTkLabel(frame_add_insumo, text="Quantidade").grid(row=0, column=1, padx=(0, 6), pady=(0, 2), sticky="w")

        self.combo_insumo = ctk.CTkComboBox(frame_add_insumo, values=["Carregando..."])
        self.combo_insumo.grid(row=1, column=0, padx=(0, 6), pady=(0, 5), sticky="ew")
        
        self.entry_qtd_insumo = ctk.CTkEntry(frame_add_insumo, placeholder_text="Numero", width=80)
        self.entry_qtd_insumo.grid(row=1, column=1, padx=(0, 6), pady=(0, 5), sticky="ew")
        self.entry_qtd_insumo.bind("<KeyRelease>", self._aplicar_mascara_decimal)
        
        btn_add = ctk.CTkButton(frame_add_insumo, text="Adicionar", width=60, command=self._adicionar_insumo_na_lista)
        btn_add.grid(row=1, column=2, pady=(0, 5), sticky="e")

        # Treeview de Insumos da Ficha Técnica
        tree_frame = ctk.CTkFrame(inner_form)
        tree_frame.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        inner_form.grid_rowconfigure(7, weight=1)
        
        cols = ("id", "nome", "qtd", "custo")
        self.tree_insumos = ttk.Treeview(tree_frame, columns=cols, show="headings", height=5)
        self.tree_insumos.heading("id", text="ID")
        self.tree_insumos.heading("nome", text="Insumo")
        self.tree_insumos.heading("qtd", text="Qtd")
        self.tree_insumos.heading("custo", text="Custo R$")
        
        self.tree_insumos.column("id", width=0, stretch=False)
        self.tree_insumos.column("nome", width=120, anchor="w")
        self.tree_insumos.column("qtd", width=50, anchor="center")
        self.tree_insumos.column("custo", width=60, anchor="center")
        self.tree_insumos.pack(fill="both", expand=True)

        self.tree_insumos.bind("<Delete>", self._remover_insumo_selecionado)
        self.tree_insumos.bind("<BackSpace>", self._remover_insumo_selecionado)
        self.tree_insumos.bind("<Double-1>", self._remover_insumo_selecionado) # Alternativa para toque

        # --- Seção Resultados e Totais ---
        frame_totais = ctk.CTkFrame(inner_form)
        frame_totais.grid(row=8, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        self.lbl_custo_receita = ctk.CTkLabel(frame_totais, text="Custo Receita: R$ 0.00", text_color="white")
        self.lbl_custo_receita.pack(anchor="w", padx=10, pady=2)
        
        self.lbl_custo_un = ctk.CTkLabel(frame_totais, text="Custo Unita.: R$ 0.00", text_color="#F44336")
        self.lbl_custo_un.pack(anchor="w", padx=10, pady=2)
        
        self.lbl_preco_venda = ctk.CTkLabel(frame_totais, text="Preço Venda: R$ 0.00", text_color="#4CAF50", font=ctk.CTkFont(weight="bold"))
        self.lbl_preco_venda.pack(anchor="w", padx=10, pady=2)

        # --- Botoes Finais ---
        frame_btns = ctk.CTkFrame(inner_form, fg_color="transparent")
        frame_btns.grid(row=9, column=0, columnspan=2, padx=10, pady=10, sticky="e")
        
        self.btn_salvar = ctk.CTkButton(frame_btns, text="Salvar", command=self._on_salvar)
        self.btn_salvar.pack(side="right", padx=5)
        
        self.btn_excluir = ctk.CTkButton(frame_btns, text="Excluir", fg_color="#c93434", hover_color="#942626", command=self._excluir_form)
        self.btn_excluir.pack(side="right", padx=5)
        self.btn_excluir.configure(state="disabled")
        
        self.btn_cancelar = ctk.CTkButton(frame_btns, text="Cancelar", fg_color="gray", hover_color="#555555", command=self._ocultar_form)
        self.btn_cancelar.pack(side="right", padx=5)

    def _carregar_dados(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        nome = self.entry_busca.get()
        produtos = self.prod_service.listar(nome=nome)
        
        for p in produtos:
            self.tree.insert("", "end", values=(
                p.id,
                p.nome,
                p.rendimento_receita,
                self._formatar_numero_br(p.custo_unitario, 2),
                f"{p.comissao_perc}%",
                self._formatar_numero_br(p.preco_venda_unitario, 2)
            ))

    def _carregar_combo_insumos(self):
        insumos = self.insumo_service.listar()
        self.matriz_insumos = {i.id: i for i in insumos}
        combo_vals = [f"{i.id} - {i.nome} ({i.unidade_medida})" for i in insumos]
        self.combo_insumo.configure(values=combo_vals)
        if combo_vals:
            self.combo_insumo.set(combo_vals[0])
        else:
            self.combo_insumo.set("Nenhum insumo.")

    def _on_novo(self):
        self.current_produto_id = None
        self.current_insumos_list.clear()
        
        self.entry_nome.delete(0, 'end')
        self.entry_rendimento.delete(0, 'end')
        self.entry_rendimento.insert(0, "1")
        self.entry_markup.delete(0, 'end')
        self.entry_markup.insert(0, "0")
        
        self.btn_excluir.configure(state="disabled")
        
        self._carregar_combo_insumos()
        self._render_tree_insumos()
        self._show_form()

    def _ocultar_form(self):
        self._show_lista()

    def _adicionar_insumo_na_lista(self):
        selecao = self.combo_insumo.get()
        qtd_txt = self.entry_qtd_insumo.get().strip().replace(",", ".")
        
        if "-" not in selecao:
            messagebox.showerror("Erro", "Selecione um insumo válido.")
            return

        if not qtd_txt:
            messagebox.showerror("Erro", "Informe a quantidade usada.")
            return

        insumo_id = int(selecao.split(" - ")[0])
        
        try:
            qtd = float(qtd_txt)
        except ValueError:
            messagebox.showerror("Erro", "Quantidade inválida. Informe apenas números.")
            return
            
        if qtd <= 0:
            messagebox.showerror("Erro", "A quantidade deve ser maior que zero.")
            return

        # Verificar se já existe na lista e somar
        existente = next((pi for pi in self.current_insumos_list if pi.insumo_id == insumo_id), None)
        if existente:
            existente.quantidade_usada_receita += qtd
        else:
            insumo_ref = self.matriz_insumos.get(insumo_id)
            if not insumo_ref:
                messagebox.showerror("Erro", "Insumo não encontrado para cálculo.")
                return
            pi = ProdutoInsumo(
                insumo_id=insumo_id,
                quantidade_usada_receita=qtd,
                insumo_nome=insumo_ref.nome,
                insumo_unidade=insumo_ref.unidade_medida
            )
            self.current_insumos_list.append(pi)
            
        self.entry_qtd_insumo.delete(0, 'end')
        self._render_tree_insumos()

    def _remover_insumo_selecionado(self, event=None):
        selected = self.tree_insumos.selection()
        if not selected: return
        
        insumo_id = int(self.tree_insumos.item(selected[0])['values'][0])
        self.current_insumos_list = [pi for pi in self.current_insumos_list if pi.insumo_id != insumo_id]
        self._render_tree_insumos()

    def _render_tree_insumos(self):
        for row in self.tree_insumos.get_children():
            self.tree_insumos.delete(row)
            
        for pi in self.current_insumos_list:
            insumo_ref = self.matriz_insumos.get(pi.insumo_id)
            if insumo_ref:
                custo_prop = pi.quantidade_usada_receita * insumo_ref.custo_por_unidade
            else:
                custo_prop = 0.0

            nome_display = f"{pi.insumo_nome}"
            qtd_display = f"{pi.quantidade_usada_receita:g} {pi.insumo_unidade}"
            
            self.tree_insumos.insert("", "end", values=(
                pi.insumo_id,
                nome_display,
                qtd_display,
                self._formatar_numero_br(custo_prop, 2)
            ))
            
        self._atualizar_calculos_label()

    def _atualizar_calculos_label(self, event=None):
        try:
            rendimento = int(self.entry_rendimento.get() or 1)
            markup = float(self.entry_markup.get().replace(",", ".") or 0)
        except ValueError:
            rendimento = 1
            markup = 0.0

        custo_total_receita = 0.0
        for pi in self.current_insumos_list:
            insumo_ref = self.matriz_insumos.get(pi.insumo_id)
            if insumo_ref:
                custo_total_receita += (pi.quantidade_usada_receita * insumo_ref.custo_por_unidade)
                
        custo_un = (custo_total_receita / rendimento) if rendimento > 0 else 0
        preco_venda = custo_un * (1 + (markup / 100))

        self.lbl_custo_receita.configure(text=f"Custo Receita: R$ {custo_total_receita:.2f}")
        self.lbl_custo_un.configure(text=f"Custo Unita.: R$ {custo_un:.2f}")
        self.lbl_preco_venda.configure(text=f"Preço Venda: R$ {preco_venda:.2f}")

    def _on_salvar(self):
        nome = self.entry_nome.get().strip()
        try:
            if not nome:
                raise ValueError("Nome é obrigatório.")

            if len(nome) < 3:
                raise ValueError("Nome deve ter ao menos 3 caracteres.")

            rend_txt = self.entry_rendimento.get().strip()
            if not rend_txt:
                raise ValueError("Rendimento é obrigatório.")

            rend = int(rend_txt)
            if rend <= 0:
                raise ValueError("Rendimento deve ser maior que zero.")

            mkup = self._parse_float_campo(self.entry_markup.get(), "Markup", minimo=0.0)

            if not self.current_insumos_list:
                raise ValueError("Adicione ao menos um insumo na ficha técnica.")

            for insumo in self.current_insumos_list:
                if insumo.quantidade_usada_receita <= 0:
                    raise ValueError("Todas as quantidades de insumos devem ser maiores que zero.")

        except ValueError as e:
            messagebox.showerror("Erro", str(e))
            return
            
        prod = Produto(
            id=self.current_produto_id,
            nome=nome,
            rendimento_receita=rend,
            comissao_perc=mkup,
            insumos=self.current_insumos_list
        )
        
        self.prod_service.salvar(prod)
        self._ocultar_form()
        self._carregar_dados()

    # --- Ações de Context Menu & Double Click ---
    def _show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.tk_popup(event.x_root, event.y_root)

    def _on_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self._on_editar_selecionado()

    def _on_editar_selecionado(self):
        selected = self.tree.selection()
        if not selected: return
        item_id = self.tree.item(selected[0])['values'][0]
        
        prod = self.prod_service.get_by_id(item_id)
        if prod:
            self.current_produto_id = prod.id
            self.entry_nome.delete(0, 'end')
            self.entry_nome.insert(0, prod.nome)
            
            self.entry_rendimento.delete(0, 'end')
            self.entry_rendimento.insert(0, str(prod.rendimento_receita))
            
            self.entry_markup.delete(0, 'end')
            self.entry_markup.insert(0, str(prod.comissao_perc))
            
            self.btn_excluir.configure(state="normal")
            
            self._carregar_combo_insumos()
            self.current_insumos_list = prod.insumos
            self._render_tree_insumos()
            
            self._show_form(editando=True)

    def _excluir_form(self):
        if self.current_produto_id:
            nome = self.entry_nome.get()
            mensagem = (
                f"Confirma a exclusao do produto '{nome}'?\n\n"
                "Esta acao nao pode ser desfeita."
            )
            resp = messagebox.askyesno("Confirmar exclusao", mensagem)
            if resp:
                self.prod_service.excluir(self.current_produto_id)
                self._carregar_dados()
                self._ocultar_form()

    def _on_duplicar_selecionado(self):
        selected = self.tree.selection()
        if not selected: return
        item_id = self.tree.item(selected[0])['values'][0]
        
        self.prod_service.duplicar(item_id)
        self._carregar_dados()

    def _on_exportar_excel(self):
        nome_busca = self.entry_busca.get().strip()
        produtos = self.prod_service.listar(nome=nome_busca)

        if not produtos:
            messagebox.showinfo("Exportar Excel", "Não há produtos para exportar com o filtro atual.")
            return

        caminho_arquivo = filedialog.asksaveasfilename(
            title="Salvar exportação de produtos",
            defaultextension=".xlsx",
            filetypes=[("Planilha Excel", "*.xlsx")],
            initialfile=f"produtos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        )
        if not caminho_arquivo:
            return

        try:
            workbook = Workbook()
            sheet_resumo = workbook.active
            sheet_resumo.title = "Produtos"

            cabecalho_resumo = [
                "ID",
                "Nome",
                "Rendimento",
                "Custo Unitário (R$)",
                "Markup (%)",
                "Preço de Venda (R$)",
            ]
            sheet_resumo.append(cabecalho_resumo)

            for celula in sheet_resumo[1]:
                celula.font = Font(bold=True, color="FFFFFF")
                celula.fill = PatternFill(fill_type="solid", fgColor="A66850")
                celula.alignment = Alignment(horizontal="center", vertical="center")

            sheet_fichas = workbook.create_sheet("Ficha Tecnica")
            cabecalho_fichas = [
                "Produto ID",
                "Produto",
                "Insumo ID",
                "Insumo",
                "Quantidade Usada",
                "Unidade",
                "Custo Proporcional (R$)",
            ]
            sheet_fichas.append(cabecalho_fichas)

            for celula in sheet_fichas[1]:
                celula.font = Font(bold=True, color="FFFFFF")
                celula.fill = PatternFill(fill_type="solid", fgColor="565b5e")
                celula.alignment = Alignment(horizontal="center", vertical="center")

            for produto in produtos:
                sheet_resumo.append([
                    produto.id,
                    produto.nome,
                    produto.rendimento_receita,
                    produto.custo_unitario,
                    produto.comissao_perc,
                    produto.preco_venda_unitario,
                ])

                produto_detalhado = self.prod_service.get_by_id(produto.id)
                if not produto_detalhado:
                    continue

                for pi in produto_detalhado.insumos:
                    sheet_fichas.append([
                        produto_detalhado.id,
                        produto_detalhado.nome,
                        pi.insumo_id,
                        pi.insumo_nome or "",
                        pi.quantidade_usada_receita,
                        pi.insumo_unidade or "",
                        pi.custo_proporcional,
                    ])

            for planilha in (sheet_resumo, sheet_fichas):
                larguras = {}
                for linha in planilha.iter_rows():
                    for celula in linha:
                        valor = "" if celula.value is None else str(celula.value)
                        larguras[celula.column_letter] = max(larguras.get(celula.column_letter, 0), len(valor))

                for coluna, largura in larguras.items():
                    planilha.column_dimensions[coluna].width = min(largura + 2, 40)

                planilha.freeze_panes = "A2"

            workbook.save(caminho_arquivo)
            messagebox.showinfo("Exportar Excel", f"Exportação concluída com sucesso.\nArquivo salvo em:\n{caminho_arquivo}")
        except Exception as exc:
            messagebox.showerror("Exportar Excel", f"Não foi possível exportar os produtos.\n\n{exc}")

    def _on_excluir_selecionado(self):
        selected = self.tree.selection()
        if not selected: return
        item_id = self.tree.item(selected[0])['values'][0]
        nome = self.tree.item(selected[0])['values'][1]
        
        mensagem = (
            f"Confirma a exclusao do produto '{nome}'?\n\n"
            "Esta acao nao pode ser desfeita."
        )
        resp = messagebox.askyesno("Confirmar exclusao", mensagem)
        if resp:
            self.prod_service.excluir(item_id)
            self._carregar_dados()
            if self.current_produto_id == item_id:
                self._ocultar_form()
