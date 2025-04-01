from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QSizePolicy, QFrame
from PySide6.QtCore import Qt, Signal
from repository.empresa_repository import criar_empresa_com_usuario
from utils.logger import logger

class CadastroEmpresaTela(QWidget):
    empresa_cadastrada = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cadastro de Nova Empresa")
        self.setGeometry(300, 200, 600, 400)
        self.setStyleSheet("background-color: #1A1F2C; color: white;")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Título
        titulo = QLabel("Cadastrar Nova Empresa")
        titulo.setStyleSheet("font-size: 20pt; font-weight: bold; color: white;")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        # Container central dos campos
        campos_frame = QFrame()
        campos_layout = QVBoxLayout(campos_frame)
        campos_layout.setAlignment(Qt.AlignCenter)
        campos_layout.setSpacing(15)

        # Campo: Razão Social
        self.input_razao = QLineEdit()
        self.input_razao.setPlaceholderText("Razão Social")
        self.input_razao.setFixedWidth(300)
        self.input_razao.setStyleSheet("padding: 8px; background-color: #2C3144; border-radius: 6px; color: white;")
        campos_layout.addWidget(self.input_razao)

        # Campo: Usuário
        self.input_usuario = QLineEdit()
        self.input_usuario.setPlaceholderText("Usuário (Login)")
        self.input_usuario.setFixedWidth(300)
        self.input_usuario.setStyleSheet("padding: 8px; background-color: #2C3144; border-radius: 6px; color: white;")
        campos_layout.addWidget(self.input_usuario)

        # Campo: Senha
        self.input_senha = QLineEdit()
        self.input_senha.setPlaceholderText("Senha")
        self.input_senha.setEchoMode(QLineEdit.Password)
        self.input_senha.setFixedWidth(300)
        self.input_senha.setStyleSheet("padding: 8px; background-color: #2C3144; border-radius: 6px; color: white;")
        campos_layout.addWidget(self.input_senha)

        # Botão: Salvar
        self.btn_salvar = QPushButton("Salvar Empresa")
        self.btn_salvar.setCursor(Qt.PointingHandCursor)
        self.btn_salvar.setFixedWidth(300)
        self.btn_salvar.clicked.connect(self.salvar_empresa)
        self.btn_salvar.setStyleSheet("""
            QPushButton {
                padding: 10px;
                margin: 30px;
                background-color: #E53935;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #5c1414;
            }
        """)
        campos_layout.addWidget(self.btn_salvar)

        layout.addStretch()
        layout.addWidget(campos_frame, alignment=Qt.AlignHCenter)
        layout.addStretch()

    def salvar_empresa(self):
        razao = self.input_razao.text().strip()
        usuario = self.input_usuario.text().strip()
        senha = self.input_senha.text().strip()

        if not razao or not usuario or not senha:
            QMessageBox.warning(self, "Erro", "Preencha todos os campos.")
            return

        sucesso, mensagem = criar_empresa_com_usuario(razao, usuario, senha)
        if sucesso:
            logger.info(f"Empresa cadastrada: '{razao}' | Usuário: '{usuario}'")
            QMessageBox.information(self, "Sucesso", "Empresa cadastrada com sucesso!")
            self.input_razao.clear()
            self.input_usuario.clear()
            self.input_senha.clear()
            self.empresa_cadastrada.emit()
        else:
            QMessageBox.warning(self, "Erro", mensagem)
