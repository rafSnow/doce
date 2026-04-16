import customtkinter as ctk
import logging
from pathlib import Path
from tkinter import messagebox

from app.db.connection import get_db_path
from app.db.schema import create_tables
from app.views.main_window import MainWindow


def _configurar_logging() -> None:
    base_dir = Path(get_db_path()).resolve().parent
    log_path = base_dir / "doce.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[logging.FileHandler(log_path, encoding="utf-8")],
    )

def main():
    _configurar_logging()

    try:
        # 1. Inicializa ou atualiza o banco de dados
        create_tables()

        # 2. Configuração do tema visual (CustomTkinter)
        ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
        ctk.set_default_color_theme("blue")  # Pode ser substituído posteriormente por um tema customizado (ex: json)

        # 3. Inicia e roda a janela principal
        app = MainWindow()
        app.mainloop()
    except Exception:
        logging.exception("Falha não tratada na inicialização/execução da aplicação")
        messagebox.showerror(
            "Erro inesperado",
            "Ocorreu um erro inesperado.\n\n"
            "Consulte o arquivo de log 'doce.log' na pasta do banco para mais detalhes.",
        )
        raise

if __name__ == "__main__":
    main()
