from typing import List, Optional
from app.db.connection import get_connection
from app.models.cliente import Cliente

class ClienteService:
    def salvar(self, cliente: Cliente) -> int:
        conn = get_connection()
        if cliente.id:
            conn.execute("UPDATE cliente SET nome=?, contato=? WHERE id=?", 
                         (cliente.nome, cliente.contato, cliente.id))
        else:
            cur = conn.execute("INSERT INTO cliente (nome, contato) VALUES (?, ?)", 
                               (cliente.nome, cliente.contato))
            cliente.id = cur.lastrowid
        conn.commit()
        return cliente.id

    def listar(self, nome: str = "") -> List[Cliente]:
        conn = get_connection()
        params = []
        q = "SELECT * FROM cliente WHERE 1=1"
        if nome:
            q += " AND nome LIKE ?"
            params.append(f"%{nome}%")
        q += " ORDER BY nome"
        
        rows = conn.execute(q, params).fetchall()
        return [Cliente(id=r["id"], nome=r["nome"], contato=r["contato"]) for r in rows]

    def excluir(self, id: int) -> None:
        conn = get_connection()
        conn.execute("DELETE FROM cliente WHERE id=?", (id,))
        conn.commit()
