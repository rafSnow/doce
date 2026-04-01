import customtkinter as ctk
from app.services.dashboard_service import DashboardService

class DashboardView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.service = DashboardService()
        
        # Configuração do grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # === Header ===
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        lbl_titulo = ctk.CTkLabel(header_frame, text="Resumo Financeiro", font=("Roboto", 24, "bold"))
        lbl_titulo.pack(side="left")
        
        btn_atualizar = ctk.CTkButton(header_frame, text="Atualizar Dados", command=self.carregar_dados)
        btn_atualizar.pack(side="right")
        
        # === Cards ===
        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        # Grid para 2 colunas e 2 linhas grandes
        self.cards_frame.grid_columnconfigure((0, 1), weight=1)
        self.cards_frame.grid_rowconfigure((0, 1), weight=1)
        
        # Criando os cards
        self.lbl_saldo_atual = self._create_card(self.cards_frame, "Saldo Atual (Realizado)", 0, 0, text_color="#4CAF50")
        self.lbl_a_receber = self._create_card(self.cards_frame, "A Receber (Pedidos Pendentes)", 0, 1, text_color="#2196F3")
        self.lbl_falta_pagar = self._create_card(self.cards_frame, "Falta Pagar (Despesas Pendentes)", 1, 0, text_color="#FF9800")
        self.lbl_saldo_previsto = self._create_card(self.cards_frame, "Saldo Previsto", 1, 1, text_color="#9C27B0")
        
        self.carregar_dados()

    def _create_card(self, parent, title, row, col, text_color="white"):
        card = ctk.CTkFrame(parent, corner_radius=10)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure((0, 1), weight=1)
        
        lbl_title = ctk.CTkLabel(card, text=title, font=("Roboto", 16))
        lbl_title.grid(row=0, column=0, pady=(30, 5))
        
        lbl_value = ctk.CTkLabel(card, text="R$ 0,00", font=("Roboto", 36, "bold"), text_color=text_color)
        lbl_value.grid(row=1, column=0, pady=(5, 30))
        
        return lbl_value

    def carregar_dados(self):
        resumo = self.service.get_resumo()
        
        def formatar_moeda(valor):
            # Formatação manual de locale para R$
            return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            
        self.lbl_saldo_atual.configure(text=formatar_moeda(resumo.saldo_atual))
        self.lbl_a_receber.configure(text=formatar_moeda(resumo.a_receber))
        self.lbl_falta_pagar.configure(text=formatar_moeda(resumo.falta_pagar))
        self.lbl_saldo_previsto.configure(text=formatar_moeda(resumo.saldo_previsto))
