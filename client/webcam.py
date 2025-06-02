from PyQt6.QtWidgets import QMainWindow, QLabel, QMessageBox
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QPixmap, QIcon
import socket

class WebcamWindow(QMainWindow):
    def __init__(self, ip="127.0.0.1", port=9998):
        super().__init__()
        self.setWindowTitle("Вебкамера")
        self.setWindowIcon(QIcon("icons/webcam.png"))
        self.setGeometry(100, 100, 640, 480)

        self.label = QLabel(self)
        self.label.setGeometry(0, 0, 640, 480)
        self.label.setScaledContents(True)

        try:
            self.sock = socket.socket()
            self.sock.connect((ip, port))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Камера: {e}")
            self.close()
            return

        self.timer = QTimer()
        self.timer.timeout.connect(self.receive_frame)
        self.timer.start(30)

    def receive_frame(self):
        try:
            header = self.sock.recv(4)
            if not header:
                return
            size = int.from_bytes(header, 'big')
            data = b''
            while len(data) < size:
                data += self.sock.recv(size - len(data))
            pixmap = QPixmap()
            pixmap.loadFromData(data, 'JPEG')
            self.label.setPixmap(pixmap)
        except:
            pass

    def closeEvent(self, event):
        self.timer.stop()
        self.sock.close()
        event.accept()