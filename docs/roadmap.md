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

## Status de Execução (Atualizado em 16/04/2026)

- Sprint atual: **Sprint 12 — Qualidade e Hardening Técnico**
- Sprint 6.1: **Concluída**
- Sprint 6.2: **Concluída**
- Sprint 6.3: **Concluída**
- Sprint 6.4: **Concluída**
- Sprint 6.5: **Concluída**
- Sprint 6.6: **Concluída**
- Sprint 6.7: **Concluída**
- Sprint 6.8: **Concluída**
- Sprint 7.1: **Concluída**
- Sprint 7.2: **Concluída**
- Sprint 7.3: **Concluída**
- Sprint 7.4: **Concluída**
- Sprint 7.5: **Concluída**
- Sprint 7.6: **Concluída**
- Sprint 7.7: **Concluída**
- Sprint 8.1: **Concluída**
- Sprint 8.2: **Concluída**
- Sprint 8.3: **Concluída**
- Sprint 8.4: **Concluída**
- Sprint 8.5: **Concluída**
- Sprint 8.6: **Concluída**
- Sprint 8.7: **Concluída**
- Sprint 9.1: **Concluída**
- Sprint 9.2: **Concluída**
- Sprint 9.3: **Concluída**
- Sprint 9.4: **Concluída**
- Sprint 9.5: **Concluída**
- Sprint 9.6: **Concluída**
- Sprint 10.1: **Concluída**
- Sprint 10.2: **Concluída**
- Sprint 10.3: **Concluída**
- Sprint 10.4: **Concluída**
- Sprint 10.5: **Concluída**
- Sprint 10.6: **Concluída**
- Sprint 11: **Concluída**
- Sprint 12: **Concluída**

### Sprint Review Objetivo — Sprint 6.1

- Objetivo da tarefa 6.1 atendido: campos de estoque (`quantidade_disponivel` e `quantidade_minima`) presentes no formulário de Insumos.
- Persistência atendida: os dois campos são salvos/atualizados no banco pelo serviço de insumos.
- Compatibilidade com bases antigas atendida: adicionada migração automática para criação das colunas caso o banco já existisse sem esses campos.
  
**Arquivos impactados na Sprint 6.1**
- `app/views/insumos_view.py` (formulário com os dois campos)
- `app/services/insumo_service.py` (salvar/listar os dois campos)
- `app/db/schema.py` (DDL + migração para bancos legados)

### Sprint Review Objetivo — Sprint 6.2

- Objetivo da tarefa 6.2 atendido: listagem de insumos com indicação visual por cor para estoque crítico e de alerta.
- Regra aplicada na listagem:
	- Vermelho para insumo com `quantidade_disponivel <= 0`.
	- Amarelo para insumo com `quantidade_disponivel <= quantidade_minima`.
- Implementação concentrada em camada de View, sem alterar regra de persistência.

**Arquivos impactados na Sprint 6.2**
- `app/views/insumos_view.py` (tags visuais no `Treeview` e marcação por condição de estoque)

### Sprint Review Objetivo — Sprint 6.3

- Objetivo da tarefa 6.3 atendido: menu de Insumos exibe badge/notificação quando há alertas de estoque.
- Regra aplicada no menu:
	- Botão lateral muda para `Insumos (N)` quando existe ao menos 1 insumo com `quantidade_disponivel <= quantidade_minima`.
	- Botão volta para `Insumos` quando não há alertas.
- Atualização do badge implementada em dois fluxos:
	- Ao navegar entre telas (recontagem no banco).
	- Ao recarregar a tela de insumos (callback em tempo de execução da própria listagem).

**Arquivos impactados na Sprint 6.3**
- `app/services/insumo_service.py` (método de contagem de alertas de estoque)
- `app/views/main_window.py` (renderização/atualização do badge no menu lateral)
- `app/views/insumos_view.py` (callback para atualizar contador após recarga da lista)

### Sprint Review Objetivo — Sprint 6.4

- Objetivo da tarefa 6.4 atendido: criado model `Despesa` com todos os campos definidos no RF-23.
- Campos contemplados no model:
	- `data`, `valor`, `descricao`, `categoria`, `responsavel`, `status`, `forma_pagamento`, `data_pagamento_final` e `id`.
- Estrutura alinhada ao padrão já utilizado nos demais models (dataclass com tipagem e defaults seguros para uso em formulário/serviço).

**Arquivos impactados na Sprint 6.4**
- `app/models/despesa.py` (novo model de domínio para despesas)

### Sprint Review Objetivo — Sprint 6.5

- Objetivo da tarefa 6.5 atendido: implementado `DespesaService` com operações de persistência para despesas.
- Funcionalidades entregues no serviço:
	- `salvar` com suporte a inserção e atualização.
	- `excluir` para remoção por identificador.
	- `listar` com suporte a filtros por período, categoria e status.
	- `total_por_categoria` para totalização de despesas agregadas por categoria.
	- `get_by_id` e mapeamento interno para o model, mantendo padrão adotado pelos demais serviços.

**Arquivos impactados na Sprint 6.5**
- `app/services/despesa_service.py` (novo serviço com CRUD e agregação por categoria)

### Sprint Review Objetivo — Sprint 6.6

- Objetivo da tarefa 6.6 atendido: implementado formulário funcional de cadastro e edição de despesas no módulo Financeiro.
- Funcionalidades entregues no formulário:
	- Cadastro de despesa com os campos definidos no RF-23.
	- Edição de despesa existente via seleção na listagem e abertura do formulário preenchido.
	- Validações de dados essenciais (data, valor, categoria, status e regra para despesa paga com data final).
	- Exclusão disponível no fluxo de edição, em aderência ao RF-24.
- Integração realizada no menu principal para abrir a nova tela de Financeiro no lugar do placeholder.

**Arquivos impactados na Sprint 6.6**
- `app/views/financeiro_view.py` (nova tela com listagem básica + formulário de cadastro/edição de despesas)
- `app/views/main_window.py` (integração do botão Financeiro com a nova view)

### Sprint Review Objetivo — Sprint 6.7

- Objetivo da tarefa 6.7 atendido: listagem de despesas evoluída com filtros por período, categoria e status.
- Funcionalidades entregues na listagem:
	- Filtro por período com `data inicial` e `data final`.
	- Filtro por `categoria` com opção de visão geral (`Todos`) ou categorias específicas.
	- Filtro por `status` com opção de visão geral (`Todos`) ou status específicos.
	- Ações de `Buscar` e `Limpar` para aplicar e resetar filtros sem sair da tela.
- Validação aplicada nos filtros:
	- Datas no padrão `DD/MM/AAAA`.
	- Bloqueio de período inválido quando data inicial é maior que data final.

**Arquivos impactados na Sprint 6.7**
- `app/views/financeiro_view.py` (barra de filtros na listagem, integração com `DespesaService.listar` e validações de período)

### Sprint Review Objetivo — Sprint 6.8

- Objetivo da tarefa 6.8 atendido: totalizador de despesas por categoria exibido na listagem do módulo Financeiro.
- Funcionalidades entregues no totalizador:
	- Exibição dos totais de `Insumos`, `Investimentos` e `Outros` na tela de listagem.
	- Exibição de `Total Geral` consolidando as categorias.
	- Atualização dinâmica dos totalizadores conforme os filtros aplicados (período, categoria e status).
	- Compatibilidade com cenário sem registros retornando totais zerados por categoria.
- Ajuste de serviço realizado para totalização aderente ao filtro de categoria selecionado na listagem.

**Arquivos impactados na Sprint 6.8**
- `app/views/financeiro_view.py` (área de totalizadores por categoria e atualização conforme filtros da listagem)
- `app/services/despesa_service.py` (filtro opcional de categoria no método de totalização por categoria)

### Sprint Review Objetivo — Sprint 7.1

- Objetivo da tarefa 7.1 atendido: criado model `Rendimento` com todos os campos base definidos para o RF-27.
- Campos contemplados no model:
	- `cliente_id`, `pag_inicial_valor`, `pag_inicial_data`, `pag_inicial_forma`, `pag_inicial_status`.
	- `pag_final_valor`, `pag_final_data`, `pag_final_forma`, `pag_final_status`, `responsavel` e `id`.
- Estrutura alinhada ao padrão do projeto: uso de `dataclass`, tipagem com `Optional` e valores padrão seguros para uso futuro em service/view.

**Arquivos impactados na Sprint 7.1**
- `app/models/rendimento.py` (novo model de domínio para rendimentos)

### Sprint Review Objetivo — Sprint 7.2

- Objetivo da tarefa 7.2 atendido: implementado `RendimentoService` com operações de persistência para rendimentos.
- Funcionalidades entregues no serviço:
	- `salvar` com suporte a inserção e atualização.
	- `excluir` para remoção por identificador.
	- `listar` com suporte a filtros por período e status de pagamento.
	- `get_by_id` e mapeamento interno para o model, mantendo o padrão adotado pelos demais serviços.
- Regra de status aplicada na listagem:
	- `Pendente`: quando pagamento inicial ou final estiver pendente.
	- `Recebido`: quando pagamento inicial e final estiverem recebidos.

**Arquivos impactados na Sprint 7.2**
- `app/services/rendimento_service.py` (novo serviço com CRUD e filtros por período/status)

### Sprint Review Objetivo — Sprint 7.3

- Objetivo da tarefa 7.3 atendido: implementado formulário de cadastro e edição de rendimentos com vínculo obrigatório a cliente cadastrado.
- Funcionalidades entregues no fluxo de rendimentos:
	- Listagem de rendimentos com abertura de edição por duplo clique.
	- Formulário com seleção de cliente (`id - nome`) para garantir vínculo com `cliente_id`.
	- Cadastro e atualização dos campos de pagamento inicial e final (valor, data, forma e status).
	- Validações de data (`DD/MM/AAAA`), valores monetários e consistência para status `Recebido` exigir data.
	- Exclusão com confirmação no fluxo de edição.
- Integração realizada no módulo Financeiro:
	- Novo botão `Rendimentos` no cabeçalho da tela de despesas para abrir a gestão de rendimentos sem afetar os fluxos já concluídos de despesas.

**Arquivos impactados na Sprint 7.3**
- `app/views/rendimentos_view.py` (nova tela de rendimentos com listagem e formulário de cadastro/edição)
- `app/views/financeiro_view.py` (integração para abrir a tela de rendimentos pelo módulo Financeiro)

### Sprint Review Objetivo — Sprint 7.4

- Objetivo da tarefa 7.4 atendido: implementada listagem de rendimentos com filtros por período e status de pagamento.
- Funcionalidades entregues na listagem:
	- Filtro por período com `data inicial` e `data final`.
	- Filtro por `status` com opção de visão geral (`Todos`) ou status específicos (`Pendente`/`Recebido`).
	- Ações de `Buscar` e `Limpar` para aplicar e resetar filtros sem sair da tela.
- Validação aplicada nos filtros:
	- Datas no padrão `DD/MM/AAAA`.
	- Bloqueio de período inválido quando data inicial é maior que a data final.

**Arquivos impactados na Sprint 7.4**
- `app/views/rendimentos_view.py` (barra de filtros na listagem, integração com `RendimentoService.listar` e validações de período)

### Sprint Review Objetivo — Sprint 7.5

- Objetivo da tarefa 7.5 atendido: adicionado no Dashboard o card de `Total investido em insumos e investimentos`.
- Regra aplicada para o indicador:
	- Soma das despesas da categoria `Insumos` e `Investimentos` com status `Pago`.
	- Valor exibido em formato monetário padrão `R$` com duas casas decimais.
- Ajuste de layout realizado no Dashboard:
	- Expansão da grade para acomodar o novo card sem remover os cards já existentes de saldo e pendências.

**Arquivos impactados na Sprint 7.5**
- `app/services/dashboard_service.py` (cálculo de `total_investido` no resumo financeiro)
- `app/views/dashboard_view.py` (novo card visual e binding do valor no carregamento dos dados)

### Sprint Review Objetivo — Sprint 7.6

- Objetivo da tarefa 7.6 atendido: implementado seletor de período no Dashboard com opções `Mês Atual`, `Trimestre Atual` e `Personalizado`.
- Funcionalidades entregues no seletor:
	- Seleção rápida de período padrão para mês e trimestre atuais, com preenchimento automático das datas.
	- Modo personalizado com edição manual de `data inicial` e `data final`.
	- Ação de aplicar período com validação de formato de data (`DD/MM/AAAA`) e bloqueio de intervalo inválido.
	- Exibição textual do período atualmente aplicado para clareza operacional da usuária.

**Arquivos impactados na Sprint 7.6**
- `app/views/dashboard_view.py` (novo seletor de período no cabeçalho e validações de aplicação)

### Sprint Review Objetivo — Sprint 7.7

- Objetivo da tarefa 7.7 atendido: todos os cards do Dashboard passaram a ser recalculados conforme o período aplicado no seletor.
- Regra implementada no recálculo:
	- `Saldo Atual`: entradas recebidas no período menos despesas pagas no período.
	- `A Receber`: pagamentos pendentes de pedidos dentro do período.
	- `Falta Pagar`: despesas pendentes dentro do período.
	- `Saldo Previsto`: combinação dos indicadores do período (`saldo_atual + a_receber - falta_pagar`).
	- `Total Investido`: despesas pagas de `Insumos` e `Investimentos` dentro do período.
- Compatibilidade de datas aplicada no serviço:
	- Parsing para formatos `DD/MM/AAAA` e `YYYY-MM-DD`, mantendo consistência com bases já existentes.

**Arquivos impactados na Sprint 7.7**
- `app/services/dashboard_service.py` (recalculo dos indicadores com filtro de período)
- `app/views/dashboard_view.py` (integração do período aplicado ao carregamento do resumo)

### Sprint Review Objetivo — Sprint 8.1

- Objetivo da tarefa 8.1 atendido: criada a Tela de Configurações com campo para nome do estabelecimento.
- Persistência entregue para o nome do estabelecimento:
	- Criação da estrutura de configurações no banco com chave/valor.
	- Leitura e salvamento do nome com valor padrão seguro para cenários sem configuração prévia.
- Integração concluída na janela principal:
	- Nome configurado é exibido no cabeçalho lateral.
	- Título da janela é atualizado imediatamente após salvar.

**Arquivos impactados na Sprint 8.1**
- `app/db/schema.py` (nova tabela `configuracao`)
- `app/services/configuracao_service.py` (serviço de leitura/gravação do nome do estabelecimento)
- `app/views/configuracoes_view.py` (nova tela de Configurações com validação e ação de salvar)
- `app/views/main_window.py` (integração da tela de Configurações e atualização visual do nome)

### Sprint Review Objetivo — Sprint 8.2

- Objetivo da tarefa 8.2 atendido: implementado botão de backup manual na tela de Configurações, com escolha do local de destino pela usuária.
- Fluxo de backup entregue:
	- Abertura de diálogo para seleção de caminho e nome do arquivo `.db`.
	- Geração da cópia do banco atual por rotina segura de backup via SQLite.
	- Criação automática da pasta de destino quando necessário.
- Feedback visual entregue conforme RNF-08:
	- Mensagem de sucesso exibindo o caminho final do backup.
	- Mensagem de erro com detalhes em caso de falha.

**Arquivos impactados na Sprint 8.2**
- `app/db/connection.py` (helper reutilizável para caminho do banco)
- `app/services/configuracao_service.py` (novo método `realizar_backup`)
- `app/views/configuracoes_view.py` (botão de backup, seletor de arquivo e feedback visual)

### Sprint Review Objetivo — Sprint 8.3

- Objetivo da tarefa 8.3 atendido: feedback visual de sucesso/erro do backup foi aprimorado na própria tela de Configurações.
- Melhorias implementadas no fluxo de feedback:
	- Indicador textual persistente com status do backup em tempo real.
	- Diferenciação visual por estado (processando, sucesso, erro) com cores específicas.
	- Mensagem com data/hora e caminho final quando o backup conclui com sucesso.
	- Mensagem de cancelamento quando a usuária desiste de sobrescrever arquivo existente.
- Robustez de usabilidade adicionada:
	- Confirmação antes de sobrescrever arquivo de backup já existente.
	- Botão de backup desabilitado durante execução para evitar cliques duplicados.

**Arquivos impactados na Sprint 8.3**
- `app/views/configuracoes_view.py` (status visual persistente, confirmação de sobrescrita e controle de estado do botão)

### Sprint Review Objetivo — Sprint 8.4

- Objetivo da tarefa 8.4 atendido: executada revisão de usabilidade com foco em tamanhos de fonte, espaçamentos e responsividade da janela.
- Melhorias aplicadas na estrutura global da navegação:
	- Sidebar com botões maiores e mais clicáveis, fonte padronizada e melhor legibilidade.
	- Ajuste responsivo automático da largura da sidebar e dos paddings da área de conteúdo conforme tamanho da janela.
	- Adaptação da tipografia principal para preservar leitura em janelas menores.
- Melhorias aplicadas em telas críticas:
	- Dashboard com tipografia escalável dos cards e ajuste responsivo dos espaçamentos para diferentes larguras.
	- Configurações com refinamento de fontes, espaçamentos e comportamento responsivo de layout.

**Arquivos impactados na Sprint 8.4**
- `app/views/main_window.py` (responsividade global, tamanhos de fonte e espaçamentos da navegação)
- `app/views/dashboard_view.py` (ajuste responsivo de tipografia e espaçamentos no resumo financeiro)
- `app/views/configuracoes_view.py` (refino de usabilidade e responsividade no formulário de configurações)

### Sprint Review Objetivo — Sprint 8.5

- Objetivo da tarefa 8.5 atendido: implementado e executado diagnóstico de performance para validar se as consultas principais respondem abaixo de 2 segundos.
- Entrega técnica da validação:
	- Novo serviço dedicado para benchmark de consultas com repetições, tempo médio e tempo máximo por operação.
	- Integração na tela de Configurações com botão `Validar desempenho` e feedback visual de resultado.
	- Resultado consolidado com alerta automático quando alguma consulta ultrapassa o limite definido.
- Resultado da medição realizada nesta sprint:
	- Todas as consultas avaliadas ficaram abaixo de 2 segundos.
	- Maior tempo máximo medido: `0,001344s`.
	- Meta de desempenho da sprint considerada atendida para o cenário atual de dados.

**Arquivos impactados na Sprint 8.5**
- `app/services/performance_service.py` (novo serviço de benchmark de consultas)
- `app/views/configuracoes_view.py` (ação de validação de desempenho e feedback visual do diagnóstico)

### Sprint Review Objetivo — Sprint 8.6

- Objetivo da tarefa 8.6 atendido: adicionados índices no banco SQLite para otimizar consultas de listagem, filtros, ordenações e joins já utilizados pela aplicação.
- Índices implementados por área de consulta:
	- Listagens por nome: `cliente`, `insumo` e `produto`.
	- Pedidos: filtros por cliente/status, ordenação por data e acesso a itens por `pedido_id`/`produto_id`.
	- Despesas: consultas por período e filtros por categoria/status.
	- Rendimentos: filtros de período por pagamento inicial/final e status de recebimento.
- Validação técnica da entrega:
	- Migração executada com sucesso e verificação de criação de `13` índices (`idx_*`) no banco atual.
	- Diagnóstico de performance pós-índices executado sem regressão, mantendo todas as consultas dentro do limite de 2 segundos.

**Arquivos impactados na Sprint 8.6**
- `app/db/schema.py` (criação de índices `CREATE INDEX IF NOT EXISTS` para consultas críticas)

### Sprint Review Objetivo — Sprint 8.7

- Objetivo da tarefa 8.7 atendido: revisadas e padronizadas as mensagens de confirmação de exclusão em todos os módulos com operação de delete.
- Padronização aplicada no fluxo de confirmação:
	- Título único de confirmação: `Confirmar exclusao`.
	- Mensagem contextual com identificação do registro (nome/descrição/ID) conforme o módulo.
	- Alerta explícito de irreversibilidade: `Esta acao nao pode ser desfeita.`
- Cobertura revisada por módulo:
	- Clientes, Insumos, Produtos, Pedidos, Despesas e Rendimentos.
	- Mantida a obrigatoriedade de confirmação antes de executar qualquer exclusão na camada de View.

**Arquivos impactados na Sprint 8.7**
- `app/views/clientes_view.py` (mensagem de confirmação contextual para exclusão de cliente)
- `app/views/insumos_view.py` (padronização das confirmações nos dois fluxos de exclusão)
- `app/views/produtos_view.py` (padronização das confirmações nos dois fluxos de exclusão)
- `app/views/pedidos_view.py` (mensagem contextual por ID do pedido)
- `app/views/financeiro_view.py` (mensagem contextual por descrição/ID da despesa)
- `app/views/rendimentos_view.py` (mensagem contextual por cliente/ID do rendimento)

### Sprint Review Objetivo — Sprint 9.1

- Objetivo da tarefa 9.1 atendido: implementada exportação da listagem de insumos para planilha Excel a partir da própria tela de Insumos.
- Fluxo entregue para a usuária:
	- Botão `Exportar Excel` disponível no cabeçalho da tela.
	- Exportação respeita os filtros atuais de busca por nome e categoria.
	- Seletor de destino permite escolher nome e pasta do arquivo `.xlsx`.
- Estrutura da planilha gerada:
	- Colunas com identificação, dados cadastrais, custo e estoque do insumo.
	- Cabeçalho formatado e primeira linha congelada para facilitar leitura.
	- Larguras de coluna ajustadas automaticamente para melhor visualização.
- Resultado de validação:
	- Implementação validada sem erros no arquivo alterado.
	- Dependência de geração de planilha já prevista no projeto via `openpyxl`.

**Arquivos impactados na Sprint 9.1**
- `app/views/insumos_view.py` (botão e rotina de exportação da listagem para Excel)

### Sprint Review Objetivo — Sprint 9.2

- Objetivo da tarefa 9.2 atendido: implementada exportação da listagem de produtos e das fichas técnicas para planilha Excel a partir da tela de Produtos.
- Fluxo entregue para a usuária:
	- Botão `Exportar Excel` disponível no cabeçalho da tela.
	- Exportação respeita o filtro atual por nome aplicado na listagem.
	- Seletor de destino permite escolher nome e pasta do arquivo `.xlsx`.
- Estrutura da planilha gerada:
	- Aba `Produtos` com resumo de nome, rendimento, custo unitário, markup e preço de venda.
	- Aba `Ficha Tecnica` com o detalhamento dos insumos de cada produto.
	- Cabeçalhos formatados, primeira linha congelada e colunas ajustadas automaticamente.
- Resultado de validação:
	- Implementação validada sem erros no arquivo alterado.
	- Dependência de geração de planilha já prevista no projeto via `openpyxl`.

**Arquivos impactados na Sprint 9.2**
- `app/views/produtos_view.py` (botão e rotina de exportação de produtos e fichas técnicas para Excel)

### Sprint Review Objetivo — Sprint 9.3

- Objetivo da tarefa 9.3 atendido: implementada exportação da listagem de pedidos e dos itens de cada pedido para planilha Excel a partir da tela de Pedidos.
- Fluxo entregue para a usuária:
	- Botão `Exportar Excel` disponível no cabeçalho da tela.
	- Exportação respeita os filtros atuais por cliente e status.
	- Seletor de destino permite escolher nome e pasta do arquivo `.xlsx`.
- Estrutura da planilha gerada:
	- Aba `Pedidos` com resumo de cliente, datas, valores e status de pagamento.
	- Aba `Itens Pedido` com o detalhamento dos produtos de cada pedido.
	- Cabeçalhos formatados, primeira linha congelada e colunas ajustadas automaticamente.
- Resultado de validação:
	- Implementação validada sem erros no arquivo alterado.
	- Dependência de geração de planilha já prevista no projeto via `openpyxl`.

**Arquivos impactados na Sprint 9.3**
- `app/views/pedidos_view.py` (botão e rotina de exportação de pedidos e itens para Excel)

### Sprint Review Objetivo — Sprint 9.4

- Objetivo da tarefa 9.4 atendido: implementada exportação das despesas para planilha Excel com totalizador por categoria, utilizando os filtros já disponíveis no módulo Financeiro.
- Fluxo entregue para a usuária:
	- Botão `Exportar Excel` disponível no cabeçalho da tela de despesas.
	- Exportação respeita os filtros atuais de período, categoria e status.
	- Seletor de destino permite escolher nome e pasta do arquivo `.xlsx`.
- Estrutura da planilha gerada:
	- Aba `Despesas` com listagem filtrada (dados de data, categoria, valor, status, forma, responsável e descrição).
	- Aba `Totais Categoria` com os totais de `Insumos`, `Investimentos`, `Outros` e `Total Geral`.
	- Cabeçalhos formatados, primeira linha congelada e colunas ajustadas automaticamente.
- Resultado de validação:
	- Implementação validada sem erros no arquivo alterado.
	- Dependência de geração de planilha já prevista no projeto via `openpyxl`.

**Arquivos impactados na Sprint 9.4**
- `app/views/financeiro_view.py` (botão e rotina de exportação de despesas com totalizador por categoria)

### Sprint Review Objetivo — Sprint 9.5

- Objetivo da tarefa 9.5 atendido: implementada exportação de rendimentos para planilha Excel com base nos filtros de período e status já existentes no módulo de Rendimentos.
- Fluxo entregue para a usuária:
	- Botão `Exportar Excel` disponível no cabeçalho da tela de rendimentos.
	- Exportação respeita os filtros atuais de período e status.
	- Seletor de destino permite escolher nome e pasta do arquivo `.xlsx`.
- Estrutura da planilha gerada:
	- Aba `Rendimentos` com listagem filtrada contendo cliente, valores, datas, formas e status de pagamento.
	- Aba `Resumo` com quantidade de rendimentos, totais inicial/final/geral e contagem de recebidos/pendentes.
	- Cabeçalhos formatados, primeira linha congelada e colunas ajustadas automaticamente.
- Resultado de validação:
	- Implementação validada sem erros no arquivo alterado.
	- Dependência de geração de planilha já prevista no projeto via `openpyxl`.

**Arquivos impactados na Sprint 9.5**
- `app/views/rendimentos_view.py` (botão e rotina de exportação de rendimentos por período/status para Excel)

### Sprint Review Objetivo — Sprint 9.6

- Objetivo da tarefa 9.6 atendido: botão de exportação consolidado em todas as telas de listagem da aplicação, garantindo cobertura completa do padrão de relatórios em Excel.
- Resultado da implementação nesta sprint:
	- Inclusão do botão `Exportar Excel` na tela de listagem de Clientes.
	- Implementação da rotina de exportação da própria listagem visível em tela, respeitando o filtro por nome aplicado.
	- Geração de planilha `.xlsx` com cabeçalho formatado, linha congelada e ajuste automático de colunas.
- Consolidação final da Sprint 9:
	- Insumos, Produtos, Pedidos, Despesas, Rendimentos e Clientes com ação de exportação disponível na listagem.
- Resultado de validação:
	- Implementação validada sem erros no arquivo alterado.
	- Dependência de geração de planilha mantida no padrão já adotado com `openpyxl`.

**Arquivos impactados na Sprint 9.6**
- `app/views/clientes_view.py` (botão e rotina de exportação da listagem de clientes para Excel)

### Sprint Review Objetivo — Sprint 10.1

- Objetivo da tarefa 10.1 atendido: criada a estrutura persistente para histórico de variação de preço de insumos no banco SQLite.
- Entrega técnica da sprint:
	- Nova tabela `historico_preco_insumo` adicionada ao schema com vínculo ao insumo (`insumo_id`).
	- Campos de histórico definidos para registrar preço anterior, preço novo, data da alteração e observação opcional.
	- Integridade referencial aplicada com `FOREIGN KEY` para `insumo(id)` e `ON DELETE CASCADE`.
	- Índices adicionados para consultas eficientes por insumo e por data de alteração.
- Compatibilidade com bancos existentes:
	- Uso de `CREATE TABLE IF NOT EXISTS` e `CREATE INDEX IF NOT EXISTS`, mantendo migração segura para bases já criadas.
- Resultado de validação:
	- Implementação validada sem erros nos arquivos alterados.

**Arquivos impactados na Sprint 10.1**
- `app/db/schema.py` (nova tabela de histórico de preço de insumos e índices de consulta)

### Sprint Review Objetivo — Sprint 10.2

- Objetivo da tarefa 10.2 atendido: alterações de preço de compra de insumo passaram a ser registradas automaticamente no histórico.
- Regra implementada no fluxo de edição de insumo:
	- Ao salvar um insumo existente, o sistema consulta o `preco_compra` anterior.
	- Após atualizar o registro, se o preço novo for diferente do anterior, grava lançamento em `historico_preco_insumo`.
- Dados persistidos por lançamento de histórico:
	- `insumo_id`, `preco_anterior`, `preco_novo`, `data_alteracao` e observação automática de origem da alteração.
- Resultado de validação:
	- Implementação validada sem erros no arquivo alterado.
	- A gravação permanece transacional no mesmo fluxo de `salvar`, com `commit` único ao final.

**Arquivos impactados na Sprint 10.2**
- `app/services/insumo_service.py` (registro automático de histórico quando há alteração de preço)

### Sprint Review Objetivo — Sprint 10.3

- Objetivo da tarefa 10.3 atendido: criada tela dedicada de histórico de preço por insumo com visualização em tabela e em linha do tempo.
- Funcionalidades entregues na nova tela:
	- Filtro por insumo (`Todos` ou item específico) para consulta direcionada.
	- Tabela de histórico com data/hora, insumo, preço anterior, preço novo, variação percentual e observação.
	- Painel de linha do tempo textual para leitura cronológica das alterações de preço.
- Integração entregue no módulo de Insumos:
	- Novo botão `Historico de Precos` no cabeçalho da listagem para abrir a tela sem impactar fluxos de cadastro/edição.
- Entrega de suporte em serviço:
	- Novo método de consulta de histórico com `JOIN` ao nome do insumo e ordenação por data mais recente.
- Resultado de validação:
	- Implementação validada sem erros nos arquivos alterados.

**Arquivos impactados na Sprint 10.3**
- `app/views/historico_preco_insumo_view.py` (nova tela com tabela e linha do tempo do histórico de preços)
- `app/views/insumos_view.py` (botão de acesso e abertura da nova tela de histórico)
- `app/services/insumo_service.py` (método de listagem do histórico com filtro por insumo)

### Sprint Review Objetivo — Sprint 10.4

- Objetivo da tarefa 10.4 atendido: implementado gráfico de barras no Dashboard para comparação mensal entre faturamento (rendimentos recebidos) e despesas pagas.
- Entrega técnica no serviço:
	- Novo método para gerar série mensal de dados com base no período aplicado no Dashboard.
	- Faturamento consolidado a partir dos pagamentos recebidos no módulo de rendimentos (inicial e final).
	- Despesas consolidadas a partir de despesas com status `Pago`.
	- Suporte a cenário sem filtro explícito, exibindo janela padrão dos últimos 6 meses.
- Entrega visual no Dashboard:
	- Nova área de gráfico abaixo dos cards financeiros.
	- Barras agrupadas por mês (faturamento x despesas), com eixos, grade, legenda e rótulos.
	- Atualização automática do gráfico ao aplicar período e ao redimensionar a janela.
- Resultado de validação:
	- Implementação validada sem erros nos arquivos alterados.

**Arquivos impactados na Sprint 10.4**
- `app/services/dashboard_service.py` (série mensal de faturamento vs despesas para o gráfico)
- `app/views/dashboard_view.py` (renderização do gráfico de barras e integração com filtros de período)

### Sprint Review Objetivo — Sprint 10.5

- Objetivo da tarefa 10.5 atendido: implementado gráfico de pizza no Dashboard para mostrar a distribuição das despesas pagas por categoria.
- Entrega técnica no serviço:
	- Novo método para consolidar despesas pagas por categoria dentro do período selecionado no Dashboard.
	- Consolidação das categorias `Insumos`, `Investimentos` e `Outros`, com cálculo de total e percentual.
	- Fallback consistente com o restante do Dashboard quando não há filtro explícito, usando janela padrão dos últimos 6 meses.
- Entrega visual no Dashboard:
	- Nova área de gráfico abaixo da série mensal, mantendo a leitura financeira em dois níveis.
	- Pizza desenhada por canvas com legenda, percentual por categoria e total centralizado.
	- Atualização automática junto com o período aplicado e com o redimensionamento da janela.
- Resultado de validação:
	- Implementação validada sem erros nos arquivos alterados.

**Arquivos impactados na Sprint 10.5**
- `app/services/dashboard_service.py` (consolidação das despesas pagas por categoria para o gráfico)
- `app/views/dashboard_view.py` (renderização do gráfico de pizza e integração com o resumo financeiro)

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

### Sprint Review Objetivo — Sprint 10.6

- Objetivo da tarefa 10.6 atendido: integrada a biblioteca `matplotlib` ao Dashboard para renderizar os gráficos da sprint dentro da interface CustomTkinter.
- Entrega técnica da sprint:
	- Dependência `matplotlib` adicionada ao projeto.
	- Gráficos do Dashboard migrados para `FigureCanvasTkAgg`, com figuras embutidas nos frames da view.
	- Ajuste automático de tamanho das figuras ao redimensionar a janela, mantendo responsividade visual.
- Resultado funcional:
	- O gráfico de barras mensal e o gráfico de pizza por categoria permanecem ativos, agora renderizados por matplotlib.
	- A legenda, as cores e a leitura de totais continuam sincronizadas com o filtro de período aplicado.
- Resultado de validação:
	- Implementação validada sem erros nos arquivos alterados.

**Arquivos impactados na Sprint 10.6**
- `requirements.txt` (adição da dependência `matplotlib`)
- `app/views/dashboard_view.py` (integração dos gráficos com `FigureCanvasTkAgg`)

### Sprint Review Objetivo — Sprint 11

- Objetivo da tarefa 11.1 atendido: criado template de recibo/ordem de serviço em PDF para pedidos, com cabeçalho do estabelecimento, dados gerais, itens, totais e situação de pagamento.
- Objetivo da tarefa 11.2 atendido: implementada pré-visualização do recibo antes de salvar, gerando arquivo temporário e abrindo no visualizador padrão.
- Objetivo da tarefa 11.3 atendido: adicionadas opções para salvar o recibo como PDF e imprimir diretamente a partir da tela de pedidos.
- Objetivo da tarefa 11.4 atendido: refinado o fluxo visual para manter legibilidade e acesso rápido às ações de documento, sem interferir no cadastro de pedidos.
- Objetivo da tarefa 11.5 atendido: gerado manual simplificado de uso em PDF na área de Configurações, com instruções de fluxo principal, recibo e dicas operacionais.
- Objetivo da tarefa 11.6 atendido: dependências e validações finais atualizadas para suportar a geração de PDF e o empacotamento do recurso.
- Resultado de validação:
	- Implementação validada sem erros nos arquivos alterados.
	- Arquivo do manual em PDF gerado com sucesso em `docs/manual_simplificado.pdf`.

**Arquivos impactados na Sprint 11**
- `app/services/recibo_service.py` (geração de recibos, pré-visualização, impressão e manual PDF)
- `app/views/pedidos_view.py` (botões e fluxos de recibo PDF na tela de pedidos)
- `app/views/configuracoes_view.py` (botão para abrir o manual simplificado em PDF)
- `requirements.txt` (adição da dependência `reportlab`)
- `docs/manual_simplificado.pdf` (manual simplificado gerado)

### Sprint Review Objetivo — Sprint 12

- Objetivo de cobertura mínima de testes atendido com suíte `pytest` para:
	- `PedidoService.salvar`
	- `DashboardService.get_resumo`
	- `ProdutoService._calcular_valores`
- Objetivo de transação robusta no salvamento de pedidos atendido:
	- `BEGIN` explícito, `commit` em sucesso e `rollback` em falha.
	- Inclusão de `data_snapshot` em itens do pedido.
- Objetivo de regras de pagamento na camada de serviço atendido:
	- Validações de status, data obrigatória para recebido e formato de data em pedidos, despesas e rendimentos.
- Objetivo de recálculo de produtos após alteração de insumo atendido:
	- Reprocessamento automático dos produtos afetados por insumo alterado.
- Objetivo de auditoria atendido:
	- Criação da tabela `auditoria` e registro de `INSERT/UPDATE/DELETE` para pedidos, despesas e rendimentos.
- Objetivo de build reproduzível atendido:
	- `build.spec` versionado no repositório e instruções atualizadas para uso de lock file.
- Objetivo de hardening no ponto de entrada atendido:
	- `main()` protegido com `try/except`, log técnico e mensagem amigável ao usuário.
- Objetivo de estratégia de versões atendido:
	- `requirements.txt` para desenvolvimento (`>=`) e `requirements-lock.txt` para release (`==`).

**Arquivos impactados na Sprint 12**
- `app/db/schema.py`
- `app/services/pedido_service.py`
- `app/services/despesa_service.py`
- `app/services/rendimento_service.py`
- `app/services/produto_service.py`
- `app/services/insumo_service.py`
- `app/services/auditoria_service.py`
- `app/services/recibo_service.py`
- `app/views/configuracoes_view.py`
- `main.py`
- `build.spec`
- `BUILD_INSTRUCTIONS.md`
- `requirements.txt`
- `requirements-lock.txt`
- `tests/test_pedido_service.py`
- `tests/test_dashboard_service.py`
- `tests/test_produto_service.py`
- `docs/arquitetura.md`
- `docs/requisitos.md`

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
| 12 | Qualidade e Hardening Técnico | Melhorias | Qualidade interna, RNF-03, RNF-05 |

---

*Roadmap v1.0 — Sistema de Gestão para Confeitaria*
