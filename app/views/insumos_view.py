import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Callable, Optional
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from app.models.insumo import Insumo
from app.services.insumo_service import InsumoService
from app.views.historico_preco_insumo_view import HistoricoPrecoInsumoView


# ── Paleta alinhada ao Dashboard ──────────────────────────────────────────────
BG_DEEP = "#12100E"
CARD_BG = "#1E1814"
CARD_BORDER = "#2E2218"
HEADER_BG = "#171310"

ACCENT = "#C8866B"
TEXT_PRIMARY = "#F0E0D0"
TEXT_SECONDARY = "#A08070"
TEXT_MUTED = "#5A4A40"


class InsumosView(ctk.CTkFrame):
    def __init__(self, master, on_estoque_alerta_change: Optional[Callable[[int], None]] = None):
        super().__init__(master, fg_color=BG_DEEP)
        self.service = InsumoService()
        self.current_insumo_id = None
        self.on_estoque_alerta_change = on_estoque_alerta_change

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # === Header (padrão dashboard) ===
        header_frame = ctk.CTkFrame(self, fg_color=HEADER_BG, corner_radius=0, height=56)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(10, 0))
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            header_frame,
            text="Gerenciamento de Insumos",
            text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(family="Roboto", size=20, weight="bold"),
        )
        self.title_label.grid(row=0, column=0, padx=20, sticky="w")

        actions = ctk.CTkFrame(header_frame, fg_color="transparent")
        actions.grid(row=0, column=1, padx=(6, 16), sticky="e")

        self.btn_novo = ctk.CTkButton(
            actions,
            text="+ Novo Insumo",
            command=self._on_novo,
            fg_color=ACCENT,
            hover_color="#A06050",
            text_color="#FFFFFF",
            height=30,
            corner_radius=20,
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        self.btn_novo.grid(row=0, column=0, padx=4)

        self.btn_historico_preco = ctk.CTkButton(
            actions,
            text="Histórico de Preços",
            command=self._on_historico_preco,
            fg_color="#241C18",
            hover_color="#2A201A",
            border_color=CARD_BORDER,
            border_width=1,
            text_color=TEXT_SECONDARY,
            height=30,
            corner_radius=20,
            font=ctk.CTkFont(size=12),
        )
        self.btn_historico_preco.grid(row=0, column=1, padx=4)

        self.btn_exportar = ctk.CTkButton(
            actions,
            text="Exportar Excel",
            command=self._on_exportar_excel,
            fg_color="#241C18",
            hover_color="#2A201A",
            border_color=CARD_BORDER,
            border_width=1,
            text_color=TEXT_SECONDARY,
            height=30,
            corner_radius=20,
            font=ctk.CTkFont(size=12),
        )
        self.btn_exportar.grid(row=0, column=2, padx=4)

        ctk.CTkFrame(self, fg_color=CARD_BORDER, height=1).grid(row=1, column=0, sticky="ew")

        # === Body (Container) ===
        self.body_container = ctk.CTkFrame(self, fg_color="transparent")
        self.body_container.grid(row=2, column=0, padx=14, pady=(10, 12), sticky="nsew")
        
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
        self.title_label.configure(text="Gerenciamento de Insumos")

    def _show_form(self, editando=False):
        self.view_lista.grid_forget()
        self.view_form.grid(row=0, column=0, sticky="nsew")
        self.btn_novo.configure(state="disabled")
        self.title_label.configure(text="Editar Insumo" if editando else "Novo Insumo")

    def _parse_float_campo(self, valor: str, campo: str, obrigatorio: bool = True, minimo: float | None = None) -> float:
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

    def _normalizar_numero_para_float(self, valor: str) -> str:
        numero_txt = valor.strip().replace(" ", "")
        if not numero_txt:
            return ""
        if "," in numero_txt:
            return numero_txt.replace(".", "").replace(",", ".")
        return numero_txt

    def _formatar_numero_br(self, valor: float, casas: int = 2) -> str:
        base = f"{valor:,.{casas}f}"
        return base.replace(",", "X").replace(".", ",").replace("X", ".")

    def _aplicar_mascara_decimal(self, event):
        entry = event.widget
        raw = entry.get().replace(".", ",")
        resultado = []
        tem_virgula = False
        for ch in raw:
            if ch.isdigit():
                resultado.append(ch)
            elif ch == "," and not tem_virgula:
                resultado.append(ch)
                tem_virgula = True
        sanitizado = "".join(resultado)
        if "," in sanitizado:
            inteiro, decimal = sanitizado.split(",", 1)
            sanitizado = f"{inteiro},{decimal[:4]}"
        entry.delete(0, "end")
        entry.insert(0, sanitizado)

    def _aplicar_mascara_moeda(self, event):
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

    def _build_table(self):
        self.view_lista.grid_columnconfigure(0, weight=1)
        self.view_lista.grid_rowconfigure(1, weight=1)

        # Filtros
        filter_frame = ctk.CTkFrame(
            self.view_lista,
            fg_color=CARD_BG,
            corner_radius=12,
            border_width=1,
            border_color=CARD_BORDER,
        )
        filter_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(
            filter_frame,
            text="Filtros",
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=10, weight="bold"),
        ).pack(side="left", padx=(12, 6), pady=10)

        self.entry_busca = ctk.CTkEntry(
            filter_frame,
            placeholder_text="Buscar por nome...",
            width=320,
            fg_color="#241C18",
            border_color=CARD_BORDER,
            text_color=TEXT_PRIMARY,
        )
        self.entry_busca.pack(side="left", padx=10)
        self.entry_busca.bind("<KeyRelease>", lambda e: self._carregar_dados())

        self.combo_categoria_filtro = ctk.CTkComboBox(
            filter_frame,
            values=["Todos", "Ingrediente", "Embalagem", "Gás"],
            command=lambda e: self._carregar_dados(),
            fg_color="#241C18",
            border_color=CARD_BORDER,
            button_color="#2A201A",
            button_hover_color="#2E2218",
            text_color=TEXT_PRIMARY,
            dropdown_fg_color=CARD_BG,
            dropdown_text_color=TEXT_PRIMARY,
            dropdown_hover_color="#2A201A",
            width=180,
        )
        self.combo_categoria_filtro.pack(side="left", padx=10)
        self.combo_categoria_filtro.set("Todos")

        table_frame = ctk.CTkFrame(
            self.view_lista,
            fg_color=CARD_BG,
            corner_radius=12,
            border_width=1,
            border_color=CARD_BORDER,
        )
        table_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Estilo para o Treeview alinhado ao novo padrão visual.
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Insumos.Treeview",
            background="#1A1512",
            foreground=TEXT_PRIMARY,
            rowheight=27,
            fieldbackground="#1A1512",
            borderwidth=0,
        )
        style.map("Insumos.Treeview", background=[("selected", "#3A2A20")])
        style.configure(
            "Insumos.Treeview.Heading",
            background="#241C18",
            foreground=TEXT_SECONDARY,
            relief="flat",
            font=("Roboto", 10, "bold"),
        )
        style.map("Insumos.Treeview.Heading", background=[("active", "#2A201A")])

        columns = ("id", "nome", "categoria", "peso", "preco", "custo", "qtd")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="Insumos.Treeview")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("nome", text="Nome")
        self.tree.heading("categoria", text="Categoria")
        self.tree.heading("peso", text="Peso/Vol")
        self.tree.heading("preco", text="Preço (R$)")
        self.tree.heading("custo", text="Custo/Un (R$)")
        self.tree.heading("qtd", text="Qtd Disp.")
        
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("nome", width=150, anchor="w")
        self.tree.column("categoria", width=100, anchor="center")
        self.tree.column("peso", width=80, anchor="center")
        self.tree.column("preco", width=80, anchor="center")
        self.tree.column("custo", width=90, anchor="center")
        self.tree.column("qtd", width=80, anchor="center")

        # Sprint 6.2: indicação visual de estoque abaixo do mínimo.
        self.tree.tag_configure("estoque_alerta", background="#5B4114", foreground="#FCE8BF")
        self.tree.tag_configure("estoque_critico", background="#5A1E1E", foreground="#FFD4D4")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(fill="both", expand=True, side="left")
        scrollbar.pack(fill="y", side="right")

        # Menu de contexto para editar/excluir
        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Button-3>", self._show_context_menu)
        
        self.context_menu = tk.Menu(self, tearoff=0, bg="#2b2b2b", fg="white")
        self.context_menu.add_command(label="Editar", command=self._on_editar_selecionado)
        self.context_menu.add_command(label="Excluir", command=self._on_excluir_selecionado)

    def _build_form_sidebar(self):
        self.form_frame = ctk.CTkFrame(
            self.view_form,
            fg_color=CARD_BG,
            corner_radius=12,
            border_width=1,
            border_color=CARD_BORDER,
        )
        self.form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        inner_form = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        inner_form.pack(expand=True, padx=20, pady=20)
        inner_form.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            inner_form,
            text="Dados do Insumo",
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=10, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=(0, 8), sticky="w")
        
        ctk.CTkLabel(inner_form, text="Nome", text_color=TEXT_SECONDARY).grid(row=1, column=0, padx=10, pady=(5, 2), sticky="w")
        self.entry_nome = ctk.CTkEntry(
            inner_form,
            width=300,
            placeholder_text="Texto",
            fg_color="#241C18",
            border_color=CARD_BORDER,
            text_color=TEXT_PRIMARY,
        )
        self.entry_nome.grid(row=2, column=0, columnspan=2, padx=10, pady=(0, 8), sticky="ew")

        ctk.CTkLabel(inner_form, text="Categoria", text_color=TEXT_SECONDARY).grid(row=3, column=0, padx=10, pady=(5, 2), sticky="w")
        self.combo_categoria = ctk.CTkComboBox(
            inner_form,
            values=["Ingrediente", "Embalagem", "Gás"],
            width=300,
            fg_color="#241C18",
            border_color=CARD_BORDER,
            button_color="#2A201A",
            button_hover_color="#2E2218",
            text_color=TEXT_PRIMARY,
            dropdown_fg_color=CARD_BG,
            dropdown_text_color=TEXT_PRIMARY,
            dropdown_hover_color="#2A201A",
        )
        self.combo_categoria.grid(row=4, column=0, columnspan=2, padx=10, pady=(0, 8), sticky="ew")

        ctk.CTkLabel(inner_form, text="Peso/Volume Total", text_color=TEXT_SECONDARY).grid(row=5, column=0, padx=10, pady=(5, 2), sticky="w")
        ctk.CTkLabel(inner_form, text="Unidade", text_color=TEXT_SECONDARY).grid(row=5, column=1, padx=10, pady=(5, 2), sticky="w")
        self.entry_peso = ctk.CTkEntry(
            inner_form,
            placeholder_text="Numero",
            fg_color="#241C18",
            border_color=CARD_BORDER,
            text_color=TEXT_PRIMARY,
        )
        self.entry_peso.grid(row=6, column=0, padx=10, pady=(0, 8), sticky="ew")
        self.combo_medida = ctk.CTkComboBox(
            inner_form,
            values=["g", "ml", "unidade"],
            width=120,
            fg_color="#241C18",
            border_color=CARD_BORDER,
            button_color="#2A201A",
            button_hover_color="#2E2218",
            text_color=TEXT_PRIMARY,
            dropdown_fg_color=CARD_BG,
            dropdown_text_color=TEXT_PRIMARY,
            dropdown_hover_color="#2A201A",
        )
        self.combo_medida.grid(row=6, column=1, padx=10, pady=(0, 8), sticky="ew")

        ctk.CTkLabel(inner_form, text="Preco de Compra (R$)", text_color=TEXT_SECONDARY).grid(row=7, column=0, padx=10, pady=(5, 2), sticky="w")
        self.entry_preco = ctk.CTkEntry(
            inner_form,
            width=300,
            placeholder_text="0,00",
            fg_color="#241C18",
            border_color=CARD_BORDER,
            text_color=TEXT_PRIMARY,
        )
        self.entry_preco.grid(row=8, column=0, columnspan=2, padx=10, pady=(0, 8), sticky="ew")
        
        self.lbl_custo_calc = ctk.CTkLabel(
            inner_form,
            text="Custo/Un: R$ 0.00",
            text_color=ACCENT,
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        self.lbl_custo_calc.grid(row=9, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        
        # binds para atualizar o custo_calc
        self.entry_peso.bind("<KeyRelease>", lambda e: (self._aplicar_mascara_decimal(e), self._atualizar_custo_label()))
        self.entry_preco.bind("<KeyRelease>", self._atualizar_custo_label)

        ctk.CTkLabel(inner_form, text="Quantidade Disponivel", text_color=TEXT_SECONDARY).grid(row=10, column=0, padx=10, pady=(5, 2), sticky="w")
        ctk.CTkLabel(inner_form, text="Quantidade Minima", text_color=TEXT_SECONDARY).grid(row=10, column=1, padx=10, pady=(5, 2), sticky="w")
        self.entry_qtd = ctk.CTkEntry(
            inner_form,
            placeholder_text="Numero",
            fg_color="#241C18",
            border_color=CARD_BORDER,
            text_color=TEXT_PRIMARY,
        )
        self.entry_qtd.grid(row=11, column=0, padx=10, pady=(0, 8), sticky="ew")
        self.entry_qtd.bind("<KeyRelease>", self._aplicar_mascara_decimal)
        self.entry_qtd_min = ctk.CTkEntry(
            inner_form,
            placeholder_text="Numero",
            fg_color="#241C18",
            border_color=CARD_BORDER,
            text_color=TEXT_PRIMARY,
        )
        self.entry_qtd_min.grid(row=11, column=1, padx=10, pady=(0, 8), sticky="ew")
        self.entry_qtd_min.bind("<KeyRelease>", self._aplicar_mascara_decimal)

        # Botoões
        frame_btns = ctk.CTkFrame(inner_form, fg_color="transparent")
        frame_btns.grid(row=12, column=0, columnspan=2, padx=10, pady=20, sticky="e")
        
        self.btn_salvar = ctk.CTkButton(
            frame_btns,
            text="Salvar",
            command=self._on_salvar,
            fg_color=ACCENT,
            hover_color="#A06050",
            text_color="#FFFFFF",
            corner_radius=10,
        )
        self.btn_salvar.pack(side="right", padx=5)
        
        self.btn_excluir = ctk.CTkButton(
            frame_btns,
            text="Excluir",
            fg_color="#7A2A2A",
            hover_color="#5C1F1F",
            text_color="#FFD4D4",
            corner_radius=10,
            command=self._excluir_form,
        )
        self.btn_excluir.pack(side="right", padx=5)
        self.btn_excluir.configure(state="disabled")
        
        self.btn_cancelar = ctk.CTkButton(
            frame_btns,
            text="Cancelar",
            fg_color="#2A201A",
            hover_color="#35271E",
            border_color=CARD_BORDER,
            border_width=1,
            text_color=TEXT_SECONDARY,
            corner_radius=10,
            command=self._ocultar_form,
        )
        self.btn_cancelar.pack(side="right", padx=5)

    def _atualizar_custo_label(self, event=None):
        try:
            peso_txt = self._normalizar_numero_para_float(self.entry_peso.get())
            preco_txt = self._normalizar_numero_para_float(self.entry_preco.get())
            peso = float(peso_txt) if peso_txt else 0.0
            preco = float(preco_txt) if preco_txt else 0.0
            if peso > 0:
                custo = preco / peso
                self.lbl_custo_calc.configure(text=f"Custo/Un: R$ {custo:.4f}")
            else:
                self.lbl_custo_calc.configure(text="Custo/Un: R$ 0.00")
        except ValueError:
            self.lbl_custo_calc.configure(text="Custo/Un: Valores inválidos")

    def _carregar_dados(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        nome_busca = self.entry_busca.get()
        categoria_busca = self.combo_categoria_filtro.get()

        insumos = self.service.listar(nome=nome_busca, categoria=categoria_busca)
        
        for insumo in insumos:
            tags = ()
            if insumo.quantidade_disponivel <= 0:
                tags = ("estoque_critico",)
            elif insumo.quantidade_disponivel <= insumo.quantidade_minima:
                tags = ("estoque_alerta",)

            self.tree.insert("", "end", values=(
                insumo.id,
                insumo.nome,
                insumo.categoria,
                f"{insumo.peso_volume_total} {insumo.unidade_medida}",
                self._formatar_numero_br(insumo.preco_compra, 2),
                self._formatar_numero_br(insumo.custo_por_unidade, 4),
                insumo.quantidade_disponivel
            ), tags=tags)

        if callable(self.on_estoque_alerta_change):
            total_alertas = sum(1 for insumo in insumos if insumo.quantidade_disponivel <= insumo.quantidade_minima)
            self.on_estoque_alerta_change(total_alertas)

    def _on_novo(self):
        self.current_insumo_id = None
        self.entry_nome.delete(0, 'end')
        self.combo_categoria.set("Ingrediente")
        self.entry_peso.delete(0, 'end')
        self.combo_medida.set("g")
        self.entry_preco.delete(0, 'end')
        self.entry_qtd.delete(0, 'end')
        self.entry_qtd.insert(0, "0")
        self.entry_qtd_min.delete(0, 'end')
        self.entry_qtd_min.insert(0, "0")
        self.lbl_custo_calc.configure(text="Custo/Un: R$ 0.00")
        self.btn_excluir.configure(state="disabled")
        
        self._show_form(editando=False)

    def _ocultar_form(self):
        self._show_lista()

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
        if not selected:
            return
        item_id = self.tree.item(selected[0])['values'][0]
        insumo = self.service.get_by_id(item_id)
        if insumo:
            self.current_insumo_id = insumo.id
            self.entry_nome.delete(0, 'end')
            self.entry_nome.insert(0, insumo.nome)
            self.combo_categoria.set(insumo.categoria)
            self.entry_peso.delete(0, 'end')
            self.entry_peso.insert(0, str(insumo.peso_volume_total))
            self.combo_medida.set(insumo.unidade_medida)
            self.entry_preco.delete(0, 'end')
            self.entry_preco.insert(0, self._formatar_numero_br(insumo.preco_compra, 2))
            
            self.entry_qtd.delete(0, 'end')
            self.entry_qtd.insert(0, str(insumo.quantidade_disponivel))
            self.entry_qtd_min.delete(0, 'end')
            self.entry_qtd_min.insert(0, str(insumo.quantidade_minima))
            
            self._atualizar_custo_label()
            self.btn_excluir.configure(state="normal")
            self._show_form(editando=True)

    def _excluir_form(self):
        if self.current_insumo_id:
            nome = self.entry_nome.get()
            mensagem = (
                f"Confirma a exclusao do insumo '{nome}'?\n\n"
                "Esta acao nao pode ser desfeita."
            )
            resp = messagebox.askyesno("Confirmar exclusao", mensagem)
            if resp:
                self.service.excluir(self.current_insumo_id)
                self._carregar_dados()
                self._ocultar_form()

    def _on_excluir_selecionado(self):
        selected = self.tree.selection()
        if not selected:
            return
        item_id = self.tree.item(selected[0])['values'][0]
        nome = self.tree.item(selected[0])['values'][1]
        
        mensagem = (
            f"Confirma a exclusao do insumo '{nome}'?\n\n"
            "Esta acao nao pode ser desfeita."
        )
        resp = messagebox.askyesno("Confirmar exclusao", mensagem)
        if resp:
            self.service.excluir(item_id)
            self._carregar_dados()
            if self.current_insumo_id == item_id:
                self._ocultar_form()

    def _on_salvar(self):
        try:
            nome = self.entry_nome.get().strip()
            categoria = self.combo_categoria.get().strip()
            medida = self.combo_medida.get().strip()

            if not nome:
                messagebox.showerror("Erro", "Nome é obrigatório.")
                return

            if categoria not in ["Ingrediente", "Embalagem", "Gás"]:
                messagebox.showerror("Erro", "Categoria inválida.")
                return

            if medida not in ["g", "ml", "unidade"]:
                messagebox.showerror("Erro", "Unidade de medida inválida.")
                return

            peso = self._parse_float_campo(self.entry_peso.get(), "Peso/Volume Total", minimo=0.000001)
            preco = self._parse_float_campo(self.entry_preco.get(), "Preço de Compra", minimo=0.0)
            qtd = self._parse_float_campo(self.entry_qtd.get(), "Quantidade Disponível", obrigatorio=False, minimo=0.0)
            qtd_min = self._parse_float_campo(self.entry_qtd_min.get(), "Quantidade Mínima", obrigatorio=False, minimo=0.0)

            if qtd_min > qtd:
                messagebox.showerror("Erro", "Quantidade mínima não pode ser maior que quantidade disponível.")
                return

            insumo = Insumo(
                id=self.current_insumo_id,
                nome=nome,
                categoria=categoria,
                peso_volume_total=peso,
                unidade_medida=medida,
                preco_compra=preco,
                quantidade_disponivel=qtd,
                quantidade_minima=qtd_min
            )
            
            self.service.salvar(insumo)
            self._ocultar_form()
            self._carregar_dados()
            
        except ValueError as e:
            messagebox.showerror("Erro", str(e))

    def _on_exportar_excel(self):
        nome_busca = self.entry_busca.get().strip()
        categoria_busca = self.combo_categoria_filtro.get().strip()
        insumos = self.service.listar(nome=nome_busca, categoria=categoria_busca)

        if not insumos:
            messagebox.showinfo("Exportar Excel", "Não há insumos para exportar com os filtros atuais.")
            return

        arquivo = filedialog.asksaveasfilename(
            title="Salvar exportação de insumos",
            defaultextension=".xlsx",
            filetypes=[("Planilha Excel", "*.xlsx")],
            initialfile=f"insumos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        )
        if not arquivo:
            return

        try:
            workbook = Workbook()
            planilha = workbook.active
            planilha.title = "Insumos"

            titulo = [
                "ID",
                "Nome",
                "Categoria",
                "Peso/Volume Total",
                "Unidade",
                "Preço de Compra",
                "Custo por Unidade",
                "Quantidade Disponível",
                "Quantidade Mínima",
                "Data da Compra",
            ]
            planilha.append(titulo)

            for celula in planilha[1]:
                celula.font = Font(bold=True, color="FFFFFF")
                celula.fill = PatternFill(fill_type="solid", fgColor="A66850")
                celula.alignment = Alignment(horizontal="center", vertical="center")

            for insumo in insumos:
                data_compra = insumo.data_compra
                if data_compra:
                    try:
                        data_compra = datetime.strptime(data_compra, "%Y-%m-%d").strftime("%d/%m/%Y")
                    except ValueError:
                        pass

                planilha.append([
                    insumo.id,
                    insumo.nome,
                    insumo.categoria,
                    insumo.peso_volume_total,
                    insumo.unidade_medida,
                    insumo.preco_compra,
                    insumo.custo_por_unidade,
                    insumo.quantidade_disponivel,
                    insumo.quantidade_minima,
                    data_compra or "",
                ])

            largura_maxima = {}
            for linha in planilha.iter_rows():
                for celula in linha:
                    valor = "" if celula.value is None else str(celula.value)
                    largura_maxima[celula.column_letter] = max(largura_maxima.get(celula.column_letter, 0), len(valor))

            for coluna, largura in largura_maxima.items():
                planilha.column_dimensions[coluna].width = min(largura + 2, 35)

            planilha.freeze_panes = "A2"
            workbook.save(arquivo)

            messagebox.showinfo("Exportar Excel", f"Exportação concluída com sucesso.\nArquivo salvo em:\n{arquivo}")
        except Exception as exc:
            messagebox.showerror("Exportar Excel", f"Não foi possível exportar os insumos.\n\n{exc}")

    def _on_historico_preco(self):
        HistoricoPrecoInsumoView(self, service=self.service)
