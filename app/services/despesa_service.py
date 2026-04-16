from typing import Dict, List, Optional
from datetime import datetime

from app.db.connection import get_connection
from app.models.despesa import Despesa
from app.services.auditoria_service import AuditoriaService


class DespesaService:
    def salvar(self, despesa: Despesa) -> int:
        conn = get_connection()
        self._validar_pagamento(despesa)

        if despesa.id:
            conn.execute(
                """
                UPDATE despesa
                   SET data=?, valor=?, descricao=?, categoria=?, responsavel=?,
                       status=?, forma_pagamento=?, data_pagamento_final=?
                 WHERE id=?
                """,
                (
                    despesa.data,
                    despesa.valor,
                    despesa.descricao,
                    despesa.categoria,
                    despesa.responsavel,
                    despesa.status,
                    despesa.forma_pagamento,
                    despesa.data_pagamento_final,
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
                    despesa.data,
                    despesa.valor,
                    despesa.descricao,
                    despesa.categoria,
                    despesa.responsavel,
                    despesa.status,
                    despesa.forma_pagamento,
                    despesa.data_pagamento_final,
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

        conn.commit()
        return int(despesa.id)

    def listar(
        self,
        data_inicio: str = "",
        data_fim: str = "",
        categoria: str = "",
        status: str = "",
    ) -> List[Despesa]:
        conn = get_connection()
        query = "SELECT * FROM despesa WHERE 1=1"
        params: list = []

        if data_inicio:
            query += " AND data >= ?"
            params.append(data_inicio)

        if data_fim:
            query += " AND data <= ?"
            params.append(data_fim)

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
        conn = get_connection()
        row = conn.execute("SELECT * FROM despesa WHERE id=?", (despesa_id,)).fetchone()
        if not row:
            return None
        return self._row_to_model(row)

    def excluir(self, despesa_id: int) -> None:
        conn = get_connection()
        conn.execute("DELETE FROM despesa WHERE id=?", (despesa_id,))
        AuditoriaService.registrar("despesa", "DELETE", despesa_id, conn=conn)
        conn.commit()

    def total_por_categoria(
        self,
        data_inicio: str = "",
        data_fim: str = "",
        status: str = "",
        categoria: str = "",
    ) -> Dict[str, float]:
        conn = get_connection()
        query = "SELECT categoria, SUM(valor) AS total FROM despesa WHERE 1=1"
        params: list = []

        if data_inicio:
            query += " AND data >= ?"
            params.append(data_inicio)

        if data_fim:
            query += " AND data <= ?"
            params.append(data_fim)

        if status and status != "Todos":
            query += " AND status = ?"
            params.append(status)

        if categoria and categoria != "Todos":
            query += " AND categoria = ?"
            params.append(categoria)

        query += " GROUP BY categoria"

        rows = conn.execute(query, params).fetchall()
        totais: Dict[str, float] = {"Insumos": 0.0, "Investimentos": 0.0, "Outros": 0.0}

        for row in rows:
            categoria = row["categoria"] or "Outros"
            totais[categoria] = float(row["total"] or 0.0)

        return totais

    def _row_to_model(self, row) -> Despesa:
        return Despesa(
            id=row["id"],
            data=row["data"],
            valor=row["valor"],
            descricao=row["descricao"],
            categoria=row["categoria"],
            responsavel=row["responsavel"],
            status=row["status"],
            forma_pagamento=row["forma_pagamento"],
            data_pagamento_final=row["data_pagamento_final"],
        )

    def _validar_pagamento(self, despesa: Despesa) -> None:
        if despesa.status not in ("Pendente", "Pago"):
            raise ValueError(f"Status de despesa inválido: {despesa.status}")
        if float(despesa.valor or 0.0) < 0:
            raise ValueError("Valor da despesa não pode ser negativo")

        if despesa.status == "Pago" and not despesa.data_pagamento_final:
            raise ValueError("Despesa com status 'Pago' exige data de pagamento final")

        if despesa.data:
            self._validar_data(despesa.data, "despesa")
        if despesa.data_pagamento_final:
            self._validar_data(despesa.data_pagamento_final, "pagamento final")

    def _validar_data(self, data: str, campo: str) -> None:
        for formato in ("%d/%m/%Y", "%Y-%m-%d"):
            try:
                datetime.strptime(data.strip(), formato)
                return
            except ValueError:
                continue
        raise ValueError(f"Data inválida para {campo}: {data}")
