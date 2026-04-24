from dataclasses import dataclass
from typing import Optional
from app.core.enums import UnidadeMedida

@dataclass
class Insumo:
    nome: str
    categoria: str               # 'Ingrediente' | 'Embalagem' | 'Gás'
    peso_volume_total: float
    unidade_medida: str          # 'g' | 'ml' | 'unidade'
    preco_compra: float
    quantidade_disponivel: float = 0.0
    quantidade_minima: float = 0.0
    data_compra: Optional[str] = None
    id: Optional[int] = None

    @property
    def custo_por_unidade(self) -> float:
        if self.peso_volume_total == 0:
            return 0.0
        return round(self.preco_compra / self.peso_volume_total, 6)

    @property
    def estoque_baixo(self) -> bool:
        return self.quantidade_disponivel <= self.quantidade_minima
