from dataclasses import dataclass, field
from typing import List, Optional
from app.models.pedido_item import PedidoItem
from app.core.enums import StatusPagamento

@dataclass
class Pedido:
    cliente_nome: str
    data_pedido: str
    cliente_id: Optional[int] = None
    data_entrega: Optional[str] = None
    valor_total: float = 0.0
    
    pag_inicial_valor: float = 0.0
    pag_inicial_data: Optional[str] = None
    pag_inicial_forma: Optional[str] = None
    pag_inicial_status: str = StatusPagamento.PENDENTE.value # Pendente / Recebido
    
    pag_final_valor: float = 0.0
    pag_final_data: Optional[str] = None
    pag_final_forma: Optional[str] = None
    pag_final_status: str = StatusPagamento.PENDENTE.value   # Pendente / Recebido
    
    responsavel: Optional[str] = None
    itens: List[PedidoItem] = field(default_factory=list)
    id: Optional[int] = None
