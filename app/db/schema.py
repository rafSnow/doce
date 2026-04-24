from app.db.connection import get_connection
from app.core.enums import StatusPagamento, CategoriaDespesa, UnidadeMedida

def create_tables():
    conn = get_connection()
    
    script = f"""
    -- Insumos (ingredientes e embalagens)
    CREATE TABLE IF NOT EXISTS insumo (
        id                    INTEGER PRIMARY KEY AUTOINCREMENT,
        nome                  TEXT NOT NULL,
        categoria             TEXT NOT NULL CHECK(categoria IN ('Ingrediente','Embalagem','Gás')),
        peso_volume_total     REAL NOT NULL,
        unidade_medida        TEXT NOT NULL CHECK(unidade_medida IN ('{UnidadeMedida.G.value}','{UnidadeMedida.ML.value}','{UnidadeMedida.UNIDADE.value}')),
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
        cliente_id         INTEGER REFERENCES cliente(id),
        cliente_nome       TEXT,
        data_pedido        TEXT NOT NULL,
        data_entrega       TEXT,
        valor_total        REAL NOT NULL DEFAULT 0,
        pag_inicial_valor  REAL DEFAULT 0,
        pag_inicial_data   TEXT,
        pag_inicial_forma  TEXT,
        pag_inicial_status TEXT DEFAULT '{StatusPagamento.PENDENTE.value}',
        pag_final_valor    REAL DEFAULT 0,
        pag_final_data     TEXT,
        pag_final_forma    TEXT,
        pag_final_status   TEXT DEFAULT '{StatusPagamento.PENDENTE.value}',
        responsavel        TEXT
    );

    -- Itens do Pedido
    CREATE TABLE IF NOT EXISTS pedido_item (
        id                      INTEGER PRIMARY KEY AUTOINCREMENT,
        pedido_id               INTEGER NOT NULL REFERENCES pedido(id) ON DELETE CASCADE,
        produto_id              INTEGER NOT NULL REFERENCES produto(id),
        quantidade              INTEGER NOT NULL,
        preco_unitario_snapshot REAL NOT NULL,
        data_snapshot           TEXT,
        valor_item              REAL NOT NULL
    );

    -- Despesas
    CREATE TABLE IF NOT EXISTS despesa (
        id                   INTEGER PRIMARY KEY AUTOINCREMENT,
        data                 TEXT NOT NULL,
        valor                REAL NOT NULL,
        descricao            TEXT,
        categoria            TEXT CHECK(categoria IN ('{CategoriaDespesa.INSUMOS.value}','{CategoriaDespesa.INVESTIMENTOS.value}','{CategoriaDespesa.OUTROS.value}')),
        responsavel          TEXT,
        status               TEXT DEFAULT '{StatusPagamento.PENDENTE.value}' CHECK(status IN ('{StatusPagamento.PENDENTE.value}','{StatusPagamento.PAGO.value}')),
        forma_pagamento      TEXT,
        data_pagamento_final TEXT,
        origem               TEXT,
        origem_id            INTEGER
    );

    -- Rendimentos
    CREATE TABLE IF NOT EXISTS rendimento (
        id                 INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id         INTEGER REFERENCES cliente(id),
        pag_inicial_valor  REAL DEFAULT 0,
        pag_inicial_data   TEXT,
        pag_inicial_forma  TEXT,
        pag_inicial_status TEXT DEFAULT '{StatusPagamento.PENDENTE.value}',
        pag_final_valor    REAL DEFAULT 0,
        pag_final_data     TEXT,
        pag_final_forma    TEXT,
        pag_final_status   TEXT DEFAULT '{StatusPagamento.PENDENTE.value}',
        responsavel        TEXT,
        pedido_id          INTEGER REFERENCES pedido(id) ON DELETE CASCADE
    );

    -- Configurações gerais
    CREATE TABLE IF NOT EXISTS configuracao (
        chave TEXT PRIMARY KEY,
        valor TEXT
    );

    -- Histórico de preços de insumos (Sprint 10.1)
    CREATE TABLE IF NOT EXISTS historico_preco_insumo (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        insumo_id     INTEGER NOT NULL REFERENCES insumo(id) ON DELETE CASCADE,
        preco_anterior REAL NOT NULL,
        preco_novo     REAL NOT NULL,
        data_alteracao TEXT NOT NULL,
        observacao     TEXT
    );

    -- Auditoria básica de operações críticas
    CREATE TABLE IF NOT EXISTS auditoria (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        entidade     TEXT NOT NULL,
        entidade_id  INTEGER,
        acao         TEXT NOT NULL,
        detalhes     TEXT,
        criado_em    TEXT NOT NULL
    );
    """
    conn.executescript(script)

    # Migração: versões antigas possuem cliente_id ao invés de cliente_nome
    cols = [r["name"] for r in conn.execute("PRAGMA table_info(pedido)").fetchall()]
    if "cliente_id" not in cols:
        conn.execute("ALTER TABLE pedido ADD COLUMN cliente_id INTEGER REFERENCES cliente(id)")
    if "cliente_nome" not in cols:
        conn.execute("ALTER TABLE pedido ADD COLUMN cliente_nome TEXT")

    # Backfill para preservar e normalizar dados históricos de bancos antigos
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

        conn.execute(
                """
                INSERT INTO cliente (nome)
                SELECT DISTINCT TRIM(p.cliente_nome)
                    FROM pedido p
                 WHERE p.cliente_nome IS NOT NULL
                     AND TRIM(p.cliente_nome) <> ''
                     AND NOT EXISTS (
                             SELECT 1
                                 FROM cliente c
                                WHERE LOWER(TRIM(c.nome)) = LOWER(TRIM(p.cliente_nome))
                     )
                """
        )

        conn.execute(
                """
                UPDATE pedido
                     SET cliente_id = (
                             SELECT c.id
                                 FROM cliente c
                                WHERE LOWER(TRIM(c.nome)) = LOWER(TRIM(pedido.cliente_nome))
                                ORDER BY c.id
                                LIMIT 1
                     )
                 WHERE cliente_id IS NULL
                     AND cliente_nome IS NOT NULL
                     AND TRIM(cliente_nome) <> ''
                """
        )

    # Migração Sprint 6.1: versões antigas de insumo podem não ter campos de estoque
    insumo_cols = [r["name"] for r in conn.execute("PRAGMA table_info(insumo)").fetchall()]
    if "quantidade_disponivel" not in insumo_cols:
        conn.execute("ALTER TABLE insumo ADD COLUMN quantidade_disponivel REAL NOT NULL DEFAULT 0")
    if "quantidade_minima" not in insumo_cols:
        conn.execute("ALTER TABLE insumo ADD COLUMN quantidade_minima REAL NOT NULL DEFAULT 0")

    # Migração: adiciona data_snapshot em pedido_item para auditoria de precificação
    pedido_item_cols = [r["name"] for r in conn.execute("PRAGMA table_info(pedido_item)").fetchall()]
    if "data_snapshot" not in pedido_item_cols:
        conn.execute("ALTER TABLE pedido_item ADD COLUMN data_snapshot TEXT")

    # Migração: adiciona colunas de rastreabilidade para ERP
    despesa_cols = [r["name"] for r in conn.execute("PRAGMA table_info(despesa)").fetchall()]
    if "origem" not in despesa_cols:
        conn.execute("ALTER TABLE despesa ADD COLUMN origem TEXT")
    if "origem_id" not in despesa_cols:
        conn.execute("ALTER TABLE despesa ADD COLUMN origem_id INTEGER")

    rendimento_cols = [r["name"] for r in conn.execute("PRAGMA table_info(rendimento)").fetchall()]
    if "pedido_id" not in rendimento_cols:
        conn.execute("ALTER TABLE rendimento ADD COLUMN pedido_id INTEGER REFERENCES pedido(id) ON DELETE CASCADE")

    # Migração ERP: Sincroniza pagamentos de pedidos existentes para a tabela de rendimentos
    conn.execute(
        f"""
        INSERT INTO rendimento (
            cliente_id, responsavel,
            pag_inicial_valor, pag_inicial_data, pag_inicial_forma, pag_inicial_status,
            pag_final_valor, pag_final_data, pag_final_forma, pag_final_status,
            pedido_id
        )
        SELECT 
            cliente_id, responsavel,
            pag_inicial_valor, pag_inicial_data, pag_inicial_forma, pag_inicial_status,
            pag_final_valor, pag_final_data, pag_final_forma, pag_final_status,
            id
        FROM pedido p
        WHERE NOT EXISTS (SELECT 1 FROM rendimento r WHERE r.pedido_id = p.id)
          AND (pag_inicial_valor > 0 OR pag_final_valor > 0)
        """
    )

    # Índices de performance (Sprint 8.6)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_cliente_nome ON cliente(nome)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_insumo_nome ON insumo(nome)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_produto_nome ON produto(nome)")

    conn.execute("CREATE INDEX IF NOT EXISTS idx_pedido_cliente_id ON pedido(cliente_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_pedido_cliente_nome ON pedido(cliente_nome)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_pedido_data_pedido_id ON pedido(data_pedido DESC, id DESC)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_pedido_status_pag ON pedido(pag_inicial_status, pag_final_status)")

    conn.execute("CREATE INDEX IF NOT EXISTS idx_pedido_item_pedido_id ON pedido_item(pedido_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_pedido_item_produto_id ON pedido_item(produto_id)")

    conn.execute("CREATE INDEX IF NOT EXISTS idx_despesa_data_id ON despesa(data DESC, id DESC)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_despesa_categoria_status ON despesa(categoria, status)")

    conn.execute("CREATE INDEX IF NOT EXISTS idx_rendimento_pag_inicial_data ON rendimento(pag_inicial_data)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_rendimento_pag_final_data ON rendimento(pag_final_data)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_rendimento_status_pag ON rendimento(pag_inicial_status, pag_final_status)")

    conn.execute("CREATE INDEX IF NOT EXISTS idx_hist_preco_insumo_insumo_data ON historico_preco_insumo(insumo_id, data_alteracao DESC)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_hist_preco_insumo_data ON historico_preco_insumo(data_alteracao DESC)")

    conn.execute("CREATE INDEX IF NOT EXISTS idx_auditoria_entidade_id ON auditoria(entidade, entidade_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_auditoria_criado_em ON auditoria(criado_em DESC)")

    conn.commit()
