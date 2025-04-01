import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from ui.login_tela import LoginTela

def carregar_estilo(app):
    try:
        with open("styles/main.qss", "r", encoding="utf-8") as f:
            estilo = f.read()
            app.setStyleSheet(estilo)
    except Exception as e:
        print(f"Erro ao aplicar estilo: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("fusion")

    icon_path = os.path.join(os.path.dirname(__file__), "images", "icone.ico")
    app.setWindowIcon(QIcon(icon_path))

    carregar_estilo(app)

    janela = LoginTela()
    janela.setWindowIcon(QIcon(icon_path))
    janela.showMaximized()

    sys.exit(app.exec())
