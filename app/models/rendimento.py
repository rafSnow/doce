from dataclasses import dataclass
from typing import Optional
from app.core.enums import StatusPagamento


@dataclass
class Rendimento:
    cliente_id: Optional[int] = None
    pag_inicial_valor: float = 0.0
    pag_inicial_data: Optional[str] = None
    pag_inicial_forma: Optional[str] = None
    pag_inicial_status: str = StatusPagamento.PENDENTE.value  # 'Pendente' | 'Recebido'
    pag_final_valor: float = 0.0
    pag_final_data: Optional[str] = None
    pag_final_forma: Optional[str] = None
    pag_final_status: str = StatusPagamento.PENDENTE.value    # 'Pendente' | 'Recebido'
    responsavel: Optional[str] = None
    id: Optional[int] = None
