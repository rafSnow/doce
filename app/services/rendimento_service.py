from typing import List, Optional
from datetime import datetime

from app.db.connection import get_connection
from app.models.rendimento import Rendimento
from app.services.auditoria_service import AuditoriaService


class RendimentoService:
    def salvar(self, rendimento: Rendimento) -> int:
        conn = get_connection()
        self._validar_pagamentos(rendimento)

        if rendimento.id:
            conn.execute(
                """
                UPDATE rendimento
                   SET cliente_id=?,
                       pag_inicial_valor=?, pag_inicial_data=?, pag_inicial_forma=?, pag_inicial_status=?,
                       pag_final_valor=?, pag_final_data=?, pag_final_forma=?, pag_final_status=?,
                       responsavel=?
                 WHERE id=?
                """,
                (
                    rendimento.cliente_id,
                    rendimento.pag_inicial_valor,
                    rendimento.pag_inicial_data,
                    rendimento.pag_inicial_forma,
                    rendimento.pag_inicial_status,
                    rendimento.pag_final_valor,
                    rendimento.pag_final_data,
                    rendimento.pag_final_forma,
                    rendimento.pag_final_status,
                    rendimento.responsavel,
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
                    responsavel
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    rendimento.cliente_id,
                    rendimento.pag_inicial_valor,
                    rendimento.pag_inicial_data,
                    rendimento.pag_inicial_forma,
                    rendimento.pag_inicial_status,
                    rendimento.pag_final_valor,
                    rendimento.pag_final_data,
                    rendimento.pag_final_forma,
                    rendimento.pag_final_status,
                    rendimento.responsavel,
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
                },
                conn=conn,
            )

        conn.commit()
        return int(rendimento.id)

    def listar(
        self,
        data_inicio: str = "",
        data_fim: str = "",
        status: str = "",
    ) -> List[Rendimento]:
        conn = get_connection()
        query = "SELECT * FROM rendimento WHERE 1=1"
        params: list = []

        if data_inicio:
            query += """
                AND (
                    (pag_inicial_data IS NOT NULL AND pag_inicial_data >= ?)
                    OR (pag_final_data IS NOT NULL AND pag_final_data >= ?)
                )
            """
            params.extend([data_inicio, data_inicio])

        if data_fim:
            query += """
                AND (
                    (pag_inicial_data IS NOT NULL AND pag_inicial_data <= ?)
                    OR (pag_final_data IS NOT NULL AND pag_final_data <= ?)
                )
            """
            params.extend([data_fim, data_fim])

        if status and status != "Todos":
            if status == "Pendente":
                query += " AND (pag_inicial_status = 'Pendente' OR pag_final_status = 'Pendente')"
            elif status == "Recebido":
                query += " AND pag_inicial_status = 'Recebido' AND pag_final_status = 'Recebido'"

        query += " ORDER BY id DESC"

        rows = conn.execute(query, params).fetchall()
        return [self._row_to_model(row) for row in rows]

    def get_by_id(self, rendimento_id: int) -> Optional[Rendimento]:
        conn = get_connection()
        row = conn.execute("SELECT * FROM rendimento WHERE id=?", (rendimento_id,)).fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def excluir(self, rendimento_id: int) -> None:
        conn = get_connection()
        conn.execute("DELETE FROM rendimento WHERE id=?", (rendimento_id,))
        AuditoriaService.registrar("rendimento", "DELETE", rendimento_id, conn=conn)
        conn.commit()

    def _row_to_model(self, row) -> Rendimento:
        return Rendimento(
            id=row["id"],
            cliente_id=row["cliente_id"],
            pag_inicial_valor=row["pag_inicial_valor"],
            pag_inicial_data=row["pag_inicial_data"],
            pag_inicial_forma=row["pag_inicial_forma"],
            pag_inicial_status=row["pag_inicial_status"],
            pag_final_valor=row["pag_final_valor"],
            pag_final_data=row["pag_final_data"],
            pag_final_forma=row["pag_final_forma"],
            pag_final_status=row["pag_final_status"],
            responsavel=row["responsavel"],
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
        if status not in ("Pendente", "Recebido"):
            raise ValueError(f"Status de rendimento {etapa} inválido: {status}")
        if float(valor or 0.0) < 0:
            raise ValueError(f"Valor de rendimento {etapa} não pode ser negativo")

        if status == "Recebido" and not data:
            raise ValueError(f"Rendimento {etapa} recebido exige data de pagamento")

        if data:
            self._validar_data(data, etapa)

    def _validar_data(self, data: str, etapa: str) -> None:
        for formato in ("%d/%m/%Y", "%Y-%m-%d"):
            try:
                datetime.strptime(data.strip(), formato)
                return
            except ValueError:
                continue
        raise ValueError(f"Data de rendimento {etapa} inválida: {data}")