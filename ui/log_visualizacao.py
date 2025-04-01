import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QPushButton, QFrame, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon

class LogVisualizacaoTela(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #1A1F2C;")
        self.setWindowTitle("Relatórios do Sistema (Log)")
        self.setGeometry(200, 100, 900, 600)
        self.log_path = os.path.join("logs", "acoes.log")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        titulo = QLabel("Relatório de Logs")
        titulo.setStyleSheet("color: white; font-size: 20pt; font-weight: bold;")
        layout.addWidget(titulo)

        # Filtro
        filtro_frame = QFrame()
        filtro_frame.setStyleSheet("background-color: #1F2536; border-radius: 8px;")
        filtro_layout = QHBoxLayout(filtro_frame)
        filtro_layout.setContentsMargins(10, 10, 10, 10)

        self.filtro_input = QLineEdit()
        self.filtro_input.setPlaceholderText("Buscar nos logs...")
        self.filtro_input.setStyleSheet("background-color: #2C3144; color: white; padding: 6px; border-radius: 6px;")
        filtro_layout.addWidget(self.filtro_input)

        self.btn_filtrar = QPushButton("Filtrar")
        self.btn_filtrar.setStyleSheet("background-color: #007BFF; color: white; padding: 6px 12px; border-radius: 6px; font-weight: bold; font-size: 14px;")
        self.btn_filtrar.clicked.connect(self.aplicar_filtro)
        self.btn_filtrar.setCursor(Qt.PointingHandCursor)
        filtro_layout.addWidget(self.btn_filtrar)

        self.btn_recarregar = QPushButton("")
        self.btn_recarregar.setIcon(QIcon("images/recarregar.png"))
        self.btn_recarregar.setStyleSheet("""
            QPushButton {
                background-color: #D32F2F;
                color: white;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #5c1414;
            }
        """)
        self.btn_recarregar.clicked.connect(self.carregar_log)
        self.btn_recarregar.setIconSize(QSize(16, 16))
        self.btn_recarregar.setCursor(Qt.PointingHandCursor)
        filtro_layout.addWidget(self.btn_recarregar)

        layout.addWidget(filtro_frame)

        # Tabela de logs
        tabela_container = QFrame()
        tabela_container.setStyleSheet("background-color: #1F2536; border: 1px solid #2C3144; border-radius: 8px;")
        tabela_layout = QVBoxLayout(tabela_container)

        self.tabela_log = QTableWidget()
        self.tabela_log.setColumnCount(3)
        self.tabela_log.setHorizontalHeaderLabels(["Data/Hora", "Nível", "Mensagem"])
        self.tabela_log.verticalHeader().setVisible(False)
        self.tabela_log.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela_log.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela_log.setStyleSheet("QTableWidget { color: white; background-color: #1F2536; gridline-color: #2C3144; } QHeaderView::section { background-color: #353A4F; color: white; font-weight: bold; padding: 6px; border: 1px solid #2C3144; }")

        header = self.tabela_log.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.Interactive)

        tabela_layout.addWidget(self.tabela_log)
        layout.addWidget(tabela_container)

        self.carregar_log()

    def carregar_log(self):
        if not os.path.exists(self.log_path):
            self.tabela_log.setRowCount(0)
            self.tabela_log.insertRow(0)
            self.tabela_log.setItem(0, 0, QTableWidgetItem("Arquivo de log não encontrado."))
            return

        with open(self.log_path, "r", encoding="utf-8") as f:
            linhas = f.readlines()[::-1]

        self.preencher_tabela(linhas)

    def aplicar_filtro(self):
        termo = self.filtro_input.text().lower()
        if not os.path.exists(self.log_path):
            return

        with open(self.log_path, "r", encoding="utf-8") as f:
            linhas = f.readlines()

        filtrado = [linha for linha in linhas if termo in linha.lower()]
        self.preencher_tabela(filtrado)

    def preencher_tabela(self, linhas):
        self.tabela_log.setRowCount(0)
        for linha in linhas:
            partes = linha.strip().split("|", 2)
            if len(partes) == 3:
                row = self.tabela_log.rowCount()
                self.tabela_log.insertRow(row)
                self.tabela_log.setItem(row, 0, QTableWidgetItem(partes[0].strip()))
                self.tabela_log.setItem(row, 1, QTableWidgetItem(partes[1].strip()))
                self.tabela_log.setItem(row, 2, QTableWidgetItem(partes[2].strip()))

                nivel = partes[1].strip().upper()
                if nivel == "ERROR":
                    for col in range(3):
                        self.tabela_log.item(row, 1).setBackground(Qt.red)
                elif nivel == "WARNING":
                    for col in range(3):
                        self.tabela_log.item(row, 1).setBackground(Qt.darkYellow)
                elif nivel == "INFO":
                    for col in range(3):
                        self.tabela_log.item(row, 1).setBackground(Qt.darkCyan)
