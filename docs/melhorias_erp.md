# Análise e Proposta de Evolução: Dolce Neves ERP

Este documento apresenta uma análise estrutural e um plano de ação para evoluir o sistema "Dolce Neves" de um gestor de cadastros isolados para um **ERP (Enterprise Resource Planning) automatizado e integrado**.

O objetivo principal é eliminar o retrabalho (dupla digitação) garantindo que as operações fins (como comprar insumos ou realizar uma venda) reflitam automaticamente nos módulos de suporte (como o financeiro e o controle de estoque).

---

## 1. Estado Atual vs. Visão ERP

### Estado Atual (Silos de Dados)
Atualmente, os módulos funcionam de forma independente:
- **Insumos:** O cadastro e a atualização de preços ou quantidades são feitos manualmente. A compra de um novo lote de insumos não gera automaticamente uma conta a pagar (Despesa).
- **Pedidos:** A venda de um produto gera o pedido, mas os pagamentos (sinal e restante) não alimentam automaticamente o fluxo de caixa (Rendimentos).
- **Financeiro:** O usuário precisa lançar manualmente uma Despesa ao comprar embalagens/ingredientes e um Rendimento ao fechar um pedido.

### Visão ERP (Fluxo Integrado via Eventos)
Em um ERP, o fluxo da informação segue o princípio da **Entrada Única de Dados**. 
- A entrada de uma nota fiscal de compra atualiza o estoque, o custo médio do insumo e gera uma Despesa financeira.
- A aprovação de um pedido baixa o estoque de produtos/insumos, gera o faturamento (Rendimento) e projeta as contas a receber.

Para o Dolce Neves, usaremos a arquitetura já iniciada com o `event_bus` para conectar esses módulos sem gerar acoplamento direto entre as classes.

---

## 2. Fluxos de Negócio Automatizados (Proposta)

### A. Módulo de Compras (Insumos ➔ Financeiro)
**Cenário:** O confeiteiro compra 5kg de farinha de trigo.
**Fluxo proposto:**
1. Na view de "Insumos" (ou em uma futura view de "Entrada de Compras"), o usuário registra a nova aquisição, informando a quantidade comprada, o valor total da nota e a forma de pagamento.
2. O `InsumoService` atualiza o estoque (`quantidade_disponivel += nova_qtd`) e recalcula o custo médio.
3. O `InsumoService` emite um evento: `event_bus.emit("estoque.entrada", valor_total=X, forma_pagamento=Y)`.
4. Um listener em `app/core/listeners.py` intercepta o evento e chama o `DespesaService.salvar()`, gerando uma Despesa automática categorizada como "Insumos".

### B. Módulo de Vendas (Pedidos ➔ Financeiro)
**Cenário:** O confeiteiro fecha uma encomenda de R$ 500, com R$ 250 de sinal via PIX e R$ 250 na entrega.
**Fluxo proposto:**
1. O usuário salva o pedido no `PedidosView`.
2. O `PedidoService` emite o evento de sucesso: `event_bus.emit("pedido.salvo", pedido_obj=pedido)`.
3. Um listener intercepta o evento e verifica os pagamentos.
4. O listener aciona o `RendimentoService.salvar()`, criando/atualizando um registro de Rendimento atrelado ao `cliente_id` com os status definidos (ex: R$ 250 "Recebido" hoje, R$ 250 "Pendente" para a data de entrega).
5. Se o pedido for excluído/cancelado, a integração estorna o rendimento associado.

### C. Módulo de Estoque (Pedidos ➔ Insumos) *[Fase Avançada]*
**Cenário:** A produção do pedido foi concluída.
**Fluxo proposto:**
1. Quando um pedido muda de status para "Concluído" ou "Entregue".
2. O sistema calcula a quantidade total de cada insumo utilizado pelas fichas técnicas (`ProdutoInsumo`) dos itens do pedido.
3. O sistema dá baixa automática no estoque (`quantidade_disponivel`) dos insumos correspondentes.

---

## 3. Arquitetura Técnica: Implementação

Para implementar essas regras sem quebrar a "Regra de Ouro" de não alterar a lógica de negócio básica e mantendo os arquivos 100% funcionais, devemos focar no **Core Listeners**:

1. **Expansão do Banco de Dados (`schema.py`):**
   - Precisamos adicionar chaves estrangeiras lógicas ou de rastreabilidade (ex: `despesa.insumo_id`, `rendimento.pedido_id`) para que uma alteração no pedido consiga encontrar o rendimento correspondente para atualizá-lo, em vez de duplicá-lo.

2. **Novos Eventos (`event_bus.py`):**
   - Mapear claramente a semântica: `pedido.salvo`, `pedido.excluido`, `insumo.comprado`.

3. **O Arquivo `app/core/listeners.py` (O Coração da Integração):**
   - Este arquivo abrigará as funções que escutam os módulos de origem e comandam os módulos de destino.
   - Exemplo conceitual:
     ```python
     def _on_pedido_salvo(pedido: Pedido):
         rend_service = RendimentoService()
         # Busca rendimento atrelado ao pedido ou cria um novo
         # Atualiza valores e datas conforme o Pedido
         rend_service.salvar(novo_rendimento)
     ```

4. **Tratamento de Exceções e Transações:**
   - Atualmente o SQLite não possui suporte fácil a transações globais inter-serviços via `event_bus` sem passar o objeto de conexão explicitamente (`conn`). Para garantir que um erro ao gerar o Rendimento dê rollback na criação do Pedido, a emissão do evento deve ocorrer de preferência *dentro* do contexto `with transacao() as conn:`, repassando a conexão, ou implementar um padrão de saga/compensação.

---

## 4. Roteiro de Ações para o Refatorador Sênior

Se formos seguir com a implementação deste ERP automatizado, a ordem correta das tarefas será:

- [ ] **Passo 1: Banco de Dados.** Adicionar as colunas de rastreabilidade. Alterar `despesa` adicionando `origem` e `origem_id` e em `rendimento` adicionar `pedido_id`. Criar script de migração no `schema.py`.
- [ ] **Passo 2: Entidades e Serviços.** Atualizar `Despesa`, `Rendimento` e seus respectivos Services para lerem e salvarem esses novos campos.
- [ ] **Passo 3: Regras de Integração de Vendas.** Criar no `listeners.py` a sincronização de `Pedido -> Rendimento`. Se um pedido for atualizado, o rendimento atrelado a ele (buscado via `pedido_id`) deve ser atualizado para refletir os valores exatos e status.
- [ ] **Passo 4: View de Insumos.** Na view de Insumos, separar a lógica de "Alterar Cadastro" da lógica de "Lançar Nova Compra/Entrada". A "Nova Compra" precisará perguntar se já foi pago, forma de pagamento e data, e emitir o evento que gerará a Despesa.
- [ ] **Passo 5: View de Pedidos e Financeiro.** Bloquear a edição manual de Rendimentos que possuem `pedido_id` atrelado e Despesas que possuem origem atrelada, forçando o usuário a alterar o documento gerador (o Pedido ou a Compra), mantendo a consistência rigorosa de um ERP real.

## Conclusão
A fundação do sistema "Dolce Neves" (Tkinter + SQLite + Event Bus) está muito sólida e madura. O uso do `event_bus` provou ser a decisão arquitetural correta para permitir esta próxima fase. Com poucas horas de refatoração nos listeners e views, podemos transformar este sistema em um ERP completamente rastreável.