from dataclasses import dataclass
from typing import Optional

@dataclass
class Cliente:
    nome: str
    contato: Optional[str] = None
    id: Optional[int] = None
