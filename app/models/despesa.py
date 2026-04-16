from dataclasses import dataclass
from typing import Optional


@dataclass
class Despesa:
    data: str
    valor: float
    descricao: Optional[str] = None
    categoria: str = "Outros"          # 'Insumos' | 'Investimentos' | 'Outros'
    responsavel: Optional[str] = None
    status: str = "Pendente"           # 'Pendente' | 'Pago'
    forma_pagamento: Optional[str] = None
    data_pagamento_final: Optional[str] = None
    id: Optional[int] = None
