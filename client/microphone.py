from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.QtCore import QTimer
import socket
import pyaudio

class MicrophoneWindow(QMainWindow):
    def __init__(self, ip="127.0.0.1", port=9996):
        super().__init__()
        self.setWindowTitle("Микрофон")
        self.setGeometry(100, 100, 300, 100)

        try:
            self.sock = socket.socket()
            self.sock.connect((ip, port))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Микрофон: {e}")
            self.close()
            return

        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=pyaudio.paInt16,
                                      channels=1,
                                      rate=44100,
                                      output=True,
                                      frames_per_buffer=1024)

        self.timer = QTimer()
        self.timer.timeout.connect(self.receive_audio)
        self.timer.start(30)

    def receive_audio(self):
        try:
            data = self.sock.recv(4096)
            self.stream.write(data)
        except:
            pass

    def closeEvent(self, event):
        self.timer.stop()
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
        self.sock.close()
        event.accept()