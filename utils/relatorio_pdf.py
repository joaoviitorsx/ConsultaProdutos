import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from PySide6.QtWidgets import QMessageBox

def gerar_pdf_relatorio_consultas(consultas, razao_social, mes, ano, user):
    try:
        nome_arquivo = f"relatorio_consultas_{razao_social}_{mes}_{ano}.pdf"
        caminho = os.path.join(os.path.expanduser("~"), "Downloads", nome_arquivo)

        doc = SimpleDocTemplate(caminho, pagesize=letter)
        elementos = []

        estilo_titulo = ParagraphStyle(
            name='Titulo', fontSize=16, alignment=1, spaceAfter=20, fontName='Helvetica-Bold'
        )

        titulo = Paragraph(f"Relatório de Consultas - {razao_social} ({mes:02}/{ano})", estilo_titulo)
        elementos.append(titulo)

        data = [["Data", "Fornecedor", "Produto", "Código", "Alíquota", "Adicional", "Total"]]

        for c in consultas:
            data.append([
                str(c["data_consulta"])[:16],
                c["nome_fornecedor"],
                c["nome_produto"],
                str(c["cod_produto"]),
                f"{c['aliquota']:.2f}%",
                f"{c['aliquota_adicional']:.2f}%",
                f"{c['aliquota_total']:.2f}%"
            ])

        tabela = Table(data, colWidths=[90, 130, 130, 60, 60, 60, 60])
        tabela.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2F4F4F")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F5F5DC")),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]))

        elementos.append(tabela)
        doc.build(elementos)

        QMessageBox.information(None, "PDF Gerado", f"Relatório salvo em:\n{caminho}")

    except Exception as e:
        QMessageBox.critical(None, "Erro ao gerar PDF", str(e))
