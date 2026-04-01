from dataclasses import dataclass
from typing import Optional

@dataclass
class ProdutoInsumo:
    insumo_id: int
    quantidade_usada_receita: float
    custo_proporcional: float = 0.0       # Calculado por quantidade * custo_por_unidade
    produto_id: Optional[int] = None
    insumo_nome: Optional[str] = None     # Apenas para facilitar exibição na UI
    insumo_unidade: Optional[str] = None  # Apenas para facilitar exibição na UI
