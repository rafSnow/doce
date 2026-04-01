from typing import List, Optional
from app.db.connection import get_connection
from app.models.produto import Produto
from app.models.produto_insumo import ProdutoInsumo

class ProdutoService:
    
    def _calcular_valores(self, produto: Produto) -> None:
        """Calcula custo proporcional, unitário e preço de venda com base na ficha técnica."""
        conn = get_connection()
        custo_total_receita = 0.0
        
        # 1. Calcula custo proporcional de cada insumo
        for pi in produto.insumos:
            row = conn.execute("SELECT custo_por_unidade, nome, unidade_medida FROM insumo WHERE id=?", (pi.insumo_id,)).fetchone()
            if row:
                pi.insumo_nome = row["nome"]
                pi.insumo_unidade = row["unidade_medida"]
                custo_un = row["custo_por_unidade"]
                pi.custo_proporcional = pi.quantidade_usada_receita * custo_un
                custo_total_receita += pi.custo_proporcional
            else:
                pi.custo_proporcional = 0.0

        # 2. Custo unitário = Custo da Receita / Rendimento
        if produto.rendimento_receita > 0:
            produto.custo_unitario = custo_total_receita / produto.rendimento_receita
        else:
            produto.custo_unitario = 0.0
            
        # 3. Preço de venda = Custo unitário + % Comissão
        markup_mult = 1 + (produto.comissao_perc / 100.0)
        produto.preco_venda_unitario = produto.custo_unitario * markup_mult

    def salvar(self, produto: Produto) -> int:
        self._calcular_valores(produto)
        conn = get_connection()
        
        if produto.id:
            conn.execute("""
                UPDATE produto 
                SET nome=?, rendimento_receita=?, comissao_perc=?, custo_unitario=?, preco_venda_unitario=?
                WHERE id=?
            """, (produto.nome, produto.rendimento_receita, produto.comissao_perc, 
                  produto.custo_unitario, produto.preco_venda_unitario, produto.id))
            
            # Limpa insumos antigos e os recria
            conn.execute("DELETE FROM produto_insumo WHERE produto_id=?", (produto.id,))
        else:
            cur = conn.execute("""
                INSERT INTO produto (nome, rendimento_receita, comissao_perc, custo_unitario, preco_venda_unitario)
                VALUES (?, ?, ?, ?, ?)
            """, (produto.nome, produto.rendimento_receita, produto.comissao_perc, 
                  produto.custo_unitario, produto.preco_venda_unitario))
            produto.id = cur.lastrowid

        # Persiste ProdutoInsumo
        for pi in produto.insumos:
            conn.execute("""
                INSERT INTO produto_insumo (produto_id, insumo_id, quantidade_usada_receita, custo_proporcional)
                VALUES (?, ?, ?, ?)
            """, (produto.id, pi.insumo_id, pi.quantidade_usada_receita, pi.custo_proporcional))

        conn.commit()
        return produto.id

    def listar(self, nome: str = "") -> List[Produto]:
        conn = get_connection()
        query = "SELECT * FROM produto"
        params = []
        if nome:
            query += " WHERE nome LIKE ?"
            params.append(f"%{nome}%")
        query += " ORDER BY nome"
        
        rows = conn.execute(query, params).fetchall()
        result = []
        for r in rows:
            prod = Produto(
                id=r["id"], 
                nome=r["nome"], 
                rendimento_receita=r["rendimento_receita"],
                comissao_perc=r["comissao_perc"], 
                custo_unitario=r["custo_unitario"],
                preco_venda_unitario=r["preco_venda_unitario"]
            )
            result.append(prod)
        return result

    def get_by_id(self, id: int) -> Optional[Produto]:
        conn = get_connection()
        row = conn.execute("SELECT * FROM produto WHERE id=?", (id,)).fetchone()
        if not row:
            return None
            
        prod = Produto(
            id=row["id"], 
            nome=row["nome"], 
            rendimento_receita=row["rendimento_receita"],
            comissao_perc=row["comissao_perc"], 
            custo_unitario=row["custo_unitario"],
            preco_venda_unitario=row["preco_venda_unitario"]
        )
        
        pi_rows = conn.execute("""
            SELECT pi.*, i.nome as insumo_nome, i.unidade_medida 
            FROM produto_insumo pi
            JOIN insumo i ON pi.insumo_id = i.id
            WHERE pi.produto_id=?
        """, (id,)).fetchall()
        
        for pir in pi_rows:
            prod.insumos.append(ProdutoInsumo(
                produto_id=pir["produto_id"],
                insumo_id=pir["insumo_id"],
                quantidade_usada_receita=pir["quantidade_usada_receita"],
                custo_proporcional=pir["custo_proporcional"],
                insumo_nome=pir["insumo_nome"],
                insumo_unidade=pir["unidade_medida"]
            ))
            
        return prod

    def excluir(self, id: int) -> None:
        conn = get_connection()
        conn.execute("DELETE FROM produto WHERE id=?", (id,))
        conn.commit()
        
    def duplicar(self, id: int) -> Optional[int]:
        prod = self.get_by_id(id)
        if not prod: return None
        prod.id = None
        prod.nome = f"{prod.nome} (Cópia)"
        return self.salvar(prod)
