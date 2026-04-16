import calendar
from datetime import datetime

import customtkinter as ctk
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter
from tkinter import messagebox

from app.services.dashboard_service import DashboardService

# ── Paleta ───────────────────────────────────────────────────────────────────
BG_DEEP        = "#12100E"
CARD_BG        = "#1E1814"
CARD_BORDER    = "#2E2218"
HEADER_BG      = "#171310"
CHART_BG       = "#181410"

ACCENT         = "#C8866B"
ACCENT_LIGHT   = "#E8A980"
GOLD           = "#E8A94A"

TEXT_PRIMARY   = "#F0E0D0"
TEXT_SECONDARY = "#A08070"
TEXT_MUTED     = "#5A4A40"

COLOR_GREEN    = "#7CC99A"
COLOR_BLUE     = "#6BACD4"
COLOR_ORANGE   = "#E8A94A"
COLOR_PURPLE   = "#B48FD4"
COLOR_COPPER   = "#C8866B"

PILL_ACTIVE_FG   = "#2A1E16"
PILL_ACTIVE_TEXT = TEXT_PRIMARY
PILL_FG          = "#1E1814"
PILL_TEXT        = TEXT_SECONDARY


# ── Helpers de widget ─────────────────────────────────────────────────────────
def _separator(parent, **kw):
    f = ctk.CTkFrame(parent, height=1, fg_color=CARD_BORDER, **kw)
    return f


def _pill_button(parent, text: str, command, active=False):
    fg   = ACCENT         if active else "#241C18"
    txt  = "#FFFFFF"      if active else TEXT_SECONDARY
    brd  = ACCENT         if active else CARD_BORDER
    btn = ctk.CTkButton(
        parent, text=text, command=command,
        fg_color=fg, text_color=txt, border_color=brd,
        border_width=1, corner_radius=20,
        hover_color="#A06050" if active else "#2A201A",
        height=30, font=ctk.CTkFont(size=12),
    )
    return btn


class StatCard(ctk.CTkFrame):
    """Card de métrica com rótulo, valor e sublabel opcionais."""

    def __init__(self, parent, title: str, value_color: str = TEXT_PRIMARY,
                 sublabel: str = "", colspan: int = 1, **kwargs):
        super().__init__(
            parent,
            fg_color=CARD_BG,
            corner_radius=12,
            border_width=1,
            border_color=CARD_BORDER,
            **kwargs,
        )
        self.grid_columnconfigure(0, weight=1)

        # barra superior colorida (4 px)
        accent_bar = ctk.CTkFrame(self, height=4, fg_color=value_color, corner_radius=2)
        accent_bar.grid(row=0, column=0, sticky="ew", padx=0, pady=0)

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.grid(row=1, column=0, sticky="nsew", padx=18, pady=(10, 14))
        inner.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            inner, text=title.upper(), anchor="w",
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=10, weight="bold"),
        ).grid(row=0, column=0, sticky="w")

        self._lbl_value = ctk.CTkLabel(
            inner, text="R$ 0,00", anchor="w",
            text_color=value_color,
            font=ctk.CTkFont(family="Roboto", size=28, weight="bold"),
        )
        self._lbl_value.grid(row=1, column=0, sticky="w", pady=(4, 0))

        if sublabel:
            ctk.CTkLabel(
                inner, text=sublabel, anchor="w",
                text_color=TEXT_MUTED,
                font=ctk.CTkFont(size=11),
            ).grid(row=2, column=0, sticky="w", pady=(2, 0))

    def set_value(self, text: str):
        self._lbl_value.configure(text=text)


class InvestedCard(ctk.CTkFrame):
    """Card expandido para Total Investido com breakdown lateral."""

    def __init__(self, parent, **kwargs):
        super().__init__(
            parent, fg_color=CARD_BG, corner_radius=12,
            border_width=1, border_color=CARD_BORDER, **kwargs,
        )
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        accent_bar = ctk.CTkFrame(self, height=4, fg_color=COLOR_COPPER, corner_radius=2)
        accent_bar.grid(row=0, column=0, columnspan=2, sticky="ew")

        # ── Lado esquerdo ─────────────────────────────────────────────────
        left = ctk.CTkFrame(self, fg_color="transparent")
        left.grid(row=1, column=0, sticky="nsew", padx=18, pady=(10, 14))

        ctk.CTkLabel(
            left, text="TOTAL INVESTIDO", anchor="w",
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=10, weight="bold"),
        ).pack(anchor="w")

        self._lbl_total = ctk.CTkLabel(
            left, text="R$ 0,00", anchor="w",
            text_color=COLOR_COPPER,
            font=ctk.CTkFont(family="Roboto", size=28, weight="bold"),
        )
        self._lbl_total.pack(anchor="w", pady=(4, 0))

        ctk.CTkLabel(
            left, text="Insumos + Investimentos", anchor="w",
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=11),
        ).pack(anchor="w", pady=(2, 0))

        # ── Separador vertical ────────────────────────────────────────────
        _separator(self, width=1).grid(row=1, column=1, sticky="ns", padx=0, pady=10)

        # ── Lado direito ──────────────────────────────────────────────────
        right = ctk.CTkFrame(self, fg_color="transparent")
        right.grid(row=1, column=2, sticky="nsew", padx=(18, 20), pady=(10, 14))

        self._lbl_insumos     = self._mini_stat(right, "Insumos",     COLOR_COPPER, 0)
        self._lbl_investimento = self._mini_stat(right, "Investimentos", COLOR_GREEN, 1)

    @staticmethod
    def _mini_stat(parent, label, color, row):
        ctk.CTkLabel(
            parent, text=label.upper(), anchor="w",
            text_color=TEXT_MUTED, font=ctk.CTkFont(size=9, weight="bold"),
        ).grid(row=row * 2, column=0, sticky="w", pady=(6 if row else 0, 0))
        lbl = ctk.CTkLabel(
            parent, text="R$ 0,00", anchor="w",
            text_color=color,
            font=ctk.CTkFont(family="Roboto", size=16, weight="bold"),
        )
        lbl.grid(row=row * 2 + 1, column=0, sticky="w")
        return lbl

    def set_values(self, total: str, insumos: str = "", investimentos: str = ""):
        self._lbl_total.configure(text=total)
        if insumos:
            self._lbl_insumos.configure(text=insumos)
        if investimentos:
            self._lbl_investimento.configure(text=investimentos)


class ChartFrame(ctk.CTkFrame):
    """Frame de gráfico com título e área matplotlib."""

    def __init__(self, parent, title: str, figsize=(8, 3.2), **kwargs):
        super().__init__(
            parent, fg_color=CARD_BG, corner_radius=12,
            border_width=1, border_color=CARD_BORDER, **kwargs,
        )
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self, text=title, anchor="w",
            text_color=TEXT_SECONDARY,
            font=ctk.CTkFont(size=11, weight="bold"),
        ).grid(row=0, column=0, padx=16, pady=(12, 2), sticky="w")

        _separator(self).grid(row=1, column=0, sticky="ew", padx=0)

        self.figure = Figure(figsize=figsize, dpi=100, facecolor=CARD_BG)
        self.ax     = self.figure.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        w = self.canvas.get_tk_widget()
        w.configure(bg=CARD_BG, highlightthickness=0)
        w.grid(row=2, column=0, padx=10, pady=(4, 10), sticky="nsew")
        self.grid_rowconfigure(2, weight=1)

    def redraw(self):
        self.canvas.draw_idle()


# ── View principal ────────────────────────────────────────────────────────────
class DashboardView(ctk.CTkFrame):

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=BG_DEEP, **kwargs)
        self.service = DashboardService()
        self._resize_job = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=1)

        self._periodo_inicio = ""
        self._periodo_fim    = ""
        self._tipo_periodo   = "Mês Atual"

        self.serie_barras: list[dict] = []
        self.serie_pizza:  list[dict] = []

        self._build_topbar()
        self._build_cards()
        self._build_charts()
        self.bind("<Configure>", self._on_resize)
        self._on_periodo("Mês Atual")

    # ── Topbar ────────────────────────────────────────────────────────────
    def _build_topbar(self):
        bar = ctk.CTkFrame(self, fg_color=HEADER_BG, corner_radius=0, height=56)
        bar.grid(row=0, column=0, sticky="ew", pady=(10, 0))
        bar.grid_propagate(False)
        bar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            bar, text="Resumo Financeiro",
            text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(family="Roboto", size=20, weight="bold"),
        ).grid(row=0, column=0, padx=20, pady=0, sticky="w")

        # pills de período
        pill_frame = ctk.CTkFrame(bar, fg_color="transparent")
        pill_frame.grid(row=0, column=1, padx=10, sticky="e")

        periodos = ["Mês Atual", "Trimestre Atual", "Personalizado"]
        self._pill_btns: dict[str, ctk.CTkButton] = {}
        for i, p in enumerate(periodos):
            btn = _pill_button(pill_frame, p, lambda x=p: self._on_periodo(x), active=(p == "Mês Atual"))
            btn.grid(row=0, column=i, padx=3)
            self._pill_btns[p] = btn

        # botão atualizar
        ctk.CTkButton(
            bar, text="↻  Atualizar", command=self.carregar_dados,
            fg_color=ACCENT, hover_color="#A06050", text_color="#fff",
            height=30, corner_radius=20,
            font=ctk.CTkFont(size=12, weight="bold"),
        ).grid(row=0, column=2, padx=(0, 20))

        # linha separadora
        _separator(self).grid(row=1, column=0, sticky="ew")

        # barra personalizada (oculta por padrão)
        self._custom_bar = ctk.CTkFrame(self, fg_color=HEADER_BG)
        self._custom_bar.grid_columnconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkLabel(
            self._custom_bar, text="De:", text_color=TEXT_SECONDARY,
            font=ctk.CTkFont(size=12),
        ).grid(row=0, column=0, padx=(20, 4), pady=6, sticky="e")

        self._entry_inicio = ctk.CTkEntry(
            self._custom_bar, placeholder_text="DD/MM/AAAA",
            fg_color=CARD_BG, border_color=CARD_BORDER, text_color=TEXT_PRIMARY,
            height=32, width=120,
        )
        self._entry_inicio.grid(row=0, column=1, padx=4, pady=6, sticky="w")
        self._entry_inicio.bind("<KeyRelease>", self._mask_date)

        ctk.CTkLabel(
            self._custom_bar, text="Até:", text_color=TEXT_SECONDARY,
            font=ctk.CTkFont(size=12),
        ).grid(row=0, column=2, padx=(16, 4), pady=6, sticky="e")

        self._entry_fim = ctk.CTkEntry(
            self._custom_bar, placeholder_text="DD/MM/AAAA",
            fg_color=CARD_BG, border_color=CARD_BORDER, text_color=TEXT_PRIMARY,
            height=32, width=120,
        )
        self._entry_fim.grid(row=0, column=3, padx=4, pady=6, sticky="w")
        self._entry_fim.bind("<KeyRelease>", self._mask_date)

        ctk.CTkButton(
            self._custom_bar, text="Aplicar",
            fg_color=ACCENT, hover_color="#A06050", text_color="#fff",
            height=30, corner_radius=20, width=90,
            command=self._aplicar_custom,
        ).grid(row=0, column=4, padx=(8, 20), pady=6)

        # label de período aplicado
        self._lbl_periodo = ctk.CTkLabel(
            self, text="", text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=11),
            anchor="w",
        )
        self._lbl_periodo.grid(row=3, column=0, sticky="w", padx=22, pady=(0, 2))

        # O período inicial é aplicado ao final do __init__, após cards e gráficos existirem.

    # ── Cards ─────────────────────────────────────────────────────────────
    def _build_cards(self):
        cards_outer = ctk.CTkFrame(self, fg_color="transparent")
        cards_outer.grid(row=4, column=0, sticky="ew", padx=16, pady=(12, 0))
        cards_outer.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self._card_saldo   = StatCard(cards_outer, "Saldo Realizado",  COLOR_GREEN,  "Receitas confirmadas")
        self._card_receber = StatCard(cards_outer, "A Receber",        COLOR_BLUE,   "Pedidos pendentes")
        self._card_pagar   = StatCard(cards_outer, "Falta Pagar",      COLOR_ORANGE, "Despesas pendentes")
        self._card_previsto= StatCard(cards_outer, "Saldo Previsto",   COLOR_PURPLE, "Projeção do período")

        self._card_saldo.grid   (row=0, column=0, padx=6, pady=0, sticky="nsew")
        self._card_receber.grid (row=0, column=1, padx=6, pady=0, sticky="nsew")
        self._card_pagar.grid   (row=0, column=2, padx=6, pady=0, sticky="nsew")
        self._card_previsto.grid(row=0, column=3, padx=6, pady=0, sticky="nsew")

        # card investido (largura total)
        self._card_investido = InvestedCard(self)
        self._card_investido.grid(row=5, column=0, padx=22, pady=(10, 0), sticky="ew")

    # ── Gráficos ──────────────────────────────────────────────────────────
    def _build_charts(self):
        charts_outer = ctk.CTkFrame(self, fg_color="transparent")
        charts_outer.grid(row=6, column=0, sticky="nsew", padx=16, pady=(10, 16))
        charts_outer.grid_columnconfigure(0, weight=2)
        charts_outer.grid_columnconfigure(1, weight=1)
        charts_outer.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(6, weight=1)

        self._cf_barras = ChartFrame(
            charts_outer,
            "FATURAMENTO MENSAL (RENDIMENTOS) VS DESPESAS PAGAS",
            figsize=(8, 3.2),
        )
        self._cf_barras.grid(row=0, column=0, padx=(6, 5), pady=0, sticky="nsew")
        self._cf_barras.figure.subplots_adjust(left=0.09, right=0.98, top=0.92, bottom=0.2)

        self._cf_pizza = ChartFrame(
            charts_outer,
            "DISTRIBUIÇÃO POR CATEGORIA",
            figsize=(4, 3.2),
        )
        self._cf_pizza.grid(row=0, column=1, padx=(5, 6), pady=0, sticky="nsew")
        self._cf_pizza.figure.subplots_adjust(left=0.02, right=0.72, top=0.95, bottom=0.05)

    # ── Período ───────────────────────────────────────────────────────────
    def _on_periodo(self, tipo: str):
        self._tipo_periodo = tipo

        for t, btn in self._pill_btns.items():
            ativo = t == tipo
            btn.configure(
                fg_color=ACCENT if ativo else "#241C18",
                text_color=TEXT_PRIMARY if ativo else TEXT_SECONDARY,
                border_color=ACCENT if ativo else CARD_BORDER,
                hover_color="#A06050" if ativo else "#2A201A",
            )

        hoje = datetime.now()
        if tipo == "Mês Atual":
            self._custom_bar.grid_remove()
            inicio = datetime(hoje.year, hoje.month, 1)
            ultimo = calendar.monthrange(hoje.year, hoje.month)[1]
            fim    = datetime(hoje.year, hoje.month, ultimo)
            self._set_periodo(inicio, fim)
            self.carregar_dados()

        elif tipo == "Trimestre Atual":
            self._custom_bar.grid_remove()
            mes_ini = ((hoje.month - 1) // 3) * 3 + 1
            inicio  = datetime(hoje.year, mes_ini, 1)
            mes_fim = mes_ini + 2
            ultimo  = calendar.monthrange(hoje.year, mes_fim)[1]
            fim     = datetime(hoje.year, mes_fim, ultimo)
            self._set_periodo(inicio, fim)
            self.carregar_dados()

        else:
            self._custom_bar.grid(row=2, column=0, sticky="ew")
            self._entry_inicio.delete(0, "end")
            self._entry_fim.delete(0, "end")
            self._periodo_inicio = ""
            self._periodo_fim    = ""
            self._lbl_periodo.configure(text="Período personalizado — informe as datas acima")

    def _set_periodo(self, inicio: datetime, fim: datetime):
        i_txt = inicio.strftime("%d/%m/%Y")
        f_txt = fim.strftime("%d/%m/%Y")
        self._periodo_inicio = i_txt
        self._periodo_fim    = f_txt
        self._lbl_periodo.configure(text=f"Período: {i_txt} → {f_txt}")

    def _aplicar_custom(self):
        i_txt = self._entry_inicio.get().strip()
        f_txt = self._entry_fim.get().strip()
        try:
            inicio = datetime.strptime(i_txt, "%d/%m/%Y")
            fim    = datetime.strptime(f_txt, "%d/%m/%Y")
        except ValueError:
            messagebox.showerror("Erro", "Informe datas válidas no formato DD/MM/AAAA.")
            return
        if inicio > fim:
            messagebox.showerror("Erro", "A data inicial não pode ser maior que a data final.")
            return
        self._periodo_inicio = i_txt
        self._periodo_fim    = f_txt
        self._lbl_periodo.configure(text=f"Período: {i_txt} → {f_txt}")
        self.carregar_dados()

    def _mask_date(self, event):
        entry  = event.widget
        digits = "".join(c for c in entry.get() if c.isdigit())[:8]
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
        entry.delete(0, "end")
        entry.insert(0, "/".join(partes))

    # ── Dados ─────────────────────────────────────────────────────────────
    def carregar_dados(self):
        resumo = self.service.get_resumo(
            data_inicio=self._periodo_inicio,
            data_fim=self._periodo_fim,
        )
        self.serie_barras = self.service.get_faturamento_vs_despesas_mensal(
            data_inicio=self._periodo_inicio,
            data_fim=self._periodo_fim,
        )
        self.serie_pizza = self.service.get_despesas_por_categoria(
            data_inicio=self._periodo_inicio,
            data_fim=self._periodo_fim,
        )

        self._card_saldo.set_value(self._fmt(resumo.saldo_atual))
        self._card_receber.set_value(self._fmt(resumo.a_receber))
        self._card_pagar.set_value(self._fmt(resumo.falta_pagar))
        self._card_previsto.set_value(self._fmt(resumo.saldo_previsto))
        self._card_investido.set_values(
            self._fmt(resumo.total_investido),
        )
        self._redesenhar()

    # ── Gráficos matplotlib ───────────────────────────────────────────────
    def _redesenhar(self):
        self._ajustar_figure(self._cf_barras)
        self._ajustar_figure(self._cf_pizza)
        self._draw_barras()
        self._draw_pizza()

    def _ajustar_figure(self, cf: ChartFrame):
        w = max(cf.canvas.get_tk_widget().winfo_width(),  320)
        h = max(cf.canvas.get_tk_widget().winfo_height(), 180)
        cf.figure.set_size_inches(w / cf.figure.dpi, h / cf.figure.dpi, forward=True)

    def _draw_barras(self):
        ax = self._cf_barras.ax
        ax.clear()
        ax.set_facecolor(CARD_BG)
        self._cf_barras.figure.patch.set_facecolor(CARD_BG)

        serie = self.serie_barras
        if not serie:
            ax.text(0.5, 0.5, "Sem dados para o período",
                    transform=ax.transAxes, ha="center", va="center",
                    color=TEXT_MUTED, fontsize=11)
            ax.set_axis_off()
            self._cf_barras.redraw()
            return

        labels      = [item["label"]       for item in serie]
        faturamento = [item["faturamento"]  for item in serie]
        despesas    = [item["despesas"]     for item in serie]
        indices     = list(range(len(serie)))
        bw          = 0.34

        ax.bar([i - bw / 2 for i in indices], faturamento, bw,
               label="Faturamento", color=COLOR_GREEN,  alpha=0.92)
        ax.bar([i + bw / 2 for i in indices], despesas,    bw,
               label="Despesas",    color="#E07060", alpha=0.92)

        ax.set_xticks(indices)
        ax.set_xticklabels(labels, color=TEXT_SECONDARY, fontsize=9)
        ax.tick_params(axis="y", colors=TEXT_MUTED, labelsize=8)
        ax.yaxis.set_major_formatter(FuncFormatter(
            lambda v, _: self._fmt_curta(v)))
        ax.grid(axis="y", color="#2A1E18", linewidth=0.7)
        ax.set_axisbelow(True)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        for sp in ("bottom", "left"):
            ax.spines[sp].set_color("#2E2218")

        ax.legend(loc="upper left", frameon=False,
                  labelcolor=TEXT_SECONDARY, fontsize=9)

        maximo = max(max(faturamento, default=0), max(despesas, default=0))
        if maximo > 0:
            ax.set_ylim(0, maximo * 1.25)

        self._cf_barras.redraw()

    def _draw_pizza(self):
        ax = self._cf_pizza.ax
        ax.clear()
        ax.set_facecolor(CARD_BG)
        self._cf_pizza.figure.patch.set_facecolor(CARD_BG)

        serie = self.serie_pizza
        if not serie:
            ax.text(0.5, 0.5, "Sem despesas\nno período",
                    transform=ax.transAxes, ha="center", va="center",
                    color=TEXT_MUTED, fontsize=10)
            ax.set_axis_off()
            self._cf_pizza.redraw()
            return

        valores    = [item["valor"]    for item in serie]
        categorias = [item["categoria"]for item in serie]
        cores      = [self._cor(c)     for c in categorias]
        total      = sum(valores)

        wedges, _, autotextos = ax.pie(
            valores, colors=cores, startangle=90,
            autopct=lambda p: f"{p:.1f}%".replace(".", ","),
            pctdistance=0.68,
            wedgeprops={"linewidth": 2.5, "edgecolor": CARD_BG},
            textprops={"color": "#ffffff", "fontsize": 9},
        )
        for t in autotextos:
            t.set_color("#ffffff")
            t.set_fontweight("bold")

        ax.legend(
            wedges,
            [f"{c} — {self._fmt(v)}" for c, v in zip(categorias, valores)],
            loc="center left", bbox_to_anchor=(1.04, 0.5),
            frameon=False, labelcolor=TEXT_SECONDARY, fontsize=9,
        )
        ax.text(0, 0, self._fmt(total),
                ha="center", va="center",
                color=TEXT_PRIMARY, fontsize=12, fontweight="bold")
        ax.set_aspect("equal")
        self._cf_pizza.redraw()

    # ── Utilitários ───────────────────────────────────────────────────────
    def _cor(self, categoria: str) -> str:
        return {
            "Insumos":       COLOR_COPPER,
            "Investimentos": COLOR_GREEN,
            "Outros":        COLOR_BLUE,
        }.get(categoria, COLOR_ORANGE)

    @staticmethod
    def _fmt(valor: float) -> str:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    @staticmethod
    def _fmt_curta(valor: float) -> str:
        if valor >= 1_000_000:
            return f"R$ {valor/1_000_000:.1f}M".replace(".", ",")
        if valor >= 1_000:
            return f"R$ {valor/1_000:.0f}k"
        return f"R$ {valor:.0f}"

    # ── Resize ────────────────────────────────────────────────────────────
    def _on_resize(self, _event=None):
        if self._resize_job:
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(60, self._redesenhar)