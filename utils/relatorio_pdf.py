import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from PySide6.QtWidgets import QMessageBox

def formatar_aliquota(valor):
    try:
        return f"{float(valor):.2f}%"
    except:
        return str(valor)

def formatar_moeda(valor):
    try:
        return f"R$ {float(valor):.2f}"
    except:
        return str(valor)

def gerar_pdf_relatorio_consultas(consultas, razao_social, mes, ano, user):
    try:
        nome_arquivo = f"relatorio_consultas_{razao_social}_{mes}_{ano}.pdf"
        caminho = os.path.join(os.path.expanduser("~"), "Downloads", nome_arquivo)

        doc = SimpleDocTemplate(caminho, pagesize=letter)
        elementos = []

        estilo_titulo = ParagraphStyle(
            name='Titulo', fontSize=16, alignment=1, spaceAfter=20, fontName='Helvetica-Bold'
        )

        estilo_celula = ParagraphStyle(
            name='Celula', fontSize=8, alignment=1, fontName='Helvetica'
        )

        titulo = Paragraph(f"Relatório de Consultas - {razao_social} ({mes:02}/{ano})", estilo_titulo)
        elementos.append(titulo)

        # Cabeçalho
        data = [[
            "Data", "Fornecedor", "Produto", "Código",
            "Alíquota", "Adicional", "Total", "Valor Base", "Valor Final"
        ]]

        for c in consultas:
            linha = [
                str(c["data_consulta"])[:16],
                Paragraph(c["nome_fornecedor"], estilo_celula),
                Paragraph(c["nome_produto"], estilo_celula),
                str(c["cod_produto"]),
                formatar_aliquota(c["aliquota"]),
                formatar_aliquota(c["aliquota_adicional"]),
                formatar_aliquota(c["aliquota_total"]),
                formatar_moeda(c["valor_base"]),
                formatar_moeda(c["valor_total"])
            ]
            data.append(linha)

        # Ajuste de larguras para comportar 9 colunas
        tabela = Table(data, colWidths=[65, 110, 110, 45, 50, 50, 50, 65, 65])
        tabela.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2F4F4F")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F5F5DC")),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]))

        elementos.append(tabela)
        doc.build(elementos)

        QMessageBox.information(None, "PDF Gerado", f"Relatório salvo em:\n{caminho}")

    except Exception as e:
        QMessageBox.critical(None, "Erro ao gerar PDF", str(e))
