import os
import sqlite3
import shutil
from datetime import datetime

from app.db.transaction import transacao
from app.db.connection import get_db_path, reset_connection


class ConfiguracaoService:
    CHAVE_NOME_ESTABELECIMENTO = "nome_estabelecimento"
    CHAVE_MARKUP_PADRAO = "markup_padrao"
    CHAVE_RESPONSAVEL_PADRAO = "responsavel_padrao"
    NOME_PADRAO = "Dolce Neves"

    def get_nome_estabelecimento(self) -> str:
        from app.db.connection import get_connection
        conn = get_connection()
        row = conn.execute(
            "SELECT valor FROM configuracao WHERE chave=?",
            (self.CHAVE_NOME_ESTABELECIMENTO,),
        ).fetchone()

        if not row or not row["valor"]:
            return self.NOME_PADRAO

        return str(row["valor"]).strip() or self.NOME_PADRAO

    def salvar_nome_estabelecimento(self, nome: str) -> None:
        with transacao() as conn:
            conn.execute(
                """
                INSERT INTO configuracao (chave, valor)
                VALUES (?, ?)
                ON CONFLICT(chave) DO UPDATE SET valor=excluded.valor
                """,
                (self.CHAVE_NOME_ESTABELECIMENTO, nome.strip()),
            )

    def get_markup_padrao(self) -> float:
        from app.db.connection import get_connection
        conn = get_connection()
        row = conn.execute("SELECT valor FROM configuracao WHERE chave=?", (self.CHAVE_MARKUP_PADRAO,)).fetchone()
        try:
            return float(row["valor"]) if row and row["valor"] else 0.0
        except ValueError:
            return 0.0

    def salvar_markup_padrao(self, valor: float) -> None:
        with transacao() as conn:
            conn.execute(
                "INSERT INTO configuracao (chave, valor) VALUES (?, ?) ON CONFLICT(chave) DO UPDATE SET valor=excluded.valor",
                (self.CHAVE_MARKUP_PADRAO, str(valor))
            )

    def get_responsavel_padrao(self) -> str:
        from app.db.connection import get_connection
        conn = get_connection()
        row = conn.execute("SELECT valor FROM configuracao WHERE chave=?", (self.CHAVE_RESPONSAVEL_PADRAO,)).fetchone()
        return str(row["valor"]) if row and row["valor"] else ""

    def salvar_responsavel_padrao(self, nome: str) -> None:
        with transacao() as conn:
            conn.execute(
                "INSERT INTO configuracao (chave, valor) VALUES (?, ?) ON CONFLICT(chave) DO UPDATE SET valor=excluded.valor",
                (self.CHAVE_RESPONSAVEL_PADRAO, nome.strip())
            )

    def realizar_backup(self, destino_arquivo: str) -> str:
        destino_arquivo = (destino_arquivo or "").strip()
        if not destino_arquivo:
            raise ValueError("Informe o caminho de destino do backup.")

        pasta_destino = os.path.dirname(destino_arquivo)
        if pasta_destino:
            os.makedirs(pasta_destino, exist_ok=True)

        from app.db.connection import get_connection
        conn = get_connection()
        conn.commit()  # Garante flush antes da cópia do arquivo.

        with sqlite3.connect(destino_arquivo) as conn_destino:
            conn.backup(conn_destino)

        return destino_arquivo

    def restaurar_backup(self, origem_arquivo: str) -> None:
        """Restaura o banco de dados a partir de um arquivo de backup (REGRA CF-05)."""
        if not os.path.exists(origem_arquivo):
            raise FileNotFoundError(f"Arquivo não encontrado: {origem_arquivo}")

        # 1. Valida se é um SQLite válido
        try:
            with sqlite3.connect(origem_arquivo) as temp_conn:
                temp_conn.execute("SELECT 1 FROM configuracao LIMIT 1")
        except Exception as e:
            raise ValueError(f"O arquivo selecionado não é um backup válido do sistema.\nErro: {e}")

        db_atual = get_db_path()
        backup_seguranca = db_atual + f".pre_restauracao_{datetime.now():%Y%m%d_%H%M%S}.bak"

        try:
            # 2. Backup automático de segurança
            shutil.copy2(db_atual, backup_seguranca)

            # 3. Fecha conexões
            reset_connection()

            # 4. Sobrescreve banco
            shutil.copy2(origem_arquivo, db_atual)

        except Exception as e:
            # Tenta reverter se algo falhou no passo 4
            if os.path.exists(backup_seguranca):
                shutil.copy2(backup_seguranca, db_atual)
            raise RuntimeError(f"Falha crítica na restauração: {e}")
        finally:
            # Reabre a conexão (mesmo se falhou, tenta garantir que o app continue com o que tiver)
            from app.db.connection import get_connection
            get_connection()
