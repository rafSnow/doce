from app.core import event_bus
from app.models.rendimento import Rendimento
from app.models.despesa import Despesa
from app.core.enums import CategoriaDespesa

# Proteção contra dupla execução (Regra CF-07)
_pedidos_processados = set()

def _on_insumo_salvo(insumo_id, custo_anterior, custo_novo, **_):
    from app.services.produto_service import ProdutoService
    if custo_anterior is not None and custo_novo != custo_anterior:
        ProdutoService().recalcular_por_insumo(insumo_id)

def _on_pedido_salvo(pedido_id, **_):
    """
    Handler consolidado para pedido.salvo:
    1. Sincronização ERP (Financeiro)
    2. Baixa de Estoque (com proteção contra dupla execução)
    3. Emissão de evento para atualização de badges
    """
    from app.services.pedido_service import PedidoService
    from app.services.rendimento_service import RendimentoService
    from app.services.produto_service import ProdutoService
    from app.services.insumo_service import InsumoService
    from app.services.auditoria_service import AuditoriaService
    
    pedido = PedidoService().get_by_id(pedido_id)
    if not pedido:
        return
        
    # 1. Sincronização Financeira (ERP)
    rend_service = RendimentoService()
    rend = rend_service.obter_por_pedido(pedido_id)
    
    if not rend:
        rend = Rendimento(pedido_id=pedido_id)
        
    rend.cliente_id = pedido.cliente_id
    rend.responsavel = pedido.responsavel
    rend.pag_inicial_valor = pedido.pag_inicial_valor
    rend.pag_inicial_data = pedido.pag_inicial_data
    rend.pag_inicial_forma = pedido.pag_inicial_forma
    rend.pag_inicial_status = pedido.pag_inicial_status
    rend.pag_final_valor = pedido.pag_final_valor
    rend.pag_final_data = pedido.pag_final_data
    rend.pag_final_forma = pedido.pag_final_forma
    rend.pag_final_status = pedido.pag_final_status
    
    rend_service.salvar(rend)

    # 2. Baixa de Estoque Automática (Regras PD-03, PD-04)
    # Proteção: evita processar estoque mais de uma vez por sessão para o mesmo ID
    if pedido_id not in _pedidos_processados:
        _pedidos_processados.add(pedido_id)
        
        ins_service = InsumoService()
        prod_service = ProdutoService()
        consumos_efetuados = []

        for item in pedido.itens:
            produto = prod_service.get_by_id(item.produto_id)
            if not produto:
                continue
                
            for pi in produto.insumos:
                rendimento = produto.rendimento_receita or 1
                consumo = (pi.quantidade_usada_receita * item.quantidade) / rendimento
                
                insumo = ins_service.get_by_id(pi.insumo_id)
                if insumo:
                    insumo.quantidade_disponivel = max(0.0, insumo.quantidade_disponivel - consumo)
                    
                    # Regra PD-04: Se ficar negativo, permite mas registra na auditoria
                    status_estoque = "OK"
                    if insumo.quantidade_disponivel <= 0:
                        status_estoque = "NEGATIVO/ZERADO"

                    ins_service.salvar(insumo)
                    
                    consumos_efetuados.append({
                        "insumo": insumo.nome,
                        "consumo": round(consumo, 4),
                        "unidade": insumo.unidade_medida,
                        "saldo_final": round(insumo.quantidade_disponivel, 4),
                        "status": status_estoque
                    })

        # Regra PD-12: Auditoria de Consumo
        if consumos_efetuados:
            AuditoriaService.registrar(
                entidade="pedido",
                acao="BAIXA_ESTOQUE",
                entidade_id=pedido_id,
                detalhes={"insumos_consumidos": consumos_efetuados}
            )
            
    # 3. Notifica atualização de estoque (para badges e dashboard)
    event_bus.emit("estoque.atualizado")

def _on_pedido_excluido(pedido_id, **_):
    from app.services.rendimento_service import RendimentoService
    rend_service = RendimentoService()
    rend = rend_service.obter_por_pedido(pedido_id)
    if rend and rend.id:
        rend_service.excluir(rend.id)

def _on_insumo_comprado(insumo_id, valor_total, data_pagamento, forma_pagamento, status_pagamento, responsavel=None, **_):
    from app.services.insumo_service import InsumoService
    from app.services.despesa_service import DespesaService
    
    insumo = InsumoService().get_by_id(insumo_id)
    if not insumo:
        return
        
    desp_service = DespesaService()
    
    despesa = Despesa(
        data=data_pagamento,
        valor=valor_total,
        descricao=f"Compra de insumo: {insumo.nome}",
        categoria=CategoriaDespesa.INSUMOS.value,
        responsavel=responsavel,
        status=status_pagamento,
        forma_pagamento=forma_pagamento,
        data_pagamento_final=data_pagamento if status_pagamento == "Pago" else None,
        origem="insumo",
        origem_id=insumo_id
    )
    desp_service.salvar(despesa)
    event_bus.emit("estoque.atualizado")

def _on_insumo_excluido(**_):
    event_bus.emit("estoque.atualizado")

def _on_produto_salvo(**_):
    # Statement of intent: novos pedidos já usarão os preços atualizados.
    pass

# Registro dos listeners
event_bus.on("insumo.salvo", _on_insumo_salvo)
event_bus.on("pedido.salvo", _on_pedido_salvo)
event_bus.on("pedido.excluido", _on_pedido_excluido)
event_bus.on("insumo.comprado", _on_insumo_comprado)
event_bus.on("insumo.excluido", _on_insumo_excluido)
event_bus.on("produto.salvo", _on_produto_salvo)
