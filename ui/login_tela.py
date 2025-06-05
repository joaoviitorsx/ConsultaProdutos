from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QSpacerItem, QSizePolicy, QFrame, QSpacerItem
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont
from PySide6.QtGui import QPixmap
from utils.logger import logger
from db.db_manager import DBManager
from utils.mensagem import mensagem_error, mensagem_aviso
from ui.admin_tela import AdminTela
import time


class LoginThread(QThread):
    resultado = Signal(bool, object)

    def __init__(self, user, password):
        super().__init__()
        self.user = user
        self.password = password

    def run(self):
        import time
        inicio = time.time()

        try:
            conn = DBManager.instance().get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, empresa_id FROM users
                    WHERE nome = %s AND senha = %s
                    LIMIT 1
                """, (self.user, self.password))
                resultado = cursor.fetchone()

            sucesso = resultado is not None
            fim = time.time()
            print(f"⏱️ Tempo total de login (query): {fim - inicio:.2f} segundos")

            if sucesso:
                user_id, empresa_id = resultado
                self.resultado.emit(True, (self.user, empresa_id))
            else:
                self.resultado.emit(False, "Usuário ou senha inválidos.")

        except Exception as e:
            self.resultado.emit(False, f"Erro inesperado: {e}")



class LoginTela(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Consultor de Produtos - Login")
        self.setGeometry(400, 100, 800, 800)
        self.setStyleSheet("background-color: #181818;")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        logo = QLabel(self)
        pixmap = QPixmap("images/logo.png")
        if not pixmap.isNull():
            logo.setPixmap(pixmap.scaled(250, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)

        card = QFrame()
        card.setObjectName("cardContainer")
        card.setFixedWidth(450)
        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignCenter)

        label_titulo = QLabel("Login")
        label_titulo.setObjectName("titulo")
        label_titulo.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(label_titulo)

        label_descricao = QLabel("Informe usuário e senha para continuar")
        label_descricao.setObjectName("descricao")
        label_descricao.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(label_descricao)

        card_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

        self.input_usuario = QLineEdit()
        self.input_usuario.setPlaceholderText("Usuário")
        self.input_usuario.setObjectName("campoInput")
        self.input_usuario.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.input_usuario)

        self.input_senha = QLineEdit()
        self.input_senha.setPlaceholderText("Senha")
        self.input_senha.setEchoMode(QLineEdit.Password)
        self.input_senha.setObjectName("campoInput")
        self.input_senha.setAlignment(Qt.AlignCenter)
        self.input_senha.returnPressed.connect(self.validar_login)
        card_layout.addWidget(self.input_senha)

        card_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

        self.btn_entrar = QPushButton("Entrar")
        self.btn_entrar.setObjectName("botaoPrincipal")
        self.btn_entrar.setStyleSheet("""
            QPushButton#botaoPrincipal {
                background-color: #E53935;
                color: white;
                border-radius: 8px;
                padding: 12px;
                font-weight: bold;
                font-size: 14px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            QPushButton#botaoPrincipal:hover {
                background-color: #C62828;
            }
            QPushButton#botaoPrincipal:disabled {
                background-color: #444444;
                color: #CCCCCC;
                border: 1px solid #333333;
            }
            """)
        self.btn_entrar.setCursor(Qt.PointingHandCursor)
        self.btn_entrar.clicked.connect(self.validar_login)
        card_layout.addWidget(self.btn_entrar)

        layout.addWidget(card)

    def validar_login(self):
        user = self.input_usuario.text().strip()
        password = self.input_senha.text().strip()

        if not user or not password:
            mensagem_aviso("Usuário e senha são obrigatórios.")
            return

        self.btn_entrar.setEnabled(False)
        self.btn_entrar.setText("Entrando...")

        self.thread = LoginThread(user, password)
        self.thread.resultado.connect(self.login_finalizado)
        self.thread.start()

    def login_finalizado(self, sucesso, dados):
        self.btn_entrar.setEnabled(True)
        self.btn_entrar.setText("Entrar")

        if sucesso:
            user, empresa_id = dados
            logger.info(f"Login realizado: user='{user}' empresa_id={empresa_id}")
            if empresa_id is None:
                from ui.admin_tela import AdminTela
                self.admin_tela = AdminTela(user)
                self.admin_tela.showMaximized()
            else:
                from ui.dashboardinicial import DashboardInicial
                self.dashboard_tela = DashboardInicial(user, empresa_id)
                self.dashboard_tela.showMaximized()
            self.close()
        else:
            mensagem_error(dados)
            logger.warning(f"Falha no login: motivo='{dados}'")
