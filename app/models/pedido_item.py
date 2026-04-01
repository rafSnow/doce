from dataclasses import dataclass
from typing import Optional

@dataclass
class PedidoItem:
    produto_id: int
    quantidade: int
    preco_unitario_snapshot: float = 0.0
    valor_item: float = 0.0
    id: Optional[int] = None
    pedido_id: Optional[int] = None
    produto_nome: Optional[str] = None # Para exibição na UI
