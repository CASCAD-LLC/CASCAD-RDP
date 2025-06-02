from PyQt6.QtWidgets import QDialog, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import pyqtSignal
import socket
import os

dir_path = os.path.dirname(os.path.abspath(__file__))

class ConnectWindow(QDialog):
    connected_signal = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Подключение к серверу")
        self.setFixedSize(300, 110)

        self.ip_input = QLineEdit(self)
        self.ip_input.setPlaceholderText("Введите IP адрес (например, 127.0.0.1)")

        self.connect_btn = QPushButton(" Подключиться", self)
        self.connect_btn.setIcon(QIcon(os.path.join(dir_path, "icons", "connect.png")))
        self.connect_btn.setFixedHeight(40)
        self.connect_btn.clicked.connect(self.try_connect)

        layout = QVBoxLayout()
        layout.addWidget(self.ip_input)
        layout.addWidget(self.connect_btn)
        self.setLayout(layout)

    def try_connect(self):
        ip = self.ip_input.text().strip()
        try:
            sock = socket.socket()
            sock.connect((ip, 9999))
            self.connected_signal.emit(sock)
            self.close()
        except ConnectionRefusedError:
            self.msgbox = QMessageBox(QMessageBox.Icon.Critical, "Ошибка сокета", "Не удалось подключиться к серверу, так как порт закрыт и/или введён неверный IP адрес", QMessageBox.StandardButton.Ok, self)
            self.msgbox.setWindowIcon(QIcon(dir_path + r"/icons/connect.png"))
            self.msgbox.show()
        except socket.gaierror:
            self.msgbox = QMessageBox(QMessageBox.Icon.Critical, "Ошибка сокета", "Не удалось подключиться к серверу, скорее всего IP адрес введён в неверном формате или его не существует", QMessageBox.StandardButton.Ok, self)
            self.msgbox.setWindowIcon(QIcon(dir_path + r"/icons/connect.png"))
            self.msgbox.show()