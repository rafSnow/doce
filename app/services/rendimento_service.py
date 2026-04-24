from typing import List, Optional

from app.core.formatters import parse_data, normalizar_data_iso, fmt_data
from app.db.transaction import transacao
from app.models.rendimento import Rendimento
from app.services.auditoria_service import AuditoriaService
from app.core.enums import StatusPagamento
from app.core import event_bus


class RendimentoService:
    def salvar(self, rendimento: Rendimento) -> int:
        self._validar_pagamentos(rendimento)

        # Normaliza datas para ISO antes de salvar
        ini_iso = normalizar_data_iso(rendimento.pag_inicial_data) if rendimento.pag_inicial_data else None
        fin_iso = normalizar_data_iso(rendimento.pag_final_data) if rendimento.pag_final_data else None

        with transacao() as conn:
            if rendimento.id:
                conn.execute(
                    """
                    UPDATE rendimento
                       SET cliente_id=?,
                           pag_inicial_valor=?, pag_inicial_data=?, pag_inicial_forma=?, pag_inicial_status=?,
                           pag_final_valor=?, pag_final_data=?, pag_final_forma=?, pag_final_status=?,
                           responsavel=?, pedido_id=?
                     WHERE id=?
                    """,
                    (
                        rendimento.cliente_id,
                        rendimento.pag_inicial_valor,
                        ini_iso,
                        rendimento.pag_inicial_forma,
                        rendimento.pag_inicial_status,
                        rendimento.pag_final_valor,
                        fin_iso,
                        rendimento.pag_final_forma,
                        rendimento.pag_final_status,
                        rendimento.responsavel,
                        rendimento.pedido_id,
                        rendimento.id,
                    ),
                )
                AuditoriaService.registrar(
                    entidade="rendimento",
                    acao="UPDATE",
                    entidade_id=rendimento.id,
                    detalhes={
                        "cliente_id": rendimento.cliente_id,
                        "pag_inicial_valor": rendimento.pag_inicial_valor,
                        "pag_final_valor": rendimento.pag_final_valor,
                        "pedido_id": rendimento.pedido_id,
                    },
                    conn=conn,
                )
            else:
                cur = conn.execute(
                    """
                    INSERT INTO rendimento (
                        cliente_id,
                        pag_inicial_valor, pag_inicial_data, pag_inicial_forma, pag_inicial_status,
                        pag_final_valor, pag_final_data, pag_final_forma, pag_final_status,
                        responsavel, pedido_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        rendimento.cliente_id,
                        rendimento.pag_inicial_valor,
                        ini_iso,
                        rendimento.pag_inicial_forma,
                        rendimento.pag_inicial_status,
                        rendimento.pag_final_valor,
                        fin_iso,
                        rendimento.pag_final_forma,
                        rendimento.pag_final_status,
                        rendimento.responsavel,
                        rendimento.pedido_id,
                    ),
                )
                rendimento.id = cur.lastrowid
                AuditoriaService.registrar(
                    entidade="rendimento",
                    acao="INSERT",
                    entidade_id=rendimento.id,
                    detalhes={
                        "cliente_id": rendimento.cliente_id,
                        "pag_inicial_valor": rendimento.pag_inicial_valor,
                        "pag_final_valor": rendimento.pag_final_valor,
                        "pedido_id": rendimento.pedido_id,
                    },
                    conn=conn,
                )

        event_bus.emit("rendimento.salvo", rendimento_id=rendimento.id)
        return int(rendimento.id)

    def listar(
        self,
        data_inicio: str = "",
        data_fim: str = "",
        status: str = "",
    ) -> List[Rendimento]:
        from app.db.connection import get_connection
        conn = get_connection()
        query = "SELECT * FROM rendimento WHERE 1=1"
        params: list = []

        if data_inicio:
            di_iso = normalizar_data_iso(data_inicio)
            query += """
                AND (
                    (pag_inicial_data IS NOT NULL AND pag_inicial_data >= ?)
                    OR (pag_final_data IS NOT NULL AND pag_final_data >= ?)
                )
            """
            params.extend([di_iso, di_iso])

        if data_fim:
            df_iso = normalizar_data_iso(data_fim)
            query += """
                AND (
                    (pag_inicial_data IS NOT NULL AND pag_inicial_data <= ?)
                    OR (pag_final_data IS NOT NULL AND pag_final_data <= ?)
                )
            """
            params.extend([df_iso, df_iso])

        if status and status != "Todos":
            if status == StatusPagamento.PENDENTE.value:
                query += f" AND (pag_inicial_status = '{StatusPagamento.PENDENTE.value}' OR pag_final_status = '{StatusPagamento.PENDENTE.value}')"
            elif status == StatusPagamento.RECEBIDO.value:
                query += f" AND pag_inicial_status = '{StatusPagamento.RECEBIDO.value}' AND pag_final_status = '{StatusPagamento.RECEBIDO.value}'"

        query += " ORDER BY id DESC"

        rows = conn.execute(query, params).fetchall()
        return [self._row_to_model(row) for row in rows]

    def get_by_id(self, rendimento_id: int) -> Optional[Rendimento]:
        from app.db.connection import get_connection
        conn = get_connection()
        row = conn.execute("SELECT * FROM rendimento WHERE id=?", (rendimento_id,)).fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def obter_por_pedido(self, pedido_id: int) -> Optional[Rendimento]:
        from app.db.connection import get_connection
        conn = get_connection()
        row = conn.execute("SELECT * FROM rendimento WHERE pedido_id=?", (pedido_id,)).fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def excluir(self, rendimento_id: int) -> None:
        with transacao() as conn:
            conn.execute("DELETE FROM rendimento WHERE id=?", (rendimento_id,))
            AuditoriaService.registrar("rendimento", "DELETE", rendimento_id, conn=conn)
        event_bus.emit("rendimento.excluido", rendimento_id=rendimento_id)

    def _row_to_model(self, row) -> Rendimento:
        return Rendimento(
            id=row["id"],
            cliente_id=row["cliente_id"],
            pag_inicial_valor=row["pag_inicial_valor"],
            pag_inicial_data=fmt_data(row["pag_inicial_data"]),
            pag_inicial_forma=row["pag_inicial_forma"],
            pag_inicial_status=row["pag_inicial_status"],
            pag_final_valor=row["pag_final_valor"],
            pag_final_data=fmt_data(row["pag_final_data"]),
            pag_final_forma=row["pag_final_forma"],
            pag_final_status=row["pag_final_status"],
            responsavel=row["responsavel"],
            pedido_id=row["pedido_id"],
        )

    def _validar_pagamentos(self, rendimento: Rendimento) -> None:
        self._validar_pagamento(
            "inicial",
            rendimento.pag_inicial_valor,
            rendimento.pag_inicial_status,
            rendimento.pag_inicial_data,
        )
        self._validar_pagamento(
            "final",
            rendimento.pag_final_valor,
            rendimento.pag_final_status,
            rendimento.pag_final_data,
        )

    def _validar_pagamento(self, etapa: str, valor: float, status: str, data: str | None) -> None:
        if status not in (StatusPagamento.PENDENTE.value, StatusPagamento.RECEBIDO.value):
            raise ValueError(f"Status de rendimento {etapa} inválido: {status}")
        if float(valor or 0.0) < 0:
            raise ValueError(f"Valor de rendimento {etapa} não pode ser negativo")

        if status == StatusPagamento.RECEBIDO.value and not data:
            raise ValueError(f"Rendimento {etapa} recebido exige data de pagamento")

        if data:
            self._validar_data(data, etapa)

    def _validar_data(self, data: str, etapa: str) -> None:
        try:
            parse_data(data, campo="Data", obrigatorio=True)
        except ValueError as exc:
            raise ValueError(f"Data de rendimento {etapa} inválida: {data}") from exc
