from app.core import event_bus
from app.services.produto_service import ProdutoService

def _on_insumo_salvo(insumo_id, custo_anterior, custo_novo, **_):
    if custo_anterior is not None and custo_novo != custo_anterior:
        ProdutoService().recalcular_por_insumo(insumo_id)

event_bus.on("insumo.salvo", _on_insumo_salvo)
