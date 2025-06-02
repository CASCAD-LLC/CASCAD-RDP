import sys
import os
import json
import socket
import struct
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

import style
from connect import ConnectWindow
from webcam import WebcamWindow
from microphone import MicrophoneWindow
from msgbox import MsgBoxWindow
from ip_info import IPInfoWindow


dir_path = os.path.dirname(os.path.abspath(__file__))

class ScreenshotReceiver(QThread):
    screenshot_received = pyqtSignal(QPixmap)

    def __init__(self, sock):
        super().__init__()
        self.sock = sock
        self.running = True

    def run(self):
        while self.running:
            try:
                size_data = self.sock.recv(4)
                if not size_data:
                    break
                size = int.from_bytes(size_data, 'big')
                data = b''
                while len(data) < size:
                    packet = self.sock.recv(size - len(data))
                    if not packet:
                        return
                    data += packet
                pixmap = QPixmap()
                pixmap.loadFromData(data, 'JPEG')
                self.screenshot_received.emit(pixmap)
            except:
                break

    def stop(self):
        self.running = False
        self.sock.close()

class Client(QMainWindow):
    def __init__(self):
        super().__init__()
        self.main_icon = QIcon(dir_path + r"/icons/icon.png")
        self.setWindowTitle("CASCAD RDP")
        self.setWindowIcon(self.main_icon)

        self.use_relay = False  
        self.relay_host = "127.0.0.1"  
        self.relay_port = 5050

        self.bar = QToolBar()
        self.bar.setIconSize(QSize(32, 32))
        self.addToolBar(self.bar)

        self.screen_label = QLabel()
        self.screen_label.setScaledContents(True)
        self.screen_label.setMouseTracking(True)
        self.setCentralWidget(self.screen_label)

        self.connect_btn = QAction(QIcon(dir_path + r"/icons/connect.png"), "Подключиться", self)
        self.connect_btn.triggered.connect(self.show_connect_win)
        self.bar.addAction(self.connect_btn)

        self.ipinfo_btn = QAction(QIcon(dir_path + r"/icons/ip.png"), "IP информация", self)
        self.ipinfo_btn.triggered.connect(self.show_ipinfo_win)
        self.bar.addAction(self.ipinfo_btn)

        self.ss_btn = QAction(QIcon(dir_path + r"/icons/screenshot.png"), "Скриншот", self)
        self.ss_btn.triggered.connect(self.save_screenshot)
        self.bar.addAction(self.ss_btn)

        self.cam_btn = QAction(QIcon(dir_path + r"/icons/webcam.png"), "Вебкамера", self)
        self.cam_btn.triggered.connect(self.show_webcam_win)
        self.bar.addAction(self.cam_btn)

        self.mic_btn = QAction(QIcon(dir_path + r"/icons/microphone.png"), "Микрофон", self)
        self.mic_btn.triggered.connect(self.show_microphone_win)
        self.bar.addAction(self.mic_btn)

        self.msgbox_btn = QAction(QIcon(dir_path + r"/icons/msgbox.png"), "Диалоговое окно", self)
        self.msgbox_btn.triggered.connect(self.show_msgbox_win)
        self.bar.addAction(self.msgbox_btn)

        self.bar.addSeparator()

        self.shutdown_btn = QAction(QIcon(dir_path + r"/icons/shutdown.png"), "Выключить сервер", self)
        self.shutdown_btn.triggered.connect(self.send_shutdown)
        self.bar.addAction(self.shutdown_btn)
        
        self.reboot_btn = QAction(QIcon(dir_path + r"/icons/reboot.png"), "Перезагрузить сервер", self)
        self.reboot_btn.triggered.connect(self.send_reboot)
        self.bar.addAction(self.reboot_btn)

        self.sleep_btn = QAction(QIcon(dir_path + r"/icons/sleep.png"), "Спящий режим", self)
        self.sleep_btn.triggered.connect(self.send_sleep)
        self.bar.addAction(self.sleep_btn)

        self.bar.addSeparator()

        self.relay_toggle = QAction("Исп. Relay", self)
        self.relay_toggle.setCheckable(True)
        self.relay_toggle.toggled.connect(self.toggle_relay_mode)
        self.bar.addAction(self.relay_toggle)

    def send_event(self, event_dict):
        try:
            msg = json.dumps(event_dict).encode('utf-8')
            length = struct.pack(">I", len(msg))
            self.sock.sendall(length + msg)
        except:
            pass

    def map_coords(self, event):
        pixmap_size = self.screen_label.pixmap().size()
        label_size = self.screen_label.size()
        x_ratio = pixmap_size.width() / label_size.width()
        y_ratio = pixmap_size.height() / label_size.height()
        x = int(event.position().x() * x_ratio)
        y = int(event.position().y() * y_ratio)
        return x, y

    def mousePressEvent(self, event):
        if event.button() in (Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton):
            x, y = self.map_coords(event)
            self.dragging = True
            self.send_event({
                "type": "mousedown",
                "x": x,
                "y": y,
                "button": "left" if event.button() == Qt.MouseButton.LeftButton else "right"
            })

    def mouseMoveEvent(self, event):
        if self.dragging:
            x, y = self.map_coords(event)
            self.send_event({
                "type": "mousemove",
                "x": x,
                "y": y
            })

    def mouseReleaseEvent(self, event):
        if event.button() in (Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton):
            x, y = self.map_coords(event)
            self.dragging = False
            self.send_event({
                "type": "mouseup",
                "x": x,
                "y": y,
                "button": "left" if event.button() == Qt.MouseButton.LeftButton else "right"
            })

    def mouseDoubleClickEvent(self, event):
        x, y = self.map_coords(event)
        self.send_event({
            "type": "double_click",
            "x": x,
            "y": y,
            "button": "left"
        })

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        self.send_event({
            "type": "scroll",
            "amount": delta
        })

    def keyPressEvent(self, event):
        text = event.text()
        if text:
            self.send_event({
                "type": "keypress",
                "key": text
            })

    def closeEvent(self, event):
        if self.receiver:
            self.receiver.stop()
        event.accept()
    
    def toggle_relay_mode(self, checked):
        self.use_relay = checked

    def show_connect_win(self):
        if self.use_relay:
            self.connect_to_relay()
        else:
            self.connect_win = ConnectWindow()
            self.connect_win.connected_signal.connect(self.on_connected)
            self.connect_win.show()
    
    def connect_to_relay(self):
        try:
            sock = socket.socket()
            sock.connect((self.relay_host, self.relay_port))
            self.on_connected(sock)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось подключиться к relay: {e}")

    def on_connected(self, sock):
            self.sock = sock
            self.server_ip = sock.getpeername()[0] if not self.use_relay else "Relay"
            self.receiver = ScreenshotReceiver(sock)
            self.receiver.screenshot_received.connect(self.screen_label.setPixmap)
            self.receiver.start()

    def show_ipinfo_win(self):
        try:
            self.ipinfo_win = IPInfoWindow(host=self.server_ip)
            self.ipinfo_win.show()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Невозможно открыть окно IP: {e}")

    def show_webcam_win(self):
        if not self.server_ip:
            QMessageBox(QMessageBox.Icon.Warning, "Нет подключения", "Сначала подключитесь к серверу!", QMessageBox.StandardButton.Ok, self).exec()
            return
        self.webcam_win = WebcamWindow(ip=self.server_ip)
        self.webcam_win.show()

    def show_microphone_win(self):
        if not self.server_ip:
            QMessageBox(QMessageBox.Icon.Warning, "Нет подключения", "Сначала подключитесь к серверу!", QMessageBox.StandardButton.Ok, self).exec()
            return
        self.mic_win = MicrophoneWindow(ip=self.server_ip)
        self.mic_win.show()

    def show_msgbox_win(self):
       if not self.sock:
            QMessageBox(QMessageBox.Icon.Warning, "Нет подключения", "Сначала подключитесь к серверу!", QMessageBox.StandardButton.Ok, self).exec()
            return
       self.msgbox_win = MsgBoxWindow()
       self.msgbox_win.send_signal.connect(self.send_msgbox_data)
       self.msgbox_win.show()

    def send_msgbox_data(self, data):
        try:
            msg = json.dumps(data).encode("utf-8")
            length = struct.pack(">I", len(msg))
            self.sock.sendall(length + msg)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось отправить сообщение: {e}")
    
    
    def send_shutdown(self):
        if not self.sock:
            QMessageBox(QMessageBox.Icon.Warning, "Нет подключения", "Сначала подключитесь к серверу!", QMessageBox.StandardButton.Ok, self).exec()
            return
        else:
            self.msgbox = QMessageBox(self)
            self.msgbox.setIcon(QMessageBox.Icon.Question)
            self.msgbox.setText("Вы уверены, что хотите выключить сервер?")
            self.msgbox.setWindowIcon(QIcon(dir_path + r"/icons/shutdown.png"))
            self.msgbox.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            self.msgbox.exec()
            if self.msgbox.StandardButton == QMessageBox.StandardButton.Yes:
                try:
                    msg = json.dumps({"type": "shutdown"}).encode("utf-8")
                    length = struct.pack(">I", len(msg))
                    self.sock.sendall(length + msg)
                    QMessageBox.information(self, "Сервер", "Команда выключения отправлена.")
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Не удалось отправить команду: {e}")
            else:
                self.msgbox.close()
    
    def send_reboot(self):
        if not self.sock:
            QMessageBox(QMessageBox.Icon.Warning, "Нет подключения", "Сначала подключитесь к серверу!", QMessageBox.StandardButton.Ok, self).exec()
            return
        else:
            self.msgbox = QMessageBox(self)
            self.msgbox.setIcon(QMessageBox.Icon.Question)
            self.msgbox.setText("Вы уверены, что хотите перезагрузить сервер?")
            self.msgbox.setWindowIcon(QIcon(dir_path + r"/icons/reboot.png"))
            self.msgbox.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            self.msgbox.exec()
            if self.msgbox.StandardButton == QMessageBox.StandardButton.Yes:
                try:
                    msg = json.dumps({"type": "reboot"}).encode("utf-8")
                    length = struct.pack(">I", len(msg))
                    self.sock.sendall(length + msg)
                    QMessageBox.information(self, "Сервер", "Команда перезагрузки отправлена.")
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Не удалось отправить команду: {e}")
            else:
                self.msgbox.close()

    def send_sleep(self):
        if not self.sock:
            QMessageBox(QMessageBox.Icon.Warning, "Нет подключения", "Сначала подключитесь к серверу!", QMessageBox.StandardButton.Ok, self).exec()
            return
        else:
            self.msgbox = QMessageBox(self)
            self.msgbox.setIcon(QMessageBox.Icon.Question)
            self.msgbox.setText("Вы уверены, что хотите отправить сервер в спящий режим?")
            self.msgbox.setWindowIcon(QIcon(dir_path + r"/icons/reboot.png"))
            self.msgbox.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            self.msgbox.exec()
            if self.msgbox.StandardButton == QMessageBox.StandardButton.Yes:
                try:
                    msg = json.dumps({"type": "sleep"}).encode("utf-8")
                    length = struct.pack(">I", len(msg))
                    self.sock.sendall(length + msg)
                    QMessageBox.information(self, "Сервер", "Команда спящего режима отправлена.")
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Не удалось отправить команду: {e}")
            else:
                self.msgbox.close()


    def save_screenshot(self):
        if not self.screen_label.pixmap():
            QMessageBox.warning(self, "Нет изображения", "Сначала подключитесь к серверу.")
            return
        filename = f"screenshot_{QDateTime.currentDateTime().toString('yyyyMMdd_HHmmss')}.jpg"
        path = os.path.join(dir_path + r"/screenshots/", filename)
        self.screen_label.pixmap().save(path, "JPG")
        QMessageBox.information(self, "Скриншот", f"Сохранено как: {filename}")

    def closeEvent(self, event):
        if self.receiver:
            self.receiver.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(style.cascad_style())
    window = Client()
    window.showMaximized()
    app.exec()
