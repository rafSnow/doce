import os
import sqlite3

from app.db.transaction import transacao


class ConfiguracaoService:
    CHAVE_NOME_ESTABELECIMENTO = "nome_estabelecimento"
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
