import os
import re
from datetime import datetime, timedelta
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QLineEdit, QHeaderView, QFrame, QPushButton
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from repository.usuario_repository import listar_empresas, listar_usuarios


class UsuarioAdminTela(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #1A1F2C;")
        self.setWindowTitle("Gerenciamento de Usuários")
        self.setGeometry(200, 100, 1000, 600)
        self.empresas_map = {}
        self.usuarios = []
        self.ultimos_logins = {}
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        titulo = QLabel("Usuários")
        titulo.setStyleSheet("color: white; font-size: 20pt; font-weight: bold;")
        layout.addWidget(titulo)

        busca_frame = QFrame()
        busca_frame.setStyleSheet("background-color: #1F2536; border-radius: 8px;")
        busca_layout = QHBoxLayout(busca_frame)
        busca_layout.setContentsMargins(10, 10, 10, 10)

        self.input_busca = QLineEdit()
        self.input_busca.setPlaceholderText("Buscar por nome ou empresa...")
        self.input_busca.setStyleSheet(
            "background-color: #2C3144; color: white; padding: 6px; border-radius: 6px;"
        )
        self.input_busca.textChanged.connect(self.filtrar_usuarios)
        busca_layout.addWidget(self.input_busca)

        self.btn_recarregar = QPushButton("")
        self.btn_recarregar.setIcon(QIcon("images/recarregar.png"))
        self.btn_recarregar.setIconSize(QSize(24, 24))
        self.btn_recarregar.setCursor(Qt.PointingHandCursor)
        self.btn_recarregar.setFixedSize(36, 36)
        self.btn_recarregar.setStyleSheet("""
            QPushButton {
                background-color: #D32F2F;
                color: white;
                font-weight: bold;
                font-size: 16px;
                border-radius: 18px;
            }
            QPushButton:hover {
                background-color: #5c1414;
            }
        """)
        self.btn_recarregar.clicked.connect(self.carregar_todos_usuarios)
        busca_layout.addWidget(self.btn_recarregar)

        layout.addWidget(busca_frame)

        tabela_container = QFrame()
        tabela_container.setStyleSheet(
            "background-color: #1F2536; border: 1px solid #2C3144; border-radius: 8px;"
        )
        tabela_layout = QVBoxLayout(tabela_container)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels(["ID", "Usuário", "Empresa", "ID Empresa", "Último Login"])
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setStyleSheet("""
            QTableWidget {
                color: white;
                background-color: #1F2536;
                gridline-color: #2C3144;
            }
            QHeaderView::section {
                background-color: #353A4F;
                color: white;
                font-weight: bold;
                padding: 6px;
                border: 1px solid #2C3144;
            }
        """)

        header = self.tabela.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.Interactive)

        tabela_layout.addWidget(self.tabela)
        layout.addWidget(tabela_container)

        self.carregar_todos_usuarios()

    def carregar_empresas(self):
        empresas = listar_empresas()
        self.empresas_map = {e['razao_social']: e['id'] for e in empresas}

    def carregar_todos_usuarios(self):
        self.carregar_empresas()
        self.extrair_ultimos_logins()

        todos = []
        for empresa_nome, empresa_id in self.empresas_map.items():
            usuarios = listar_usuarios(empresa_id)
            for u in usuarios:
                u['empresa'] = empresa_nome
                todos.append(u)
        self.usuarios = todos
        self.mostrar_usuarios(self.usuarios)

    def mostrar_usuarios(self, lista):
        self.tabela.setRowCount(len(lista))
        for row, usuario in enumerate(lista):
            nome = usuario["nome"].lower()
            ultimo_login = self.ultimos_logins.get(nome, "NUNCA")
            self.tabela.setItem(row, 0, QTableWidgetItem(str(usuario["id"])))
            self.tabela.setItem(row, 1, QTableWidgetItem(usuario["nome"]))
            self.tabela.setItem(row, 2, QTableWidgetItem(usuario.get("empresa", "Não vinculado")))
            self.tabela.setItem(row, 3, QTableWidgetItem(str(usuario.get("empresa_id", "-"))))
            self.tabela.setItem(row, 4, QTableWidgetItem(ultimo_login))
        self.tabela.resizeColumnsToContents()

    def filtrar_usuarios(self, texto):
        texto = texto.lower()
        filtrados = [
            u for u in self.usuarios
            if texto in u["nome"].lower() or texto in u.get("empresa", "").lower()
        ]
        self.mostrar_usuarios(filtrados)

    def extrair_ultimos_logins(self):
        log_path = os.path.join(os.getcwd(), "logs/acoes.log")
        if not os.path.exists(log_path):
            return

        pattern = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+ \| INFO \| Login realizado: user='(.+?)'")
        logins = {}

        with open(log_path, encoding="utf-8") as f:
            for line in f:
                match = pattern.match(line)
                if match:
                    data_str, user = match.groups()
                    data = datetime.strptime(data_str, "%Y-%m-%d %H:%M:%S")
                    logins[user.lower()] = max(logins.get(user.lower(), datetime.min), data)

        now = datetime.now()
        self.ultimos_logins = {}
        for user, last_login in logins.items():
            delta = now - last_login
            if delta < timedelta(minutes=1):
                tempo = "agora"
            elif delta < timedelta(hours=1):
                tempo = f"{int(delta.total_seconds() // 60)} min"
            elif delta < timedelta(days=1):
                tempo = f"{int(delta.total_seconds() // 3600)} h"
            elif delta < timedelta(days=7):
                tempo = f"{delta.days} d"
            else:
                semanas = delta.days // 7
                tempo = f"{semanas} sem"
            self.ultimos_logins[user] = tempo
