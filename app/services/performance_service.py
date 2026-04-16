from dataclasses import dataclass
from time import perf_counter
from typing import Callable, List

from app.services.cliente_service import ClienteService
from app.services.dashboard_service import DashboardService
from app.services.despesa_service import DespesaService
from app.services.insumo_service import InsumoService
from app.services.pedido_service import PedidoService
from app.services.produto_service import ProdutoService
from app.services.rendimento_service import RendimentoService


@dataclass
class MedicaoConsulta:
    nome: str
    tempo_medio: float
    tempo_maximo: float
    aprovado: bool
    erro: str = ""


@dataclass
class DiagnosticoPerformance:
    limite_segundos: float
    repeticoes: int
    total_consultas: int
    aprovado_geral: bool
    maior_tempo_medido: float
    medicoes: List[MedicaoConsulta]


class PerformanceService:
    def __init__(self):
        self.cliente_service = ClienteService()
        self.insumo_service = InsumoService()
        self.produto_service = ProdutoService()
        self.pedido_service = PedidoService()
        self.despesa_service = DespesaService()
        self.rendimento_service = RendimentoService()
        self.dashboard_service = DashboardService()

    def executar_diagnostico(self, limite_segundos: float = 2.0, repeticoes: int = 5) -> DiagnosticoPerformance:
        testes: list[tuple[str, Callable[[], object]]] = [
            ("ClienteService.listar", lambda: self.cliente_service.listar()),
            ("InsumoService.listar", lambda: self.insumo_service.listar()),
            ("ProdutoService.listar", lambda: self.produto_service.listar()),
            ("PedidoService.listar", lambda: self.pedido_service.listar()),
            ("DespesaService.listar", lambda: self.despesa_service.listar()),
            ("RendimentoService.listar", lambda: self.rendimento_service.listar()),
            ("DashboardService.get_resumo", lambda: self.dashboard_service.get_resumo()),
        ]

        medicoes: list[MedicaoConsulta] = []

        for nome, consulta in testes:
            tempos: list[float] = []
            erro = ""

            for _ in range(repeticoes):
                inicio = perf_counter()
                try:
                    consulta()
                except Exception as exc:
                    erro = str(exc)
                    break
                fim = perf_counter()
                tempos.append(fim - inicio)

            if tempos:
                tempo_medio = sum(tempos) / len(tempos)
                tempo_maximo = max(tempos)
            else:
                tempo_medio = 0.0
                tempo_maximo = limite_segundos + 1.0

            aprovado = (tempo_maximo < limite_segundos) and not erro
            medicoes.append(
                MedicaoConsulta(
                    nome=nome,
                    tempo_medio=tempo_medio,
                    tempo_maximo=tempo_maximo,
                    aprovado=aprovado,
                    erro=erro,
                )
            )

        maior_tempo = max((m.tempo_maximo for m in medicoes), default=0.0)
        aprovado_geral = all(m.aprovado for m in medicoes)

        return DiagnosticoPerformance(
            limite_segundos=limite_segundos,
            repeticoes=repeticoes,
            total_consultas=len(medicoes),
            aprovado_geral=aprovado_geral,
            maior_tempo_medido=maior_tempo,
            medicoes=medicoes,
        )
