# Documento de Requisitos de Software (SRS)
## Sistema de Gestão para Confeitaria
**Versão:** 1.0  
**Data:** Março de 2026  
**Plataforma:** Aplicação Desktop — Python + SQLite + CustomTkinter  

---

## 1. Introdução

### 1.1 Objetivo

Este documento descreve os requisitos funcionais e não funcionais do sistema de gestão para confeitaria artesanal. O sistema substituirá planilhas manuais do Google Sheets por uma aplicação desktop executável, desenvolvida em Python, com banco de dados SQLite local, focada em simplicidade, confiabilidade e uso sem necessidade de internet.

### 1.2 Escopo

O sistema contempla os seguintes módulos:

| Módulo | Responsabilidade |
|---|---|
| **Insumos / Estoque** | Cadastro de ingredientes e embalagens, custo por unidade, alertas de estoque |
| **Precificação** | Ficha técnica dos produtos, cálculo de custo e preço de venda |
| **Pedidos** | Registro de pedidos por cliente, controle de pagamento em duas etapas |
| **Financeiro** | Despesas e rendimentos do negócio |
| **Dashboard** | Resumo financeiro consolidado — saldo, a receber, a pagar |
| **Configurações** | Backup do banco, nome do estabelecimento |

### 1.3 Tecnologias

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.10+ |
| Interface gráfica | CustomTkinter |
| Banco de dados | SQLite (arquivo `.db` local) |
| Distribuição | Executável `.exe` via PyInstaller (Windows) |
| Relatórios | Exportação para Excel via `openpyxl` (fase futura) |

### 1.4 Perfis de Usuário

- **Confeiteira responsável** — usuário principal, realiza todas as operações de cadastro, consulta e gestão.
- **Colaborador futuro** — uso no mesmo computador, sem diferenciação de perfil na versão inicial.

---

## 2. Requisitos Funcionais

### 2.1 Módulo: Insumos e Estoque

> Gerencia todos os ingredientes e embalagens utilizados na produção.

| ID | Requisito | Prioridade |
|---|---|---|
| RF-01 | Cadastrar insumo com: nome, unidade de medida, peso/volume total da embalagem, preço de compra e data de compra | Alta |
| RF-02 | Editar e excluir insumos cadastrados | Alta |
| RF-03 | Listar todos os insumos com filtro por nome e categoria (Ingrediente / Embalagem) | Alta |
| RF-04 | Registrar quantidade disponível em estoque de cada insumo | Alta |
| RF-05 | Alertar visualmente quando a quantidade disponível estiver zerada ou abaixo do mínimo definido | Média |
| RF-06 | Calcular automaticamente o custo por unidade (g / ml / unidade) a partir do preço e do volume total da embalagem | Alta |

### 2.2 Módulo: Precificação de Produtos

> Cada produto possui uma ficha técnica com ingredientes, embalagens, rendimento e margem de lucro.

| ID | Requisito | Prioridade |
|---|---|---|
| RF-07 | Cadastrar produto com nome e rendimento da receita (quantidade de unidades produzidas por receita) | Alta |
| RF-08 | Associar ingredientes e embalagens ao produto com a quantidade usada por receita (g / ml / unidade) | Alta |
| RF-09 | Calcular automaticamente o custo total da receita somando o custo proporcional de cada insumo | Alta |
| RF-10 | Definir percentual de markup e calcular o preço de venda unitário sobre o custo | Alta |
| RF-11 | Dado um pedido (quantidade de unidades), calcular quantas receitas são necessárias e o custo total do pedido | Alta |
| RF-12 | Exibir o valor total a cobrar do cliente e o lucro estimado sobre a venda | Alta |
| RF-13 | Permitir duplicar uma ficha de produto para criar variações (ex: Brigadeiro 70%, Brigadeiro Ninho) | Média |
| RF-14 | Listar todos os produtos cadastrados e permitir edição e exclusão | Alta |

### 2.3 Módulo: Pedidos

> Registra e acompanha os pedidos por cliente, com controle de pagamento em duas etapas (sinal + pagamento final).

| ID | Requisito | Prioridade |
|---|---|---|
| RF-15 | Cadastrar pedido vinculado a um cliente, com data de entrega prevista | Alta |
| RF-16 | Adicionar múltiplos produtos a um mesmo pedido, com suas respectivas quantidades | Alta |
| RF-17 | Registrar o pagamento inicial (sinal): valor, data, forma de pagamento (Pix / Dinheiro) e status (Recebido / Pendente) | Alta |
| RF-18 | Registrar o pagamento final: valor, data, forma de pagamento e status | Alta |
| RF-19 | Exibir o valor total a cobrar do cliente, calculado automaticamente pela soma dos produtos do pedido | Alta |
| RF-20 | Listar pedidos com filtro por cliente, status de pagamento e período | Alta |
| RF-21 | Indicar visualmente pedidos com pagamento pendente | Média |
| RF-22 | Cadastrar e gerenciar clientes (nome, contato) | Média |

### 2.4 Módulo: Financeiro — Despesas

> Registro de todas as saídas financeiras do negócio.

| ID | Requisito | Prioridade |
|---|---|---|
| RF-23 | Cadastrar despesa com: data, valor, descrição, categoria (Insumos / Investimentos / Outros), responsável, status (Pendente / Pago), forma de pagamento e data de pagamento final | Alta |
| RF-24 | Editar e excluir despesas cadastradas | Alta |
| RF-25 | Listar despesas com filtro por período, categoria e status | Alta |
| RF-26 | Totalizar despesas por categoria e por período | Média |

### 2.5 Módulo: Financeiro — Rendimentos

> Registro de todas as entradas financeiras do negócio.

| ID | Requisito | Prioridade |
|---|---|---|
| RF-27 | Cadastrar rendimento vinculado a um cliente, com pagamento inicial e final (valor, data, forma de pagamento, status) | Alta |
| RF-28 | Editar e excluir rendimentos cadastrados | Alta |
| RF-29 | Listar rendimentos com filtro por período e status de pagamento | Alta |

### 2.6 Módulo: Dashboard / Resumo Financeiro

> Painel principal com visão consolidada da saúde financeira do negócio.

| ID | Requisito | Prioridade |
|---|---|---|
| RF-30 | Exibir saldo atual (entradas recebidas − despesas pagas) | Alta |
| RF-31 | Exibir total de despesas pendentes (falta pagar) | Alta |
| RF-32 | Exibir total de valores a receber (pagamentos de clientes pendentes) | Alta |
| RF-33 | Exibir saldo previsto (saldo atual + a receber − falta pagar) | Alta |
| RF-34 | Exibir total investido em insumos e em investimentos no período | Média |
| RF-35 | Filtrar o dashboard por período (mês, trimestre, intervalo personalizado) | Média |

---

## 3. Requisitos Não Funcionais

| ID | Requisito | Prioridade | Categoria |
|---|---|---|---|
| RNF-01 | O sistema deve funcionar completamente offline, sem necessidade de internet | Alta | Infraestrutura |
| RNF-02 | O banco de dados deve ser um arquivo SQLite único, local e de fácil backup manual (copiar o arquivo) | Alta | Infraestrutura |
| RNF-03 | O sistema deve ser distribuído como `.exe` para Windows, sem necessidade de instalar Python | Alta | Distribuição |
| RNF-04 | A interface deve ser simples e intuitiva, adequada para usuário não técnico | Alta | Usabilidade |
| RNF-05 | O tempo de resposta de qualquer consulta deve ser inferior a 2 segundos | Média | Desempenho |
| RNF-06 | Todos os valores monetários devem ser armazenados e exibidos em R$ com duas casas decimais | Alta | Dados |
| RNF-07 | O sistema deve exibir mensagens de confirmação antes de excluir qualquer registro | Alta | Segurança |
| RNF-08 | O sistema deve permitir realizar backup manual do banco de dados a partir da interface | Média | Segurança |

---

## 4. Modelo de Dados

### 4.1 Entidade: Insumo

| Campo | Tipo | Descrição |
|---|---|---|
| `id` | INTEGER PK | Identificador único |
| `nome` | TEXT | Nome do ingrediente ou embalagem |
| `categoria` | TEXT | Ingrediente / Embalagem / Gás |
| `peso_volume_total` | REAL | Quantidade total da embalagem (g, ml ou unidades) |
| `unidade_medida` | TEXT | g / ml / unidade |
| `preco_compra` | REAL | Preço pago pela embalagem (R$) |
| `custo_por_unidade` | REAL | **Calculado:** `preco_compra / peso_volume_total` |
| `quantidade_disponivel` | REAL | Estoque atual disponível |
| `quantidade_minima` | REAL | Alerta quando abaixo deste valor |
| `data_compra` | DATE | Data de aquisição |

### 4.2 Entidade: Produto

| Campo | Tipo | Descrição |
|---|---|---|
| `id` | INTEGER PK | Identificador único |
| `nome` | TEXT | Nome do produto (ex: Brigadeiro de Ninho) |
| `rendimento_receita` | INTEGER | Unidades produzidas por receita |
| `comissao_perc` | REAL | Percentual de markup sobre o custo |
| `custo_unitario` | REAL | **Calculado:** `custo_total_receita / rendimento` |
| `preco_venda_unitario` | REAL | **Calculado:** `custo × (1 + comissao / 100)` |

### 4.3 Entidade: ProdutoInsumo (N:N)

| Campo | Tipo | Descrição |
|---|---|---|
| `produto_id` | INTEGER FK | Referência ao produto |
| `insumo_id` | INTEGER FK | Referência ao insumo |
| `quantidade_usada_receita` | REAL | Quantidade do insumo em 1 receita (g/ml/un) |
| `custo_proporcional` | REAL | **Calculado:** `(qtd_usada / peso_total) × preco_insumo` |

### 4.4 Entidade: Cliente

| Campo | Tipo | Descrição |
|---|---|---|
| `id` | INTEGER PK | Identificador único |
| `nome` | TEXT | Nome completo do cliente |
| `contato` | TEXT | WhatsApp ou e-mail (opcional) |

### 4.5 Entidade: Pedido

| Campo | Tipo | Descrição |
|---|---|---|
| `id` | INTEGER PK | Identificador único |
| `cliente_id` | INTEGER FK | Referência ao cliente |
| `data_pedido` | DATE | Data em que o pedido foi feito |
| `data_entrega` | DATE | Data prevista para entrega |
| `valor_total` | REAL | Soma dos itens do pedido |
| `pag_inicial_valor` | REAL | Valor do sinal pago |
| `pag_inicial_data` | DATE | Data do pagamento inicial |
| `pag_inicial_forma` | TEXT | Pix / Dinheiro / Cartão |
| `pag_inicial_status` | TEXT | Recebido / Pendente |
| `pag_final_valor` | REAL | Valor do pagamento restante |
| `pag_final_data` | DATE | Data do pagamento final |
| `pag_final_forma` | TEXT | Pix / Dinheiro / Cartão |
| `pag_final_status` | TEXT | Recebido / Pendente |
| `responsavel` | TEXT | Nome da confeiteira responsável |

### 4.6 Entidade: PedidoItem

| Campo | Tipo | Descrição |
|---|---|---|
| `id` | INTEGER PK | Identificador único |
| `pedido_id` | INTEGER FK | Referência ao pedido |
| `produto_id` | INTEGER FK | Referência ao produto |
| `quantidade` | INTEGER | Número de unidades solicitadas |
| `preco_unitario_snapshot` | REAL | Preço no momento do pedido (histórico) |
| `valor_item` | REAL | **Calculado:** `quantidade × preco_unitario_snapshot` |

### 4.7 Entidade: Despesa

| Campo | Tipo | Descrição |
|---|---|---|
| `id` | INTEGER PK | Identificador único |
| `data` | DATE | Data da despesa |
| `valor` | REAL | Valor em reais |
| `descricao` | TEXT | Descrição da despesa |
| `categoria` | TEXT | Insumos / Investimentos / Outros |
| `responsavel` | TEXT | Nome do responsável |
| `status` | TEXT | Pendente / Pago |
| `forma_pagamento` | TEXT | Pix / Dinheiro / Cartão |
| `data_pagamento_final` | DATE | Data em que a despesa foi quitada |

### 4.8 Entidade: Rendimento

| Campo | Tipo | Descrição |
|---|---|---|
| `id` | INTEGER PK | Identificador único |
| `cliente_id` | INTEGER FK | Referência ao cliente (opcional) |
| `pag_inicial_valor` | REAL | Valor do sinal recebido |
| `pag_inicial_data` | DATE | Data do recebimento inicial |
| `pag_inicial_forma` | TEXT | Pix / Dinheiro |
| `pag_inicial_status` | TEXT | Recebido / Pendente |
| `pag_final_valor` | REAL | Valor final recebido |
| `pag_final_data` | DATE | Data do recebimento final |
| `pag_final_forma` | TEXT | Pix / Dinheiro |
| `pag_final_status` | TEXT | Recebido / Pendente |
| `responsavel` | TEXT | Confeiteira responsável |

---

## 5. Navegação e Fluxo Principal

### 5.1 Estrutura de Navegação

```
Aplicação
├── 🏠 Dashboard        → Resumo financeiro (tela inicial)
├── 🧂 Insumos          → Cadastro e listagem de ingredientes/embalagens
├── 🍫 Produtos         → Fichas de precificação
├── 📦 Pedidos          → Gestão de pedidos e clientes
├── 💰 Financeiro       → Despesas e rendimentos
└── ⚙️ Configurações    → Backup do banco, nome do estabelecimento
```

### 5.2 Fluxo Típico de Uso

```
1. Confeiteira recebe pedido de cliente
   ↓
2. Verifica se o produto existe em Produtos
   → Se não: cadastra Insumos → cria ficha em Produtos
   ↓
3. Cadastra o Pedido (seleciona produto + quantidade)
   → Sistema calcula valor total automaticamente
   ↓
4. Registra pagamento inicial (sinal)
   ↓
5. Na entrega: registra pagamento final
   ↓
6. Dashboard é atualizado refletindo os novos valores
```

---

## 6. Critérios de Aceite — Fase 1 (MVP)

O sistema será considerado aprovado quando:

- [ ] For possível cadastrar ao menos 10 insumos e 3 produtos sem erros
- [ ] O custo unitário e o preço de venda forem calculados automaticamente e corretamente
- [ ] Um pedido com múltiplos produtos mostrar o valor total correto
- [ ] O dashboard exibir saldo atual e total a receber coerentes com os lançamentos
- [ ] O executável `.exe` rodar em Windows sem instalação adicional de Python
- [ ] O banco de dados sobreviver ao fechamento e reabertura com todos os dados intactos

---

*Documento de Requisitos v1.0 — Sistema de Gestão para Confeitaria*
