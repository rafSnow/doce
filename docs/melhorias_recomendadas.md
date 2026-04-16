# Melhorias Recomendadas do Projeto

## Objetivo
Consolidar melhorias de arquitetura, qualidade e entrega para aumentar confiabilidade em produção, reduzir regressões e facilitar manutenção.

## Status de execução
- Concluído em 16/04/2026.
- Implementações aplicadas em código, build, testes e documentação.

## Prioridade Alta

### 1. Cobertura de testes automatizados
- Criar suíte mínima com `pytest` para regras críticas.
- Começar por:
  - `PedidoService.salvar` (fluxo de itens + pagamentos)
  - `DashboardService.get_resumo`
  - `ProdutoService._calcular_valores`
- Meta inicial: testes de regressão para fluxos financeiros e cálculo de preço.

### 2. Build reproduzível
- Versionar arquivo `.spec` do PyInstaller no repositório.
- Ajustar instruções de build para refletir o fluxo real.
- Garantir que o comando documentado execute em máquina limpa.

### 3. Transação robusta no salvamento de pedidos
- Encapsular `UPDATE/DELETE/INSERT` de `pedido` e `pedido_item` em transação explícita.
- Em caso de falha, aplicar `rollback` para evitar pedido parcial.

### 4. Recalcular produtos após alteração de insumo
- Definir estratégia para manter `custo_unitario` e `preco_venda_unitario` consistentes.
- Opções:
  - Recalcular produtos afetados ao atualizar insumo.
  - Ou calcular sob demanda (evita dado derivado defasado).

### 5. Validar regras de pagamento na camada de serviço
- Validar consistência de status/data/valor também em `services`, não só em `views`.
- Exemplo: status `Recebido` deve exigir data de pagamento.

## Prioridade Média

### 6. Tratar erros globais no ponto de entrada
- Envolver `main()` em `try/except` com mensagem amigável e log técnico.

### 7. Padronizar modelo de dados entre documentação e código
- Alinhar docs para o uso atual de `cliente_nome` em pedidos.
- Ou migrar de volta para FK (`cliente_id`) se esse for o modelo desejado.

### 8. Estruturar logs de auditoria
- Registrar eventos de `INSERT/UPDATE/DELETE` para rastreabilidade.
- Foco inicial em pedidos, despesas e rendimentos.

### 9. Fortalecer estratégia de versão de dependências
- Definir política clara (`==` para release, `>=` para desenvolvimento).
- Gerar arquivo de lock para builds previsíveis.

### 10. Garantir manual PDF no executável
- Revisar caminho de geração/abertura do manual no modo empacotado.
- Validar comportamento no `.exe` fora do ambiente de desenvolvimento.

## Melhorias de documentação

### 11. Documento de arquitetura
- Atualizar seção de schema para refletir estado real do banco.
- Adicionar decisão arquitetural sobre snapshots de preço no pedido.

### 12. Documento de requisitos
- Atualizar modelo de entidades de pedidos para o formato atual.
- Revisar critérios de aceite incluindo cobertura mínima de testes.

### 13. Roadmap
- Incluir uma sprint técnica de qualidade com foco em:
  - testes
  - transações
  - auditoria
  - hardening de build

## Sugestão de execução (2 ondas)

### Onda 1 (rápida, alto impacto)
- Testes críticos
- Transação em pedidos
- Alinhamento build/spec

### Onda 2 (estabilização)
- Recalculo de produtos por mudança de insumo
- Auditoria e logs
- Alinhamento total docs x código
