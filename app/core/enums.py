from enum import Enum

class StatusPagamento(str, Enum):
    PENDENTE = "Pendente"
    RECEBIDO = "Recebido"
    PAGO = "Pago"

class CategoriaDespesa(str, Enum):
    INSUMOS = "Insumos"
    INVESTIMENTOS = "Investimentos"
    OUTROS = "Outros"

class UnidadeMedida(str, Enum):
    G = "g"
    ML = "ml"
    UNIDADE = "unidade"

class FormaPagamento(str, Enum):
    PIX = "PIX"
    DINHEIRO = "Dinheiro"
    CARTAO_CREDITO = "Cartão Crédito"
    CARTAO_DEBITO = "Cartão Débito"
    BOLETO = "Boleto"
    TRANSFERENCIA = "Transferência"
