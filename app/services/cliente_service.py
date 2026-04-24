from typing import List, Optional
from app.db.transaction import transacao
from app.models.cliente import Cliente
from app.services.auditoria_service import AuditoriaService

class ClienteService:
    def obter_por_nome_normalizado(self, nome: str) -> Optional[Cliente]:
        nome_limpo = (nome or "").strip()
        if not nome_limpo:
            return None

        from app.db.connection import get_connection
        conn = get_connection()
        row = conn.execute(
            """
            SELECT *
              FROM cliente
             WHERE LOWER(TRIM(nome)) = LOWER(TRIM(?))
             ORDER BY id
             LIMIT 1
            """,
            (nome_limpo,),
        ).fetchone()

        if not row:
            return None

        return Cliente(id=row["id"], nome=row["nome"], contato=row["contato"])

    def obter_ou_criar_por_nome(self, nome: str) -> Optional[Cliente]:
        nome_limpo = (nome or "").strip()
        if not nome_limpo:
            return None

        existente = self.obter_por_nome_normalizado(nome_limpo)
        if existente:
            return existente

        cliente = Cliente(nome=nome_limpo)
        self.salvar(cliente)
        return cliente

    def salvar(self, cliente: Cliente) -> int:
        with transacao() as conn:
            acao = "INSERT"
            if cliente.id:
                acao = "UPDATE"
                conn.execute("UPDATE cliente SET nome=?, contato=? WHERE id=?", 
                             (cliente.nome, cliente.contato, cliente.id))
            else:
                cur = conn.execute("INSERT INTO cliente (nome, contato) VALUES (?, ?)", 
                                   (cliente.nome, cliente.contato))
                cliente.id = cur.lastrowid
            
            AuditoriaService.registrar(
                entidade="cliente",
                acao=acao,
                entidade_id=cliente.id,
                detalhes={
                    "nome": cliente.nome,
                    "contato": cliente.contato
                },
                conn=conn
            )
            
        from app.core import event_bus
        event_bus.emit("cliente.salvo", cliente_id=cliente.id)
        return cliente.id

    def listar(self, nome: str = "") -> List[Cliente]:
        from app.db.connection import get_connection
        conn = get_connection()
        params = []
        q = "SELECT * FROM cliente WHERE 1=1"
        if nome:
            q += " AND nome LIKE ?"
            params.append(f"%{nome}%")
        q += " ORDER BY nome"
        
        rows = conn.execute(q, params).fetchall()
        return [Cliente(id=r["id"], nome=r["nome"], contato=r["contato"]) for r in rows]

    def get_resumo_cliente(self, cliente_id: int) -> dict:
        """Retorna estatísticas de compras do cliente."""
        from app.db.connection import get_connection
        conn = get_connection()
        row = conn.execute(
            """
            SELECT 
                COUNT(id) as total_pedidos,
                COALESCE(SUM(valor_total), 0) as total_gasto,
                MAX(data_pedido) as ultimo_pedido
            FROM pedido
            WHERE cliente_id = ?
            """,
            (cliente_id,),
        ).fetchone()
        
        return {
            "total_pedidos": row["total_pedidos"],
            "total_gasto": row["total_gasto"],
            "ultimo_pedido": row["ultimo_pedido"]
        }

    def excluir(self, id: int) -> None:
        from app.db.connection import get_connection
        conn_check = get_connection()
        
        # Validação: verifica pedidos vinculados
        pedidos = conn_check.execute(
            "SELECT COUNT(*) as total FROM pedido WHERE cliente_id = ?", (id,)
        ).fetchone()
        
        if pedidos["total"] > 0:
            cliente = self.obter_por_nome_normalizado(
                conn_check.execute("SELECT nome FROM cliente WHERE id = ?", (id,)).fetchone()["nome"]
            )
            nome = cliente.nome if cliente else f"ID {id}"
            raise ValueError(f"Cliente '{nome}' possui {pedidos['total']} pedido(s) vinculado(s). Não é possível excluir.")

        with transacao() as conn:
            conn.execute("DELETE FROM cliente WHERE id=?", (id,))
            AuditoriaService.registrar("cliente", "DELETE", id, conn=conn)

        from app.core import event_bus
        event_bus.emit("cliente.excluido", cliente_id=id)
