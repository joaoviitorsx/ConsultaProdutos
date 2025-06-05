from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QHBoxLayout,QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QMessageBox,QSizePolicy
from PySide6.QtGui import QFont, QCursor, QIcon
from PySide6.QtCore import Qt, QSize
from repository.consulta_repository import buscar_consultas_por_data
from utils.relatorio_pdf import gerar_pdf_relatorio_consultas
from datetime import datetime


class RelatorioTela(QWidget):
    def __init__(self, user: str, empresa_id: int):
        super().__init__()
        self.user = user
        self.empresa_id = empresa_id
        self.setWindowTitle("Relatório de Consultas")
        self.setGeometry(300, 100, 1200, 800)
        self.setStyleSheet("""
            QWidget {
                background-color: #181818;
                color: #e0e0e0;
                font-family: 'Segoe UI', sans-serif;
            }

            QComboBox {
                background-color: #2d2d2d;
                color: white;
                padding: 10px 18px;
                border-radius: 8px;
                font-size: 13px;
                border: 1px solid #3a3a3a;
            }

            QComboBox:hover {
                border: 1px solid #e53935;
                background-color: #2f2f2f;
            }

            QComboBox:focus {
                border: 1px solid #e53935;
                background-color: #2f2f2f;
            }

            QComboBox::drop-down {
                border: none;
                width: 0px;
            }

            QComboBox::down-arrow {
                image: none;
                width: 0px;
                height: 0px;
            }

            QComboBox QAbstractItemView {
                background-color: #2b2b2b;
                border: 1px solid #444;
                selection-background-color: #e53935;
                selection-color: white;
                color: white;
                font-size: 13px;
                padding: 6px;
            }

            QPushButton {
                background-color: #2d2d2d;
                color: white;
                padding: 10px 18px;
                border-radius: 8px;
                font-size: 13px;
                border: 1px solid #3a3a3a;
            }

            QPushButton:hover {
                background-color: #e53935;
                border: 1px solid #e53935;
                color: white;
            }

            QHeaderView::section {
                background-color: #333333;
                padding: 10px;
                font-weight: bold;
                color: white;
                border: none;
            }

            QTableWidget {
                background-color: #202020;
                border: 1px solid #333;
                font-size: 13px;
                border-radius: 8px;
            }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(20)

        header = QHBoxLayout()

        btn_voltar = QPushButton("")
        btn_voltar.setCursor(Qt.PointingHandCursor)
        btn_voltar.setIcon(QIcon("images/voltar.png"))
        btn_voltar.setIconSize(QSize(22, 22))
        btn_voltar.setStyleSheet("""
            QPushButton {
                background-color: #E53935;
                color: white;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #c62828;
            }
        """)
        btn_voltar.clicked.connect(self.voltar_dashboard)

        titulo = QLabel("Relatório de Consultas")
        titulo.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        titulo.setAlignment(Qt.AlignCenter)

        header.addWidget(btn_voltar)
        header.addStretch()
        header.addWidget(titulo)
        header.addStretch()
        layout.addLayout(header)

        filtros = QHBoxLayout()
        filtros.setSpacing(20)

        self.combo_mes = QComboBox()
        self.combo_mes.addItems([
            "01 - Janeiro", "02 - Fevereiro", "03 - Março", "04 - Abril",
            "05 - Maio", "06 - Junho", "07 - Julho", "08 - Agosto",
            "09 - Setembro", "10 - Outubro", "11 - Novembro", "12 - Dezembro"
        ])
        self.combo_mes.setFixedWidth(150)
        self.combo_mes.currentIndexChanged.connect(self.gerar_relatorio)

        ano_atual = datetime.now().year
        anos = [str(ano_atual - 2), str(ano_atual - 1), str(ano_atual)]
        self.combo_ano = QComboBox()
        self.combo_ano.addItems(anos)
        self.combo_ano.setFixedWidth(100)
        self.combo_ano.currentIndexChanged.connect(self.gerar_relatorio)

        self.btn_gerar = QPushButton("Gerar PDF")
        self.btn_gerar.setStyleSheet("font-size: 13px; font-weight: bold;")
        self.btn_gerar.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_gerar.setFixedWidth(150)
        self.btn_gerar.clicked.connect(self.gerar_pdf)

        filtros.addWidget(QLabel("Mês:"))
        filtros.addWidget(self.combo_mes)
        filtros.addSpacing(10)
        filtros.addWidget(QLabel("Ano:"))
        filtros.addWidget(self.combo_ano)
        filtros.addStretch()
        filtros.addWidget(self.btn_gerar)
        layout.addLayout(filtros)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(9)
        self.tabela.setHorizontalHeaderLabels([
            "Data", "Fornecedor", "Produto", "Código",
            "Valor Base", "Alíquota", "Adicional", "Total", "Valor Final"
        ])
        self.tabela.horizontalHeader().setStretchLastSection(True)
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout.addWidget(self.tabela)

        self.combo_mes.setCurrentIndex(datetime.now().month - 1)
        self.combo_ano.setCurrentText(str(ano_atual))
        self.gerar_relatorio()

    def gerar_relatorio(self):
        mes = self.combo_mes.currentIndex() + 1
        ano = int(self.combo_ano.currentText())
        consultas = buscar_consultas_por_data(self.empresa_id, mes, ano)

        self.tabela.setRowCount(0)
        if not consultas:
            return

        self.tabela.setRowCount(len(consultas))
        for row, c in enumerate(consultas):
            self.tabela.setItem(row, 0, QTableWidgetItem(str(c["data_consulta"])[:16]))
            self.tabela.setItem(row, 1, QTableWidgetItem(c["nome_fornecedor"]))
            self.tabela.setItem(row, 2, QTableWidgetItem(c["nome_produto"]))
            self.tabela.setItem(row, 3, QTableWidgetItem(str(c["cod_produto"])))
            self.tabela.setItem(row, 4, QTableWidgetItem(f"R$ {float(c['valor_base']):.2f}"))
            self.tabela.setItem(row, 5, QTableWidgetItem(f"{float(c['aliquota']):.2f}%"))
            self.tabela.setItem(row, 6, QTableWidgetItem(f"{float(c['aliquota_adicional']):.2f}%"))
            self.tabela.setItem(row, 7, QTableWidgetItem(f"{float(c['aliquota_total']):.2f}%"))
            self.tabela.setItem(row, 8, QTableWidgetItem(f"R$ {float(c['valor_total']):.2f}"))

    def gerar_pdf(self):
        mes = self.combo_mes.currentIndex() + 1
        ano = int(self.combo_ano.currentText())
        consultas = buscar_consultas_por_data(self.empresa_id, mes, ano)

        if not consultas:
            QMessageBox.information(self, "Sem Dados", "Nenhuma consulta encontrada para o período selecionado.")
            return

        gerar_pdf_relatorio_consultas(consultas, self.user, mes, ano, self.user)

    def voltar_dashboard(self):
        from ui.dashboardinicial import DashboardInicial
        self.dashboard = DashboardInicial(self.user, self.empresa_id)
        self.dashboard.showMaximized()
        self.close()
