# Cenario de Teste Funcional Completo

## 1. Objetivo

Este documento define um roteiro funcional completo para validar o sistema desktop da confeitaria, cobrindo:

- Dashboard
- Insumos (cadastro, estoque, historico de preco)
- Produtos (ficha tecnica e precificacao)
- Pedidos (itens, pagamentos, recibo PDF)
- Financeiro (Despesas e Rendimentos)
- Configuracoes (nome, backup, desempenho, manual)

Tambem inclui o que preencher em cada etapa para aumentar a chance de o teste passar de primeira.

## 2. Escopo e base tecnica analisada

Baseado no codigo atual do projeto (views, services, schema e testes automatizados existentes).

## 3. Ambiente de teste

## 3.1 Pre-requisitos

1. Windows com Python 3.10+.
2. Dependencias instaladas:
   - `pip install -r requirements.txt`
3. Banco criado automaticamente na primeira execucao.
4. Execucao da aplicacao:
   - `python .\main.py`

## 3.2 Dados e arquivos importantes

- Banco local: `confeitaria.db` (raiz do projeto em dev, ou ao lado do `.exe` no build).
- Log de erros: `doce.log`.

## 3.3 Limpeza opcional antes dos testes

Para rodar regressao limpa:

1. Fechar app.
2. Renomear `confeitaria.db` para `confeitaria_backup_pre_teste.db`.
3. Abrir app novamente para recriar base vazia.

## 4. Massa de dados padrao (preencher exatamente assim)

Use estes dados para os cenarios abaixo.

## 4.1 Insumos

### Insumo 1
- Nome: `Leite Condensado`
- Categoria: `Ingrediente`
- Peso/Volume Total: `395`
- Unidade: `g`
- Preco de Compra: `7,90`
- Quantidade Disponivel: `20`
- Quantidade Minima: `5`

### Insumo 2
- Nome: `Chocolate em Po 50%`
- Categoria: `Ingrediente`
- Peso/Volume Total: `1000`
- Unidade: `g`
- Preco de Compra: `24,00`
- Quantidade Disponivel: `2`
- Quantidade Minima: `3`

### Insumo 3
- Nome: `Caixa para 4 Doces`
- Categoria: `Embalagem`
- Peso/Volume Total: `100`
- Unidade: `unidade`
- Preco de Compra: `32,00`
- Quantidade Disponivel: `0`
- Quantidade Minima: `10`

## 4.2 Produto

- Nome: `Brigadeiro Tradicional`
- Rendimento: `20`
- Markup (%): `120`
- Ficha tecnica:
  - Leite Condensado: `395`
  - Chocolate em Po 50%: `80`
  - Caixa para 4 Doces: `5`

## 4.3 Pedido

- Cliente (texto): `Ana Souza`
- Data pedido: `20/04/2026`
- Data entrega: `22/04/2026`
- Responsavel: `Rafaela`
- Itens:
  - Brigadeiro Tradicional, qtd `10`
- Pagamento inicial:
  - Valor: `20,00`
  - Data: `20/04/2026`
  - Forma: `PIX`
  - Status: `Recebido`
- Pagamento final:
  - Valor: `0,00`
  - Data: (vazio)
  - Forma: `PIX`
  - Status: `Pendente`

## 4.4 Despesa

- Data: `20/04/2026`
- Valor: `35,00`
- Categoria: `Insumos`
- Status: `Pago`
- Forma de pagamento: `Pix`
- Data pagamento: `20/04/2026`
- Responsavel: `Rafaela`
- Descricao: `Compra emergencial de leite`

## 4.5 Rendimento

Requer cliente cadastrado na tabela `cliente`.

- Cliente: primeiro cliente disponivel no combo
- Responsavel: `Rafaela`
- Valor inicial: `30,00`
- Data inicial: `20/04/2026`
- Forma inicial: `Pix`
- Status inicial: `Recebido`
- Valor final: `50,00`
- Data final: `22/04/2026`
- Forma final: `Pix`
- Status final: `Pendente`

## 5. Matriz de cenarios funcionais

Legenda de prioridade: Alta (A), Media (M).

| ID | Modulo | Cenario | Prioridade |
|---|---|---|---|
| CT-DASH-001 | Dashboard | Carregar indicadores no mes atual | A |
| CT-DASH-002 | Dashboard | Filtro trimestre atual | M |
| CT-DASH-003 | Dashboard | Filtro personalizado valido | A |
| CT-DASH-004 | Dashboard | Erro em data invalida no personalizado | A |
| CT-INS-001 | Insumos | Cadastrar insumo valido | A |
| CT-INS-002 | Insumos | Validar campos obrigatorios e numericos | A |
| CT-INS-003 | Insumos | Alertas visuais de estoque | A |
| CT-INS-004 | Insumos | Editar insumo e gerar historico de preco | A |
| CT-INS-005 | Insumos | Excluir insumo com confirmacao | A |
| CT-INS-006 | Insumos | Exportar insumos para Excel | M |
| CT-INS-007 | Insumos | Filtrar historico de preco por insumo | M |
| CT-PROD-001 | Produtos | Cadastrar produto com ficha tecnica | A |
| CT-PROD-002 | Produtos | Validar regras de nome/rendimento/insumos | A |
| CT-PROD-003 | Produtos | Duplicar produto | M |
| CT-PROD-004 | Produtos | Excluir produto com confirmacao | A |
| CT-PROD-005 | Produtos | Exportar produtos + ficha tecnica | M |
| CT-PED-001 | Pedidos | Cadastrar pedido com item e snapshot de preco | A |
| CT-PED-002 | Pedidos | Validar datas e obrigatorios | A |
| CT-PED-003 | Pedidos | Validar regras de pagamento recebido sem data | A |
| CT-PED-004 | Pedidos | Editar pedido existente | A |
| CT-PED-005 | Pedidos | Excluir pedido com confirmacao | A |
| CT-PED-006 | Pedidos | Pre-visualizar recibo PDF | M |
| CT-PED-007 | Pedidos | Salvar recibo PDF | M |
| CT-PED-008 | Pedidos | Exportar pedidos e itens para Excel | M |
| CT-FIN-DES-001 | Financeiro/Despesas | Cadastrar despesa paga | A |
| CT-FIN-DES-002 | Financeiro/Despesas | Validar data e valor minimo | A |
| CT-FIN-DES-003 | Financeiro/Despesas | Filtros e totalizadores | A |
| CT-FIN-DES-004 | Financeiro/Despesas | Excluir despesa | A |
| CT-FIN-DES-005 | Financeiro/Despesas | Exportar despesas | M |
| CT-FIN-REN-001 | Financeiro/Rendimentos | Cadastrar rendimento com cliente | A |
| CT-FIN-REN-002 | Financeiro/Rendimentos | Validar recebido sem data | A |
| CT-FIN-REN-003 | Financeiro/Rendimentos | Filtros por status/periodo | M |
| CT-FIN-REN-004 | Financeiro/Rendimentos | Excluir rendimento | A |
| CT-FIN-REN-005 | Financeiro/Rendimentos | Exportar rendimentos | M |
| CT-CONF-001 | Configuracoes | Alterar nome do estabelecimento | A |
| CT-CONF-002 | Configuracoes | Executar backup com sucesso | A |
| CT-CONF-003 | Configuracoes | Cancelar sobrescrita de backup | M |
| CT-CONF-004 | Configuracoes | Validar desempenho | M |
| CT-CONF-005 | Configuracoes | Gerar e abrir manual PDF | M |

## 6. Roteiro detalhado (passo a passo)

## 6.1 Dashboard

### CT-DASH-001 - Carregar indicadores no mes atual
Pre-condicao: existir pelo menos 1 pedido e 1 despesa na base.

Passos:
1. Abrir Dashboard.
2. Manter pill `Mes Atual`.
3. Clicar `Atualizar`.

Resultado esperado:
- Cards mostram valores em R$ com 2 casas.
- Grafico de barras e pizza sao renderizados sem erro.

### CT-DASH-004 - Data personalizada invalida
Passos:
1. Selecionar `Personalizado`.
2. Preencher inicio `31/02/2026` e fim `20/04/2026`.
3. Clicar `Aplicar`.

Resultado esperado:
- Mensagem: `Informe datas validas no formato DD/MM/AAAA.`

## 6.2 Insumos

### CT-INS-001 - Cadastro valido
Passos:
1. Ir em `Insumos` > `+ Novo Insumo`.
2. Preencher dados do item 4.1 (Insumo 1).
3. Salvar.

Resultado esperado:
- Registro aparece na lista.
- Custo/Un e calculado automaticamente.

### CT-INS-002 - Validacoes
Entradas invalidas sugeridas:
- Nome vazio.
- Categoria invalida (forcar via edicao de banco ou automacao).
- Peso/volume `0`.
- Quantidade minima maior que quantidade disponivel.

Resultado esperado:
- Sistema bloqueia e mostra mensagem de erro coerente.

### CT-INS-003 - Alertas de estoque
Passos:
1. Cadastrar Insumo 2 e Insumo 3 da massa.
2. Voltar para lista.

Resultado esperado:
- Linhas com estoque baixo/critico destacadas.
- Badge de alerta no menu lateral `Insumos` atualizado.

### CT-INS-004 - Historico de preco
Passos:
1. Editar `Leite Condensado` e alterar preco de `7,90` para `8,40`.
2. Salvar.
3. Ir para aba `Historico de Precos`.

Resultado esperado:
- Registro com preco anterior/novo, variacao e data/hora.
- Timeline lateral atualizada.

### CT-INS-006 - Exportar Excel
Passos:
1. Aplicar filtro opcional.
2. Clicar `Exportar Excel`.
3. Salvar arquivo.

Resultado esperado:
- Arquivo `.xlsx` criado com cabecalho e dados.

## 6.3 Produtos

### CT-PROD-001 - Cadastro com ficha tecnica
Passos:
1. Ir em `Produtos` > `+ Novo Produto`.
2. Preencher dados do item 4.2.
3. Adicionar 3 insumos na ficha tecnica.
4. Salvar.

Resultado esperado:
- Produto aparece na lista com custo e preco de venda.
- Labels de custo receita/custo unitario/preco venda atualizam na tela.

### CT-PROD-002 - Validacoes
Casos invalidos:
- Nome vazio ou com menos de 3 caracteres.
- Rendimento `0`.
- Markup negativo.
- Nenhum insumo adicionado.

Resultado esperado:
- Bloqueio do salvamento com mensagem de erro.

### CT-PROD-003 - Duplicar
Passos:
1. Clique direito em um produto.
2. Selecionar `Duplicar`.

Resultado esperado:
- Novo produto criado com sufixo `(Copia)`.

## 6.4 Pedidos

### CT-PED-001 - Cadastro completo
Passos:
1. Ir em `Pedidos` > `+ Novo Pedido`.
2. Preencher dados do item 4.3.
3. Salvar.

Resultado esperado:
- Pedido salvo com sucesso.
- Total do pedido calculado pela soma dos itens.
- Item salva `preco_unitario_snapshot` e `data_snapshot`.

### CT-PED-002 - Validacoes de formulario
Casos:
- Cliente vazio.
- Nenhum item.
- Responsavel vazio.
- Data entrega menor que data pedido.
- Quantidade item <= 0.

Resultado esperado:
- Mensagem de erro/aviso e bloqueio.

### CT-PED-003 - Pagamento recebido sem data
Passos:
1. Definir status inicial `Recebido`.
2. Deixar data inicial vazia.
3. Salvar.

Resultado esperado:
- Erro: pagamento recebido exige data.

### CT-PED-006 - Pre-visualizar recibo
Passos:
1. Com formulario valido, clicar `Pre-visualizar`.

Resultado esperado:
- PDF temporario gerado e aberto no visualizador padrao.

### CT-PED-007 - Salvar PDF
Passos:
1. Clicar `Salvar PDF`.
2. Selecionar caminho.

Resultado esperado:
- Arquivo PDF salvo no local escolhido.

## 6.5 Financeiro - Despesas

### CT-FIN-DES-001 - Cadastro despesa paga
Passos:
1. Ir em `Financeiro` (aba `Despesas`) > `+ Novo`.
2. Preencher dados do item 4.4.
3. Salvar.

Resultado esperado:
- Registro na lista.
- Valor refletido em totalizadores (Insumos/Total).

### CT-FIN-DES-002 - Regras de validacao
Casos:
- Valor `0,00` (deve falhar no minimo 0.01).
- Data invalida.
- Status `Pago` sem data de pagamento.

Resultado esperado:
- Bloqueio com mensagem.

### CT-FIN-DES-003 - Filtros
Passos:
1. Aplicar periodo, categoria e status.
2. Buscar.

Resultado esperado:
- Lista filtrada corretamente.
- Totalizadores recalculados.

## 6.6 Financeiro - Rendimentos

### CT-FIN-REN-001 - Cadastro rendimento
Pre-condicao: existir cliente na base.

Passos:
1. Abrir aba `Rendimentos` > `+ Novo`.
2. Preencher dados do item 4.5.
3. Salvar.

Resultado esperado:
- Registro salvo e exibido na grade.

### CT-FIN-REN-002 - Recebido sem data
Passos:
1. Status inicial `Recebido`.
2. Data inicial vazia.
3. Salvar.

Resultado esperado:
- Erro solicitando data do pagamento recebido.

## 6.7 Configuracoes

### CT-CONF-001 - Nome estabelecimento
Passos:
1. Ir em `Configuracoes`.
2. Preencher nome: `Doce Testes QA`.
3. Salvar.

Resultado esperado:
- Nome atualizado no sidebar e titulo da janela.

### CT-CONF-002 - Backup
Passos:
1. Clicar `Fazer backup`.
2. Escolher caminho `.db`.
3. Confirmar.

Resultado esperado:
- Backup criado com mensagem de sucesso.

### CT-CONF-004 - Validar desempenho
Passos:
1. Clicar `Validar desempenho`.

Resultado esperado:
- Diagnostico executado.
- Mensagem de sucesso ou warning com consultas acima do limite.

### CT-CONF-005 - Manual PDF
Passos:
1. Clicar `Abrir manual PDF`.

Resultado esperado:
- Manual gerado e aberto.

## 7. Checklist de preenchimento rapido por modulo

Use este checklist antes de clicar em Salvar.

### Insumos
- Nome preenchido
- Categoria valida (`Ingrediente`, `Embalagem`, `Gas`)
- Peso/volume > 0
- Preco >= 0
- Quantidade minima <= disponivel

### Produtos
- Nome com 3+ caracteres
- Rendimento inteiro > 0
- Markup >= 0
- Pelo menos 1 insumo na ficha tecnica

### Pedidos
- Nome do cliente preenchido
- Data pedido valida
- Data entrega >= data pedido (quando informada)
- Responsavel preenchido
- Pelo menos 1 item
- Se status `Recebido`, data de pagamento preenchida

### Despesas
- Data valida
- Valor >= 0,01
- Categoria e status validos
- Se status `Pago`, data pagamento preenchida

### Rendimentos
- Cliente valido selecionado
- Valores >= 0
- Status validos
- Se status `Recebido`, data correspondente preenchida

## 8. Evidencias que devem ser coletadas

Para cada caso de teste executado, salvar:

1. Screenshot da tela antes de salvar.
2. Screenshot da mensagem de sucesso/erro.
3. Screenshot da linha criada na listagem.
4. Arquivo exportado (quando houver): Excel/PDF.
5. Resultado no log de execucao de testes (planilha de controle).

Modelo de registro:

| Caso | Executor | Data | Resultado (OK/NOK) | Evidencia | Observacoes |
|---|---|---|---|---|---|
| CT-INS-001 |  |  |  |  |  |

## 9. Riscos e pontos de atencao no estado atual

1. O menu principal nao expoe uma tela de cadastro de clientes, mas o modulo de Rendimentos exige cliente cadastrado.
2. A `ClientesView` usa campos (telefone, email, endereco, cpf_cnpj etc.) que nao aparecem no schema atual da tabela `cliente` e tambem usa metodos nao presentes no `ClienteService` atual (`get_by_id`).
3. Para testar Rendimentos sem erro, pode ser necessario inserir cliente previamente na base (`cliente.nome`, `cliente.contato`) por script/sql.

## 10. Criterios de aceite da regressao funcional

Considerar regressao aprovada quando:

1. Todos os casos de prioridade Alta passarem.
2. Nenhum erro bloqueante impedir cadastro, edicao, exclusao e exportacao dos modulos principais.
3. Backup, recibo PDF e manual PDF forem gerados com sucesso.
4. Dashboard refletir dados coerentes com pedidos/despesas/rendimentos cadastrados.
