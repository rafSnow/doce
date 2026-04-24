from app.core import event_bus
from app.services.produto_service import ProdutoService
from app.models.rendimento import Rendimento
from app.models.despesa import Despesa
from app.core.enums import CategoriaDespesa

def _on_insumo_salvo(insumo_id, custo_anterior, custo_novo, **_):
    if custo_anterior is not None and custo_novo != custo_anterior:
        ProdutoService().recalcular_por_insumo(insumo_id)

def _on_pedido_salvo(pedido_id, **_):
    from app.services.pedido_service import PedidoService
    from app.services.rendimento_service import RendimentoService
    
    pedido = PedidoService().get_by_id(pedido_id)
    if not pedido:
        return
        
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
    # Verifica se já existe uma despesa para esta compra específica (seria bom ter um ID de transação de compra)
    # Mas como é um evento disparado na hora da compra, vamos apenas criar.
    
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

event_bus.on("insumo.salvo", _on_insumo_salvo)
event_bus.on("pedido.salvo", _on_pedido_salvo)
event_bus.on("pedido.excluido", _on_pedido_excluido)
event_bus.on("insumo.comprado", _on_insumo_comprado)
