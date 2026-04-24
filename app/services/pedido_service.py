from typing import List, Optional
from datetime import datetime

from app.core.formatters import normalizar_data_iso, parse_data, fmt_data
from app.db.transaction import transacao
from app.services.cliente_service import ClienteService
from app.models.pedido import Pedido
from app.models.pedido_item import PedidoItem
from app.services.auditoria_service import AuditoriaService
from app.core.enums import StatusPagamento
from app.core import event_bus

class PedidoService:
    def calcular_lucro_pedido(self, pedido_id: int) -> float:
        from app.db.connection import get_connection
        conn = get_connection()
        row = conn.execute(
            """
            SELECT
                COALESCE(SUM((pi.preco_unitario_snapshot - pr.custo_unitario) * pi.quantidade), 0) AS lucro
            FROM pedido_item pi
            JOIN produto pr ON pr.id = pi.produto_id
            WHERE pi.pedido_id = ?
            """,
            (pedido_id,),
        ).fetchone()
        return float((row["lucro"] if row else 0.0) or 0.0)

    def calcular_lucro_total_vendas(self, data_inicio: str = "", data_fim: str = "") -> float:
        from app.db.connection import get_connection
        conn = get_connection()
        rows = conn.execute(
            """
            SELECT
                p.data_pedido,
                pi.quantidade,
                pi.preco_unitario_snapshot,
                pr.custo_unitario
            FROM pedido_item pi
            JOIN pedido p ON p.id = pi.pedido_id
            JOIN produto pr ON pr.id = pi.produto_id
            """
        ).fetchall()

        inicio = self._parse_data(data_inicio)
        fim = self._parse_data(data_fim)
        lucro_total = 0.0

        for row in rows:
            data_pedido = self._parse_data(row["data_pedido"])
            if not self._esta_no_periodo(data_pedido, inicio, fim):
                continue

            quantidade = float(row["quantidade"] or 0.0)
            preco_venda = float(row["preco_unitario_snapshot"] or 0.0)
            custo_unitario = float(row["custo_unitario"] or 0.0)
            lucro_total += (preco_venda - custo_unitario) * quantidade

        return lucro_total

    def salvar(self, pedido: Pedido) -> int:
        cliente_service = ClienteService()

        cliente_nome = (pedido.cliente_nome or "").strip()
        if not cliente_nome:
            raise ValueError("Informe o nome do cliente.")

        cliente = cliente_service.obter_ou_criar_por_nome(cliente_nome)
        pedido.cliente_id = cliente.id if cliente else None
        pedido.cliente_nome = cliente.nome if cliente else (pedido.cliente_nome or "").strip()

        self._validar_pagamentos_pedido(pedido)

        # Normaliza datas para ISO antes de salvar
        dp_iso  = normalizar_data_iso(pedido.data_pedido) if pedido.data_pedido else None
        de_iso  = normalizar_data_iso(pedido.data_entrega) if pedido.data_entrega else None
        pi_iso  = normalizar_data_iso(pedido.pag_inicial_data) if pedido.pag_inicial_data else None
        pf_iso  = normalizar_data_iso(pedido.pag_final_data) if pedido.pag_final_data else None

        with transacao() as conn:
            total = 0.0
            momento_snapshot = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for item in pedido.itens:
                # Se o snapshot está zerado ou nulo, pegamos o preço atual do produto.
                if item.preco_unitario_snapshot <= 0:
                    row = conn.execute("SELECT preco_venda_unitario FROM produto WHERE id=?", (item.produto_id,)).fetchone()
                    if row:
                        item.preco_unitario_snapshot = row["preco_venda_unitario"]
                item.valor_item = item.quantidade * item.preco_unitario_snapshot
                item.data_snapshot = item.data_snapshot or momento_snapshot
                total += item.valor_item

            pedido.valor_total = total

            acao = "INSERT"
            if pedido.id:
                acao = "UPDATE"
                conn.execute("""
                    UPDATE pedido SET
                        cliente_id=?, cliente_nome=?, data_pedido=?, data_entrega=?, valor_total=?,
                        pag_inicial_valor=?, pag_inicial_data=?, pag_inicial_forma=?, pag_inicial_status=?,
                        pag_final_valor=?, pag_final_data=?, pag_final_forma=?, pag_final_status=?,
                        responsavel=?
                    WHERE id=?
                """, (
                    pedido.cliente_id, pedido.cliente_nome, dp_iso, de_iso, pedido.valor_total,
                    pedido.pag_inicial_valor, pi_iso, pedido.pag_inicial_forma, pedido.pag_inicial_status,
                    pedido.pag_final_valor, pf_iso, pedido.pag_final_forma, pedido.pag_final_status,
                    pedido.responsavel, pedido.id
                ))
                # Remove itens antigos e recria.
                conn.execute("DELETE FROM pedido_item WHERE pedido_id=?", (pedido.id,))
            else:
                cur = conn.execute("""
                    INSERT INTO pedido (
                        cliente_id, cliente_nome, data_pedido, data_entrega, valor_total,
                        pag_inicial_valor, pag_inicial_data, pag_inicial_forma, pag_inicial_status,
                        pag_final_valor, pag_final_data, pag_final_forma, pag_final_status,
                        responsavel
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    pedido.cliente_id, pedido.cliente_nome, dp_iso, de_iso, pedido.valor_total,
                    pedido.pag_inicial_valor, pi_iso, pedido.pag_inicial_forma, pedido.pag_inicial_status,
                    pedido.pag_final_valor, pf_iso, pedido.pag_final_forma, pedido.pag_final_status,
                    pedido.responsavel
                ))
                pedido.id = cur.lastrowid

            for item in pedido.itens:
                conn.execute("""
                    INSERT INTO pedido_item (
                        pedido_id,
                        produto_id,
                        quantidade,
                        preco_unitario_snapshot,
                        data_snapshot,
                        valor_item
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    pedido.id,
                    item.produto_id,
                    item.quantidade,
                    item.preco_unitario_snapshot,
                    item.data_snapshot,
                    item.valor_item,
                ))

            AuditoriaService.registrar(
                entidade="pedido",
                acao=acao,
                entidade_id=pedido.id,
                detalhes={
                    "cliente_nome": pedido.cliente_nome,
                    "valor_total": pedido.valor_total,
                    "itens": len(pedido.itens),
                    "responsavel": pedido.responsavel,
                },
                conn=conn,
            )

        event_bus.emit("pedido.salvo", pedido_id=pedido.id)
        return pedido.id

    def listar(self, cliente_nome: str = "", status_pagamento: str = "Todos") -> List[Pedido]:
        from app.db.connection import get_connection
        conn = get_connection()
        query = """
            SELECT p.*
            FROM pedido p
            WHERE 1=1
        """
        params = []
        if cliente_nome:
            query += " AND p.cliente_nome LIKE ?"
            params.append(f"%{cliente_nome}%")
            
        if status_pagamento != "Todos":
            if status_pagamento == StatusPagamento.PENDENTE.value:
                query += f" AND (p.pag_inicial_status = '{StatusPagamento.PENDENTE.value}' OR p.pag_final_status = '{StatusPagamento.PENDENTE.value}')"
            elif status_pagamento == StatusPagamento.RECEBIDO.value:
                query += f" AND p.pag_inicial_status = '{StatusPagamento.RECEBIDO.value}' AND p.pag_final_status = '{StatusPagamento.RECEBIDO.value}'"
                
        query += " ORDER BY p.data_pedido DESC, p.id DESC"
        
        rows = conn.execute(query, params).fetchall()
        result = []
        for r in rows:
            ped = Pedido(
                id=r["id"],
                cliente_id=r["cliente_id"],
                cliente_nome=r["cliente_nome"],
                data_pedido=fmt_data(r["data_pedido"]),
                data_entrega=fmt_data(r["data_entrega"]),
                valor_total=r["valor_total"],
                pag_inicial_valor=r["pag_inicial_valor"],
                pag_inicial_data=fmt_data(r["pag_inicial_data"]),
                pag_inicial_forma=r["pag_inicial_forma"],
                pag_inicial_status=r["pag_inicial_status"],
                pag_final_valor=r["pag_final_valor"],
                pag_final_data=fmt_data(r["pag_final_data"]),
                pag_final_forma=r["pag_final_forma"],
                pag_final_status=r["pag_final_status"],
                responsavel=r["responsavel"]
            )
            result.append(ped)
        return result

    def get_by_id(self, id: int) -> Optional[Pedido]:
        from app.db.connection import get_connection
        conn = get_connection()
        r = conn.execute("""
            SELECT p.*
            FROM pedido p
            WHERE p.id=?
        """, (id,)).fetchone()
        
        if not r:
            return None
            
        ped = Pedido(
            id=r["id"],
            cliente_id=r["cliente_id"],
            cliente_nome=r["cliente_nome"],
            data_pedido=fmt_data(r["data_pedido"]),
            data_entrega=fmt_data(r["data_entrega"]),
            valor_total=r["valor_total"],
            pag_inicial_valor=r["pag_inicial_valor"],
            pag_inicial_data=fmt_data(r["pag_inicial_data"]),
            pag_inicial_forma=r["pag_inicial_forma"],
            pag_inicial_status=r["pag_inicial_status"],
            pag_final_valor=r["pag_final_valor"],
            pag_final_data=fmt_data(r["pag_final_data"]),
            pag_final_forma=r["pag_final_forma"],
            pag_final_status=r["pag_final_status"],
            responsavel=r["responsavel"]
        )
        
        itens_rows = conn.execute("""
            SELECT pi.*, pr.nome as produto_nome
            FROM pedido_item pi
            JOIN produto pr ON pi.produto_id = pr.id
            WHERE pi.pedido_id=?
        """, (id,)).fetchall()
        
        for ir in itens_rows:
            ped.itens.append(PedidoItem(
                id=ir["id"],
                pedido_id=ir["pedido_id"],
                produto_id=ir["produto_id"],
                quantidade=ir["quantidade"],
                preco_unitario_snapshot=ir["preco_unitario_snapshot"],
                data_snapshot=fmt_data(ir["data_snapshot"]),
                valor_item=ir["valor_item"],
                produto_nome=ir["produto_nome"]
            ))
            
        return ped

    def excluir(self, id: int) -> None:
        with transacao() as conn:
            conn.execute("DELETE FROM pedido WHERE id=?", (id,))
            AuditoriaService.registrar("pedido", "DELETE", id, conn=conn)
        event_bus.emit("pedido.excluido", pedido_id=id)

    def _validar_pagamentos_pedido(self, pedido: Pedido) -> None:
        self._validar_pagamento(
            etapa="inicial",
            valor=pedido.pag_inicial_valor,
            status=pedido.pag_inicial_status,
            data=pedido.pag_inicial_data,
        )
        self._validar_pagamento(
            etapa="final",
            valor=pedido.pag_final_valor,
            status=pedido.pag_final_status,
            data=pedido.pag_final_data,
        )

    def _validar_pagamento(self, etapa: str, valor: float, status: str, data: str | None) -> None:
        if status not in (StatusPagamento.PENDENTE.value, StatusPagamento.RECEBIDO.value):
            raise ValueError(f"Status de pagamento {etapa} inválido: {status}")
        if float(valor or 0.0) < 0:
            raise ValueError(f"Valor de pagamento {etapa} não pode ser negativo")

        if status == StatusPagamento.RECEBIDO.value:
            if not data or not data.strip():
                raise ValueError(f"Pagamento {etapa} recebido exige data de pagamento")
            self._validar_data(data, etapa)

        if data:
            self._validar_data(data, etapa)

    def _validar_data(self, data: str, etapa: str) -> None:
        try:
            parse_data(data, campo="Data", obrigatorio=True)
        except ValueError as exc:
            raise ValueError(f"Data de pagamento {etapa} inválida: {data}") from exc

    def _parse_data(self, data_txt: str | None) -> datetime | None:
        if not data_txt:
            return None

        valor = data_txt.strip()
        if not valor:
            return None

        try:
            return datetime.strptime(normalizar_data_iso(valor), "%Y-%m-%d")
        except ValueError:
            return None

    def _esta_no_periodo(self, data: datetime | None, inicio: datetime | None, fim: datetime | None) -> bool:
        if inicio is None and fim is None:
            return True
        if data is None:
            return False
        if inicio is not None and data < inicio:
            return False
        if fim is not None and data > fim:
            return False
        return True
