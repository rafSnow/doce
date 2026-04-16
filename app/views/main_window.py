import customtkinter as ctk
import tkinter as tk

# ── Paleta de cores ──────────────────────────────────────────────────────────
BG_DEEP       = "#12100E"   # fundo da janela
SIDEBAR_BG    = "#1A1612"   # sidebar
SIDEBAR_HOVER = "#221D18"   # hover
SIDEBAR_ACTIVE= "#2A201A"   # ativo
CARD_BG       = "#1E1814"   # cards e frames secundários
BORDER        = "#2E2218"   # bordas suaves

ACCENT        = "#C8866B"   # terracota / cobre
ACCENT_LIGHT  = "#E8A980"   # tom mais claro do accent
GOLD          = "#E8A94A"   # dourado para badges/alertas

TEXT_PRIMARY   = "#F0E0D0"  # texto principal
TEXT_SECONDARY = "#A08070"  # texto secundário
TEXT_MUTED     = "#5A4A40"  # texto muito discreto

COLOR_GREEN  = "#7CC99A"
COLOR_BLUE   = "#6BACD4"
COLOR_ORANGE = "#E8A94A"
COLOR_PURPLE = "#B48FD4"


class NavButton(ctk.CTkFrame):
    """Botão de navegação personalizado com indicador lateral ativo."""

    ICON_MAP = {
        "Dashboard":     "⊞",
        "Insumos":       "⊟",
        "Produtos":      "⊡",
        "Pedidos":       "⊠",
        "Financeiro":    "⊛",
        "Configurações": "⊙",
    }

    def __init__(self, parent, text: str, command, **kwargs):
        super().__init__(parent, fg_color="transparent", height=40, **kwargs)
        self.grid_propagate(False)
        self.grid_columnconfigure(1, weight=1)

        self._command  = command
        self._active   = False
        self._text_raw = text

        # indicador esquerdo (ativo)
        self._indicator = tk.Frame(self, width=3, bg=SIDEBAR_BG)
        self._indicator.grid(row=0, column=0, sticky="ns", padx=(0, 0))

        # área clicável
        self._btn_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=8)
        self._btn_frame.grid(row=0, column=1, sticky="nsew", padx=(4, 6), pady=3)
        self._btn_frame.grid_columnconfigure(1, weight=1)

        icon = self.ICON_MAP.get(text, "◦")
        self._lbl_icon = ctk.CTkLabel(
            self._btn_frame, text=icon, width=22,
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=14),
        )
        self._lbl_icon.grid(row=0, column=0, padx=(10, 4), pady=0, sticky="w")

        self._lbl_text = ctk.CTkLabel(
            self._btn_frame, text=text, anchor="w",
            text_color=TEXT_SECONDARY,
            font=ctk.CTkFont(family="Roboto", size=13, weight="normal"),
        )
        self._lbl_text.grid(row=0, column=1, pady=0, sticky="ew")

        # badge (alertas)
        self._badge_var = ctk.StringVar(value="")
        self._lbl_badge = ctk.CTkLabel(
            self._btn_frame, textvariable=self._badge_var,
            fg_color="#3A2A10", text_color=GOLD,
            corner_radius=10, font=ctk.CTkFont(size=10, weight="bold"),
            width=0, height=18,
        )

        for w in (self, self._btn_frame, self._lbl_icon, self._lbl_text):
            w.bind("<Button-1>", lambda e: self._command())
            w.bind("<Enter>",    lambda e: self._on_hover(True))
            w.bind("<Leave>",    lambda e: self._on_hover(False))

    # ── API pública ────────────────────────────────────────────────────────
    def set_active(self, active: bool):
        self._active = active
        if active:
            self._indicator.configure(bg=ACCENT)
            self._btn_frame.configure(fg_color=SIDEBAR_ACTIVE)
            self._lbl_icon.configure(text_color=ACCENT_LIGHT)
            self._lbl_text.configure(
                text_color=TEXT_PRIMARY,
                font=ctk.CTkFont(family="Roboto", size=13, weight="bold"),
            )
        else:
            self._indicator.configure(bg=SIDEBAR_BG)
            self._btn_frame.configure(fg_color="transparent")
            self._lbl_icon.configure(text_color=TEXT_MUTED)
            self._lbl_text.configure(
                text_color=TEXT_SECONDARY,
                font=ctk.CTkFont(family="Roboto", size=13, weight="normal"),
            )

    def set_badge(self, count: int):
        if count > 0:
            self._badge_var.set(f" {count} ")
            self._lbl_badge.grid(row=0, column=2, padx=(0, 10), pady=0)
        else:
            self._badge_var.set("")
            self._lbl_badge.grid_remove()

    # ── Hover ──────────────────────────────────────────────────────────────
    def _on_hover(self, entering: bool):
        if self._active:
            return
        color = SIDEBAR_HOVER if entering else "transparent"
        self._btn_frame.configure(fg_color=color)


class Divider(ctk.CTkFrame):
    """Linha separadora horizontal."""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, height=1, fg_color=BORDER, **kwargs)
        self.grid_propagate(False)


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ── serviços (mantidos iguais) ─────────────────────────────────────
        from app.services.configuracao_service import ConfiguracaoService
        from app.services.insumo_service import InsumoService
        self.insumo_service  = InsumoService()
        self.config_service  = ConfiguracaoService()
        self.nome_estabelecimento = self.config_service.get_nome_estabelecimento()

        # ── janela ────────────────────────────────────────────────────────
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.configure(fg_color=BG_DEEP)
        self.title(f"{self.nome_estabelecimento} — Gestão para Confeitaria")
        self.geometry("1220x820")
        self.minsize(880, 640)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self._nav_buttons: dict[str, NavButton] = {}
        self._active_view = ""

        self._build_sidebar()
        self._build_content()
        self._atualizar_badge_alerta_insumos()
        self.bind("<Configure>", self._on_resize)

    # ── Sidebar ───────────────────────────────────────────────────────────
    def _build_sidebar(self):
        self._sidebar_width = 210
        self.sidebar = ctk.CTkFrame(
            self, width=self._sidebar_width, corner_radius=0,
            fg_color=SIDEBAR_BG,
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_columnconfigure(0, weight=1)

        # ── Logo ──────────────────────────────────────────────────────────
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=16, pady=(20, 14), sticky="ew")

        ctk.CTkLabel(
            logo_frame, text="GESTÃO", anchor="w",
            text_color=ACCENT, font=ctk.CTkFont(size=10, weight="bold"),
        ).pack(anchor="w")

        self.lbl_nome = ctk.CTkLabel(
            logo_frame,
            text=self.nome_estabelecimento,
            anchor="w", justify="left",
            text_color=TEXT_PRIMARY,
            wraplength=self._sidebar_width - 36,
            font=ctk.CTkFont(family="Roboto", size=17, weight="bold"),
        )
        self.lbl_nome.pack(anchor="w", pady=(2, 0))

        Divider(self.sidebar).grid(row=1, column=0, sticky="ew", padx=12, pady=0)

        # ── Navegação principal ───────────────────────────────────────────
        nav_main = [
            ("Dashboard",   self.show_dashboard_view),
            ("Insumos",     self.show_insumos_view),
            ("Produtos",    self.show_produtos_view),
            ("Pedidos",     self.show_pedidos_view),
            ("Financeiro",  self.show_financeiro_view),
        ]
        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=8)
        nav_frame.grid_columnconfigure(0, weight=1)

        for i, (label, cmd) in enumerate(nav_main):
            btn = NavButton(nav_frame, label, cmd)
            btn.grid(row=i, column=0, sticky="ew", padx=0, pady=1)
            self._nav_buttons[label] = btn

        # ── Espaçador ─────────────────────────────────────────────────────
        self.sidebar.grid_rowconfigure(3, weight=1)

        # ── Configurações (rodapé) ─────────────────────────────────────────
        Divider(self.sidebar).grid(row=4, column=0, sticky="ew", padx=12, pady=0)
        btn_config = NavButton(self.sidebar, "Configurações", self.show_config_view)
        btn_config.grid(row=5, column=0, sticky="ew", padx=0, pady=(4, 12))
        self._nav_buttons["Configurações"] = btn_config

        # ── Rodapé versão ─────────────────────────────────────────────────
        ctk.CTkLabel(
            self.sidebar, text="v1.0.0",
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=10),
        ).grid(row=6, column=0, pady=(0, 12))

    # ── Área de conteúdo ──────────────────────────────────────────────────
    def _build_content(self):
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # tela de boas-vindas
        welcome = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        welcome.grid(row=0, column=0)

        ctk.CTkLabel(
            welcome, text="Bem-vinda! 🎂",
            text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(family="Roboto", size=28, weight="bold"),
        ).pack(pady=(0, 8))

        ctk.CTkLabel(
            welcome, text="Selecione uma opção no menu lateral para começar.",
            text_color=TEXT_SECONDARY,
            font=ctk.CTkFont(size=14),
        ).pack()

    # ── Navegação ─────────────────────────────────────────────────────────
    def _set_active(self, nome: str):
        for label, btn in self._nav_buttons.items():
            btn.set_active(label == nome)
        self._active_view = nome

    def _clear_content(self):
        for w in self.content_frame.winfo_children():
            w.destroy()

    def _atualizar_badge_alerta_insumos(self, total: int | None = None):
        if total is None:
            total = self.insumo_service.contar_alertas_estoque()
        btn = self._nav_buttons.get("Insumos")
        if btn:
            btn.set_badge(total)

    # ── Views ─────────────────────────────────────────────────────────────
    def show_dashboard_view(self):
        self._clear_content()
        self._set_active("Dashboard")
        self._atualizar_badge_alerta_insumos()
        from app.views.dashboard_view import DashboardView
        DashboardView(self.content_frame).grid(row=0, column=0, sticky="nsew")

    def show_insumos_view(self):
        self._clear_content()
        self._set_active("Insumos")
        from app.views.insumos_view import InsumosView
        InsumosView(
            self.content_frame,
            on_estoque_alerta_change=self._atualizar_badge_alerta_insumos,
        ).grid(row=0, column=0, sticky="nsew")

    def show_produtos_view(self):
        self._clear_content()
        self._set_active("Produtos")
        self._atualizar_badge_alerta_insumos()
        from app.views.produtos_view import ProdutosView
        ProdutosView(self.content_frame).grid(row=0, column=0, sticky="nsew")

    def show_pedidos_view(self):
        self._clear_content()
        self._set_active("Pedidos")
        self._atualizar_badge_alerta_insumos()
        from app.views.pedidos_view import PedidosView
        PedidosView(self.content_frame).grid(row=0, column=0, sticky="nsew")

    def show_financeiro_view(self):
        self._clear_content()
        self._set_active("Financeiro")
        self._atualizar_badge_alerta_insumos()
        from app.views.financeiro_view import FinanceiroView
        FinanceiroView(self.content_frame).grid(row=0, column=0, sticky="nsew")

    def show_config_view(self):
        self._clear_content()
        self._set_active("Configurações")
        self._atualizar_badge_alerta_insumos()
        from app.views.configuracoes_view import ConfiguracoesView
        ConfiguracoesView(
            self.content_frame,
            nome_atual=self.nome_estabelecimento,
            on_nome_alterado=self._on_nome_alterado,
        ).grid(row=0, column=0, sticky="nsew")

    def _on_nome_alterado(self, novo_nome: str):
        self.nome_estabelecimento = novo_nome
        self.lbl_nome.configure(text=novo_nome)
        self.title(f"{novo_nome} — Gestão para Confeitaria")

    # ── Responsividade ────────────────────────────────────────────────────
    def _on_resize(self, _event=None):
        w = self.winfo_width()
        target = 180 if w <= 980 else 210
        if target != self._sidebar_width:
            self._sidebar_width = target
            self.sidebar.configure(width=target)
            self.lbl_nome.configure(wraplength=target - 36)