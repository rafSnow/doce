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

    @staticmethod
    def listar(
        entidade: str = "Todos",
        data_inicio: str = "",
        data_fim: str = "",
        acao: str = "",
    ) -> list[dict[str, Any]]:
        from app.db.connection import get_connection
        from app.core.formatters import normalizar_data_iso

        conn = get_connection()
        query = "SELECT * FROM auditoria WHERE 1=1"
        params = []

        if entidade and entidade != "Todos":
            query += " AND entidade = ?"
            params.append(entidade.lower())

        if data_inicio:
            try:
                # Normaliza para YYYY-MM-DD e adiciona o início do dia
                iso_ini = normalizar_data_iso(data_inicio) + " 00:00:00"
                query += " AND criado_em >= ?"
                params.append(iso_ini)
            except ValueError:
                pass

        if data_fim:
            try:
                # Normaliza para YYYY-MM-DD e adiciona o fim do dia
                iso_fim = normalizar_data_iso(data_fim) + " 23:59:59"
                query += " AND criado_em <= ?"
                params.append(iso_fim)
            except ValueError:
                pass

        if acao:
            query += " AND acao LIKE ?"
            params.append(f"%{acao}%")

        query += " ORDER BY criado_em DESC"
        
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    def obter_entidades_unicas() -> list[str]:
        from app.db.connection import get_connection
        conn = get_connection()
        rows = conn.execute("SELECT DISTINCT entidade FROM auditoria ORDER BY entidade").fetchall()
        return [r["entidade"] for r in rows]
