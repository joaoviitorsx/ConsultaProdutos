from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton,
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt
from repository.consulta_repository import buscar_consultas_por_data
from utils.relatorio_pdf import gerar_pdf_relatorio_consultas


class RelatorioTela(QWidget):
    def __init__(self, empresa_id: int, razao_social: str, user: str):
        super().__init__()
        self.setWindowTitle("Relatório Mensal de Consultas")
        self.setGeometry(300, 100, 900, 600)
        self.empresa_id = empresa_id
        self.razao_social = razao_social
        self.user = user
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        titulo = QLabel("📄 Relatório Mensal de Consultas")
        titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        # Filtros de mês e ano
        self.combo_mes = QComboBox()
        self.combo_mes.addItems([
            "01 - Janeiro", "02 - Fevereiro", "03 - Março", "04 - Abril",
            "05 - Maio", "06 - Junho", "07 - Julho", "08 - Agosto",
            "09 - Setembro", "10 - Outubro", "11 - Novembro", "12 - Dezembro"
        ])

        self.combo_ano = QComboBox()
        self.combo_ano.addItems(["2023", "2024", "2025"])

        layout.addWidget(QLabel("Selecione o mês:"))
        layout.addWidget(self.combo_mes)
        layout.addWidget(QLabel("Selecione o ano:"))
        layout.addWidget(self.combo_ano)

        # Botão de gerar relatório
        self.btn_gerar = QPushButton("📥 Gerar Relatório em PDF")
        self.btn_gerar.setStyleSheet("padding: 10px; font-weight: bold;")
        self.btn_gerar.clicked.connect(self.gerar_relatorio)
        layout.addWidget(self.btn_gerar)

        # Tabela de visualização
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(7)
        self.tabela.setHorizontalHeaderLabels([
            "Data", "Fornecedor", "Produto", "Código", "Alíquota", "Adicional", "Total"
        ])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tabela)

    def gerar_relatorio(self):
        mes = self.combo_mes.currentIndex() + 1
        ano = int(self.combo_ano.currentText())

        consultas = buscar_consultas_por_data(self.empresa_id, mes, ano)

        if not consultas:
            QMessageBox.information(self, "Sem Dados", "Nenhuma consulta encontrada para o período selecionado.")
            self.tabela.setRowCount(0)
            return

        # Exibir os dados na tabela
        self.tabela.setRowCount(len(consultas))
        for row, c in enumerate(consultas):
            self.tabela.setItem(row, 0, QTableWidgetItem(str(c["data_consulta"])))
            self.tabela.setItem(row, 1, QTableWidgetItem(c["nome_fornecedor"]))
            self.tabela.setItem(row, 2, QTableWidgetItem(c["nome_produto"]))
            self.tabela.setItem(row, 3, QTableWidgetItem(str(c["cod_produto"])))
            self.tabela.setItem(row, 4, QTableWidgetItem(f"{c['aliquota']:.2f}%"))
            self.tabela.setItem(row, 5, QTableWidgetItem(f"{c['aliquota_adicional']:.2f}%"))
            self.tabela.setItem(row, 6, QTableWidgetItem(f"{c['aliquota_total']:.2f}%"))

        # Gerar PDF após exibir na tela
        gerar_pdf_relatorio_consultas(
            consultas, self.razao_social, mes, ano, self.user
        )
