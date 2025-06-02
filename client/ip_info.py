from PyQt6.QtWidgets import QMainWindow, QLabel, QLineEdit, QMessageBox
from PyQt6.QtGui import QIcon
import socket
import json
import struct

class IPInfoWindow(QMainWindow):
    def __init__(self, host="127.0.0.1", port=10000):
        super().__init__()
        self.setWindowTitle("IP информация о сервере")
        self.setWindowIcon(QIcon("icons/ip.png"))
        self.setGeometry(200, 200, 400, 300)

        labels = ["IP", "Страна", "Город", "Координаты", "Адрес", "Индекс"]
        self.fields = {}

        for i, label_text in enumerate(labels):
            label = QLabel(label_text + ":", self)
            label.move(20, 30 + i * 40)
            field = QLineEdit(self)
            field.setGeometry(120, 30 + i * 40, 250, 25)
            field.setReadOnly(True)
            self.fields[label_text] = field

        try:
            sock = socket.socket()
            sock.connect((host, port))

            msg = json.dumps({"type": "get_ip_info"}).encode("utf-8")
            length = struct.pack(">I", len(msg))
            sock.sendall(length + msg)

            size_data = sock.recv(4)
            size = struct.unpack(">I", size_data)[0]
            data = b""
            while len(data) < size:
                data += sock.recv(size - len(data))
            ipinfo = json.loads(data.decode("utf-8"))

            self.fields["IP"].setText(ipinfo.get("query", ""))
            self.fields["Страна"].setText(ipinfo.get("country", ""))
            self.fields["Город"].setText(ipinfo.get("city", ""))
            coords = f"{ipinfo.get('lat', '')}, {ipinfo.get('lon', '')}"
            self.fields["Координаты"].setText(coords)
            self.fields["Адрес"].setText(ipinfo.get("regionName", ""))
            self.fields["Индекс"].setText(ipinfo.get("zip", ""))

            sock.close()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось получить IP информацию: {e}")
            self.close()
