from app.db.connection import get_connection

def create_tables():
    conn = get_connection()
    
    script = """
    -- Insumos (ingredientes e embalagens)
    CREATE TABLE IF NOT EXISTS insumo (
        id                    INTEGER PRIMARY KEY AUTOINCREMENT,
        nome                  TEXT NOT NULL,
        categoria             TEXT NOT NULL CHECK(categoria IN ('Ingrediente','Embalagem','Gás')),
        peso_volume_total     REAL NOT NULL,
        unidade_medida        TEXT NOT NULL CHECK(unidade_medida IN ('g','ml','unidade')),
        preco_compra          REAL NOT NULL,
        custo_por_unidade     REAL NOT NULL,          -- calculado: preco / peso_volume
        quantidade_disponivel REAL NOT NULL DEFAULT 0,
        quantidade_minima     REAL NOT NULL DEFAULT 0,
        data_compra           TEXT                    -- ISO-8601: YYYY-MM-DD
    );

    -- Produtos (fichas técnicas)
    CREATE TABLE IF NOT EXISTS produto (
        id                   INTEGER PRIMARY KEY AUTOINCREMENT,
        nome                 TEXT NOT NULL,
        rendimento_receita   INTEGER NOT NULL,
        comissao_perc        REAL NOT NULL DEFAULT 0,
        custo_unitario       REAL NOT NULL DEFAULT 0, -- calculado
        preco_venda_unitario REAL NOT NULL DEFAULT 0  -- calculado
    );

    -- Relação Produto ↔ Insumo (N:N)
    CREATE TABLE IF NOT EXISTS produto_insumo (
        produto_id               INTEGER NOT NULL REFERENCES produto(id) ON DELETE CASCADE,
        insumo_id                INTEGER NOT NULL REFERENCES insumo(id),
        quantidade_usada_receita REAL NOT NULL,
        custo_proporcional       REAL NOT NULL,        -- calculado
        PRIMARY KEY (produto_id, insumo_id)
    );

    -- Clientes
    CREATE TABLE IF NOT EXISTS cliente (
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        nome    TEXT NOT NULL,
        contato TEXT
    );

    -- Pedidos
    CREATE TABLE IF NOT EXISTS pedido (
        id                 INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_nome       TEXT,
        data_pedido        TEXT NOT NULL,
        data_entrega       TEXT,
        valor_total        REAL NOT NULL DEFAULT 0,
        pag_inicial_valor  REAL DEFAULT 0,
        pag_inicial_data   TEXT,
        pag_inicial_forma  TEXT,
        pag_inicial_status TEXT DEFAULT 'Pendente',
        pag_final_valor    REAL DEFAULT 0,
        pag_final_data     TEXT,
        pag_final_forma    TEXT,
        pag_final_status   TEXT DEFAULT 'Pendente',
        responsavel        TEXT
    );

    -- Itens do Pedido
    CREATE TABLE IF NOT EXISTS pedido_item (
        id                      INTEGER PRIMARY KEY AUTOINCREMENT,
        pedido_id               INTEGER NOT NULL REFERENCES pedido(id) ON DELETE CASCADE,
        produto_id              INTEGER NOT NULL REFERENCES produto(id),
        quantidade              INTEGER NOT NULL,
        preco_unitario_snapshot REAL NOT NULL,
        valor_item              REAL NOT NULL
    );

    -- Despesas
    CREATE TABLE IF NOT EXISTS despesa (
        id                   INTEGER PRIMARY KEY AUTOINCREMENT,
        data                 TEXT NOT NULL,
        valor                REAL NOT NULL,
        descricao            TEXT,
        categoria            TEXT CHECK(categoria IN ('Insumos','Investimentos','Outros')),
        responsavel          TEXT,
        status               TEXT DEFAULT 'Pendente' CHECK(status IN ('Pendente','Pago')),
        forma_pagamento      TEXT,
        data_pagamento_final TEXT
    );

    -- Rendimentos
    CREATE TABLE IF NOT EXISTS rendimento (
        id                 INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id         INTEGER REFERENCES cliente(id),
        pag_inicial_valor  REAL DEFAULT 0,
        pag_inicial_data   TEXT,
        pag_inicial_forma  TEXT,
        pag_inicial_status TEXT DEFAULT 'Pendente',
        pag_final_valor    REAL DEFAULT 0,
        pag_final_data     TEXT,
        pag_final_forma    TEXT,
        pag_final_status   TEXT DEFAULT 'Pendente',
        responsavel        TEXT
    );
    """
    conn.executescript(script)

    # Migração: versões antigas possuem cliente_id ao invés de cliente_nome
    cols = [r["name"] for r in conn.execute("PRAGMA table_info(pedido)").fetchall()]
    if "cliente_nome" not in cols:
        conn.execute("ALTER TABLE pedido ADD COLUMN cliente_nome TEXT")

    # Backfill para preservar dados históricos de bancos antigos
    if "cliente_id" in cols:
        conn.execute("""
            UPDATE pedido
               SET cliente_nome = (
                   SELECT nome
                     FROM cliente
                    WHERE cliente.id = pedido.cliente_id
               )
             WHERE (cliente_nome IS NULL OR cliente_nome = '')
               AND cliente_id IS NOT NULL
        """)

    conn.commit()
