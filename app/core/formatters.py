"""Utilitarios centralizados para formatacao e parsing de valores e datas."""

from __future__ import annotations

from datetime import datetime


def fmt_moeda(valor: float, casas: int = 2) -> str:
    """Formata numero no padrao brasileiro sem prefixo de moeda."""
    return f"{float(valor):,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_data(valor: str | None) -> str:
    """Normaliza datas em DD/MM/AAAA (ou DD/MM/AAAA HH:MM para datetime)."""
    if not valor:
        return ""

    texto = str(valor).strip()
    if not texto:
        return ""

    for formato_entrada, formato_saida in (
        ("%d/%m/%Y", "%d/%m/%Y"),
        ("%Y-%m-%d", "%d/%m/%Y"),
        ("%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M"),
        ("%d/%m/%Y %H:%M", "%d/%m/%Y %H:%M"),
    ):
        try:
            return datetime.strptime(texto, formato_entrada).strftime(formato_saida)
        except ValueError:
            continue

    return texto


def parse_float(
    texto: str,
    campo: str,
    obrigatorio: bool = True,
    minimo: float | None = None,
) -> float:
    """Converte texto em float aceitando formatos brasileiro e internacional."""
    valor = (texto or "").strip().replace(" ", "")
    if "," in valor:
        valor = valor.replace(".", "").replace(",", ".")

    if not valor:
        if obrigatorio:
            raise ValueError(f"O campo {campo} e obrigatorio.")
        return 0.0

    try:
        numero = float(valor)
    except ValueError as exc:
        raise ValueError(f"O campo {campo} deve ser numerico.") from exc

    if minimo is not None and numero < minimo:
        raise ValueError(f"O campo {campo} nao pode ser menor que {minimo}.")

    return numero


def normalizar_data_iso(valor: str) -> str:
    """Converte DD/MM/AAAA ou YYYY-MM-DD para YYYY-MM-DD."""
    texto = (valor or "").strip()
    if not texto:
        raise ValueError("Data vazia.")

    for formato in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(texto, formato).strftime("%Y-%m-%d")
        except ValueError:
            continue

    raise ValueError("Data invalida.")


def parse_data(texto: str, campo: str, obrigatorio: bool = False) -> str:
    """Valida data e devolve no formato DD/MM/AAAA."""
    valor = (texto or "").strip()
    if not valor:
        if obrigatorio:
            raise ValueError(f"O campo {campo} e obrigatorio.")
        return ""

    try:
        iso = normalizar_data_iso(valor)
        return datetime.strptime(iso, "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError as exc:
        raise ValueError(f"O campo {campo} deve estar no formato DD/MM/AAAA.") from exc
