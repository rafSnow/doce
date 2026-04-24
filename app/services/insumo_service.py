from typing import List, Optional
from datetime import datetime
from app.db.transaction import transacao
from app.models.insumo import Insumo
from app.core.enums import UnidadeMedida
from app.core.formatters import normalizar_data_iso, fmt_data
from app.core import event_bus
from app.services.auditoria_service import AuditoriaService

class InsumoService:
    def salvar(self, insumo: Insumo) -> int:
        custo_calc = insumo.custo_por_unidade
        custo_anterior = None
        
        # Normaliza data para ISO antes de salvar
        dt_compra_iso = normalizar_data_iso(insumo.data_compra) if insumo.data_compra else None

        with transacao() as conn:
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
                      dt_compra_iso, insumo.id))

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
                
                AuditoriaService.registrar(
                    entidade="insumo",
                    acao="UPDATE",
                    entidade_id=insumo.id,
                    detalhes={
                        "nome": insumo.nome,
                        "preco_compra": insumo.preco_compra,
                        "quantidade_disponivel": insumo.quantidade_disponivel
                    },
                    conn=conn
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
                      dt_compra_iso))
                insumo.id = cur.lastrowid
                
                AuditoriaService.registrar(
                    entidade="insumo",
                    acao="INSERT",
                    entidade_id=insumo.id,
                    detalhes={
                        "nome": insumo.nome,
                        "preco_compra": insumo.preco_compra,
                        "quantidade_disponivel": insumo.quantidade_disponivel
                    },
                    conn=conn
                )

        event_bus.emit("insumo.salvo", insumo_id=insumo.id, custo_anterior=custo_anterior, custo_novo=float(custo_calc))
        return insumo.id

    def listar(self, nome: str = "", categoria: str = "") -> List[Insumo]:
        from app.db.connection import get_connection
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
        from app.db.connection import get_connection
        conn = get_connection()
        cursor = conn.execute("SELECT * FROM insumo WHERE id=?", (id,))
        row = cursor.fetchone()
        if row:
            return self._row_to_model(row)
        return None

    def excluir(self, id: int) -> None:
        with transacao() as conn:
            conn.execute("DELETE FROM insumo WHERE id=?", (id,))
            AuditoriaService.registrar("insumo", "DELETE", id, conn=conn)
        event_bus.emit("insumo.excluido", insumo_id=id)

    def contar_alertas_estoque(self) -> int:
        from app.db.connection import get_connection
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
        from app.db.connection import get_connection
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
            data_compra=fmt_data(row["data_compra"])
        )
