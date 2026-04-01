import customtkinter as ctk
from app.db.schema import create_tables
from app.views.main_window import MainWindow

def main():
    # 1. Inicializa ou atualiza o banco de dados
    create_tables()

    # 2. Configuração do tema visual (CustomTkinter)
    ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Pode ser substituído posteriormente por um tema customizado (ex: json)

    # 3. Inicia e roda a janela principal
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    main()
