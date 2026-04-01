from dataclasses import dataclass, field
from typing import List, Optional
from app.models.produto_insumo import ProdutoInsumo

@dataclass
class Produto:
    nome: str
    rendimento_receita: int
    comissao_perc: float
    custo_unitario: float = 0.0          # Calculado: soma(custo_proporcional) / rendimento
    preco_venda_unitario: float = 0.0    # Calculado: custo_unitario * (1 + comissao/100)
    insumos: List[ProdutoInsumo] = field(default_factory=list)
    id: Optional[int] = None
