import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from app.core.formatters import fmt_moeda
from app.models.cliente import Cliente
from app.services.cliente_service import ClienteService
from app.ui.theme import (
    ACCENT,
    BG_DEEP,
    CARD_BG,
    CARD_BORDER,
    FIELD_BG,
    HEADER_BG,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    _btn_accent,
    _btn_danger,
    _btn_ghost,
    _card,
    _entry,
    _sep,
    _treeview_style,
)

class ClientesView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=BG_DEEP, **kwargs)
        self.service = ClienteService()
        self.current_id = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_topbar()
        self._build_filters()
        self._build_content()
        self._carregar_dados()

    def refresh(self):
        self._carregar_dados()

    def _build_topbar(self):
        bar = ctk.CTkFrame(self, fg_color=HEADER_BG, corner_radius=0, height=56)
        bar.grid(row=0, column=0, sticky="ew", pady=(10, 0))
        bar.grid_propagate(False)
        bar.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            bar, text="Gestão de Clientes",
            text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(family="Roboto", size=20, weight="bold"),
        ).grid(row=0, column=0, padx=20, sticky="w")

        actions = ctk.CTkFrame(bar, fg_color="transparent")
        actions.grid(row=0, column=1, padx=(6, 16), sticky="e")
        
        self.btn_novo = _btn_accent(actions, "+ Novo Cliente", self._on_novo)
        self.btn_novo.grid(row=0, column=0, padx=4)

    def _build_filters(self):
        fc = _card(self)
        fc.grid(row=1, column=0, padx=16, pady=(10, 0), sticky="ew")
        fc.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(fc, text="FILTROS", text_color=TEXT_MUTED,
                     font=ctk.CTkFont(size=10, weight="bold")
                     ).grid(row=0, column=0, padx=16, pady=(12, 6), sticky="w")

        ctrl = ctk.CTkFrame(fc, fg_color="transparent")
        ctrl.grid(row=1, column=0, padx=16, pady=(0, 12), sticky="ew")

        self.entry_busca = _entry(ctrl, placeholder_text="Buscar por nome...", width=400)
        self.entry_busca.pack(side="left", padx=(0, 10))
        self.entry_busca.bind("<KeyRelease>", lambda e: self._carregar_dados())

        _btn_accent(ctrl, "Buscar", self._carregar_dados, width=100).pack(side="left")

    def _build_content(self):
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=2, column=0, sticky="nsew", padx=14, pady=12)
        self.content.grid_columnconfigure(0, weight=3) # Tabela
        self.content.grid_columnconfigure(1, weight=1) # Form
        self.content.grid_rowconfigure(0, weight=1)

        # ── Tabela ────────────────────────────────────────────────────────
        tf = _card(self.content)
        tf.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        tf.grid_columnconfigure(0, weight=1); tf.grid_rowconfigure(0, weight=1)

        style = _treeview_style("Clientes", rowheight=32)
        cols = ("id", "nome", "contato", "pedidos", "total")
        self.tree = ttk.Treeview(tf, columns=cols, show="headings", style=style)
        
        for col, txt, w, anc in [
            ("id",      "ID",       50,  "center"),
            ("nome",    "Nome",     250, "w"),
            ("contato", "Contato",  180, "w"),
            ("pedidos", "Pedidos",  80,  "center"),
            ("total",   "Total Gasto", 120, "e"),
        ]:
            self.tree.heading(col, text=txt)
            self.tree.column(col, width=w, anchor=anc)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        sb = ttk.Scrollbar(tf, orient="vertical", command=self.tree.yview)
        sb.grid(row=0, column=1, sticky="ns", pady=2)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.bind("<<TreeviewSelect>>", self._on_selected)
        self.tree.bind("<Double-1>", lambda e: self._ver_pedidos())

        # ── Formulário ────────────────────────────────────────────────────
        self.form = _card(self.content)
        self.form.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        self.form.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.form, text="DETALHES DO CLIENTE", text_color=TEXT_MUTED,
                     font=ctk.CTkFont(size=10, weight="bold")
                     ).grid(row=0, column=0, padx=16, pady=(12, 8), sticky="w")

        # Campos
        self.entry_nome = self._add_field("Nome*", 1)
        self.entry_contato = self._add_field("Contato", 3)

        # Resumo Financeiro no Form
        self.lbl_resumo = ctk.CTkLabel(
            self.form, text="", justify="left", text_color=TEXT_SECONDARY,
            font=ctk.CTkFont(size=11)
        )
        self.lbl_resumo.grid(row=5, column=0, padx=16, pady=(15, 5), sticky="w")

        # Ações
        self.btn_frame = ctk.CTkFrame(self.form, fg_color="transparent")
        self.btn_frame.grid(row=6, column=0, padx=16, pady=20, sticky="ew")
        self.btn_frame.grid_columnconfigure((0, 1), weight=1)

        self.btn_salvar = _btn_accent(self.btn_frame, "Salvar", self._on_save)
        self.btn_salvar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=5)

        self.btn_pedidos = _btn_ghost(self.btn_frame, "Ver Pedidos", self._ver_pedidos)
        self.btn_pedidos.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)

        self.btn_excluir = _btn_danger(self.btn_frame, "Excluir", self._on_delete)
        self.btn_excluir.grid(row=2, column=0, columnspan=2, sticky="ew", pady=5)
        self.btn_excluir.configure(state="disabled")

        ctk.CTkLabel(self.form, text="* Campos obrigatórios", text_color=TEXT_MUTED,
                     font=ctk.CTkFont(size=10)).grid(row=7, column=0, padx=16, pady=(0, 5), sticky="w")

    def _add_field(self, label, row):
        ctk.CTkLabel(self.form, text=label, text_color=TEXT_SECONDARY,
                     font=ctk.CTkFont(size=12)).grid(row=row, column=0, padx=16, pady=(5, 0), sticky="w")
        e = _entry(self.form)
        e.grid(row=row+1, column=0, padx=16, pady=(2, 10), sticky="ew")
        return e

    def _carregar_dados(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        clientes = self.service.listar(nome=self.entry_busca.get())
        for c in clientes:
            resumo = self.service.get_resumo_cliente(c.id)
            self.tree.insert("", "end", values=(
                c.id, c.nome, c.contato or "",
                resumo["total_pedidos"],
                f"R$ {fmt_moeda(resumo['total_gasto'])}"
            ))

    def _on_selected(self, _=None):
        sel = self.tree.selection()
        if not sel: return
        cid = int(self.tree.item(sel[0])["values"][0])
        clientes = self.service.listar()
        cliente = next((c for c in clientes if c.id == cid), None)
        
        if cliente:
            self.current_id = cliente.id
            self.entry_nome.delete(0, "end"); self.entry_nome.insert(0, cliente.nome)
            self.entry_contato.delete(0, "end"); self.entry_contato.insert(0, cliente.contato or "")
            self.btn_excluir.configure(state="normal")
            
            resumo = self.service.get_resumo_cliente(cid)
            texto_resumo = (
                f"Total de Pedidos: {resumo['total_pedidos']}\n"
                f"Total Gasto: R$ {fmt_moeda(resumo['total_gasto'])}\n"
                f"Último Pedido: {resumo['ultimo_pedido'] or '—'}"
            )
            self.lbl_resumo.configure(text=texto_resumo)

    def _on_novo(self):
        self.current_id = None
        self.entry_nome.delete(0, "end")
        self.entry_contato.delete(0, "end")
        self.lbl_resumo.configure(text="")
        self.btn_excluir.configure(state="disabled")
        self.entry_nome.focus_set()

    def _on_save(self):
        nome = self.entry_nome.get().strip()
        if not nome:
            messagebox.showerror("Erro", "O campo Nome é obrigatório."); return
            
        try:
            self.service.salvar(Cliente(
                id=self.current_id,
                nome=nome,
                contato=self.entry_contato.get().strip() or None
            ))
            self._carregar_dados()
            self._on_novo()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _on_delete(self):
        if not self.current_id: return
        if messagebox.askyesno("Confirmar", "Deseja realmente excluir este cliente?"):
            try:
                self.service.excluir(self.current_id)
                self._carregar_dados()
                self._on_novo()
            except ValueError as e:
                messagebox.showwarning("Bloqueio de Exclusão", str(e))
            except Exception as e:
                messagebox.showerror("Erro", str(e))

    def _ver_pedidos(self):
        if not self.current_id:
            messagebox.showwarning("Aviso", "Selecione um cliente para ver os pedidos."); return
            
        nome = self.entry_nome.get().strip()
        try:
            main_window = self.winfo_toplevel()
            if hasattr(main_window, "show_pedidos_view"):
                # Filtra a view de pedidos pelo nome do cliente
                main_window.show_pedidos_view(cliente_nome=nome)
        except Exception as e:
            messagebox.showerror("Erro de Navegação", f"Não foi possível abrir os pedidos: {e}")
