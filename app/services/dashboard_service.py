from dataclasses import dataclass
from datetime import datetime
import calendar

from app.core.formatters import normalizar_data_iso
from app.db.connection import get_connection
from app.core.enums import StatusPagamento, CategoriaDespesa

@dataclass
class DashboardResumo:
    saldo_atual: float
    falta_pagar: float
    a_receber: float
    saldo_previsto: float
    total_investido: float
    lucro_total_vendas: float

class DashboardService:
    def get_resumo(self, data_inicio: str = "", data_fim: str = "") -> DashboardResumo:
        conn = get_connection()
        inicio = self._parse_data(data_inicio)
        fim = self._parse_data(data_fim)

        total_recebido = 0.0
        a_receber = 0.0
        despesas_pagas = 0.0
        falta_pagar = 0.0
        total_investido = 0.0
        lucro_total_vendas = 0.0

        pedidos = conn.execute(
            """
            SELECT
                pag_inicial_valor, pag_inicial_data, pag_inicial_status,
                pag_final_valor, pag_final_data, pag_final_status
            FROM pedido
            """
        ).fetchall()

        for pedido in pedidos:
            pag_ini_data = self._parse_data(pedido["pag_inicial_data"])
            pag_fin_data = self._parse_data(pedido["pag_final_data"])

            if pedido["pag_inicial_status"] == StatusPagamento.RECEBIDO.value and self._esta_no_periodo(pag_ini_data, inicio, fim):
                total_recebido += float(pedido["pag_inicial_valor"] or 0.0)
            if pedido["pag_final_status"] == StatusPagamento.RECEBIDO.value and self._esta_no_periodo(pag_fin_data, inicio, fim):
                total_recebido += float(pedido["pag_final_valor"] or 0.0)

            if pedido["pag_inicial_status"] == StatusPagamento.PENDENTE.value and self._esta_no_periodo(pag_ini_data, inicio, fim):
                a_receber += float(pedido["pag_inicial_valor"] or 0.0)
            if pedido["pag_final_status"] == StatusPagamento.PENDENTE.value and self._esta_no_periodo(pag_fin_data, inicio, fim):
                a_receber += float(pedido["pag_final_valor"] or 0.0)

        itens_pedido = conn.execute(
            """
            SELECT
                p.data_pedido,
                pi.quantidade,
                pi.preco_unitario_snapshot,
                pr.custo_unitario
            FROM pedido_item pi
            JOIN pedido p ON p.id = pi.pedido_id
            JOIN produto pr ON pr.id = pi.produto_id
            """
        ).fetchall()

        for item in itens_pedido:
            data_pedido = self._parse_data(item["data_pedido"])
            if not self._esta_no_periodo(data_pedido, inicio, fim):
                continue

            quantidade = float(item["quantidade"] or 0.0)
            preco_venda = float(item["preco_unitario_snapshot"] or 0.0)
            custo_unitario = float(item["custo_unitario"] or 0.0)
            lucro_total_vendas += (preco_venda - custo_unitario) * quantidade

        despesas = conn.execute(
            """
            SELECT data, valor, categoria, status
            FROM despesa
            """
        ).fetchall()

        for despesa in despesas:
            data_despesa = self._parse_data(despesa["data"])
            if not self._esta_no_periodo(data_despesa, inicio, fim):
                continue

            valor = float(despesa["valor"] or 0.0)
            status = despesa["status"]
            categoria = despesa["categoria"]

            if status == StatusPagamento.PAGO.value:
                despesas_pagas += valor
                if categoria in (CategoriaDespesa.INSUMOS.value, CategoriaDespesa.INVESTIMENTOS.value):
                    total_investido += valor
            elif status == StatusPagamento.PENDENTE.value:
                falta_pagar += valor
        
        # Cálculos finais
        saldo_atual = total_recebido - despesas_pagas
        saldo_previsto = saldo_atual + a_receber - falta_pagar
        
        return DashboardResumo(
            saldo_atual=saldo_atual,
            falta_pagar=falta_pagar,
            a_receber=a_receber,
            saldo_previsto=saldo_previsto,
            total_investido=total_investido,
            lucro_total_vendas=lucro_total_vendas,
        )

    def get_faturamento_vs_despesas_mensal(self, data_inicio: str = "", data_fim: str = "") -> list[dict]:
        conn = get_connection()
        inicio = self._parse_data(data_inicio)
        fim = self._parse_data(data_fim)

        # Sem filtro aplicado, mostra os últimos 6 meses até o mês atual.
        if inicio is None and fim is None:
            hoje = datetime.now()
            ano_inicio = hoje.year
            mes_inicio = hoje.month - 5
            while mes_inicio <= 0:
                mes_inicio += 12
                ano_inicio -= 1
            inicio = datetime(ano_inicio, mes_inicio, 1)
            fim = datetime(hoje.year, hoje.month, calendar.monthrange(hoje.year, hoje.month)[1])

        if inicio is None and fim is not None:
            inicio = datetime(fim.year, fim.month, 1)
        if fim is None and inicio is not None:
            fim = datetime(inicio.year, inicio.month, calendar.monthrange(inicio.year, inicio.month)[1])

        if inicio is None or fim is None:
            return []

        meses = self._iterar_meses(inicio, fim)
        serie = {
            chave: {
                "mes": chave,
                "label": f"{chave[5:7]}/{chave[0:4]}",
                "faturamento": 0.0,
                "despesas": 0.0,
            }
            for chave in meses
        }

        rendimentos = conn.execute(
            """
            SELECT
                pag_inicial_valor, pag_inicial_data, pag_inicial_status,
                pag_final_valor, pag_final_data, pag_final_status
            FROM rendimento
            """
        ).fetchall()

        for rendimento in rendimentos:
            data_ini = self._parse_data(rendimento["pag_inicial_data"])
            if rendimento["pag_inicial_status"] == StatusPagamento.RECEBIDO.value and self._esta_no_periodo(data_ini, inicio, fim):
                chave = data_ini.strftime("%Y-%m") if data_ini else None
                if chave in serie:
                    serie[chave]["faturamento"] += float(rendimento["pag_inicial_valor"] or 0.0)

            data_fin = self._parse_data(rendimento["pag_final_data"])
            if rendimento["pag_final_status"] == StatusPagamento.RECEBIDO.value and self._esta_no_periodo(data_fin, inicio, fim):
                chave = data_fin.strftime("%Y-%m") if data_fin else None
                if chave in serie:
                    serie[chave]["faturamento"] += float(rendimento["pag_final_valor"] or 0.0)

        despesas = conn.execute(
            """
            SELECT data, valor, status
            FROM despesa
            """
        ).fetchall()

        for despesa in despesas:
            data_despesa = self._parse_data(despesa["data"])
            if despesa["status"] != StatusPagamento.PAGO.value or not self._esta_no_periodo(data_despesa, inicio, fim):
                continue

            chave = data_despesa.strftime("%Y-%m") if data_despesa else None
            if chave in serie:
                serie[chave]["despesas"] += float(despesa["valor"] or 0.0)

        return [serie[chave] for chave in meses]

    def get_despesas_por_categoria(self, data_inicio: str = "", data_fim: str = "") -> list[dict]:
        conn = get_connection()
        inicio = self._parse_data(data_inicio)
        fim = self._parse_data(data_fim)

        # Sem filtro aplicado, mostra os últimos 6 meses até o mês atual.
        if inicio is None and fim is None:
            hoje = datetime.now()
            ano_inicio = hoje.year
            mes_inicio = hoje.month - 5
            while mes_inicio <= 0:
                mes_inicio += 12
                ano_inicio -= 1
            inicio = datetime(ano_inicio, mes_inicio, 1)
            fim = datetime(hoje.year, hoje.month, calendar.monthrange(hoje.year, hoje.month)[1])

        if inicio is None and fim is not None:
            inicio = datetime(fim.year, fim.month, 1)
        if fim is None and inicio is not None:
            fim = datetime(inicio.year, inicio.month, calendar.monthrange(inicio.year, inicio.month)[1])

        if inicio is None or fim is None:
            return []

        totais = {
            CategoriaDespesa.INSUMOS.value: 0.0,
            CategoriaDespesa.INVESTIMENTOS.value: 0.0,
            CategoriaDespesa.OUTROS.value: 0.0,
        }
        total_geral = 0.0

        despesas = conn.execute(
            """
            SELECT data, valor, categoria, status
            FROM despesa
            """
        ).fetchall()

        for despesa in despesas:
            data_despesa = self._parse_data(despesa["data"])
            if despesa["status"] != StatusPagamento.PAGO.value or not self._esta_no_periodo(data_despesa, inicio, fim):
                continue

            valor = float(despesa["valor"] or 0.0)
            categoria = despesa["categoria"] or CategoriaDespesa.OUTROS.value
            if categoria not in totais:
                categoria = CategoriaDespesa.OUTROS.value

            totais[categoria] += valor
            total_geral += valor

        if total_geral <= 0:
            return []

        resultado = []
        for categoria in (CategoriaDespesa.INSUMOS.value, CategoriaDespesa.INVESTIMENTOS.value, CategoriaDespesa.OUTROS.value):
            valor = totais[categoria]
            if valor <= 0:
                continue
            resultado.append(
                {
                    "categoria": categoria,
                    "valor": valor,
                    "percentual": (valor / total_geral) * 100,
                }
            )

        return resultado

    def _iterar_meses(self, inicio: datetime, fim: datetime) -> list[str]:
        atual = datetime(inicio.year, inicio.month, 1)
        limite = datetime(fim.year, fim.month, 1)
        meses = []
        while atual <= limite:
            meses.append(atual.strftime("%Y-%m"))
            if atual.month == 12:
                atual = datetime(atual.year + 1, 1, 1)
            else:
                atual = datetime(atual.year, atual.month + 1, 1)
        return meses

    def _parse_data(self, data_txt: str | None) -> datetime | None:
        if not data_txt:
            return None

        valor = data_txt.strip()
        if not valor:
            return None

        try:
            return datetime.strptime(normalizar_data_iso(valor), "%Y-%m-%d")
        except ValueError:
            return None

    def _esta_no_periodo(self, data: datetime | None, inicio: datetime | None, fim: datetime | None) -> bool:
        if inicio is None and fim is None:
            return True
        if data is None:
            return False
        if inicio is not None and data < inicio:
            return False
        if fim is not None and data > fim:
            return False
        return True
