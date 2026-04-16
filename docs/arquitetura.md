# Documento de Arquitetura
## Sistema de Gestão para Confeitaria
**Versão:** 1.0  
**Data:** Março de 2026  
**Plataforma:** Python 3.10+ · CustomTkinter · SQLite · PyInstaller  

---

## 1. Visão Geral

O sistema é uma **aplicação desktop monolítica** executada localmente em Windows, sem dependências de rede. O banco de dados SQLite reside no mesmo sistema de arquivos que o executável, garantindo funcionamento 100% offline, portabilidade e backup trivial (copiar o arquivo `.db`).

```
┌─────────────────────────────────────────────┐
│              Usuário (Confeiteira)           │
└───────────────────┬─────────────────────────┘
                    │ interação direta
┌───────────────────▼─────────────────────────┐
│           Interface Gráfica (UI)            │
│              CustomTkinter                  │
│  Dashboard │ Insumos │ Produtos │ Pedidos   │
│         Financeiro │ Configurações          │
└───────────────────┬─────────────────────────┘
                    │ chamadas de serviço
┌───────────────────▼─────────────────────────┐
│             Camada de Serviços              │
│  InsumoService │ ProdutoService             │
│  PedidoService │ DespesaService             │
│  RendimentoService │ DashboardService       │
└───────────────────┬─────────────────────────┘
                    │ queries SQL
┌───────────────────▼─────────────────────────┐
│          Camada de Acesso a Dados           │
│        SQLite via sqlite3 (stdlib)          │
│           confeitaria.db (local)            │
└─────────────────────────────────────────────┘
```

---

## 2. Arquitetura em Camadas

O projeto adota uma **arquitetura em 3 camadas** simples e adequada ao contexto desktop:

| Camada | Responsabilidade | Tecnologia |
|---|---|---|
| **View (UI)** | Renderizar telas, capturar eventos do usuário, exibir dados | CustomTkinter |
| **Service (Negócio)** | Regras de negócio, cálculos, validações | Python puro |
| **Repository (Dados)** | Queries SQL, mapeamento de resultados, conexão com o banco | `sqlite3` (stdlib) |

> **Princípio:** a camada View **nunca** acessa o banco diretamente. Toda lógica de negócio e acesso a dados passa pelos Services.

---

## 3. Estrutura de Diretórios

```
confeitaria/
├── main.py                     # Ponto de entrada da aplicação
├── confeitaria.db              # Banco de dados SQLite (gerado na 1ª execução)
├── requirements.txt
│
├── app/
│   ├── db/
│   │   ├── connection.py       # Singleton de conexão SQLite
│   │   └── schema.py           # DDL: CREATE TABLE IF NOT EXISTS
│   │
│   ├── models/                 # Dataclasses representando entidades
│   │   ├── insumo.py
│   │   ├── produto.py
│   │   ├── produto_insumo.py
│   │   ├── cliente.py
│   │   ├── pedido.py
│   │   ├── pedido_item.py
│   │   ├── despesa.py
│   │   └── rendimento.py
│   │
│   ├── services/               # Regras de negócio e cálculos
│   │   ├── insumo_service.py
│   │   ├── produto_service.py
│   │   ├── pedido_service.py
│   │   ├── cliente_service.py
│   │   ├── despesa_service.py
│   │   ├── rendimento_service.py
│   │   └── dashboard_service.py
│   │
│   ├── views/                  # Telas CustomTkinter
│   │   ├── main_window.py      # Janela principal com navegação
│   │   ├── dashboard_view.py
│   │   ├── insumos_view.py
│   │   ├── produtos_view.py
│   │   ├── pedidos_view.py
│   │   ├── financeiro_view.py
│   │   └── configuracoes_view.py
│   │
│   └── utils/
│       ├── formatters.py       # Formatação de moeda, datas
│       └── validators.py       # Validações de campos (não vazio, número > 0, etc.)
│
└── build/
    └── confeitaria.spec        # Configuração do PyInstaller
```

---

## 4. Banco de Dados

### 4.1 Schema Completo

```sql
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
    data_snapshot           TEXT,
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

-- Auditoria
CREATE TABLE IF NOT EXISTS auditoria (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    entidade     TEXT NOT NULL,
    entidade_id  INTEGER,
    acao         TEXT NOT NULL,
    detalhes     TEXT,
    criado_em    TEXT NOT NULL
);
```

### 4.2 Diagrama de Relacionamentos

```
insumo ──────────────── produto_insumo ─────── produto
  (1)                       (N:N)               (1)
                                                  │
                                             pedido_item
                                                  │ N
                                              pedido (N)
                                                  │
                                              cliente (1)
                                                  │
                                           rendimento (N)
```

### 4.3 Convenções do Banco

- **Datas** armazenadas como `TEXT` no formato ISO-8601 (`YYYY-MM-DD`)
- **Valores monetários** como `REAL` com precisão de 2 casas decimais (formatados na UI)
- **Campos calculados** persistidos no banco para evitar recálculo a cada leitura
- **ON DELETE CASCADE** nos itens dependentes para manter integridade referencial

### 4.4 Decisão Arquitetural — Snapshot de Preço em Pedido

- O `preco_unitario_snapshot` é salvo no `pedido_item` no momento do fechamento do pedido.
- O campo `data_snapshot` registra quando o snapshot foi capturado.
- Essa decisão preserva histórico financeiro: mudanças futuras no preço de produto não alteram pedidos antigos.

---

## 5. Padrões de Código

### 5.1 Models — Dataclasses

```python
# app/models/insumo.py
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Insumo:
    nome: str
    categoria: str               # 'Ingrediente' | 'Embalagem' | 'Gás'
    peso_volume_total: float
    unidade_medida: str          # 'g' | 'ml' | 'unidade'
    preco_compra: float
    quantidade_disponivel: float = 0.0
    quantidade_minima: float = 0.0
    data_compra: Optional[str] = None
    id: Optional[int] = None

    @property
    def custo_por_unidade(self) -> float:
        if self.peso_volume_total == 0:
            return 0.0
        return round(self.preco_compra / self.peso_volume_total, 6)

    @property
    def estoque_baixo(self) -> bool:
        return self.quantidade_disponivel <= self.quantidade_minima
```

### 5.2 Services — Regras de Negócio

```python
# app/services/insumo_service.py
from app.db.connection import get_connection
from app.models.insumo import Insumo

class InsumoService:
    def salvar(self, insumo: Insumo) -> int:
        conn = get_connection()
        if insumo.id:
            conn.execute("""
                UPDATE insumo SET nome=?, categoria=?, preco_compra=?, ...
                WHERE id=?
            """, (..., insumo.id))
        else:
            cur = conn.execute("""
                INSERT INTO insumo (nome, categoria, ...) VALUES (?, ?, ...)
            """, (...))
            insumo.id = cur.lastrowid
        conn.commit()
        return insumo.id

    def listar(self, nome: str = "", categoria: str = "") -> list[Insumo]:
        ...

    def excluir(self, id: int) -> None:
        get_connection().execute("DELETE FROM insumo WHERE id=?", (id,))
        get_connection().commit()
```

### 5.3 Views — Padrão de Telas

Cada `View` segue o padrão:

```python
# app/views/insumos_view.py
import customtkinter as ctk
from app.services.insumo_service import InsumoService

class InsumosView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.service = InsumoService()
        self._build_ui()
        self._carregar_dados()

    def _build_ui(self):
        # construção estática da interface
        ...

    def _carregar_dados(self):
        # consulta ao service e preenchimento da tabela
        ...

    def _on_salvar(self):
        # coleta campos → chama service.salvar() → recarrega dados
        ...

    def _on_excluir(self, id: int):
        # confirmação → service.excluir() → recarrega dados
        ...
```

---

## 6. Módulo de Conexão com o Banco

```python
# app/db/connection.py
import sqlite3
import os

_conn: sqlite3.Connection | None = None

def get_connection() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        db_path = os.path.join(os.path.dirname(__file__), "../../confeitaria.db")
        _conn = sqlite3.connect(db_path, check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        _conn.execute("PRAGMA foreign_keys = ON")
    return _conn
```

> `sqlite3.Row` permite acessar colunas por nome (`row["nome"]`), tornando o código mais legível e seguro.

---

## 7. Cálculos de Negócio

### 7.1 Custo por Unidade de Insumo

```
custo_por_unidade = preco_compra / peso_volume_total
```

### 7.2 Custo Total da Receita (Produto)

```
custo_proporcional(insumo) = (quantidade_usada_receita / peso_volume_total_insumo) × preco_compra_insumo
custo_total_receita = Σ custo_proporcional para todos os insumos da ficha
```

### 7.3 Custo e Preço Unitários do Produto

```
custo_unitario = custo_total_receita / rendimento_receita
preco_venda_unitario = custo_unitario × (1 + comissao_perc / 100)
```

### 7.4 Valor de um Pedido

```
receitas_necessarias = CEIL(quantidade_pedida / rendimento_receita)
custo_total_pedido   = receitas_necessarias × custo_total_receita
valor_cobrado_pedido = quantidade_pedida × preco_venda_unitario
lucro_estimado       = valor_cobrado_pedido − custo_total_pedido
```

### 7.5 Dashboard Financeiro

```
saldo_atual    = Σ (pag recebidos de pedidos) − Σ (despesas pagas)
a_receber      = Σ (pagamentos de pedidos com status Pendente)
falta_pagar    = Σ (despesas com status Pendente)
saldo_previsto = saldo_atual + a_receber − falta_pagar
```

---

## 8. Interface Gráfica

### 8.1 Navegação Principal

```
┌────────────────────────────────────────────────────────┐
│  🍫 Gestão Confeitaria          [nome estabelecimento] │
├──────────┬─────────────────────────────────────────────┤
│ MENU     │                                             │
│          │         ÁREA DE CONTEÚDO                    │
│ Dashboard│         (troca conforme seleção)            │
│ Insumos  │                                             │
│ Produtos │                                             │
│ Pedidos  │                                             │
│ Financ.  │                                             │
│ Config.  │                                             │
└──────────┴─────────────────────────────────────────────┘
```

### 8.2 Padrão de Telas de Listagem

```
[ Buscar: _____________ ]  [ Filtro: ▼ ]  [ + Novo ]
┌─────────────────────────────────────────────────────┐
│  Nome         │  Categoria │  Custo/un  │  Ações    │
│─────────────────────────────────────────────────────│
│  Chocolate em │  Ingredien │  R$ 0,048  │ ✏️ 🗑️    │
│  Pó 50g Lata  │  te        │            │           │
└─────────────────────────────────────────────────────┘
```

### 8.3 Paleta de Cores Sugerida

| Uso | Cor |
|---|---|
| Primária (accent) | `#C8866B` (terracota/cacau) |
| Fundo escuro | `#1E1E1E` |
| Fundo claro | `#F5F0EB` |
| Sucesso / saldo positivo | `#4CAF50` |
| Alerta / pendente | `#FF9800` |
| Erro / exclusão | `#F44336` |

---

## 9. Empacotamento com PyInstaller

### 9.1 Comando de Build

```bash
pyinstaller --onefile --windowed \
  --name "ConfeitariaGestao" \
  --icon assets/icon.ico \
  --add-data "assets;assets" \
  main.py
```

### 9.2 Considerações

- O arquivo `confeitaria.db` é criado em tempo de execução no mesmo diretório do `.exe`
- `--windowed` elimina a janela de terminal no Windows
- `--onefile` gera um único executável portátil
- Dados do usuário (banco SQLite) permanecem fora do `.exe`, permitindo backup simples

---

## 10. Decisões Arquiteturais (ADRs)

### ADR-01: SQLite como banco de dados
**Decisão:** Usar SQLite como único mecanismo de persistência.  
**Justificativa:** Funciona offline, não requer servidor, backup por cópia de arquivo, biblioteca nativa no Python (sem instalação adicional), suficiente para volume de dados de uma confeitaria artesanal.  
**Trade-off aceito:** Não há suporte a múltiplos usuários simultâneos (fora do escopo no MVP).

### ADR-02: CustomTkinter como framework de UI
**Decisão:** Usar CustomTkinter sobre Tkinter puro.  
**Justificativa:** Visual moderno compatível com Windows 10/11, sem dependências externas pesadas, distribuição simples via PyInstaller, suporte a temas claro/escuro.  
**Trade-off aceito:** Menos componentes prontos que PyQt/wxPython, mas suficiente para o escopo.

### ADR-03: Campos calculados persistidos no banco
**Decisão:** Campos como `custo_por_unidade`, `custo_unitario` e `preco_venda_unitario` são calculados e salvos no banco, não recalculados em cada leitura.  
**Justificativa:** Simplifica queries de listagem e garante que o `preco_unitario_snapshot` nos pedidos reflita o preço histórico.  
**Trade-off aceito:** Necessidade de recalcular e atualizar ao editar insumos/produtos.

### ADR-04: Arquitetura em 3 camadas sem ORM
**Decisão:** Usar SQL puro via `sqlite3` stdlib, sem ORM (SQLAlchemy).  
**Justificativa:** Reduz dependências, torna o projeto mais simples de empacotar, e o volume de queries é pequeno e bem definido.  
**Trade-off aceito:** Mais código manual de mapeamento em comparação ao SQLAlchemy.

---

*Documento de Arquitetura v1.0 — Sistema de Gestão para Confeitaria*
