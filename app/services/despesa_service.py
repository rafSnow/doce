from typing import Dict, List, Optional

from app.core.formatters import parse_data, normalizar_data_iso, fmt_data
from app.db.transaction import transacao
from app.models.despesa import Despesa
from app.services.auditoria_service import AuditoriaService
from app.core.enums import StatusPagamento, CategoriaDespesa
from app.core import event_bus


class DespesaService:
    def salvar(self, despesa: Despesa) -> int:
        self._validar_pagamento(despesa)

        # Normaliza datas para ISO antes de salvar
        data_iso = normalizar_data_iso(despesa.data) if despesa.data else None
        dt_pag_iso = normalizar_data_iso(despesa.data_pagamento_final) if despesa.data_pagamento_final else None

        with transacao() as conn:
            if despesa.id:
                conn.execute(
                    """
                    UPDATE despesa
                       SET data=?, valor=?, descricao=?, categoria=?, responsavel=?,
                           status=?, forma_pagamento=?, data_pagamento_final=?
                     WHERE id=?
                    """,
                    (
                        data_iso,
                        despesa.valor,
                        despesa.descricao,
                        despesa.categoria,
                        despesa.responsavel,
                        despesa.status,
                        despesa.forma_pagamento,
                        dt_pag_iso,
                        despesa.id,
                    ),
                )
                AuditoriaService.registrar(
                    entidade="despesa",
                    acao="UPDATE",
                    entidade_id=despesa.id,
                    detalhes={
                        "valor": despesa.valor,
                        "categoria": despesa.categoria,
                        "status": despesa.status,
                    },
                    conn=conn,
                )
            else:
                cur = conn.execute(
                    """
                    INSERT INTO despesa (
                        data, valor, descricao, categoria, responsavel,
                        status, forma_pagamento, data_pagamento_final
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        data_iso,
                        despesa.valor,
                        despesa.descricao,
                        despesa.categoria,
                        despesa.responsavel,
                        despesa.status,
                        despesa.forma_pagamento,
                        dt_pag_iso,
                    ),
                )
                despesa.id = cur.lastrowid
                AuditoriaService.registrar(
                    entidade="despesa",
                    acao="INSERT",
                    entidade_id=despesa.id,
                    detalhes={
                        "valor": despesa.valor,
                        "categoria": despesa.categoria,
                        "status": despesa.status,
                    },
                    conn=conn,
                )

        event_bus.emit("despesa.salva", despesa_id=despesa.id)
        return int(despesa.id)

    def listar(
        self,
        data_inicio: str = "",
        data_fim: str = "",
        categoria: str = "",
        status: str = "",
    ) -> List[Despesa]:
        from app.db.connection import get_connection
        conn = get_connection()
        query = "SELECT * FROM despesa WHERE 1=1"
        params: list = []

        if data_inicio:
            query += " AND data >= ?"
            params.append(normalizar_data_iso(data_inicio))

        if data_fim:
            query += " AND data <= ?"
            params.append(normalizar_data_iso(data_fim))

        if categoria and categoria != "Todos":
            query += " AND categoria = ?"
            params.append(categoria)

        if status and status != "Todos":
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY data DESC, id DESC"

        rows = conn.execute(query, params).fetchall()
        return [self._row_to_model(row) for row in rows]

    def get_by_id(self, despesa_id: int) -> Optional[Despesa]:
        from app.db.connection import get_connection
        conn = get_connection()
        row = conn.execute("SELECT * FROM despesa WHERE id=?", (despesa_id,)).fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def excluir(self, despesa_id: int) -> None:
        with transacao() as conn:
            conn.execute("DELETE FROM despesa WHERE id=?", (despesa_id,))
            AuditoriaService.registrar("despesa", "DELETE", despesa_id, conn=conn)
        event_bus.emit("despesa.excluida", despesa_id=despesa_id)

    def total_por_categoria(
        self,
        data_inicio: str = "",
        data_fim: str = "",
        status: str = "",
        categoria: str = "",
    ) -> Dict[str, float]:
        from app.db.connection import get_connection
        conn = get_connection()
        query = "SELECT categoria, SUM(valor) AS total FROM despesa WHERE 1=1"
        params: list = []

        if data_inicio:
            query += " AND data >= ?"
            params.append(normalizar_data_iso(data_inicio))

        if data_fim:
            query += " AND data <= ?"
            params.append(normalizar_data_iso(data_fim))

        if status and status != "Todos":
            query += " AND status = ?"
            params.append(status)

        if categoria and categoria != "Todos":
            query += " AND categoria = ?"
            params.append(categoria)

        query += " GROUP BY categoria"

        rows = conn.execute(query, params).fetchall()
        totais: Dict[str, float] = {
            CategoriaDespesa.INSUMOS.value: 0.0,
            CategoriaDespesa.INVESTIMENTOS.value: 0.0,
            CategoriaDespesa.OUTROS.value: 0.0
        }

        for row in rows:
            cat_row = row["categoria"] or CategoriaDespesa.OUTROS.value
            totais[cat_row] = float(row["total"] or 0.0)

        return totais

    def _row_to_model(self, row) -> Despesa:
        return Despesa(
            id=row["id"],
            data=fmt_data(row["data"]),
            valor=row["valor"],
            descricao=row["descricao"],
            categoria=row["categoria"],
            responsavel=row["responsavel"],
            status=row["status"],
            forma_pagamento=row["forma_pagamento"],
            data_pagamento_final=fmt_data(row["data_pagamento_final"]),
        )

    def _validar_pagamento(self, despesa: Despesa) -> None:
        if despesa.status not in (StatusPagamento.PENDENTE.value, StatusPagamento.PAGO.value):
            raise ValueError(f"Status de despesa inválido: {despesa.status}")
        if float(despesa.valor or 0.0) < 0:
            raise ValueError("Valor da despesa não pode ser negativo")

        if despesa.status == StatusPagamento.PAGO.value and not despesa.data_pagamento_final:
            raise ValueError("Despesa com status 'Pago' exige data de pagamento final")

        if despesa.data:
            self._validar_data(despesa.data, "despesa")
        if despesa.data_pagamento_final:
            self._validar_data(despesa.data_pagamento_final, "pagamento final")

    def _validar_data(self, data: str, campo: str) -> None:
        try:
            parse_data(data, campo="Data", obrigatorio=True)
        except ValueError as exc:
            raise ValueError(f"Data inválida para {campo}: {data}") from exc
