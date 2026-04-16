from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from app.db.connection import get_connection


class AuditoriaService:
    @staticmethod
    def registrar(
        entidade: str,
        acao: str,
        entidade_id: int | None = None,
        detalhes: dict[str, Any] | None = None,
        conn=None,
    ) -> None:
        conexao = conn or get_connection()
        payload = json.dumps(detalhes or {}, ensure_ascii=False)
        conexao.execute(
            """
            INSERT INTO auditoria (entidade, entidade_id, acao, detalhes, criado_em)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                entidade,
                entidade_id,
                acao,
                payload,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
