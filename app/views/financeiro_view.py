import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

from app.models.despesa import Despesa
from app.services.despesa_service import DespesaService


class FinanceiroView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.service = DespesaService()
        self.current_despesa_id = None
        self.rendimentos_window = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.title_label = ctk.CTkLabel(header_frame, text="Financeiro - Despesas", font=("Roboto", 20, "bold"))
        self.title_label.pack(side="left", padx=10, pady=10)

        self.btn_exportar = ctk.CTkButton(header_frame, text="Exportar Excel", command=self._on_exportar_excel)
        self.btn_exportar.pack(side="right", padx=(0, 10), pady=10)

        self.btn_rendimentos = ctk.CTkButton(header_frame, text="Rendimentos", command=self._abrir_rendimentos)
        self.btn_rendimentos.pack(side="right", padx=(0, 10), pady=10)

        self.btn_novo = ctk.CTkButton(header_frame, text="Nova Despesa", command=self._on_novo)
        self.btn_novo.pack(side="right", padx=10, pady=10)

        self.body_container = ctk.CTkFrame(self, fg_color="transparent")
        self.body_container.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.body_container.grid_columnconfigure(0, weight=1)
        self.body_container.grid_rowconfigure(0, weight=1)

        self.view_lista = ctk.CTkFrame(self.body_container, fg_color="transparent")
        self.view_form = ctk.CTkFrame(self.body_container, fg_color="transparent")

        self._build_table()
        self._build_form()

        self._show_lista()
        self._carregar_dados_seguro()

    def _show_lista(self):
        self.view_form.grid_forget()
        self.view_lista.grid(row=0, column=0, sticky="nsew")
        self.btn_novo.configure(state="normal")
        self.title_label.configure(text="Financeiro - Despesas")

    def _show_form(self, editando: bool = False):
        self.view_lista.grid_forget()
        self.view_form.grid(row=0, column=0, sticky="nsew")
        self.btn_novo.configure(state="disabled")
        self.title_label.configure(text="Editar Despesa" if editando else "Nova Despesa")

    def _build_table(self):
        self.view_lista.grid_columnconfigure(0, weight=1)
        self.view_lista.grid_rowconfigure(1, weight=1)
        self.view_lista.grid_rowconfigure(2, weight=0)

        filtro_frame = ctk.CTkFrame(self.view_lista)
        filtro_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))

        ctk.CTkLabel(filtro_frame, text="Período:").pack(side="left", padx=(10, 4), pady=10)

        self.filtro_data_inicio = ctk.CTkEntry(filtro_frame, width=110, placeholder_text="DD/MM/AAAA")
        self.filtro_data_inicio.pack(side="left", padx=4, pady=10)
        self.filtro_data_inicio.bind("<KeyRelease>", self._aplicar_mascara_data)

        ctk.CTkLabel(filtro_frame, text="até").pack(side="left", padx=4, pady=10)

        self.filtro_data_fim = ctk.CTkEntry(filtro_frame, width=110, placeholder_text="DD/MM/AAAA")
        self.filtro_data_fim.pack(side="left", padx=4, pady=10)
        self.filtro_data_fim.bind("<KeyRelease>", self._aplicar_mascara_data)

        ctk.CTkLabel(filtro_frame, text="Categoria:").pack(side="left", padx=(14, 4), pady=10)
        self.filtro_categoria = ctk.CTkOptionMenu(filtro_frame, values=["Todos", "Insumos", "Investimentos", "Outros"])
        self.filtro_categoria.pack(side="left", padx=4, pady=10)
        self.filtro_categoria.set("Todos")

        ctk.CTkLabel(filtro_frame, text="Status:").pack(side="left", padx=(14, 4), pady=10)
        self.filtro_status = ctk.CTkOptionMenu(filtro_frame, values=["Todos", "Pendente", "Pago"])
        self.filtro_status.pack(side="left", padx=4, pady=10)
        self.filtro_status.set("Todos")

        self.btn_filtrar = ctk.CTkButton(filtro_frame, text="Buscar", width=90, command=self._carregar_dados_seguro)
        self.btn_filtrar.pack(side="left", padx=(14, 4), pady=10)

        self.btn_limpar_filtros = ctk.CTkButton(
            filtro_frame,
            text="Limpar",
            width=90,
            fg_color="gray",
            hover_color="#555555",
            command=self._limpar_filtros,
        )
        self.btn_limpar_filtros.pack(side="left", padx=4, pady=10)

        table_frame = ctk.CTkFrame(self.view_lista)
        table_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2b2b2b", foreground="white", rowheight=25, fieldbackground="#2b2b2b", borderwidth=0)
        style.map("Treeview", background=[("selected", "#1f538d")])
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat")

        columns = ("id", "data", "categoria", "valor", "status", "responsavel")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        self.tree.heading("id", text="ID")
        self.tree.heading("data", text="Data")
        self.tree.heading("categoria", text="Categoria")
        self.tree.heading("valor", text="Valor")
        self.tree.heading("status", text="Status")
        self.tree.heading("responsavel", text="Responsável")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("data", width=100, anchor="center")
        self.tree.column("categoria", width=130, anchor="center")
        self.tree.column("valor", width=100, anchor="e")
        self.tree.column("status", width=100, anchor="center")
        self.tree.column("responsavel", width=160, anchor="w")

        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.bind("<Double-1>", self._on_editar_selecionado)

        totalizador_frame = ctk.CTkFrame(self.view_lista)
        totalizador_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        totalizador_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.lbl_total_insumos = ctk.CTkLabel(totalizador_frame, text="Insumos: R$ 0,00", anchor="w")
        self.lbl_total_insumos.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.lbl_total_investimentos = ctk.CTkLabel(totalizador_frame, text="Investimentos: R$ 0,00", anchor="w")
        self.lbl_total_investimentos.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        self.lbl_total_outros = ctk.CTkLabel(totalizador_frame, text="Outros: R$ 0,00", anchor="w")
        self.lbl_total_outros.grid(row=0, column=2, padx=10, pady=10, sticky="w")

        self.lbl_total_geral = ctk.CTkLabel(totalizador_frame, text="Total Geral: R$ 0,00", font=("Roboto", 14, "bold"), anchor="w")
        self.lbl_total_geral.grid(row=0, column=3, padx=10, pady=10, sticky="w")

    def _build_form(self):
        form_frame = ctk.CTkFrame(self.view_form)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        form_frame.grid_columnconfigure((1, 3), weight=1)

        ctk.CTkLabel(form_frame, text="Data da Despesa*").grid(row=0, column=0, padx=10, pady=8, sticky="e")
        self.entry_data = ctk.CTkEntry(form_frame, placeholder_text="DD/MM/AAAA")
        self.entry_data.grid(row=0, column=1, padx=10, pady=8, sticky="ew")
        self.entry_data.bind("<KeyRelease>", self._aplicar_mascara_data)

        ctk.CTkLabel(form_frame, text="Valor (R$)*").grid(row=0, column=2, padx=10, pady=8, sticky="e")
        self.entry_valor = ctk.CTkEntry(form_frame, placeholder_text="0,00")
        self.entry_valor.grid(row=0, column=3, padx=10, pady=8, sticky="ew")
        self.entry_valor.bind("<KeyRelease>", self._aplicar_mascara_moeda)

        ctk.CTkLabel(form_frame, text="Categoria*").grid(row=1, column=0, padx=10, pady=8, sticky="e")
        self.cb_categoria = ctk.CTkComboBox(form_frame, values=["Insumos", "Investimentos", "Outros"])
        self.cb_categoria.grid(row=1, column=1, padx=10, pady=8, sticky="ew")

        ctk.CTkLabel(form_frame, text="Status*").grid(row=1, column=2, padx=10, pady=8, sticky="e")
        self.cb_status = ctk.CTkComboBox(form_frame, values=["Pendente", "Pago"])
        self.cb_status.grid(row=1, column=3, padx=10, pady=8, sticky="ew")

        ctk.CTkLabel(form_frame, text="Forma de Pagamento").grid(row=2, column=0, padx=10, pady=8, sticky="e")
        self.cb_forma_pagamento = ctk.CTkComboBox(
            form_frame,
            values=["Pix", "Dinheiro", "Cartão Crédito", "Cartão Débito", "Boleto", "Transferência"],
        )
        self.cb_forma_pagamento.grid(row=2, column=1, padx=10, pady=8, sticky="ew")

        ctk.CTkLabel(form_frame, text="Data Pagamento Final").grid(row=2, column=2, padx=10, pady=8, sticky="e")
        self.entry_data_pagamento = ctk.CTkEntry(form_frame, placeholder_text="DD/MM/AAAA")
        self.entry_data_pagamento.grid(row=2, column=3, padx=10, pady=8, sticky="ew")
        self.entry_data_pagamento.bind("<KeyRelease>", self._aplicar_mascara_data)

        ctk.CTkLabel(form_frame, text="Responsável").grid(row=3, column=0, padx=10, pady=8, sticky="e")
        self.entry_responsavel = ctk.CTkEntry(form_frame, placeholder_text="Texto")
        self.entry_responsavel.grid(row=3, column=1, columnspan=3, padx=10, pady=8, sticky="ew")

        ctk.CTkLabel(form_frame, text="Descrição").grid(row=4, column=0, padx=10, pady=8, sticky="ne")
        self.text_descricao = ctk.CTkTextbox(form_frame, height=120)
        self.text_descricao.grid(row=4, column=1, columnspan=3, padx=10, pady=8, sticky="ew")

        frame_acoes = ctk.CTkFrame(form_frame, fg_color="transparent")
        frame_acoes.grid(row=5, column=0, columnspan=4, padx=10, pady=16, sticky="e")

        self.btn_salvar = ctk.CTkButton(frame_acoes, text="Salvar", command=self._on_salvar)
        self.btn_salvar.pack(side="right", padx=5)

        self.btn_excluir = ctk.CTkButton(frame_acoes, text="Excluir", fg_color="#c93434", hover_color="#942626", command=self._on_excluir)
        self.btn_excluir.pack(side="right", padx=5)

        self.btn_cancelar = ctk.CTkButton(frame_acoes, text="Cancelar", fg_color="gray", hover_color="#555555", command=self._show_lista)
        self.btn_cancelar.pack(side="right", padx=5)

        self._limpar_form()

    def _carregar_dados(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        data_inicio = self._validar_data(self.filtro_data_inicio.get().strip(), "Data inicial")
        data_fim = self._validar_data(self.filtro_data_fim.get().strip(), "Data final")

        if data_inicio and data_fim:
            inicio_dt = datetime.strptime(data_inicio, "%d/%m/%Y")
            fim_dt = datetime.strptime(data_fim, "%d/%m/%Y")
            if inicio_dt > fim_dt:
                raise ValueError("A data inicial não pode ser maior que a data final.")

        categoria = self.filtro_categoria.get().strip() if hasattr(self, "filtro_categoria") else "Todos"
        status = self.filtro_status.get().strip() if hasattr(self, "filtro_status") else "Todos"

        despesas = self.service.listar(
            data_inicio=data_inicio,
            data_fim=data_fim,
            categoria=categoria,
            status=status,
        )
        for despesa in despesas:
            self.tree.insert(
                "",
                "end",
                values=(
                    despesa.id,
                    despesa.data,
                    despesa.categoria,
                    f"R$ {self._formatar_moeda_ui(despesa.valor)}",
                    despesa.status,
                    despesa.responsavel or "",
                ),
            )

        totais = self.service.total_por_categoria(
            data_inicio=data_inicio,
            data_fim=data_fim,
            status=status,
            categoria=categoria,
        )
        self._atualizar_totalizadores(totais)

    def _atualizar_totalizadores(self, totais: dict[str, float]):
        total_insumos = float(totais.get("Insumos", 0.0) or 0.0)
        total_investimentos = float(totais.get("Investimentos", 0.0) or 0.0)
        total_outros = float(totais.get("Outros", 0.0) or 0.0)
        total_geral = total_insumos + total_investimentos + total_outros

        self.lbl_total_insumos.configure(text=f"Insumos: R$ {self._formatar_moeda_ui(total_insumos)}")
        self.lbl_total_investimentos.configure(text=f"Investimentos: R$ {self._formatar_moeda_ui(total_investimentos)}")
        self.lbl_total_outros.configure(text=f"Outros: R$ {self._formatar_moeda_ui(total_outros)}")
        self.lbl_total_geral.configure(text=f"Total Geral: R$ {self._formatar_moeda_ui(total_geral)}")

    def _carregar_dados_seguro(self):
        try:
            self._carregar_dados()
        except ValueError as exc:
            messagebox.showerror("Erro", str(exc))

    def _limpar_filtros(self):
        self.filtro_data_inicio.delete(0, "end")
        self.filtro_data_fim.delete(0, "end")
        self.filtro_categoria.set("Todos")
        self.filtro_status.set("Todos")
        self._carregar_dados_seguro()

    def _on_exportar_excel(self):
        try:
            data_inicio = self._validar_data(self.filtro_data_inicio.get().strip(), "Data inicial")
            data_fim = self._validar_data(self.filtro_data_fim.get().strip(), "Data final")

            if data_inicio and data_fim:
                inicio_dt = datetime.strptime(data_inicio, "%d/%m/%Y")
                fim_dt = datetime.strptime(data_fim, "%d/%m/%Y")
                if inicio_dt > fim_dt:
                    raise ValueError("A data inicial não pode ser maior que a data final.")

            categoria = self.filtro_categoria.get().strip()
            status = self.filtro_status.get().strip()

            despesas = self.service.listar(
                data_inicio=data_inicio,
                data_fim=data_fim,
                categoria=categoria,
                status=status,
            )
            if not despesas:
                messagebox.showinfo("Exportar Excel", "Não há despesas para exportar com os filtros atuais.")
                return

            totais = self.service.total_por_categoria(
                data_inicio=data_inicio,
                data_fim=data_fim,
                status=status,
                categoria=categoria,
            )

            arquivo = filedialog.asksaveasfilename(
                title="Salvar exportação de despesas",
                defaultextension=".xlsx",
                filetypes=[("Planilha Excel", "*.xlsx")],
                initialfile=f"despesas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            )
            if not arquivo:
                return

            workbook = Workbook()
            sheet_despesas = workbook.active
            sheet_despesas.title = "Despesas"

            cabecalho_despesas = [
                "ID",
                "Data",
                "Categoria",
                "Valor (R$)",
                "Status",
                "Forma de Pagamento",
                "Responsável",
                "Descrição",
            ]
            sheet_despesas.append(cabecalho_despesas)

            for celula in sheet_despesas[1]:
                celula.font = Font(bold=True, color="FFFFFF")
                celula.fill = PatternFill(fill_type="solid", fgColor="A66850")
                celula.alignment = Alignment(horizontal="center", vertical="center")

            for despesa in despesas:
                sheet_despesas.append([
                    despesa.id,
                    despesa.data,
                    despesa.categoria,
                    despesa.valor,
                    despesa.status,
                    despesa.forma_pagamento or "",
                    despesa.responsavel or "",
                    despesa.descricao or "",
                ])

            sheet_totais = workbook.create_sheet("Totais Categoria")
            cabecalho_totais = ["Categoria", "Total (R$)"]
            sheet_totais.append(cabecalho_totais)

            for celula in sheet_totais[1]:
                celula.font = Font(bold=True, color="FFFFFF")
                celula.fill = PatternFill(fill_type="solid", fgColor="565b5e")
                celula.alignment = Alignment(horizontal="center", vertical="center")

            total_insumos = float(totais.get("Insumos", 0.0) or 0.0)
            total_investimentos = float(totais.get("Investimentos", 0.0) or 0.0)
            total_outros = float(totais.get("Outros", 0.0) or 0.0)
            total_geral = total_insumos + total_investimentos + total_outros

            sheet_totais.append(["Insumos", total_insumos])
            sheet_totais.append(["Investimentos", total_investimentos])
            sheet_totais.append(["Outros", total_outros])
            sheet_totais.append(["Total Geral", total_geral])

            for planilha in (sheet_despesas, sheet_totais):
                larguras = {}
                for linha in planilha.iter_rows():
                    for celula in linha:
                        valor = "" if celula.value is None else str(celula.value)
                        larguras[celula.column_letter] = max(larguras.get(celula.column_letter, 0), len(valor))

                for coluna, largura in larguras.items():
                    planilha.column_dimensions[coluna].width = min(largura + 2, 45)

                planilha.freeze_panes = "A2"

            workbook.save(arquivo)
            messagebox.showinfo("Exportar Excel", f"Exportação concluída com sucesso.\nArquivo salvo em:\n{arquivo}")
        except ValueError as exc:
            messagebox.showerror("Erro", str(exc))
        except Exception as exc:
            messagebox.showerror("Exportar Excel", f"Não foi possível exportar as despesas.\n\n{exc}")

    def _limpar_form(self):
        self.current_despesa_id = None
        self.entry_data.delete(0, "end")
        self.entry_data.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.entry_valor.delete(0, "end")
        self.entry_valor.insert(0, "0,00")
        self.cb_categoria.set("Outros")
        self.cb_status.set("Pendente")
        self.cb_forma_pagamento.set("Pix")
        self.entry_data_pagamento.delete(0, "end")
        self.entry_responsavel.delete(0, "end")
        self.text_descricao.delete("0.0", "end")
        self.btn_excluir.configure(state="disabled")

    def _on_novo(self):
        self._limpar_form()
        self._show_form(editando=False)

    def _abrir_rendimentos(self):
        if self.rendimentos_window and self.rendimentos_window.winfo_exists():
            self.rendimentos_window.focus()
            return

        from app.views.rendimentos_view import RendimentosView

        self.rendimentos_window = RendimentosView(self)

    def _on_editar_selecionado(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return

        despesa_id = int(self.tree.item(selected[0])["values"][0])
        despesa = self.service.get_by_id(despesa_id)
        if not despesa:
            return

        self._limpar_form()
        self.current_despesa_id = despesa.id

        self.entry_data.delete(0, "end")
        self.entry_data.insert(0, despesa.data or "")

        self.entry_valor.delete(0, "end")
        self.entry_valor.insert(0, self._formatar_moeda_ui(despesa.valor or 0.0))

        self.cb_categoria.set(despesa.categoria or "Outros")
        self.cb_status.set(despesa.status or "Pendente")

        forma = despesa.forma_pagamento or "Pix"
        self.cb_forma_pagamento.set(forma)

        self.entry_data_pagamento.delete(0, "end")
        self.entry_data_pagamento.insert(0, despesa.data_pagamento_final or "")

        self.entry_responsavel.delete(0, "end")
        self.entry_responsavel.insert(0, despesa.responsavel or "")

        self.text_descricao.delete("0.0", "end")
        self.text_descricao.insert("0.0", despesa.descricao or "")

        self.btn_excluir.configure(state="normal")
        self._show_form(editando=True)

    def _on_salvar(self):
        try:
            data = self._validar_data(self.entry_data.get().strip(), "Data da Despesa", obrigatorio=True)
            valor = self._parse_float_campo(self.entry_valor.get().strip(), "Valor", obrigatorio=True, minimo=0.01)

            categoria = self.cb_categoria.get().strip()
            if categoria not in ["Insumos", "Investimentos", "Outros"]:
                raise ValueError("Categoria inválida.")

            status = self.cb_status.get().strip()
            if status not in ["Pendente", "Pago"]:
                raise ValueError("Status inválido.")

            forma_pagamento = self.cb_forma_pagamento.get().strip()
            data_pagamento = self._validar_data(self.entry_data_pagamento.get().strip(), "Data do Pagamento Final")

            if status == "Pago" and not data_pagamento:
                raise ValueError("Para despesas pagas, informe a data do pagamento final.")

            despesa = Despesa(
                id=self.current_despesa_id,
                data=data,
                valor=valor,
                descricao=self.text_descricao.get("0.0", "end").strip() or None,
                categoria=categoria,
                responsavel=self.entry_responsavel.get().strip() or None,
                status=status,
                forma_pagamento=forma_pagamento or None,
                data_pagamento_final=data_pagamento or None,
            )

            self.service.salvar(despesa)
            self._carregar_dados_seguro()
            self._show_lista()

        except ValueError as exc:
            messagebox.showerror("Erro", str(exc))

    def _on_excluir(self):
        if not self.current_despesa_id:
            return

        descricao = self.text_descricao.get("0.0", "end").strip() or f"ID {self.current_despesa_id}"
        mensagem = (
            f"Confirma a exclusao da despesa '{descricao}'?\n\n"
            "Esta acao nao pode ser desfeita."
        )
        if messagebox.askyesno("Confirmar exclusao", mensagem):
            self.service.excluir(self.current_despesa_id)
            self._carregar_dados_seguro()
            self._show_lista()

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

        formatado = "/".join(partes)
        entry.delete(0, "end")
        entry.insert(0, formatado)

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

    def _validar_data(self, valor: str, campo: str, obrigatorio: bool = False) -> str:
        if not valor:
            if obrigatorio:
                raise ValueError(f"O campo {campo} é obrigatório.")
            return ""

        try:
            datetime.strptime(valor, "%d/%m/%Y")
        except ValueError as exc:
            raise ValueError(f"O campo {campo} deve estar no formato DD/MM/AAAA.") from exc

        return valor

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

    def _normalizar_numero_para_float(self, valor: str) -> str:
        numero_txt = valor.strip().replace(" ", "")
        if not numero_txt:
            return ""

        if "," in numero_txt:
            return numero_txt.replace(".", "").replace(",", ".")

        return numero_txt

    def _formatar_moeda_ui(self, valor: float) -> str:
        return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
