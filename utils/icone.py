import os
import sys
import urllib.request
from PySide6 import QtGui

def recurso_caminho(caminho_relativo):
    """ Garante que o caminho funcione mesmo em app empacotado (ex: PyInstaller) """
    try:
        base_path = sys._MEIPASS  # PyInstaller cria esse atributo
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, caminho_relativo)
    
def usar_icone(janela):
    pasta = "images"
    nome_icone = "icone.png"
    caminho = os.path.join(pasta, nome_icone)

    os.makedirs(pasta, exist_ok=True)

    # Baixa o ícone apenas se não existir
    if not os.path.exists(caminho):
        url = "https://assertivuscontabil.com.br/wp-content/uploads/2023/11/76.png"
        try:
            urllib.request.urlretrieve(url, caminho)
        except Exception as e:
            print(f"Erro ao baixar ícone: {e}")
            return

    janela.setWindowIcon(QtGui.QIcon(caminho))
