import sqlite3

from app.db import schema
from app.services.dashboard_service import DashboardService
import app.db.schema as schema_module
import app.services.dashboard_service as dashboard_module


def _setup_memory_db(monkeypatch):
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    monkeypatch.setattr(schema_module, "get_connection", lambda: conn)
    monkeypatch.setattr(dashboard_module, "get_connection", lambda: conn)

    schema.create_tables()
    return conn


def test_get_resumo_calcula_indicadores_financeiros(monkeypatch):
    conn = _setup_memory_db(monkeypatch)

    conn.execute(
        """
        INSERT INTO pedido (
            cliente_nome, data_pedido, valor_total,
            pag_inicial_valor, pag_inicial_data, pag_inicial_status,
            pag_final_valor, pag_final_data, pag_final_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("A", "2026-04-10", 140.0, 100.0, "2026-04-10", "Recebido", 40.0, "2026-04-12", "Pendente"),
    )
    conn.execute(
        """
        INSERT INTO despesa (
            data, valor, categoria, status
        ) VALUES (?, ?, ?, ?)
        """,
        ("2026-04-11", 30.0, "Insumos", "Pago"),
    )
    conn.execute(
        """
        INSERT INTO despesa (
            data, valor, categoria, status
        ) VALUES (?, ?, ?, ?)
        """,
        ("2026-04-13", 20.0, "Outros", "Pendente"),
    )
    conn.commit()

    resumo = DashboardService().get_resumo("2026-04-01", "2026-04-30")

    assert resumo.saldo_atual == 70.0
    assert resumo.a_receber == 40.0
    assert resumo.falta_pagar == 20.0
    assert resumo.saldo_previsto == 90.0
    assert resumo.total_investido == 30.0
