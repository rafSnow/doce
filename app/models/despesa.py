from dataclasses import dataclass
from typing import Optional
from app.core.enums import CategoriaDespesa, StatusPagamento


@dataclass
class Despesa:
    data: str
    valor: float
    descricao: Optional[str] = None
    categoria: str = CategoriaDespesa.OUTROS.value          # 'Insumos' | 'Investimentos' | 'Outros'
    responsavel: Optional[str] = None
    status: str = StatusPagamento.PENDENTE.value           # 'Pendente' | 'Pago'
    forma_pagamento: Optional[str] = None
    data_pagamento_final: Optional[str] = None
    id: Optional[int] = None
