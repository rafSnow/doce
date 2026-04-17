from __future__ import annotations

import os
import tempfile
import webbrowser
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.models.pedido import Pedido
from app.db.connection import get_db_path
from app.services.configuracao_service import ConfiguracaoService


class ReciboService:
    def __init__(self):
        self.config_service = ConfiguracaoService()

    def gerar_recibo_pdf(self, pedido: Pedido, caminho_saida: str, nome_estabelecimento: str | None = None) -> str:
        caminho = Path(caminho_saida).expanduser().resolve()
        if caminho.parent:
            caminho.parent.mkdir(parents=True, exist_ok=True)

        self._renderizar_documento(
            caminho,
            self._montar_story_recibo(pedido, nome_estabelecimento or self.config_service.get_nome_estabelecimento()),
            titulo="Recibo / Ordem de Servico",
        )
        return str(caminho)

    def gerar_previsao_recibo(self, pedido: Pedido, nome_estabelecimento: str | None = None) -> str:
        arquivo_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        arquivo_tmp.close()
        self.gerar_recibo_pdf(pedido, arquivo_tmp.name, nome_estabelecimento=nome_estabelecimento)
        return arquivo_tmp.name

    def imprimir_pdf(self, caminho_pdf: str) -> None:
        caminho = Path(caminho_pdf).resolve()
        if os.name != "nt":
            raise RuntimeError("Impressao direta foi preparada para Windows.")
        os.startfile(str(caminho), "print")

    def abrir_pdf(self, caminho_pdf: str) -> None:
        caminho = Path(caminho_pdf).resolve()
        if os.name == "nt":
            os.startfile(str(caminho))
        else:
            webbrowser.open(caminho.as_uri())

    def gerar_manual_uso_pdf(self, caminho_saida: str, nome_estabelecimento: str | None = None) -> str:
        caminho = Path(caminho_saida).expanduser().resolve()
        if caminho.parent:
            caminho.parent.mkdir(parents=True, exist_ok=True)

        self._renderizar_documento(
            caminho,
            self._montar_story_manual(nome_estabelecimento or self.config_service.get_nome_estabelecimento()),
            titulo="Manual Operacional de Uso",
        )
        return str(caminho)

    def get_caminho_manual_padrao(self) -> str:
        base_dir = Path(get_db_path()).resolve().parent
        pasta_manual = base_dir / "docs"
        pasta_manual.mkdir(parents=True, exist_ok=True)
        return str((pasta_manual / "manual_simplificado.pdf").resolve())

    def _renderizar_documento(self, caminho: Path, story: list, titulo: str) -> None:
        doc = SimpleDocTemplate(
            str(caminho),
            pagesize=A4,
            leftMargin=16 * mm,
            rightMargin=16 * mm,
            topMargin=18 * mm,
            bottomMargin=16 * mm,
        )
        doc.title = titulo
        doc.author = self.config_service.get_nome_estabelecimento()
        doc.subject = titulo
        doc.build(
            story,
            onFirstPage=lambda canvas, document: self._desenhar_cabecalho_rodape(canvas, document, titulo),
            onLaterPages=lambda canvas, document: self._desenhar_cabecalho_rodape(canvas, document, titulo),
        )

    def _base_styles(self):
        styles = getSampleStyleSheet()
        styles.add(
            ParagraphStyle(
                name="TituloDocumento",
                parent=styles["Title"],
                fontName="Helvetica-Bold",
                fontSize=18,
                leading=22,
                textColor=colors.HexColor("#A66850"),
                spaceAfter=6,
            )
        )
        styles.add(
            ParagraphStyle(
                name="SubtituloDocumento",
                parent=styles["Heading2"],
                fontName="Helvetica-Bold",
                fontSize=12,
                leading=15,
                textColor=colors.HexColor("#444444"),
                spaceBefore=8,
                spaceAfter=4,
            )
        )
        styles.add(
            ParagraphStyle(
                name="CorpoDocumento",
                parent=styles["BodyText"],
                fontName="Helvetica",
                fontSize=9.5,
                leading=13,
                textColor=colors.HexColor("#222222"),
                spaceAfter=4,
            )
        )
        styles.add(
            ParagraphStyle(
                name="PequenoDocumento",
                parent=styles["BodyText"],
                fontName="Helvetica",
                fontSize=8.5,
                leading=11,
                textColor=colors.HexColor("#444444"),
            )
        )
        return styles

    def _montar_story_recibo(self, pedido: Pedido, nome_estabelecimento: str) -> list:
        styles = self._base_styles()
        story: list = []

        total_itens = sum(item.valor_item for item in pedido.itens)
        total_recebido = float(pedido.pag_inicial_valor or 0.0) + float(pedido.pag_final_valor or 0.0)
        saldo_pendente = max(total_itens - total_recebido, 0.0)

        story.append(Paragraph(nome_estabelecimento, styles["TituloDocumento"]))
        story.append(Paragraph("Recibo / Ordem de Servico", styles["SubtituloDocumento"]))
        story.append(Spacer(1, 6))

        dados_gerais = [
            ["Pedido", f"#{pedido.id if pedido.id is not None else 'PREVIA'}"],
            ["Cliente", pedido.cliente_nome or ""],
            ["Data do pedido", self._formatar_data(pedido.data_pedido)],
            ["Data de entrega", self._formatar_data(pedido.data_entrega)],
            ["Responsavel", pedido.responsavel or ""],
        ]
        tabela_geral = Table(dados_gerais, colWidths=[38 * mm, 120 * mm])
        tabela_geral.setStyle(self._estilo_tabela_base())
        story.append(tabela_geral)
        story.append(Spacer(1, 8))

        story.append(Paragraph("Itens do pedido", styles["SubtituloDocumento"]))
        itens = [["Produto", "Qtd", "Preco unit. (snapshot)", "Subtotal"]]
        for item in pedido.itens:
            itens.append([
                item.produto_nome or f"Produto {item.produto_id}",
                str(item.quantidade),
                self._formatar_moeda(item.preco_unitario_snapshot),
                self._formatar_moeda(item.valor_item),
            ])

        tabela_itens = Table(itens, colWidths=[82 * mm, 18 * mm, 38 * mm, 38 * mm], repeatRows=1)
        tabela_itens.setStyle(self._estilo_tabela_itens())
        story.append(tabela_itens)
        story.append(Spacer(1, 8))

        resumo_financeiro = [
            ["Valor total dos itens", self._formatar_moeda(total_itens)],
            ["Pagamento inicial", self._formatar_moeda(pedido.pag_inicial_valor or 0.0)],
            ["Pagamento final", self._formatar_moeda(pedido.pag_final_valor or 0.0)],
            ["Total recebido", self._formatar_moeda(total_recebido)],
            ["Saldo pendente", self._formatar_moeda(saldo_pendente)],
        ]
        tabela_resumo = Table(resumo_financeiro, colWidths=[52 * mm, 48 * mm], hAlign="RIGHT")
        tabela_resumo.setStyle(self._estilo_tabela_resumo())
        story.append(tabela_resumo)
        story.append(Spacer(1, 10))

        linhas_pagamento = [
            f"Pagamento inicial: {self._formatar_moeda(pedido.pag_inicial_valor or 0.0)} | Forma: {pedido.pag_inicial_forma or '-'} | Status: {pedido.pag_inicial_status or '-'} | Data: {self._formatar_data(pedido.pag_inicial_data)}",
            f"Pagamento final: {self._formatar_moeda(pedido.pag_final_valor or 0.0)} | Forma: {pedido.pag_final_forma or '-'} | Status: {pedido.pag_final_status or '-'} | Data: {self._formatar_data(pedido.pag_final_data)}",
        ]
        for linha in linhas_pagamento:
            story.append(Paragraph(linha, styles["PequenoDocumento"]))

        story.append(Spacer(1, 8))
        story.append(Paragraph("Observacao: este documento resume os dados cadastrados no sistema e pode ser usado como comprovante interno do pedido.", styles["PequenoDocumento"]))

        return story

    def _montar_story_manual(self, nome_estabelecimento: str) -> list:
        styles = self._base_styles()
        story: list = []

        story.append(Paragraph(nome_estabelecimento, styles["TituloDocumento"]))
        story.append(Paragraph("Manual Operacional de Uso", styles["SubtituloDocumento"]))
        story.append(
            Paragraph(
                "Guia completo para operacao diaria, controle financeiro, emissao de documentos e manutencao segura dos dados.",
                styles["CorpoDocumento"],
            )
        )
        story.append(Paragraph(f"Versao do manual: {datetime.now().strftime('%d/%m/%Y')}", styles["PequenoDocumento"]))
        story.append(Spacer(1, 8))

        story.append(Paragraph("1. Objetivo e publico", styles["SubtituloDocumento"]))
        story.extend(
            self._manual_bullets(
                [
                    "Padronizar o uso do sistema para reduzir erros operacionais e retrabalho.",
                    "Garantir rastreabilidade das informacoes de pedidos, insumos, produtos e financeiro.",
                    "Apoiar equipe administrativa, atendimento e responsavel pela producao.",
                ],
                styles,
            )
        )

        story.append(Paragraph("2. Rotina diaria recomendada", styles["SubtituloDocumento"]))
        story.extend(
            self._manual_bullets(
                [
                    "Inicio do dia: validar Dashboard e revisar alertas de estoque.",
                    "Durante o dia: registrar novos pedidos e atualizar pagamentos recebidos.",
                    "Fim do dia: conferir despesas/rendimentos, emitir recibos pendentes e executar backup.",
                ],
                styles,
            )
        )

        story.append(Paragraph("3. Fluxo operacional de ponta a ponta", styles["SubtituloDocumento"]))
        fluxo = [
            ["Etapa", "Acao principal", "Resultado esperado"],
            ["1. Cadastro base", "Atualizar insumos, produtos e clientes", "Base pronta para novos pedidos"],
            ["2. Pedido", "Criar pedido e incluir itens", "Valor total calculado e registrado"],
            ["3. Pagamentos", "Informar entradas iniciais/finais", "Status financeiro atualizado"],
            ["4. Recibo", "Pre-visualizar, salvar ou imprimir PDF", "Documento formal do pedido"],
            ["5. Financeiro", "Conferir despesas e rendimentos", "Visao real do caixa"],
            ["6. Encerramento", "Executar backup e checar desempenho", "Operacao protegida"],
        ]
        tabela_fluxo = Table(fluxo, colWidths=[38 * mm, 62 * mm, 62 * mm], repeatRows=1)
        tabela_fluxo.setStyle(self._estilo_tabela_base())
        story.append(tabela_fluxo)
        story.append(Spacer(1, 8))

        story.append(PageBreak())

        story.append(Paragraph("4. Modulos do sistema", styles["SubtituloDocumento"]))

        story.append(Paragraph("4.1 Dashboard", styles["CorpoDocumento"]))
        story.extend(
            self._manual_bullets(
                [
                    "Exibe saldo realizado, a receber, falta pagar e saldo previsto.",
                    "Permite trocar periodo para leitura executiva rapida.",
                    "Use como primeira tela de analise antes de decisoes financeiras.",
                ],
                styles,
            )
        )

        story.append(Paragraph("4.2 Insumos", styles["CorpoDocumento"]))
        story.extend(
            self._manual_bullets(
                [
                    "Cadastre nome, categoria, preco, unidade e quantidades disponivel/minima.",
                    "Observe linhas destacadas para estoque critico ou abaixo do minimo.",
                    "Atualize sempre que houver nova compra para manter custo por unidade correto.",
                ],
                styles,
            )
        )

        story.append(Paragraph("4.3 Produtos", styles["CorpoDocumento"]))
        story.extend(
            self._manual_bullets(
                [
                    "Monte produtos com base nos insumos cadastrados.",
                    "Revise rendimento e custos para manter margem saudavel.",
                    "Ajustes em produto impactam novos pedidos e estimativas.",
                ],
                styles,
            )
        )

        story.append(Paragraph("4.4 Pedidos", styles["CorpoDocumento"]))
        story.extend(
            self._manual_bullets(
                [
                    "Selecione cliente, informe datas e adicione itens do pedido.",
                    "Registre responsavel e observacoes para facilitar atendimento.",
                    "Use recibo para documentar a negociacao e forma de pagamento.",
                ],
                styles,
            )
        )

        story.append(Paragraph("4.5 Financeiro", styles["CorpoDocumento"]))
        story.extend(
            self._manual_bullets(
                [
                    "Despesas: registre saidas, categorias e status de pagamento.",
                    "Rendimentos: registre entradas de clientes e status inicial/final.",
                    "Use filtros por periodo/status para auditoria e fechamento.",
                ],
                styles,
            )
        )

        story.append(Paragraph("4.6 Configuracoes", styles["CorpoDocumento"]))
        story.extend(
            self._manual_bullets(
                [
                    "Atualize o nome do estabelecimento para refletir nos documentos.",
                    "Execute backup recorrente e teste restauracao periodicamente.",
                    "Rode validacao de desempenho para monitorar degradacoes.",
                ],
                styles,
            )
        )

        story.append(Spacer(1, 8))
        story.append(Paragraph("5. Recibos e documentos", styles["SubtituloDocumento"]))
        story.extend(
            self._manual_bullets(
                [
                    "Pre-visualizar: gera PDF temporario para revisao antes da entrega.",
                    "Salvar PDF: arquiva documento em pasta definida pelo usuario.",
                    "Imprimir: envia o arquivo para a impressora padrao do Windows.",
                    "Boa pratica: validar cliente, itens, valores e status antes de emitir.",
                ],
                styles,
            )
        )

        story.append(PageBreak())

        story.append(Paragraph("6. Solucao de problemas", styles["SubtituloDocumento"]))
        incidentes = [
            ["Situacao", "Causa comum", "Acao recomendada"],
            ["PDF nao abre", "Associacao de arquivo no sistema", "Salvar localmente e abrir manualmente no leitor PDF"],
            ["Lentidao em consultas", "Base grande ou ambiente sobrecarregado", "Executar validacao de desempenho e fechar apps paralelos"],
            ["Divergencia em valores", "Cadastro desatualizado", "Revisar insumos/produtos e atualizar snapshots em novos pedidos"],
            ["Erro em backup", "Permissao/caminho", "Escolher pasta local com permissao de escrita"],
        ]
        tabela_incidentes = Table(incidentes, colWidths=[45 * mm, 52 * mm, 65 * mm], repeatRows=1)
        tabela_incidentes.setStyle(self._estilo_tabela_base())
        story.append(tabela_incidentes)
        story.append(Spacer(1, 8))

        story.append(Paragraph("7. Boas praticas de seguranca e governanca", styles["SubtituloDocumento"]))
        story.extend(
            self._manual_bullets(
                [
                    "Nao compartilhe o arquivo do banco (.db) por canais sem protecao.",
                    "Mantenha pelo menos 3 backups recentes em locais diferentes.",
                    "Padronize responsavel em pedidos/despesas/rendimentos para auditoria.",
                    "Faça revisao semanal dos dados financeiros pendentes.",
                ],
                styles,
            )
        )

        story.append(Paragraph("8. Checklist de fechamento semanal", styles["SubtituloDocumento"]))
        story.extend(
            self._manual_bullets(
                [
                    "Conferir pedidos pendentes e datas de entrega.",
                    "Conferir despesas pendentes e pagamentos realizados.",
                    "Conferir rendimentos pendentes e recebidos.",
                    "Emitir relatorios/exportacoes necessarias para controle externo.",
                    "Gerar backup e validar abertura do arquivo salvo.",
                ],
                styles,
            )
        )

        story.append(Spacer(1, 10))
        story.append(
            Paragraph(
                "Documento gerado automaticamente pelo sistema. Atualize o manual sempre que novos fluxos forem incorporados.",
                styles["PequenoDocumento"],
            )
        )
        return story

    def _manual_bullets(self, linhas: list[str], styles) -> list:
        return [Paragraph(f"- {linha}", styles["CorpoDocumento"]) for linha in linhas]

    def _estilo_tabela_base(self) -> TableStyle:
        return TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#A66850")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#222222")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("LEADING", (0, 0), (-1, -1), 11),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D8C4BA")),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#FFF8F5")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )

    def _estilo_tabela_itens(self) -> TableStyle:
        return TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E1E1E")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#222222")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#C9C9C9")),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F7F7")]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )

    def _estilo_tabela_resumo(self) -> TableStyle:
        return TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F5F0EB")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D0B7A8")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#222222")),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )

    def _desenhar_cabecalho_rodape(self, canvas, document, titulo: str) -> None:
        canvas.saveState()
        largura, altura = A4
        canvas.setStrokeColor(colors.HexColor("#A66850"))
        canvas.setLineWidth(1.2)
        canvas.line(document.leftMargin, altura - 14 * mm, largura - document.rightMargin, altura - 14 * mm)

        canvas.setFont("Helvetica-Bold", 10)
        canvas.setFillColor(colors.HexColor("#A66850"))
        canvas.drawString(document.leftMargin, altura - 11 * mm, titulo)

        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#666666"))
        canvas.drawRightString(largura - document.rightMargin, altura - 11 * mm, self.config_service.get_nome_estabelecimento())

        canvas.setStrokeColor(colors.HexColor("#C9B8AE"))
        canvas.setLineWidth(0.6)
        canvas.line(document.leftMargin, 12 * mm, largura - document.rightMargin, 12 * mm)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#666666"))
        canvas.drawString(document.leftMargin, 8 * mm, datetime.now().strftime("Gerado em %d/%m/%Y %H:%M"))
        canvas.drawRightString(largura - document.rightMargin, 8 * mm, f"Pagina {canvas.getPageNumber()}")
        canvas.restoreState()

    def _formatar_moeda(self, valor: float) -> str:
        return f"R$ {float(valor or 0.0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def _formatar_data(self, valor: str | None) -> str:
        if not valor:
            return "-"

        texto = str(valor).strip()
        if not texto:
            return "-"

        for formato in ("%d/%m/%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(texto, formato).strftime("%d/%m/%Y")
            except ValueError:
                continue

        return texto
