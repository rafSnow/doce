from typing import List, Optional
from app.db.connection import get_connection
from app.models.pedido import Pedido
from app.models.pedido_item import PedidoItem

class PedidoService:
    def salvar(self, pedido: Pedido) -> int:
        conn = get_connection()
        
        total = 0.0
        for item in pedido.itens:
            # Se o snapshot está zerado ou nulo, pegamos o preço atual do produto
            if item.preco_unitario_snapshot <= 0:
                row = conn.execute("SELECT preco_venda_unitario FROM produto WHERE id=?", (item.produto_id,)).fetchone()
                if row:
                    item.preco_unitario_snapshot = row["preco_venda_unitario"]
            item.valor_item = item.quantidade * item.preco_unitario_snapshot
            total += item.valor_item
            
        pedido.valor_total = total

        if pedido.id:
            conn.execute("""
                UPDATE pedido SET 
                    cliente_nome=?, data_pedido=?, data_entrega=?, valor_total=?,
                    pag_inicial_valor=?, pag_inicial_data=?, pag_inicial_forma=?, pag_inicial_status=?,
                    pag_final_valor=?, pag_final_data=?, pag_final_forma=?, pag_final_status=?,
                    responsavel=?
                WHERE id=?
            """, (
                pedido.cliente_nome, pedido.data_pedido, pedido.data_entrega, pedido.valor_total,
                pedido.pag_inicial_valor, pedido.pag_inicial_data, pedido.pag_inicial_forma, pedido.pag_inicial_status,
                pedido.pag_final_valor, pedido.pag_final_data, pedido.pag_final_forma, pedido.pag_final_status,
                pedido.responsavel, pedido.id
            ))
            # Remove itens antigos e recria
            conn.execute("DELETE FROM pedido_item WHERE pedido_id=?", (pedido.id,))
        else:
            cur = conn.execute("""
                INSERT INTO pedido (
                    cliente_nome, data_pedido, data_entrega, valor_total,
                    pag_inicial_valor, pag_inicial_data, pag_inicial_forma, pag_inicial_status,
                    pag_final_valor, pag_final_data, pag_final_forma, pag_final_status,
                    responsavel
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pedido.cliente_nome, pedido.data_pedido, pedido.data_entrega, pedido.valor_total,
                pedido.pag_inicial_valor, pedido.pag_inicial_data, pedido.pag_inicial_forma, pedido.pag_inicial_status,
                pedido.pag_final_valor, pedido.pag_final_data, pedido.pag_final_forma, pedido.pag_final_status,
                pedido.responsavel
            ))
            pedido.id = cur.lastrowid

        for item in pedido.itens:
            conn.execute("""
                INSERT INTO pedido_item (pedido_id, produto_id, quantidade, preco_unitario_snapshot, valor_item)
                VALUES (?, ?, ?, ?, ?)
            """, (pedido.id, item.produto_id, item.quantidade, item.preco_unitario_snapshot, item.valor_item))

        conn.commit()
        return pedido.id

    def listar(self, cliente_nome: str = "", status_pagamento: str = "Todos") -> List[Pedido]:
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
            if status_pagamento == "Pendente":
                query += " AND (p.pag_inicial_status = 'Pendente' OR p.pag_final_status = 'Pendente')"
            elif status_pagamento == "Recebido":
                query += " AND p.pag_inicial_status = 'Recebido' AND p.pag_final_status = 'Recebido'"
                
        query += " ORDER BY p.data_pedido DESC, p.id DESC"
        
        rows = conn.execute(query, params).fetchall()
        result = []
        for r in rows:
            ped = Pedido(
                id=r["id"],
                cliente_nome=r["cliente_nome"],
                data_pedido=r["data_pedido"],
                data_entrega=r["data_entrega"],
                valor_total=r["valor_total"],
                pag_inicial_valor=r["pag_inicial_valor"],
                pag_inicial_data=r["pag_inicial_data"],
                pag_inicial_forma=r["pag_inicial_forma"],
                pag_inicial_status=r["pag_inicial_status"],
                pag_final_valor=r["pag_final_valor"],
                pag_final_data=r["pag_final_data"],
                pag_final_forma=r["pag_final_forma"],
                pag_final_status=r["pag_final_status"],
                responsavel=r["responsavel"]
            )
            result.append(ped)
        return result

    def get_by_id(self, id: int) -> Optional[Pedido]:
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
            cliente_nome=r["cliente_nome"],
            data_pedido=r["data_pedido"],
            data_entrega=r["data_entrega"],
            valor_total=r["valor_total"],
            pag_inicial_valor=r["pag_inicial_valor"],
            pag_inicial_data=r["pag_inicial_data"],
            pag_inicial_forma=r["pag_inicial_forma"],
            pag_inicial_status=r["pag_inicial_status"],
            pag_final_valor=r["pag_final_valor"],
            pag_final_data=r["pag_final_data"],
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
                valor_item=ir["valor_item"],
                produto_nome=ir["produto_nome"]
            ))
            
        return ped

    def excluir(self, id: int) -> None:
        conn = get_connection()
        conn.execute("DELETE FROM pedido WHERE id=?", (id,))
        conn.commit()
