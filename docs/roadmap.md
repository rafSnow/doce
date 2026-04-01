# Roadmap de Desenvolvimento — Sprints por Funcionalidade
## Sistema de Gestão para Confeitaria
**Plataforma:** Python + CustomTkinter + SQLite  
**Distribuição:** Executável `.exe` via PyInstaller (Windows)  

---

## Visão Geral das Fases

| Fase | Foco | Sprints | Entrega |
|---|---|---|---|
| **Fase 1 — MVP** | Base funcional completa para uso real | 1 a 5 | ~5 semanas |
| **Fase 2 — Evolução** | Estoque com alertas, financeiro completo, backup | 6 a 8 | ~3 semanas |
| **Fase 3 — Melhorias** | Relatórios, gráficos, histórico de preços | 9 a 11 | ~3 semanas |

---

## FASE 1 — MVP

---

### Sprint 1 — Fundação do Projeto e Banco de Dados
**Duração:** 1 semana  
**Objetivo:** Estrutura do projeto, configuração do ambiente e criação do banco de dados com todas as entidades.

#### Tarefas

| # | Tarefa | Requisito |
|---|---|---|
| 1.1 | Criar estrutura de pastas do projeto (`app/`, `models/`, `views/`, `services/`, `db/`) | — |
| 1.2 | Configurar `requirements.txt` com dependências (CustomTkinter, openpyxl) | RNF-01 |
| 1.3 | Implementar módulo de conexão com SQLite (`db/connection.py`) | RNF-02 |
| 1.4 | Criar script de inicialização do banco (`db/schema.py`) com todas as tabelas | RF-01..RF-35 |
| 1.5 | Implementar migrations simples: verificar se tabelas existem antes de criar | RNF-02 |
| 1.6 | Criar janela principal (`MainApp`) com menu lateral/abas de navegação | RNF-04 |
| 1.7 | Implementar tema e estilo visual padrão (paleta de cores, fontes) | RNF-04 |
| 1.8 | Configurar PyInstaller: gerar `.exe` funcional com banco embutido | RNF-03 |

#### Entregável
> Aplicação abre sem erros, banco SQLite criado automaticamente, janela principal exibida, `.exe` compilando.

---

### Sprint 2 — Módulo de Insumos (Cadastro e Listagem)
**Duração:** 1 semana  
**Objetivo:** CRUD completo de insumos com cálculo automático de custo por unidade.

#### Tarefas

| # | Tarefa | Requisito |
|---|---|---|
| 2.1 | Criar model `Insumo` com todos os campos e validações | RF-01 |
| 2.2 | Implementar serviço `InsumoService` (insert, update, delete, list, get_by_id) | RF-01, RF-02 |
| 2.3 | Calcular e persistir `custo_por_unidade` automaticamente ao salvar | RF-06 |
| 2.4 | Tela de listagem de insumos com tabela, barra de busca por nome e filtro por categoria | RF-03 |
| 2.5 | Formulário de cadastro de insumo (modal/frame lateral) com validação de campos obrigatórios | RF-01 |
| 2.6 | Formulário de edição com campos pré-preenchidos | RF-02 |
| 2.7 | Confirmação de exclusão com `messagebox` | RF-02, RNF-07 |
| 2.8 | Exibir custo por unidade calculado ao lado dos campos de preço/volume no formulário | RF-06 |

#### Entregável
> CRUD de insumos funcionando, custo por unidade calculado e exibido, filtros por nome e categoria operacionais.

---

### Sprint 3 — Módulo de Precificação de Produtos
**Duração:** 1 semana  
**Objetivo:** Fichas técnicas de produtos com cálculo automático de custo e preço de venda.

#### Tarefas

| # | Tarefa | Requisito |
|---|---|---|
| 3.1 | Criar model `Produto` e model `ProdutoInsumo` (tabela relacional N:N) | RF-07, RF-08 |
| 3.2 | Implementar `ProdutoService` (insert, update, delete, list, duplicate) | RF-07, RF-13, RF-14 |
| 3.3 | Tela de listagem de produtos com tabela e botões de ação | RF-14 |
| 3.4 | Formulário de cadastro de produto: nome, rendimento, markup | RF-07, RF-10 |
| 3.5 | Componente de seleção de insumos na ficha: adicionar/remover insumo com quantidade usada | RF-08 |
| 3.6 | Calcular custo total da receita e custo unitário em tempo real (ao editar ingredientes) | RF-09 |
| 3.7 | Calcular e exibir preço de venda unitário com base no markup definido | RF-10 |
| 3.8 | Exibir lucro estimado para um pedido ao informar a quantidade de unidades | RF-11, RF-12 |
| 3.9 | Funcionalidade de duplicar ficha (clonar produto com novos insumos editáveis) | RF-13 |

#### Entregável
> Ficha técnica completa criada e editada, cálculos automáticos de custo e preço de venda corretos, duplicação funcionando.

---

### Sprint 4 — Módulo de Pedidos e Clientes
**Duração:** 1 semana  
**Objetivo:** Gestão de pedidos por cliente com controle de pagamento em duas etapas.

#### Tarefas

| # | Tarefa | Requisito |
|---|---|---|
| 4.1 | Criar model `Cliente`, `Pedido` e `PedidoItem` | RF-22, RF-15, RF-16 |
| 4.2 | Implementar `ClienteService` (CRUD simples) | RF-22 |
| 4.3 | Tela de listagem de clientes (modal ou sub-tela em Pedidos) | RF-22 |
| 4.4 | Formulário de pedido: seleção de cliente, data de entrega | RF-15 |
| 4.5 | Componente de adição de itens ao pedido: selecionar produto + quantidade | RF-16 |
| 4.6 | Calcular e exibir valor total do pedido automaticamente | RF-19 |
| 4.7 | Registrar pagamento inicial (sinal): valor, data, forma e status | RF-17 |
| 4.8 | Registrar pagamento final: valor, data, forma e status | RF-18 |
| 4.9 | Salvar `preco_unitario_snapshot` do produto no momento do pedido | RF-19 |
| 4.10 | Tela de listagem de pedidos com filtro por cliente, status e período | RF-20 |
| 4.11 | Indicação visual (cor/ícone) para pedidos com pagamento pendente | RF-21 |

#### Entregável
> Pedidos criados com múltiplos itens, valor total calculado, pagamentos registrados, listagem com filtros e destaque visual de pendências.

---

### Sprint 5 — Dashboard MVP e Empacotamento
**Duração:** 1 semana  
**Objetivo:** Dashboard com resumo financeiro básico e geração do executável `.exe` validado.

#### Tarefas

| # | Tarefa | Requisito |
|---|---|---|
| 5.1 | Implementar queries de agregação: saldo atual, a receber, despesas pendentes, saldo previsto | RF-30..RF-33 |
| 5.2 | Tela de Dashboard com cards de resumo financeiro | RF-30, RF-31, RF-32, RF-33 |
| 5.3 | Atualizar dashboard automaticamente ao navegar para ele | RF-30..RF-33 |
| 5.4 | Validar todos os critérios de aceite da Fase 1 | — |
| 5.5 | Ajustes de UX: mensagens de erro, validações, feedback visual em operações | RNF-04, RNF-07 |
| 5.6 | Formatar todos os valores monetários em R$ com 2 casas decimais | RNF-06 |
| 5.7 | Testar e validar `.exe` em máquina Windows sem Python instalado | RNF-03 |
| 5.8 | Corrigir issues encontrados nos testes de aceite | — |

#### Entregável
> **MVP entregável.** Dashboard com saldo real, a receber e pendências. Executável `.exe` validado em Windows.

---

## FASE 2 — EVOLUÇÃO

---

### Sprint 6 — Estoque com Alertas e Módulo Financeiro (Despesas)
**Duração:** 1 semana  
**Objetivo:** Controle de quantidade em estoque com alertas visuais e CRUD de despesas.

#### Tarefas

| # | Tarefa | Requisito |
|---|---|---|
| 6.1 | Adicionar campos `quantidade_disponivel` e `quantidade_minima` ao form de Insumos | RF-04 |
| 6.2 | Indicação visual (cor vermelha/amarela) na listagem de insumos para itens abaixo do mínimo | RF-05 |
| 6.3 | Badge/notificação no menu de insumos quando houver alertas de estoque | RF-05 |
| 6.4 | Criar model `Despesa` com todos os campos | RF-23 |
| 6.5 | Implementar `DespesaService` (insert, update, delete, list, total por categoria) | RF-23, RF-24, RF-26 |
| 6.6 | Formulário de cadastro e edição de despesas | RF-23, RF-24 |
| 6.7 | Tela de listagem de despesas com filtros por período, categoria e status | RF-25 |
| 6.8 | Totalizador de despesas por categoria exibido na listagem | RF-26 |

#### Entregável
> Alertas de estoque visuais funcionando, módulo de despesas com CRUD completo e filtros operacionais.

---

### Sprint 7 — Módulo Financeiro (Rendimentos) e Dashboard Completo
**Duração:** 1 semana  
**Objetivo:** CRUD de rendimentos e dashboard expandido com filtros por período.

#### Tarefas

| # | Tarefa | Requisito |
|---|---|---|
| 7.1 | Criar model `Rendimento` com todos os campos | RF-27 |
| 7.2 | Implementar `RendimentoService` (insert, update, delete, list) | RF-27, RF-28, RF-29 |
| 7.3 | Formulário de cadastro e edição de rendimentos com vínculo ao cliente | RF-27 |
| 7.4 | Tela de listagem de rendimentos com filtros por período e status | RF-29 |
| 7.5 | Adicionar card de "Total investido em insumos e investimentos" ao Dashboard | RF-34 |
| 7.6 | Implementar seletor de período no Dashboard (mês, trimestre, personalizado) | RF-35 |
| 7.7 | Recalcular todos os cards do Dashboard conforme período selecionado | RF-35 |

#### Entregável
> Módulo financeiro completo (despesas + rendimentos). Dashboard com filtros por período funcionais.

---

### Sprint 8 — Backup, Configurações e Refinamentos
**Duração:** 1 semana  
**Objetivo:** Backup manual do banco pela interface, tela de configurações e polimento geral.

#### Tarefas

| # | Tarefa | Requisito |
|---|---|---|
| 8.1 | Tela de Configurações com campo para nome do estabelecimento | — |
| 8.2 | Botão de backup: copia o arquivo `.db` para local escolhido pelo usuário | RNF-08 |
| 8.3 | Feedback visual de sucesso/erro no backup | RNF-08 |
| 8.4 | Revisão geral de usabilidade: tamanhos de fonte, espaçamentos, responsividade da janela | RNF-04 |
| 8.5 | Testar performance: verificar que consultas respondem em < 2 segundos | RNF-05 |
| 8.6 | Adicionar índices ao banco onde necessário para performance | RNF-05 |
| 8.7 | Revisão de mensagens de confirmação de exclusão em todos os módulos | RNF-07 |

#### Entregável
> **Fase 2 completa.** Backup funcional, configurações persistidas, performance validada.

---

## FASE 3 — MELHORIAS

---

### Sprint 9 — Exportação para Excel
**Duração:** 1 semana  
**Objetivo:** Relatórios exportáveis em `.xlsx` para os principais módulos.

| # | Tarefa | Módulo |
|---|---|---|
| 9.1 | Exportar listagem de insumos para Excel | Insumos |
| 9.2 | Exportar fichas de produtos com custo e preço de venda | Produtos |
| 9.3 | Exportar pedidos com itens e status de pagamento | Pedidos |
| 9.4 | Exportar despesas por período com totalizador por categoria | Financeiro |
| 9.5 | Exportar rendimentos por período | Financeiro |
| 9.6 | Botão "Exportar" presente em cada tela de listagem | — |

---

### Sprint 10 — Histórico de Preços e Gráficos
**Duração:** 1 semana  
**Objetivo:** Rastrear variação de preço dos insumos ao longo do tempo e exibir gráficos de desempenho.

| # | Tarefa | Módulo |
|---|---|---|
| 10.1 | Criar tabela `HistoricoPrecoInsumo` para registrar variações de preço por data | Insumos |
| 10.2 | Ao editar preço de insumo, registrar a alteração com data no histórico | Insumos |
| 10.3 | Tela de histórico de preço por insumo (tabela + linha do tempo) | Insumos |
| 10.4 | Gráfico de barras: faturamento mensal (rendimentos) vs despesas | Dashboard |
| 10.5 | Gráfico de pizza: distribuição de despesas por categoria | Dashboard |
| 10.6 | Integrar biblioteca de gráficos (matplotlib embutido no CustomTkinter) | — |

---

### Sprint 11 — Impressão de Recibo e Finalização
**Duração:** 1 semana  
**Objetivo:** Geração de recibo/ordem de serviço e polimento final da aplicação.

| # | Tarefa | Módulo |
|---|---|---|
| 11.1 | Template de recibo/ordem de serviço em PDF para pedidos | Pedidos |
| 11.2 | Pré-visualização do recibo antes de imprimir/salvar | Pedidos |
| 11.3 | Opção de salvar recibo como PDF ou imprimir diretamente | Pedidos |
| 11.4 | Revisão completa de acessibilidade e UX | Geral |
| 11.5 | Documentação de uso (manual simplificado em PDF) | — |
| 11.6 | Build final do `.exe` com todas as funcionalidades validadas | — |

---

## Resumo de Sprints

| Sprint | Módulo Principal | Fase | RFs Cobertos |
|---|---|---|---|
| 1 | Fundação + Banco de Dados | MVP | — |
| 2 | Insumos (CRUD) | MVP | RF-01..RF-06 |
| 3 | Precificação de Produtos | MVP | RF-07..RF-14 |
| 4 | Pedidos e Clientes | MVP | RF-15..RF-22 |
| 5 | Dashboard MVP + `.exe` | MVP | RF-30..RF-33 |
| 6 | Estoque + Despesas | Evolução | RF-04, RF-05, RF-23..RF-26 |
| 7 | Rendimentos + Dashboard Completo | Evolução | RF-27..RF-29, RF-34..RF-35 |
| 8 | Backup + Config + Refinamentos | Evolução | RNF-05..RNF-08 |
| 9 | Exportação Excel | Melhorias | — |
| 10 | Histórico de Preços + Gráficos | Melhorias | — |
| 11 | Impressão de Recibo + Finalização | Melhorias | — |

---

*Roadmap v1.0 — Sistema de Gestão para Confeitaria*
