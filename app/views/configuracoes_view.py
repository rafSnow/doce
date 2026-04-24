import customtkinter as ctk
import tkinter as tk
import json
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

from app.services.configuracao_service import ConfiguracaoService
from app.services.performance_service import PerformanceService
from app.services.recibo_service import ReciboService
from app.services.auditoria_service import AuditoriaService
from app.core.formatters import fmt_data
from app.ui.theme import (
    ACCENT,
    BG_DEEP,
    CARD_BG,
    CARD_BORDER,
    COLOR_GREEN,
    COLOR_ORANGE,
    COLOR_RED,
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
    _optmenu,
    _sep as _separator,
    _treeview_style,
)


def _mask_date(event):
    e = event.widget
    d = "".join(c for c in e.get() if c.isdigit())[:8]
    parts = []
    if len(d) >= 2:  parts.append(d[:2])
    elif d:           parts.append(d)
    if len(d) >= 4:  parts.append(d[2:4])
    elif len(d) > 2: parts.append(d[2:])
    if len(d) > 4:   parts.append(d[4:])
    e.delete(0, "end"); e.insert(0, "/".join(parts))


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  PAINEL GERAL DE CONFIGURAÇÕES                                              ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
class GeralPanel(ctk.CTkFrame):
    def __init__(self, master, nome_atual: str = "", on_nome_alterado=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.service              = ConfiguracaoService()
        self.performance_service  = PerformanceService()
        self.recibo_service       = ReciboService()
        self.on_nome_alterado     = on_nome_alterado

        self.grid_columnconfigure(0, weight=1)
        self._build_body(nome_atual)

    def _build_body(self, nome_atual: str):
        # ── Identidade ────────────────────────────────────────────────────
        card_nome = _card(self)
        card_nome.grid(row=0, column=0, sticky="ew", padx=6, pady=(0, 10))
        card_nome.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(card_nome, text="IDENTIDADE", text_color=TEXT_MUTED,
                     font=ctk.CTkFont(size=10, weight="bold"),
                     ).grid(row=0, column=0, columnspan=2, padx=16, pady=(12, 8), sticky="w")

        ctk.CTkLabel(card_nome, text="Nome do estabelecimento*",
                     text_color=TEXT_SECONDARY, font=ctk.CTkFont(size=12),
                     ).grid(row=1, column=0, padx=12, pady=(2, 10), sticky="e")

        self.entry_nome = ctk.CTkEntry(
            card_nome, placeholder_text="Ex: Doce da Maria",
            fg_color=FIELD_BG, border_color=CARD_BORDER,
            text_color=TEXT_PRIMARY, height=32,
        )
        self.entry_nome.grid(row=1, column=1, padx=(0, 14), pady=(2, 10), sticky="ew")

        valor_inicial = (nome_atual.strip() if nome_atual and nome_atual.strip()
                         else self.service.get_nome_estabelecimento())
        self.entry_nome.insert(0, valor_inicial)

        ctk.CTkLabel(
            card_nome,
            text="Esse nome será exibido no menu lateral e no título da janela.",
            text_color=TEXT_MUTED, font=ctk.CTkFont(size=11),
            justify="left", anchor="w",
        ).grid(row=2, column=0, columnspan=2, padx=16, pady=(0, 5), sticky="ew")

        ctk.CTkLabel(card_nome, text="* Campos obrigatórios", text_color=TEXT_MUTED,
                     font=ctk.CTkFont(size=10)).grid(row=3, column=0, columnspan=2, padx=16, pady=(0, 5), sticky="w")

        # ── Preferências (Avançado) ────────────────────────────────────────
        card_pref = _card(self)
        card_pref.grid(row=1, column=0, sticky="ew", padx=6, pady=(0, 10))
        card_pref.grid_columnconfigure((1, 3), weight=1)

        ctk.CTkLabel(card_pref, text="PREFERÊNCIAS", text_color=TEXT_MUTED,
                     font=ctk.CTkFont(size=10, weight="bold"),
                     ).grid(row=0, column=0, columnspan=4, padx=16, pady=(12, 8), sticky="w")

        ctk.CTkLabel(card_pref, text="Markup padrão (%)",
                     text_color=TEXT_SECONDARY, font=ctk.CTkFont(size=12),
                     ).grid(row=1, column=0, padx=(12, 4), pady=(2, 10), sticky="e")
        self.entry_markup = ctk.CTkEntry(card_pref, fg_color=FIELD_BG, border_color=CARD_BORDER, height=32)
        self.entry_markup.grid(row=1, column=1, padx=4, pady=(2, 10), sticky="ew")
        self.entry_markup.insert(0, str(self.service.get_markup_padrao()))

        ctk.CTkLabel(card_pref, text="Responsável padrão",
                     text_color=TEXT_SECONDARY, font=ctk.CTkFont(size=12),
                     ).grid(row=1, column=2, padx=(12, 4), pady=(2, 10), sticky="e")
        self.entry_resp = ctk.CTkEntry(card_pref, fg_color=FIELD_BG, border_color=CARD_BORDER, height=32)
        self.entry_resp.grid(row=1, column=3, padx=(4, 14), pady=(2, 10), sticky="ew")
        self.entry_resp.insert(0, self.service.get_responsavel_padrao())

        # ── Backup ────────────────────────────────────────────────────────
        card_backup = _card(self)
        card_backup.grid(row=2, column=0, sticky="ew", padx=6, pady=(0, 10))
        card_backup.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card_backup, text="BACKUP", text_color=TEXT_MUTED,
                     font=ctk.CTkFont(size=10, weight="bold"),
                     ).grid(row=0, column=0, padx=16, pady=(12, 8), sticky="w")

        row_backup = ctk.CTkFrame(card_backup, fg_color="transparent")
        row_backup.grid(row=1, column=0, padx=16, pady=(0, 8), sticky="ew")
        row_backup.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(row_backup, text="Backup do banco de dados",
                     text_color=TEXT_SECONDARY).grid(row=0, column=0, sticky="w")
        
        btn_box = ctk.CTkFrame(row_backup, fg_color="transparent")
        btn_box.grid(row=0, column=1, sticky="e")

        self.btn_backup = _btn_ghost(btn_box, "Fazer backup", self._on_backup)
        self.btn_backup.pack(side="left", padx=4)

        self.btn_restaurar = _btn_danger(btn_box, "Restaurar Backup", self._on_restaurar_backup)
        self.btn_restaurar.pack(side="left", padx=4)

        self.lbl_backup_status = ctk.CTkLabel(
            card_backup, text="Nenhum backup executado nesta sessão.",
            text_color=TEXT_MUTED, font=ctk.CTkFont(size=11),
            justify="left", anchor="w",
        )
        self.lbl_backup_status.grid(row=2, column=0, padx=16, pady=(0, 12), sticky="ew")

        # ── Performance ───────────────────────────────────────────────────
        card_perf = _card(self)
        card_perf.grid(row=3, column=0, sticky="ew", padx=6, pady=(0, 10))
        card_perf.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card_perf, text="PERFORMANCE", text_color=TEXT_MUTED,
                     font=ctk.CTkFont(size=10, weight="bold"),
                     ).grid(row=0, column=0, padx=16, pady=(12, 8), sticky="w")

        row_perf = ctk.CTkFrame(card_perf, fg_color="transparent")
        row_perf.grid(row=1, column=0, padx=16, pady=(0, 8), sticky="ew")
        row_perf.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(row_perf, text="Diagnóstico de consultas",
                     text_color=TEXT_SECONDARY).grid(row=0, column=0, sticky="w")
        self.btn_performance = _btn_ghost(row_perf, "Validar desempenho", self._on_validar_desempenho)
        self.btn_performance.grid(row=0, column=1, sticky="e")

        self.lbl_performance_status = ctk.CTkLabel(
            card_perf, text="Validação de desempenho ainda não executada.",
            text_color=TEXT_MUTED, font=ctk.CTkFont(size=11),
            justify="left", anchor="w",
        )
        self.lbl_performance_status.grid(row=2, column=0, padx=16, pady=(0, 12), sticky="ew")

        # ── Documentação ──────────────────────────────────────────────────
        card_manual = _card(self)
        card_manual.grid(row=4, column=0, sticky="ew", padx=6, pady=0)
        card_manual.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card_manual, text="DOCUMENTAÇÃO", text_color=TEXT_MUTED,
                     font=ctk.CTkFont(size=10, weight="bold"),
                     ).grid(row=0, column=0, padx=16, pady=(12, 8), sticky="w")

        row_manual = ctk.CTkFrame(card_manual, fg_color="transparent")
        row_manual.grid(row=1, column=0, padx=16, pady=(0, 12), sticky="ew")
        row_manual.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(row_manual, text="Manual em PDF",
                     text_color=TEXT_SECONDARY).grid(row=0, column=0, sticky="w")
        self.btn_manual = _btn_ghost(row_manual, "Abrir manual PDF", self._on_manual_uso)
        self.btn_manual.grid(row=0, column=1, sticky="e")

    def _on_salvar(self):
        nome = self.entry_nome.get().strip()
        if not nome:
            messagebox.showerror("Erro", "Informe o nome do estabelecimento."); return
        if len(nome) < 3:
            messagebox.showerror("Erro", "O nome deve ter ao menos 3 caracteres."); return
        
        try:
            markup = float(self.entry_markup.get().replace(",", "."))
            resp = self.entry_resp.get().strip()
            
            self.service.salvar_nome_estabelecimento(nome)
            self.service.salvar_markup_padrao(markup)
            self.service.salvar_responsavel_padrao(resp)
            
            if callable(self.on_nome_alterado):
                self.on_nome_alterado(nome)
            messagebox.showinfo("Sucesso", "Configurações atualizadas com sucesso.")
        except ValueError:
            messagebox.showerror("Erro", "Markup deve ser um valor numérico.")

    def _on_restaurar_backup(self):
        caminho = filedialog.askopenfilename(
            title="Selecionar backup para restauração",
            filetypes=[("Banco SQLite", "*.db"), ("Todos os arquivos", "*.*")]
        )
        if not caminho: return

        msg = "Esta ação substituirá TODOS os dados atuais pelos dados do backup.\n\nUm backup de segurança dos dados atuais será feito automaticamente.\n\nDeseja continuar?"
        if not messagebox.askyesno("Confirmar Restauração", msg):
            return

        try:
            self.btn_restaurar.configure(state="disabled", text="Restaurando...")
            self.update_idletasks()
            
            self.service.restaurar_backup(caminho)
            
            messagebox.showinfo("Sucesso", "Backup restaurado com sucesso!\nO sistema será reiniciado internamente.")
            # Opcional: forçar refresh de todas as views ou avisar que os dados mudaram
            # No nosso caso, o MainWindow gerencia as views, mas como fechamos e reabrimos a conexão, 
            # as próximas consultas usarão o novo banco.
        except Exception as e:
            messagebox.showerror("Erro na Restauração", str(e))
        finally:
            self.btn_restaurar.configure(state="normal", text="Restaurar Backup")

    def _on_backup(self):
        nome_padrao = f"confeitaria-backup-{datetime.now():%Y%m%d-%H%M%S}.db"
        caminho = filedialog.asksaveasfilename(
            title="Salvar backup do banco", defaultextension=".db",
            initialfile=nome_padrao,
            filetypes=[("Banco SQLite","*.db"),("Todos os arquivos","*.*")],
        )
        if not caminho: return

        if os.path.exists(caminho):
            if not messagebox.askyesno("Confirmar sobrescrita",
                                       "Já existe um arquivo com esse nome. Deseja sobrescrever?"):
                self._atualizar_status_backup("Backup cancelado.", "warning"); return

        self.btn_backup.configure(state="disabled", text="Gerando backup...")
        self._atualizar_status_backup("Executando backup...", "warning")
        self.update_idletasks()

        try:
            caminho_final = self.service.realizar_backup(caminho)
        except Exception as exc:
            self._atualizar_status_backup("Falha ao gerar backup. Verifique os detalhes.", "error")
            messagebox.showerror("Erro", f"Não foi possível concluir o backup.\n\nDetalhes: {exc}")
            self.btn_backup.configure(state="normal", text="Fazer backup"); return

        self._atualizar_status_backup(
            f"Backup concluído em {datetime.now():%d/%m/%Y %H:%M:%S}: {caminho_final}", "success")
        messagebox.showinfo("Sucesso", f"Backup criado com sucesso em:\n{caminho_final}")
        self.btn_backup.configure(state="normal", text="Fazer backup")

    def _on_validar_desempenho(self):
        self.btn_performance.configure(state="disabled", text="Validando...")
        self._atualizar_status_performance("Executando diagnóstico de performance...", "warning")
        self.update_idletasks()

        try:
            diagnostico = self.performance_service.executar_diagnostico(limite_segundos=2.0, repeticoes=5)
        except Exception as exc:
            self._atualizar_status_performance("Falha ao executar diagnóstico.", "error")
            messagebox.showerror("Erro", f"Não foi possível validar desempenho.\n\nDetalhes: {exc}")
            self.btn_performance.configure(state="normal", text="Validar desempenho"); return

        lentas = [m for m in diagnostico.medicoes if not m.aprovado]
        if diagnostico.aprovado_geral:
            self._atualizar_status_performance(
                f"Desempenho OK: maior consulta em {diagnostico.maior_tempo_medido:.3f}s (limite 2,0s).", "success")
            messagebox.showinfo("Desempenho validado",
                                "Todas as consultas avaliadas ficaram abaixo de 2 segundos.")
        else:
            resumo = "\n".join(
                f"- {m.nome}: max {m.tempo_maximo:.3f}s" + (f" (erro: {m.erro})" if m.erro else "")
                for m in lentas
            )
            self._atualizar_status_performance(
                f"Atenção: {len(lentas)} consulta(s) acima do limite de 2,0s.", "error")
            messagebox.showwarning("Desempenho acima do limite",
                                   "Consultas acima do alvo de 2 segundos:\n\n" + resumo)

        self.btn_performance.configure(state="normal", text="Validar desempenho")

    def _on_manual_uso(self):
        caminho_manual = self.recibo_service.get_caminho_manual_padrao()
        try:
            self.recibo_service.gerar_manual_uso_pdf(
                caminho_manual, self.service.get_nome_estabelecimento())
            self.recibo_service.abrir_pdf(caminho_manual)
            messagebox.showinfo("Manual de uso",
                                f"Manual PDF gerado e aberto em:\n{caminho_manual}")
        except Exception as exc:
            messagebox.showerror("Erro", f"Não foi possível abrir o manual.\n\nDetalhes: {exc}")

    def _atualizar_status_backup(self, mensagem: str, tipo: str):
        self.lbl_backup_status.configure(text=mensagem, text_color=self._cor_tipo(tipo))

    def _atualizar_status_performance(self, mensagem: str, tipo: str):
        self.lbl_performance_status.configure(text=mensagem, text_color=self._cor_tipo(tipo))

    @staticmethod
    def _cor_tipo(tipo: str) -> str:
        return {"success": COLOR_GREEN, "error": COLOR_RED, "warning": COLOR_ORANGE}.get(tipo, TEXT_MUTED)


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  PAINEL DE AUDITORIA                                                        ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
class AuditoriaPanel(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.service = AuditoriaService()
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self._build_filters()
        self._build_lista()
        self._carregar_dados()

    def _build_filters(self):
        fc = _card(self)
        fc.grid(row=0, column=0, padx=4, pady=(0, 10), sticky="ew")
        fc.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(fc, text="FILTROS DE AUDITORIA", text_color=TEXT_MUTED,
                     font=ctk.CTkFont(size=10, weight="bold")
                     ).grid(row=0, column=0, padx=14, pady=(10, 4), sticky="w")

        ctrl = ctk.CTkFrame(fc, fg_color="transparent")
        ctrl.grid(row=1, column=0, padx=14, pady=(0, 10), sticky="ew")

        # Período
        ctk.CTkLabel(ctrl, text="Período:", text_color=TEXT_SECONDARY).pack(side="left", padx=(0, 4))
        self.f_ini = _entry(ctrl, width=100, placeholder_text="Início")
        self.f_ini.pack(side="left", padx=(0, 4))
        self.f_ini.bind("<KeyRelease>", _mask_date)
        
        self.f_fim = _entry(ctrl, width=100, placeholder_text="Fim")
        self.f_fim.pack(side="left", padx=(0, 12))
        self.f_fim.bind("<KeyRelease>", _mask_date)

        # Entidade
        ctk.CTkLabel(ctrl, text="Entidade:", text_color=TEXT_SECONDARY).pack(side="left", padx=(0, 4))
        entidades = ["Todos"] + self.service.obter_entidades_unicas()
        self.f_entidade = _optmenu(ctrl, entidades)
        self.f_entidade.pack(side="left", padx=(0, 12))
        self.f_entidade.set("Todos")

        # Ação
        ctk.CTkLabel(ctrl, text="Ação:", text_color=TEXT_SECONDARY).pack(side="left", padx=(0, 4))
        self.f_acao = _entry(ctrl, width=120, placeholder_text="Ex: INSERT")
        self.f_acao.pack(side="left", padx=(0, 12))

        _btn_accent(ctrl, "Buscar", self._carregar_dados).pack(side="left", padx=(0, 8))
        _btn_ghost(ctrl, "Limpar", self._limpar_filtros).pack(side="left")

    def _build_lista(self):
        tf = _card(self)
        tf.grid(row=1, column=0, sticky="nsew", padx=4)
        tf.grid_columnconfigure(0, weight=1); tf.grid_rowconfigure(0, weight=1)

        style = _treeview_style("Audit")
        cols = ("id", "data", "entidade", "entidade_id", "acao", "detalhes")
        self.tree = ttk.Treeview(tf, columns=cols, show="headings", style=style)
        
        for col, txt, w, anc in [
            ("id",          "ID",           50,  "center"),
            ("data",        "Data/Hora",    150, "center"),
            ("entidade",    "Entidade",     100, "center"),
            ("entidade_id", "ID Ent.",      70,  "center"),
            ("acao",        "Ação",         100, "center"),
            ("detalhes",    "Detalhes",     400, "w"),
        ]:
            self.tree.heading(col, text=txt)
            self.tree.column(col, width=w, anchor=anc)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        sb = ttk.Scrollbar(tf, orient="vertical", command=self.tree.yview)
        sb.grid(row=0, column=1, sticky="ns", pady=2)
        self.tree.configure(yscrollcommand=sb.set)
        
        self.tree.bind("<Double-1>", self._on_double_click)

    def _limpar_filtros(self):
        self.f_ini.delete(0, "end")
        self.f_fim.delete(0, "end")
        self.f_entidade.set("Todos")
        self.f_acao.delete(0, "end")
        self._carregar_dados()

    def _carregar_dados(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        logs = self.service.listar(
            entidade=self.f_entidade.get(),
            data_inicio=self.f_ini.get().strip(),
            data_fim=self.f_fim.get().strip(),
            acao=self.f_acao.get().strip()
        )
        
        for log in logs:
            detalhes_raw = log.get("detalhes") or "{}"
            try:
                det_obj = json.loads(detalhes_raw)
                detalhes_resumo = str(det_obj)[:100] + "..." if len(str(det_obj)) > 100 else str(det_obj)
            except:
                detalhes_resumo = detalhes_raw[:100]

            self.tree.insert("", "end", values=(
                log["id"],
                fmt_data(log["criado_em"]),
                log["entidade"],
                log["entidade_id"] or "-",
                log["acao"],
                detalhes_resumo
            ))

    def _on_double_click(self, event):
        sel = self.tree.selection()
        if not sel: return
        
        item_id = self.tree.item(sel[0])["values"][0]
        # Busca o log completo pelo ID
        # Como o listar já retorna tudo, podemos filtrar na lista atual ou buscar de novo.
        # Por simplicidade, vamos buscar de novo se necessário, ou apenas usar o que temos.
        # Mas detalhes_resumo foi truncado. Vamos buscar o objeto original.
        
        from app.db.connection import get_connection
        conn = get_connection()
        row = conn.execute("SELECT * FROM auditoria WHERE id = ?", (item_id,)).fetchone()
        if not row: return
        
        self._abrir_popup_detalhes(dict(row))

    def _abrir_popup_detalhes(self, log: dict):
        popup = ctk.CTkToplevel(self)
        popup.title(f"Detalhes da Auditoria #{log['id']}")
        popup.geometry("600x500")
        popup.after(100, popup.lift) # Garante que fica na frente
        
        popup.grid_columnconfigure(0, weight=1)
        popup.grid_rowconfigure(1, weight=1)
        
        # Cabeçalho
        header = ctk.CTkFrame(popup, fg_color=HEADER_BG, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        info = (f"Entidade: {log['entidade']} | ID: {log['entidade_id'] or '-'}\n"
                f"Ação: {log['acao']} | Em: {fmt_data(log['criado_em'])}")
        
        ctk.CTkLabel(header, text=info, text_color=TEXT_PRIMARY, 
                     font=ctk.CTkFont(weight="bold"), justify="left").pack(padx=15, pady=10, side="left")

        # JSON formatado
        try:
            det_obj = json.loads(log["detalhes"] or "{}")
            det_fmt = json.dumps(det_obj, indent=2, ensure_ascii=False)
        except:
            det_fmt = log["detalhes"] or "{}"
            
        txt_frame = _card(popup)
        txt_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        txt_frame.grid_columnconfigure(0, weight=1); txt_frame.grid_rowconfigure(0, weight=1)
        
        textbox = ctk.CTkTextbox(txt_frame, fg_color=FIELD_BG, text_color=TEXT_PRIMARY, font=("Consolas", 11))
        textbox.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        textbox.insert("1.0", det_fmt)
        textbox.configure(state="disabled")


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  CONFIGURAÇÕES VIEW (CONTAINER)                                             ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
class ConfiguracoesView(ctk.CTkFrame):
    def __init__(self, master, nome_atual: str = "", on_nome_alterado=None, **kwargs):
        super().__init__(master, fg_color=BG_DEEP, **kwargs)

        self._aba_ativa = "Geral"
        self._tab_btns: dict[str, tk.Frame]     = {}
        self._tab_lbls: dict[str, ctk.CTkLabel] = {}
        
        self.nome_atual = nome_atual
        self.on_nome_alterado = on_nome_alterado

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_topbar()
        self._build_tabbar()
        self._build_content()
        self._switch_aba("Geral")

    def _build_topbar(self):
        bar = ctk.CTkFrame(self, fg_color=HEADER_BG, corner_radius=0, height=56)
        bar.grid(row=0, column=0, sticky="ew")
        bar.grid_propagate(False)
        bar.grid_columnconfigure(1, weight=1)

        self.lbl_title = ctk.CTkLabel(
            bar, text="Configurações",
            text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(family="Roboto", size=20, weight="bold"),
        )
        self.lbl_title.grid(row=0, column=0, padx=20, sticky="w")

        actions = ctk.CTkFrame(bar, fg_color="transparent")
        actions.grid(row=0, column=1, padx=(6, 16), sticky="e")
        self.btn_salvar = _btn_accent(actions, "Salvar", self._on_salvar_clique)
        self.btn_salvar.grid(row=0, column=0, padx=4)

    def _build_tabbar(self):
        self._tabbar = ctk.CTkFrame(self, fg_color=HEADER_BG, corner_radius=0, height=40)
        self._tabbar.grid(row=1, column=0, sticky="ew")
        self._tabbar.grid_propagate(False)

        for aba in ["Geral", "Auditoria"]:
            tab = tk.Frame(self._tabbar, bg=HEADER_BG, cursor="hand2")
            tab.pack(side="left", padx=(16, 0))
            self._tab_btns[aba] = tab

            lbl = ctk.CTkLabel(tab, text=aba, fg_color="transparent",
                               text_color=TEXT_MUTED, font=ctk.CTkFont(size=13))
            lbl.pack(pady=(8, 0))
            self._tab_lbls[aba] = lbl

            ind = tk.Frame(tab, bg=HEADER_BG, height=2)
            ind.pack(fill="x", pady=(4, 0))
            tab._indicator = ind  # type: ignore

            tab.bind("<Button-1>", lambda e, a=aba: self._switch_aba(a))
            lbl.bind("<Button-1>", lambda e, a=aba: self._switch_aba(a))

        _separator(self).grid(row=1, column=0, sticky="sew")

    def _build_content(self):
        self._content = ctk.CTkFrame(self, fg_color="transparent")
        self._content.grid(row=2, column=0, sticky="nsew", padx=14, pady=(10, 14))
        self._content.grid_columnconfigure(0, weight=1)
        self._content.grid_rowconfigure(0, weight=1)

        self._panel_geral = GeralPanel(self._content, nome_atual=self.nome_atual, on_nome_alterado=self.on_nome_alterado)
        self._panel_audit = AuditoriaPanel(self._content)

    def _switch_aba(self, aba: str):
        self._aba_ativa = aba
        for nome, tab in self._tab_btns.items():
            ativo = nome == aba
            self._tab_lbls[nome].configure(
                text_color=TEXT_PRIMARY if ativo else TEXT_MUTED,
                font=ctk.CTkFont(size=13, weight="bold" if ativo else "normal"),
            )
            tab._indicator.configure(bg=ACCENT if ativo else HEADER_BG)

        self.lbl_title.configure(text=f"Configurações — {aba}")
        self._panel_geral.grid_forget()
        self._panel_audit.grid_forget()

        if aba == "Geral":
            self._panel_geral.grid(row=0, column=0, sticky="nsew")
            self.btn_salvar.grid(row=0, column=0, padx=4)
        else:
            self._panel_audit.grid(row=0, column=0, sticky="nsew")
            self.btn_salvar.grid_remove()

    def _on_salvar_clique(self):
        if self._aba_ativa == "Geral":
            self._panel_geral._on_salvar()
