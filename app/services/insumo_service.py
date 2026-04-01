from typing import List, Optional
from app.db.connection import get_connection
from app.models.insumo import Insumo

class InsumoService:
    def salvar(self, insumo: Insumo) -> int:
        conn = get_connection()
        custo_calc = insumo.custo_por_unidade
        
        if insumo.id:
            conn.execute("""
                UPDATE insumo 
                SET nome=?, categoria=?, peso_volume_total=?, unidade_medida=?, 
                    preco_compra=?, custo_por_unidade=?, quantidade_disponivel=?, 
                    quantidade_minima=?, data_compra=?
                WHERE id=?
            """, (insumo.nome, insumo.categoria, insumo.peso_volume_total, 
                  insumo.unidade_medida, insumo.preco_compra, custo_calc, 
                  insumo.quantidade_disponivel, insumo.quantidade_minima, 
                  insumo.data_compra, insumo.id))
        else:
            cur = conn.execute("""
                INSERT INTO insumo (nome, categoria, peso_volume_total, unidade_medida, 
                                    preco_compra, custo_por_unidade, quantidade_disponivel, 
                                    quantidade_minima, data_compra) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (insumo.nome, insumo.categoria, insumo.peso_volume_total, 
                  insumo.unidade_medida, insumo.preco_compra, custo_calc, 
                  insumo.quantidade_disponivel, insumo.quantidade_minima, 
                  insumo.data_compra))
            insumo.id = cur.lastrowid
        conn.commit()
        return insumo.id

    def listar(self, nome: str = "", categoria: str = "") -> List[Insumo]:
        conn = get_connection()
        query = "SELECT * FROM insumo WHERE 1=1"
        params = []
        
        if nome:
            query += " AND nome LIKE ?"
            params.append(f"%{nome}%")
        if categoria and categoria != "Todos":
            query += " AND categoria = ?"
            params.append(categoria)
            
        query += " ORDER BY nome"
        
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        
        return [self._row_to_model(row) for row in rows]

    def get_by_id(self, id: int) -> Optional[Insumo]:
        conn = get_connection()
        cursor = conn.execute("SELECT * FROM insumo WHERE id=?", (id,))
        row = cursor.fetchone()
        if row:
            return self._row_to_model(row)
        return None

    def excluir(self, id: int) -> None:
        conn = get_connection()
        conn.execute("DELETE FROM insumo WHERE id=?", (id,))
        conn.commit()

    def _row_to_model(self, row) -> Insumo:
        return Insumo(
            id=row["id"],
            nome=row["nome"],
            categoria=row["categoria"],
            peso_volume_total=row["peso_volume_total"],
            unidade_medida=row["unidade_medida"],
            preco_compra=row["preco_compra"],
            quantidade_disponivel=row["quantidade_disponivel"],
            quantidade_minima=row["quantidade_minima"],
            data_compra=row["data_compra"]
        )
