from dataclasses import dataclass
from app.db.connection import get_connection

@dataclass
class DashboardResumo:
    saldo_atual: float
    falta_pagar: float
    a_receber: float
    saldo_previsto: float

class DashboardService:
    def get_resumo(self) -> DashboardResumo:
        conn = get_connection()
        
        # Pedidos: Entradas (Sinal + Pagamento Final)
        pedidos_row = conn.execute("""
            SELECT 
                SUM(CASE WHEN pag_inicial_status = 'Recebido' THEN pag_inicial_valor ELSE 0 END) +
                SUM(CASE WHEN pag_final_status = 'Recebido' THEN pag_final_valor ELSE 0 END) as total_recebido,
                
                SUM(CASE WHEN pag_inicial_status = 'Pendente' THEN pag_inicial_valor ELSE 0 END) +
                SUM(CASE WHEN pag_final_status = 'Pendente' THEN pag_final_valor ELSE 0 END) as total_a_receber
            FROM pedido
        """).fetchone()
        
        total_recebido = pedidos_row["total_recebido"] or 0.0
        a_receber = pedidos_row["total_a_receber"] or 0.0
        
        # Despesas: Pagas e Pendentes (será populado na Sprint 6, mas a consulta já fica pronta)
        despesas_row = conn.execute("""
            SELECT 
                SUM(CASE WHEN status = 'Pago' THEN valor ELSE 0 END) as total_pago,
                SUM(CASE WHEN status = 'Pendente' THEN valor ELSE 0 END) as total_pendente
            FROM despesa
        """).fetchone()
        
        despesas_pagas = despesas_row["total_pago"] or 0.0
        falta_pagar = despesas_row["total_pendente"] or 0.0
        
        # Cálculos finais
        saldo_atual = total_recebido - despesas_pagas
        saldo_previsto = saldo_atual + a_receber - falta_pagar
        
        return DashboardResumo(
            saldo_atual=saldo_atual,
            falta_pagar=falta_pagar,
            a_receber=a_receber,
            saldo_previsto=saldo_previsto
        )
