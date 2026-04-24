import sqlite3

import pytest

from app.db import schema
from app.models.pedido import Pedido
from app.models.pedido_item import PedidoItem
from app.services.pedido_service import PedidoService
import app.db.schema as schema_module
import app.services.cliente_service as cliente_module
import app.services.pedido_service as pedido_module


def _setup_memory_db(monkeypatch):
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    monkeypatch.setattr(schema_module, "get_connection", lambda: conn)
    monkeypatch.setattr(cliente_module, "get_connection", lambda: conn)
    monkeypatch.setattr(pedido_module, "get_connection", lambda: conn)

    schema.create_tables()
    return conn


def test_salvar_pedido_com_transacao_e_snapshot(monkeypatch):
    conn = _setup_memory_db(monkeypatch)
    conn.execute(
        """
        INSERT INTO produto (nome, rendimento_receita, comissao_perc, custo_unitario, preco_venda_unitario)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("Brigadeiro", 10, 50.0, 2.0, 10.0),
    )
    conn.commit()

    pedido = Pedido(
        cliente_nome="Cliente Teste",
        data_pedido="2026-04-16",
        pag_inicial_valor=20.0,
        pag_inicial_data="2026-04-16",
        pag_inicial_status="Recebido",
        pag_final_valor=0.0,
        pag_final_status="Pendente",
        itens=[
            PedidoItem(produto_id=1, quantidade=2),
            PedidoItem(produto_id=1, quantidade=3),
        ],
    )

    pedido_id = PedidoService().salvar(pedido)

    assert pedido_id > 0
    assert pedido.valor_total == 50.0

    itens = conn.execute("SELECT * FROM pedido_item WHERE pedido_id=?", (pedido_id,)).fetchall()
    assert len(itens) == 2
    assert all(row["data_snapshot"] for row in itens)

    audit = conn.execute("SELECT * FROM auditoria WHERE entidade='pedido' AND entidade_id=?", (pedido_id,)).fetchone()
    assert audit is not None
    assert audit["acao"] == "INSERT"


def test_salvar_pedido_rejeita_pagamento_recebido_sem_data(monkeypatch):
    _setup_memory_db(monkeypatch)

    pedido = Pedido(
        cliente_nome="Cliente Sem Data",
        data_pedido="2026-04-16",
        pag_inicial_valor=10.0,
        pag_inicial_status="Recebido",
        itens=[],
    )

    with pytest.raises(ValueError):
        PedidoService().salvar(pedido)


def test_salvar_pedido_cria_e_vincula_cliente(monkeypatch):
    conn = _setup_memory_db(monkeypatch)
    conn.execute(
        """
        INSERT INTO produto (nome, rendimento_receita, comissao_perc, custo_unitario, preco_venda_unitario)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("Brigadeiro", 10, 50.0, 2.0, 10.0),
    )
    conn.commit()

    pedido = Pedido(
        cliente_nome="  Ana Souza  ",
        data_pedido="2026-04-16",
        pag_inicial_status="Pendente",
        pag_final_status="Pendente",
        itens=[PedidoItem(produto_id=1, quantidade=1)],
    )

    pedido_id = PedidoService().salvar(pedido)

    cliente = conn.execute("SELECT * FROM cliente WHERE LOWER(TRIM(nome)) = LOWER(TRIM(?))", ("Ana Souza",)).fetchone()
    pedido_db = conn.execute("SELECT * FROM pedido WHERE id=?", (pedido_id,)).fetchone()

    assert cliente is not None
    assert pedido_db is not None
    assert pedido_db["cliente_id"] == cliente["id"]
    assert pedido_db["cliente_nome"] == cliente["nome"]
