import customtkinter as ctk

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Dolce Neves - Gestão para Confeitaria")
        self.geometry("1024x768")
        self.minsize(800, 600)
        
        # Configuração do grid principal
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Configuração de cores e temas (baseado na arquitetura)
        self.primary_color = "#C8866B"

        self._build_sidebar()
        self._build_content_area()

    def _build_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(7, weight=1) # Empurra conteúdo para cima

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Dolce Neves", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))

        # Botões do menu
        self.btn_dashboard = ctk.CTkButton(self.sidebar_frame, text="Dashboard", fg_color="transparent", 
                                           text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                           command=self.show_dashboard_view)
        self.btn_dashboard.grid(row=1, column=0, padx=20, pady=10, sticky="w")

        self.btn_insumos = ctk.CTkButton(self.sidebar_frame, text="Insumos", fg_color="transparent", 
                                         text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                         command=self.show_insumos_view)
        self.btn_insumos.grid(row=2, column=0, padx=20, pady=10, sticky="w")

        self.btn_produtos = ctk.CTkButton(self.sidebar_frame, text="Produtos", fg_color="transparent", 
                                          text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                          command=self.show_produtos_view)
        self.btn_produtos.grid(row=3, column=0, padx=20, pady=10, sticky="w")

        self.btn_pedidos = ctk.CTkButton(self.sidebar_frame, text="Pedidos", fg_color="transparent", 
                                         text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                         command=self.show_pedidos_view)
        self.btn_pedidos.grid(row=4, column=0, padx=20, pady=10, sticky="w")

        self.btn_financeiro = ctk.CTkButton(self.sidebar_frame, text="Financeiro", fg_color="transparent", 
                                            text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                            command=self.show_financeiro_view)
        self.btn_financeiro.grid(row=5, column=0, padx=20, pady=10, sticky="w")

        self.btn_config = ctk.CTkButton(self.sidebar_frame, text="Configurações", fg_color="transparent", 
                                        text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                        command=self.show_config_view)
        self.btn_config.grid(row=6, column=0, padx=20, pady=10, sticky="w")

    def _build_content_area(self):
        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        self.current_view_label = ctk.CTkLabel(self.content_frame, text="Bem-vinda!\nSelecione uma opção no menu lateral.", font=ctk.CTkFont(size=24))
        self.current_view_label.grid(row=0, column=0)

    def _clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_dashboard_view(self):
        self._clear_content()
        from app.views.dashboard_view import DashboardView
        view = DashboardView(self.content_frame)
        view.grid(row=0, column=0, sticky="nsew")

    def show_insumos_view(self):
        self._clear_content()
        from app.views.insumos_view import InsumosView
        view = InsumosView(self.content_frame)
        view.grid(row=0, column=0, sticky="nsew")

    def show_produtos_view(self):
        self._clear_content()
        from app.views.produtos_view import ProdutosView
        view = ProdutosView(self.content_frame)
        view.grid(row=0, column=0, sticky="nsew")

    def show_pedidos_view(self):
        self._clear_content()
        from app.views.pedidos_view import PedidosView
        view = PedidosView(self.content_frame)
        view.grid(row=0, column=0, sticky="nsew")

    def show_financeiro_view(self):
        self._clear_content()
        lbl = ctk.CTkLabel(self.content_frame, text="Tela do Financeiro (Em breve)", font=ctk.CTkFont(size=24))
        lbl.grid(row=0, column=0)

    def show_config_view(self):
        self._clear_content()
        lbl = ctk.CTkLabel(self.content_frame, text="Tela de Configurações (Em breve)", font=ctk.CTkFont(size=24))
        lbl.grid(row=0, column=0)
