import os
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

dir_path = os.path.dirname(os.path.abspath(__file__))

class MsgBoxWindow(QMainWindow):
    send_signal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Диалоговое окно")
        self.setWindowIcon(QIcon(dir_path + "/icons/msgbox.png"))
        self.setFixedSize(300, 300)

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout()
        central.setLayout(layout)

        layout.addWidget(QLabel("Заголовок:"))
        self.title_edit = QLineEdit()
        layout.addWidget(self.title_edit)

        layout.addWidget(QLabel("Сообщение:"))
        self.message_edit = QLineEdit()
        layout.addWidget(self.message_edit)

        layout.addWidget(QLabel("Тип сообщения:"))
        self.radio_group = QButtonGroup(self)

        self.error_radio = QRadioButton("Ошибка")
        self.warning_radio = QRadioButton("Предупреждение")
        self.question_radio = QRadioButton("Вопрос (Да/Нет)")
        self.info_radio = QRadioButton("Информация")
        self.info_radio.setChecked(True)

        for i, radio in enumerate([self.error_radio, self.warning_radio, self.question_radio, self.info_radio]):
            self.radio_group.addButton(radio, i)
            layout.addWidget(radio)

        button_layout = QHBoxLayout()
        self.send_btn = QPushButton("Отправить")
        self.send_btn.clicked.connect(self.send_msgbox)
        button_layout.addWidget(self.send_btn)
        layout.addLayout(button_layout)

    def send_msgbox(self):
        msg_type = self.radio_group.checkedId()
        msg_data = {
            "type": "msgbox",
            "title": self.title_edit.text(),
            "message": self.message_edit.text(),
            "msg_type": msg_type
        }
        self.send_signal.emit(msg_data)
        QMessageBox.information(self, "Отправлено", "Сообщение отправлено на сервер.")
        self.close()