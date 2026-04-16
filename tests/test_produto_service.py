import sqlite3

from app.db import schema
from app.models.produto import Produto
from app.models.produto_insumo import ProdutoInsumo
from app.services.produto_service import ProdutoService
import app.db.schema as schema_module
import app.services.produto_service as produto_module


def _setup_memory_db(monkeypatch):
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    monkeypatch.setattr(schema_module, "get_connection", lambda: conn)
    monkeypatch.setattr(produto_module, "get_connection", lambda: conn)

    schema.create_tables()
    return conn


def test_calcular_valores_produto(monkeypatch):
    conn = _setup_memory_db(monkeypatch)

    conn.execute(
        """
        INSERT INTO insumo (
            nome, categoria, peso_volume_total, unidade_medida,
            preco_compra, custo_por_unidade, quantidade_disponivel, quantidade_minima, data_compra
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("Chocolate", "Ingrediente", 1000.0, "g", 20.0, 2.0, 0.0, 0.0, "2026-04-16"),
    )
    conn.commit()

    produto = Produto(
        nome="Brigadeiro",
        rendimento_receita=10,
        comissao_perc=50.0,
        insumos=[ProdutoInsumo(insumo_id=1, quantidade_usada_receita=5.0)],
    )

    ProdutoService()._calcular_valores(produto)

    assert produto.insumos[0].custo_proporcional == 10.0
    assert produto.custo_unitario == 1.0
    assert produto.preco_venda_unitario == 1.5
