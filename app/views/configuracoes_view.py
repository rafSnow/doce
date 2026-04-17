import customtkinter as ctk
from datetime import datetime
from tkinter import filedialog, messagebox
import os

from app.services.configuracao_service import ConfiguracaoService
from app.services.performance_service import PerformanceService
from app.services.recibo_service import ReciboService


BG_DEEP = "#12100E"
CARD_BG = "#1E1814"
CARD_BORDER = "#2E2218"
HEADER_BG = "#171310"
FIELD_BG = "#241C18"

ACCENT = "#C8866B"
TEXT_PRIMARY = "#F0E0D0"
TEXT_SECONDARY = "#A08070"
TEXT_MUTED = "#5A4A40"


def _separator(parent, **kwargs):
    return ctk.CTkFrame(parent, fg_color=CARD_BORDER, height=1, **kwargs)


def _card(parent, **kwargs):
    return ctk.CTkFrame(
        parent,
        fg_color=CARD_BG,
        corner_radius=12,
        border_width=1,
        border_color=CARD_BORDER,
        **kwargs,
    )


def _btn_accent(parent, text, command, **kwargs):
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        fg_color=ACCENT,
        hover_color="#A06050",
        text_color="#FFFFFF",
        height=30,
        corner_radius=20,
        font=ctk.CTkFont(size=12, weight="bold"),
        **kwargs,
    )


def _btn_ghost(parent, text, command, **kwargs):
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        fg_color=FIELD_BG,
        hover_color="#2A201A",
        border_color=CARD_BORDER,
        border_width=1,
        text_color=TEXT_SECONDARY,
        height=30,
        corner_radius=20,
        font=ctk.CTkFont(size=12),
        **kwargs,
    )


class ConfiguracoesView(ctk.CTkFrame):
    def __init__(self, master, nome_atual: str = "", on_nome_alterado=None, **kwargs):
        super().__init__(master, fg_color=BG_DEEP, **kwargs)

        self.service = ConfiguracaoService()
        self.performance_service = PerformanceService()
        self.recibo_service = ReciboService()
        self.on_nome_alterado = on_nome_alterado

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_topbar()
        _separator(self).grid(row=1, column=0, sticky="ew")
        self._build_body(nome_atual)

    def _build_topbar(self):
        bar = ctk.CTkFrame(self, fg_color=HEADER_BG, corner_radius=0, height=56)
        bar.grid(row=0, column=0, sticky="ew", pady=(10, 0))
        bar.grid_propagate(False)
        bar.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            bar,
            text="Configuracoes",
            text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(family="Roboto", size=20, weight="bold"),
        ).grid(row=0, column=0, padx=20, sticky="w")

        actions = ctk.CTkFrame(bar, fg_color="transparent")
        actions.grid(row=0, column=1, padx=(6, 16), sticky="e")
        self.btn_salvar = _btn_accent(actions, "Salvar", self._on_salvar)
        self.btn_salvar.grid(row=0, column=0, padx=4)

    def _build_body(self, nome_atual: str):
        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.grid(row=2, column=0, padx=16, pady=(12, 16), sticky="nsew")
        self.body.grid_columnconfigure(0, weight=1)
        self.body.grid_rowconfigure(3, weight=1)

        card_nome = _card(self.body)
        card_nome.grid(row=0, column=0, sticky="ew", padx=6, pady=(0, 10))
        card_nome.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            card_nome,
            text="IDENTIDADE",
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=10, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, padx=16, pady=(12, 8), sticky="w")

        ctk.CTkLabel(
            card_nome,
            text="Nome do estabelecimento*",
            text_color=TEXT_SECONDARY,
            font=ctk.CTkFont(size=12),
        ).grid(row=1, column=0, padx=12, pady=(2, 10), sticky="e")

        self.entry_nome = ctk.CTkEntry(
            card_nome,
            placeholder_text="Ex: Doce da Maria",
            fg_color=FIELD_BG,
            border_color=CARD_BORDER,
            text_color=TEXT_PRIMARY,
            height=32,
        )
        self.entry_nome.grid(row=1, column=1, padx=(0, 14), pady=(2, 10), sticky="ew")

        valor_inicial = nome_atual.strip() if nome_atual and nome_atual.strip() else self.service.get_nome_estabelecimento()
        self.entry_nome.insert(0, valor_inicial)

        self.lbl_info = ctk.CTkLabel(
            card_nome,
            text="Esse nome sera exibido no menu lateral e no titulo da janela.",
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=11),
            justify="left",
            anchor="w",
        )
        self.lbl_info.grid(row=2, column=0, columnspan=2, padx=16, pady=(0, 12), sticky="ew")

        card_backup = _card(self.body)
        card_backup.grid(row=1, column=0, sticky="ew", padx=6, pady=(0, 10))
        card_backup.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card_backup,
            text="BACKUP",
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=10, weight="bold"),
        ).grid(row=0, column=0, padx=16, pady=(12, 8), sticky="w")

        row_backup = ctk.CTkFrame(card_backup, fg_color="transparent")
        row_backup.grid(row=1, column=0, padx=16, pady=(0, 8), sticky="ew")
        row_backup.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(row_backup, text="Backup do banco de dados", text_color=TEXT_SECONDARY).grid(row=0, column=0, sticky="w")
        self.btn_backup = _btn_ghost(row_backup, "Fazer backup", self._on_backup)
        self.btn_backup.grid(row=0, column=1, sticky="e")

        self.lbl_backup_status = ctk.CTkLabel(
            card_backup,
            text="Nenhum backup executado nesta sessao.",
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=11),
            justify="left",
            anchor="w",
        )
        self.lbl_backup_status.grid(row=2, column=0, padx=16, pady=(0, 12), sticky="ew")

        card_perf = _card(self.body)
        card_perf.grid(row=2, column=0, sticky="ew", padx=6, pady=(0, 10))
        card_perf.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card_perf,
            text="PERFORMANCE",
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=10, weight="bold"),
        ).grid(row=0, column=0, padx=16, pady=(12, 8), sticky="w")

        row_perf = ctk.CTkFrame(card_perf, fg_color="transparent")
        row_perf.grid(row=1, column=0, padx=16, pady=(0, 8), sticky="ew")
        row_perf.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(row_perf, text="Diagnostico de consultas", text_color=TEXT_SECONDARY).grid(row=0, column=0, sticky="w")
        self.btn_performance = _btn_ghost(row_perf, "Validar desempenho", self._on_validar_desempenho)
        self.btn_performance.grid(row=0, column=1, sticky="e")

        self.lbl_performance_status = ctk.CTkLabel(
            card_perf,
            text="Validacao de desempenho ainda nao executada.",
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=11),
            justify="left",
            anchor="w",
        )
        self.lbl_performance_status.grid(row=2, column=0, padx=16, pady=(0, 12), sticky="ew")

        card_manual = _card(self.body)
        card_manual.grid(row=3, column=0, sticky="ew", padx=6, pady=0)
        card_manual.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card_manual,
            text="DOCUMENTACAO",
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=10, weight="bold"),
        ).grid(row=0, column=0, padx=16, pady=(12, 8), sticky="w")

        row_manual = ctk.CTkFrame(card_manual, fg_color="transparent")
        row_manual.grid(row=1, column=0, padx=16, pady=(0, 12), sticky="ew")
        row_manual.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(row_manual, text="Manual em PDF", text_color=TEXT_SECONDARY).grid(row=0, column=0, sticky="w")
        self.btn_manual = _btn_ghost(row_manual, "Abrir manual PDF", self._on_manual_uso)
        self.btn_manual.grid(row=0, column=1, sticky="e")

    def _on_salvar(self):
        nome = self.entry_nome.get().strip()

        if not nome:
            messagebox.showerror("Erro", "Informe o nome do estabelecimento.")
            return

        if len(nome) < 3:
            messagebox.showerror("Erro", "O nome deve ter ao menos 3 caracteres.")
            return

        self.service.salvar_nome_estabelecimento(nome)

        if callable(self.on_nome_alterado):
            self.on_nome_alterado(nome)

        messagebox.showinfo("Sucesso", "Nome do estabelecimento atualizado com sucesso.")

    def _on_backup(self):
        nome_padrao = f"confeitaria-backup-{datetime.now():%Y%m%d-%H%M%S}.db"
        caminho_destino = filedialog.asksaveasfilename(
            title="Salvar backup do banco",
            defaultextension=".db",
            initialfile=nome_padrao,
            filetypes=[("Banco SQLite", "*.db"), ("Todos os arquivos", "*.*")],
        )

        if not caminho_destino:
            return

        if os.path.exists(caminho_destino):
            sobrescrever = messagebox.askyesno(
                "Confirmar sobrescrita",
                "Já existe um arquivo com esse nome. Deseja sobrescrever?",
            )
            if not sobrescrever:
                self._atualizar_status_backup("Backup cancelado pela usuária.", "warning")
                return

        self.btn_backup.configure(state="disabled", text="Gerando backup...")
        self._atualizar_status_backup("Executando backup...", "warning")
        self.update_idletasks()

        try:
            caminho_final = self.service.realizar_backup(caminho_destino)
        except Exception as exc:
            self._atualizar_status_backup("Falha ao gerar backup. Verifique os detalhes do erro.", "error")
            messagebox.showerror("Erro", f"Não foi possível concluir o backup.\n\nDetalhes: {exc}")
            self.btn_backup.configure(state="normal", text="Fazer backup")
            return

        self._atualizar_status_backup(
            f"Backup concluído em {datetime.now():%d/%m/%Y %H:%M:%S}: {caminho_final}",
            "success",
        )
        messagebox.showinfo("Sucesso", f"Backup criado com sucesso em:\n{caminho_final}")
        self.btn_backup.configure(state="normal", text="Fazer backup")

    def _on_validar_desempenho(self):
        self.btn_performance.configure(state="disabled", text="Validando...")
        self._atualizar_status_performance("Executando diagnóstico de performance...", "warning")
        self.update_idletasks()

        try:
            diagnostico = self.performance_service.executar_diagnostico(limite_segundos=2.0, repeticoes=5)
        except Exception as exc:
            self._atualizar_status_performance("Falha ao executar diagnóstico de performance.", "error")
            messagebox.showerror("Erro", f"Não foi possível validar desempenho.\n\nDetalhes: {exc}")
            self.btn_performance.configure(state="normal", text="Validar desempenho")
            return

        lentas = [m for m in diagnostico.medicoes if not m.aprovado]

        if diagnostico.aprovado_geral:
            self._atualizar_status_performance(
                f"Desempenho OK: maior consulta em {diagnostico.maior_tempo_medido:.3f}s (limite 2,0s).",
                "success",
            )
            messagebox.showinfo(
                "Desempenho validado",
                "Todas as consultas avaliadas ficaram abaixo de 2 segundos.",
            )
        else:
            resumo_lentas = "\n".join(
                f"- {m.nome}: max {m.tempo_maximo:.3f}s" + (f" (erro: {m.erro})" if m.erro else "")
                for m in lentas
            )
            self._atualizar_status_performance(
                f"Atenção: {len(lentas)} consulta(s) acima do limite de 2,0s.",
                "error",
            )
            messagebox.showwarning(
                "Desempenho acima do limite",
                "Consultas acima do alvo de 2 segundos:\n\n" + resumo_lentas,
            )

        self.btn_performance.configure(state="normal", text="Validar desempenho")

    def _on_manual_uso(self):
        caminho_manual = self.recibo_service.get_caminho_manual_padrao()

        try:
            self.recibo_service.gerar_manual_uso_pdf(caminho_manual, self.service.get_nome_estabelecimento())
            self.recibo_service.abrir_pdf(caminho_manual)
            messagebox.showinfo("Manual de uso", f"Manual PDF gerado e aberto em:\n{caminho_manual}")
        except Exception as exc:
            messagebox.showerror("Erro", f"Não foi possível abrir o manual em PDF.\n\nDetalhes: {exc}")

    def _atualizar_status_backup(self, mensagem: str, tipo: str):
        cores = {
            "success": "#7CC99A",
            "error": "#F1B0A0",
            "warning": "#E8A94A",
        }
        cor = cores.get(tipo, TEXT_MUTED)
        self.lbl_backup_status.configure(text=mensagem, text_color=cor)

    def _atualizar_status_performance(self, mensagem: str, tipo: str):
        cores = {
            "success": "#7CC99A",
            "error": "#F1B0A0",
            "warning": "#E8A94A",
        }
        cor = cores.get(tipo, TEXT_MUTED)
        self.lbl_performance_status.configure(text=mensagem, text_color=cor)
