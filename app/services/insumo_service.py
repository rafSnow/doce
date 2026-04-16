from typing import List, Optional
from datetime import datetime
from app.db.connection import get_connection
from app.models.insumo import Insumo

class InsumoService:
    def salvar(self, insumo: Insumo) -> int:
        conn = get_connection()
        custo_calc = insumo.custo_por_unidade
        custo_anterior = None
        
        if insumo.id:
            preco_anterior = conn.execute(
                "SELECT preco_compra, custo_por_unidade FROM insumo WHERE id=?",
                (insumo.id,),
            ).fetchone()
            if preco_anterior:
                custo_anterior = float(preco_anterior["custo_por_unidade"] or 0.0)

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

            if preco_anterior and float(preco_anterior["preco_compra"]) != float(insumo.preco_compra):
                conn.execute(
                    """
                    INSERT INTO historico_preco_insumo (
                        insumo_id,
                        preco_anterior,
                        preco_novo,
                        data_alteracao,
                        observacao
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        insumo.id,
                        float(preco_anterior["preco_compra"]),
                        float(insumo.preco_compra),
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Alteracao automatica via edicao de insumo",
                    ),
                )
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

        # Mantém custo de produtos sincronizado quando o insumo muda.
        if insumo.id and custo_anterior is not None and float(custo_calc) != custo_anterior:
            from app.services.produto_service import ProdutoService

            ProdutoService().recalcular_por_insumo(insumo.id)

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

    def contar_alertas_estoque(self) -> int:
        conn = get_connection()
        row = conn.execute(
            """
            SELECT COUNT(*) AS total
            FROM insumo
            WHERE quantidade_disponivel <= quantidade_minima
            """
        ).fetchone()
        return int(row["total"] or 0)

    def listar_historico_preco(self, insumo_id: Optional[int] = None) -> List[dict]:
        conn = get_connection()
        query = """
            SELECT h.id,
                   h.insumo_id,
                   i.nome AS insumo_nome,
                   h.preco_anterior,
                   h.preco_novo,
                   h.data_alteracao,
                   h.observacao
              FROM historico_preco_insumo h
              JOIN insumo i ON i.id = h.insumo_id
             WHERE 1=1
        """
        params: list = []

        if insumo_id is not None:
            query += " AND h.insumo_id = ?"
            params.append(insumo_id)

        query += " ORDER BY h.data_alteracao DESC, h.id DESC"
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

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
