import customtkinter as ctk
from datetime import datetime
from tkinter import filedialog, messagebox

from app.services.configuracao_service import ConfiguracaoService
from app.services.performance_service import PerformanceService
from app.services.recibo_service import ReciboService


class ConfiguracoesView(ctk.CTkFrame):
    def __init__(self, master, nome_atual: str = "", on_nome_alterado=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.service = ConfiguracaoService()
        self.performance_service = PerformanceService()
        self.recibo_service = ReciboService()
        self.on_nome_alterado = on_nome_alterado

        self.title_font = ctk.CTkFont(family="Roboto", size=22, weight="bold")
        self.body_font = ctk.CTkFont(family="Roboto", size=14)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self)
        header.grid(row=0, column=0, padx=16, pady=16, sticky="ew")
        self.header = header

        ctk.CTkLabel(header, text="Configurações", font=self.title_font).pack(side="left", padx=14, pady=12)

        body = ctk.CTkFrame(self)
        body.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="nsew")
        body.grid_columnconfigure(1, weight=1)
        self.body = body

        ctk.CTkLabel(body, text="Nome do estabelecimento*", font=self.body_font).grid(row=0, column=0, padx=12, pady=14, sticky="e")
        self.entry_nome = ctk.CTkEntry(body, placeholder_text="Ex: Doce da Maria")
        self.entry_nome.grid(row=0, column=1, padx=12, pady=14, sticky="ew")

        valor_inicial = nome_atual.strip() if nome_atual and nome_atual.strip() else self.service.get_nome_estabelecimento()
        self.entry_nome.insert(0, valor_inicial)

        self.lbl_info = ctk.CTkLabel(
            body,
            text="Esse nome será exibido no menu lateral e no título da janela.",
            font=self.body_font,
            text_color=("gray30", "gray70"),
        )
        self.lbl_info.grid(row=1, column=0, columnspan=2, padx=12, pady=(0, 14), sticky="w")

        ctk.CTkLabel(body, text="Backup do banco", font=self.body_font).grid(row=2, column=0, padx=12, pady=14, sticky="e")
        self.btn_backup = ctk.CTkButton(body, text="Fazer backup", command=self._on_backup, height=36)
        self.btn_backup.grid(row=2, column=1, padx=12, pady=14, sticky="w")

        self.lbl_backup_status = ctk.CTkLabel(
            body,
            text="Nenhum backup executado nesta sessão.",
            font=self.body_font,
            text_color=("gray30", "gray70"),
            justify="left",
            anchor="w",
        )
        self.lbl_backup_status.grid(row=3, column=0, columnspan=2, padx=12, pady=(0, 12), sticky="ew")

        ctk.CTkLabel(body, text="Desempenho de consultas", font=self.body_font).grid(row=4, column=0, padx=12, pady=14, sticky="e")
        self.btn_performance = ctk.CTkButton(body, text="Validar desempenho", command=self._on_validar_desempenho, height=36)
        self.btn_performance.grid(row=4, column=1, padx=12, pady=14, sticky="w")

        self.lbl_performance_status = ctk.CTkLabel(
            body,
            text="Validação de desempenho ainda não executada.",
            font=self.body_font,
            text_color=("gray30", "gray70"),
            justify="left",
            anchor="w",
        )
        self.lbl_performance_status.grid(row=5, column=0, columnspan=2, padx=12, pady=(0, 12), sticky="ew")

        ctk.CTkLabel(body, text="Manual de uso", font=self.body_font).grid(row=6, column=0, padx=12, pady=14, sticky="e")
        self.btn_manual = ctk.CTkButton(body, text="Abrir manual PDF", command=self._on_manual_uso, height=36)
        self.btn_manual.grid(row=6, column=1, padx=12, pady=14, sticky="w")

        frame_acoes = ctk.CTkFrame(body, fg_color="transparent")
        frame_acoes.grid(row=7, column=0, columnspan=2, padx=12, pady=(8, 16), sticky="e")

        self.btn_salvar = ctk.CTkButton(frame_acoes, text="Salvar", command=self._on_salvar, height=36)
        self.btn_salvar.pack(side="right")

        self.bind("<Configure>", self._on_resize)

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
            "success": ("#0F5132", "#75E3B5"),
            "error": ("#842029", "#FF9AA2"),
            "warning": ("#664D03", "#FFD166"),
        }
        cor = cores.get(tipo, ("gray30", "gray70"))
        self.lbl_backup_status.configure(text=mensagem, text_color=cor)

    def _atualizar_status_performance(self, mensagem: str, tipo: str):
        cores = {
            "success": ("#0F5132", "#75E3B5"),
            "error": ("#842029", "#FF9AA2"),
            "warning": ("#664D03", "#FFD166"),
        }
        cor = cores.get(tipo, ("gray30", "gray70"))
        self.lbl_performance_status.configure(text=mensagem, text_color=cor)

    def _on_resize(self, _event=None):
        largura = self.winfo_width()

        if largura <= 900:
            self.title_font.configure(size=20)
            self.body_font.configure(size=13)
            self.header.grid_configure(padx=10, pady=10)
            self.body.grid_configure(padx=10, pady=(0, 10))
        else:
            self.title_font.configure(size=22)
            self.body_font.configure(size=14)
            self.header.grid_configure(padx=16, pady=16)
            self.body.grid_configure(padx=16, pady=(0, 16))
