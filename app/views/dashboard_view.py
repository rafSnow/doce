import calendar
from datetime import datetime

import customtkinter as ctk
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter
from tkinter import messagebox

from app.services.dashboard_service import DashboardService
from app.core.enums import CategoriaDespesa
from app.ui.theme import (
    ACCENT,
    BG_DEEP,
    CARD_BG,
    CARD_BORDER,
    COLOR_BLUE,
    COLOR_GREEN,
    COLOR_RED,
    COLOR_ORANGE,
    COLOR_PURPLE,
    HEADER_BG,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    _sep as _separator,
)

CHART_BG       = "#FFFFFF"   # fundo dos gráficos

ACCENT_LIGHT   = "#D98590"   # rosa mais claro
GOLD           = "#A0404E"   # rosa escuro — badges

COLOR_COPPER   = "#C96B7A"   # usa o rosa como "cobre" no contexto Dolce

PILL_ACTIVE_FG   = ACCENT
PILL_ACTIVE_TEXT = "#FFFFFF"
PILL_FG          = "#FAE8EC"
PILL_TEXT        = TEXT_SECONDARY


def _pill_button(parent, text: str, command, active=False):
    fg   = ACCENT       if active else "#FAE8EC"
    txt  = "#FFFFFF"    if active else TEXT_SECONDARY
    brd  = ACCENT       if active else CARD_BORDER
    return ctk.CTkButton(
        parent, text=text, command=command,
        fg_color=fg, text_color=txt, border_color=brd,
        border_width=1, corner_radius=20,
        hover_color="#A84F5E" if active else "#F2D5DC",
        height=30, font=ctk.CTkFont(size=12),
    )


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

        self._lbl_insumos      = self._mini_stat(right, "Insumos",        COLOR_COPPER, 0)
        self._lbl_investimento = self._mini_stat(right, "Investimentos",   COLOR_GREEN,  1)

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

        self.figure = Figure(figsize=figsize, dpi=100, facecolor=CHART_BG)
        self.ax     = self.figure.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        w = self.canvas.get_tk_widget()
        w.configure(bg=CHART_BG, highlightthickness=0)
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

    def refresh(self):
        self.carregar_dados()

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
            fg_color=ACCENT, hover_color="#A84F5E", text_color="#FFFFFF",
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
            fg_color=ACCENT, hover_color="#A84F5E", text_color="#FFFFFF",
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

    # ── Cards ─────────────────────────────────────────────────────────────
    def _build_cards(self):
        cards_outer = ctk.CTkFrame(self, fg_color="transparent")
        cards_outer.grid(row=4, column=0, sticky="ew", padx=16, pady=(12, 0))
        
        # Primeira linha (4 cards)
        cards_outer.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        self._card_saldo    = StatCard(cards_outer, "Saldo Realizado",  COLOR_GREEN,  "Receitas confirmadas")
        self._card_receber  = StatCard(cards_outer, "A Receber",        COLOR_BLUE,   "Pedidos pendentes")
        self._card_pagar    = StatCard(cards_outer, "Falta Pagar",      COLOR_ORANGE, "Despesas pendentes")
        self._card_previsto = StatCard(cards_outer, "Saldo Previsto",   COLOR_PURPLE, "Projeção do período")

        self._card_saldo.grid   (row=0, column=0, padx=6, pady=(0, 10), sticky="nsew")
        self._card_receber.grid (row=0, column=1, padx=6, pady=(0, 10), sticky="nsew")
        self._card_pagar.grid   (row=0, column=2, padx=6, pady=(0, 10), sticky="nsew")
        self._card_previsto.grid(row=0, column=3, padx=6, pady=(0, 10), sticky="nsew")
        
        # Segunda linha (3 cards métricos)
        row2 = ctk.CTkFrame(cards_outer, fg_color="transparent")
        row2.grid(row=1, column=0, columnspan=4, sticky="ew")
        row2.grid_columnconfigure((0, 1, 2), weight=1)
        
        self._card_lucro   = StatCard(row2, "Lucro em Vendas",   ACCENT,       "Venda - custo dos produtos")
        self._card_margem  = StatCard(row2, "Margem de Lucro",  COLOR_PURPLE, "Lucro / Faturamento")
        self._card_ticket  = StatCard(row2, "Ticket Médio",     COLOR_BLUE,   "Faturamento / Pedidos")
        
        self._card_lucro.grid (row=0, column=0, padx=6, pady=0, sticky="nsew")
        self._card_margem.grid(row=0, column=1, padx=6, pady=0, sticky="nsew")
        self._card_ticket.grid(row=0, column=2, padx=6, pady=0, sticky="nsew")

        # REGRA E-04: Alertas de Estoque
        self._frame_alertas = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=12, border_width=1, border_color=CARD_BORDER)
        self._frame_alertas.grid(row=5, column=0, padx=22, pady=(15, 0), sticky="ew")
        self._frame_alertas.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self._frame_alertas, text="⚠ ALERTAS DE ESTOQUE", text_color=COLOR_ORANGE,
                     font=ctk.CTkFont(size=10, weight="bold")).grid(row=0, column=0, padx=16, pady=(10, 5), sticky="w")
        
        self._container_alertas = ctk.CTkFrame(self._frame_alertas, fg_color="transparent")
        self._container_alertas.grid(row=1, column=0, padx=16, pady=(0, 10), sticky="ew")

        # card investido
        self._card_investido = InvestedCard(self)
        self._card_investido.grid(row=6, column=0, padx=22, pady=(15, 0), sticky="ew")

    # ── Gráficos ──────────────────────────────────────────────────────────
    def _build_charts(self):
        charts_outer = ctk.CTkFrame(self, fg_color="transparent")
        charts_outer.grid(row=7, column=0, sticky="nsew", padx=16, pady=(10, 16))
        charts_outer.grid_columnconfigure(0, weight=2)
        charts_outer.grid_columnconfigure(1, weight=1)
        charts_outer.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(7, weight=1)

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
                fg_color=ACCENT if ativo else "#FAE8EC",
                text_color="#FFFFFF" if ativo else TEXT_SECONDARY,
                border_color=ACCENT if ativo else CARD_BORDER,
                hover_color="#A84F5E" if ativo else "#F2D5DC",
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
        self._card_lucro.set_value(self._fmt(resumo.lucro_total_vendas))
        
        # Ticket Médio
        self._card_ticket.set_value(self._fmt(resumo.ticket_medio))
        
        # Margem de Lucro (Regra DA-13)
        margem = resumo.margem_lucro_perc
        cor_margem = COLOR_RED
        if margem >= 30:
            cor_margem = COLOR_PURPLE
        elif margem >= 10:
            cor_margem = COLOR_ORANGE
            
        self._card_margem.set_value(f"{margem:.1f}%".replace(".", ","))
        self._card_margem._lbl_value.configure(text_color=cor_margem)

        self._card_investido.set_values(
            self._fmt(resumo.total_investido),
            self._fmt(resumo.investido_insumos),
            self._fmt(resumo.investido_investimentos),
        )

        # REGRA E-04: Carregar Alertas
        from app.services.insumo_service import InsumoService
        insumos = InsumoService().listar()
        alertas = [i for i in insumos if i.quantidade_disponivel <= i.quantidade_minima]
        
        for w in self._container_alertas.winfo_children():
            w.destroy()
            
        if not alertas:
            self._frame_alertas.grid_remove()
        else:
            self._frame_alertas.grid()
            for i, alert in enumerate(alertas):
                cor = COLOR_RED if alert.quantidade_disponivel <= 0 else COLOR_ORANGE
                txt = f"• {alert.nome}: {alert.quantidade_disponivel:g} {alert.unidade_medida} (mín: {alert.quantidade_minima:g})"
                ctk.CTkLabel(self._container_alertas, text=txt, text_color=cor, 
                             font=ctk.CTkFont(size=12)).grid(row=i//2, column=i%2, sticky="w", padx=10, pady=2)

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
        ax.set_facecolor(CHART_BG)
        self._cf_barras.figure.patch.set_facecolor(CHART_BG)

        serie = self.serie_barras
        if not serie:
            ax.text(0.5, 0.5, "Sem dados para o período",
                    transform=ax.transAxes, ha="center", va="center",
                    color=TEXT_MUTED, fontsize=11)
            ax.set_axis_off()
            self._cf_barras.redraw()
            return

        labels      = [item["label"]      for item in serie]
        faturamento = [item["faturamento"] for item in serie]
        despesas    = [item["despesas"]    for item in serie]
        indices     = list(range(len(serie)))
        bw          = 0.34

        ax.bar([i - bw / 2 for i in indices], faturamento, bw,
               label="Faturamento", color=COLOR_GREEN,  alpha=0.88)
        ax.bar([i + bw / 2 for i in indices], despesas,    bw,
               label="Despesas",    color=ACCENT, alpha=0.88)

        ax.set_xticks(indices)
        ax.set_xticklabels(labels, color=TEXT_SECONDARY, fontsize=9)
        ax.tick_params(axis="y", colors=TEXT_MUTED, labelsize=8)
        ax.yaxis.set_major_formatter(FuncFormatter(
            lambda v, _: self._fmt_curta(v)))
        ax.grid(axis="y", color="#F0E0E4", linewidth=0.7)
        ax.set_axisbelow(True)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        for sp in ("bottom", "left"):
            ax.spines[sp].set_color(CARD_BORDER)

        ax.legend(loc="upper left", frameon=False,
                  labelcolor=TEXT_SECONDARY, fontsize=9)

        maximo = max(max(faturamento, default=0), max(despesas, default=0))
        if maximo > 0:
            ax.set_ylim(0, maximo * 1.25)

        self._cf_barras.redraw()

    def _draw_pizza(self):
        ax = self._cf_pizza.ax
        ax.clear()
        ax.set_facecolor(CHART_BG)
        self._cf_pizza.figure.patch.set_facecolor(CHART_BG)

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
            wedgeprops={"linewidth": 2.5, "edgecolor": CHART_BG},
            textprops={"color": "#FFFFFF", "fontsize": 9},
        )
        for t in autotextos:
            t.set_color("#FFFFFF")
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
            CategoriaDespesa.INSUMOS.value:       COLOR_COPPER,
            CategoriaDespesa.INVESTIMENTOS.value: COLOR_GREEN,
            CategoriaDespesa.OUTROS.value:        COLOR_BLUE,
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