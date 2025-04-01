# utils/pdf.py
import os
from PySide6.QtWidgets import QMessageBox
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Image, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from utils.icone import recurso_caminho

class PDFGenerator:
    def __init__(self, user, razao_social, cnpj, cnae_codigo, uf, cnae_valido, simples):
        self.user = user
        self.razao_social = razao_social
        self.cnpj = cnpj
        self.cnae_codigo = cnae_codigo
        self.uf = uf
        self.cnae_valido = "Sim" if cnae_valido else "Não"
        self.simples = "Sim" if simples else "Não"

    def converter_aliquota(self, valor):
        try:
            return float(str(valor).replace('%', '').replace(',', '.').strip())
        except Exception as e:
            print(f"Erro ao converter alíquota: {e}")
            return 0.0

    def generate_pdf(self, file_path, product_code, produto, ncm, aliquota):
        try:
            # Cálculo da alíquota total
            aliquota_adicional = '3.00%' if self.simples == 'Sim' else '0.00%'
            aliquota_base = self.converter_aliquota(aliquota)
            adicional = self.converter_aliquota(aliquota_adicional)
            aliquota_total = f"{aliquota_base + adicional:.2f}%"

            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            pdf = SimpleDocTemplate(file_path, pagesize=letter)
            styles = getSampleStyleSheet()
            estilo_titulo = ParagraphStyle(
                name='Titulo', fontSize=16, alignment=1, spaceAfter=20, fontName='Helvetica-Bold'
            )

            titulo = Paragraph("CONSULTA DE PRODUTO - RELATÓRIO", estilo_titulo)

            # Logos
            logo_assertivus = recurso_caminho("images/icone.png")
            logo_empresa = recurso_caminho(f"images/{self.user}-logo.jpeg") \
                if self.user in ['atacado', 'jm'] else logo_assertivus

            img_assertivus = Image(logo_assertivus, width=100, height=50)
            img_empresa = Image(logo_empresa, width=100, height=50)

            logo_table = Table([[img_empresa, img_assertivus]], colWidths=[250, 250])
            logo_table.setStyle(TableStyle([
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]))

            # Dados da tabela
            data = [
                ["Campo", "Informação"],
                ["Razão Social", self.razao_social],
                ["CNPJ", self.cnpj],
                ["CNAE", self.cnae_codigo],
                ["UF", self.uf],
                ["DECRETO", self.cnae_valido],
                ["SIMPLES", self.simples],
                ["Código do Produto", product_code],
                ["Produto", produto],
                ["NCM", ncm],
                ["Alíquota", f"{aliquota_base:.2f}%"],
                ["Alíquota (Simples)", aliquota_adicional],
                ["Alíquota Total", aliquota_total],
            ]

            tabela = Table(data, colWidths=[150, 350])
            tabela.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2F4F4F")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F5F5DC")),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]))

            pdf.build([logo_table, Spacer(1, 12), titulo, Spacer(1, 12), tabela])
            QMessageBox.information(None, "Sucesso", f"PDF gerado com sucesso em:\n{file_path}")

        except PermissionError:
            QMessageBox.warning(None, "Erro", "Não foi possível salvar o arquivo. Feche o arquivo se ele estiver aberto.")
        except Exception as e:
            QMessageBox.critical(None, "Erro", f"Erro ao gerar PDF:\n{str(e)}")