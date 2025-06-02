def cascad_style():
    return """
QMainWindow {
    background-color: #f1f1f1;
}

QToolBar {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0.0  #d9efff,
        stop:0.08 #bde2ff,
        stop:0.2  #a4d4f7,
        stop:0.4  #91c9f0,
        stop:0.65 #7ab7e3,
        stop:0.85 #a5d1f5,
        stop:1.0  #d7edff
    );
    border-bottom: 1px solid #6fa5d2;
    padding: 5px;
    spacing: 4px;
}

QToolButton {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0   #fafdff,
        stop:0.4 #d0eaff,
        stop:0.6 #a7d4f5,
        stop:1.0 #93c6ef);
    border: 1px solid #6caee0;
    border-radius: 5px;
    padding: 2px 4px;
}

QToolButton:hover {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0   #ffffff,
        stop:0.3 #e5f4ff,
        stop:0.6 #bde3ff,
        stop:1.0 #99d0f7);
    border: 1px solid #55a0dd;
}

QToolButton:pressed {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0   #a1d7f5,
        stop:0.5 #7dc2eb,
        stop:1.0 #54a8e2);
    border: 1px solid #3a94c8;
}

QPushButton {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0.0 #ffffff,
        stop:0.2 #eaf6ff,
        stop:0.5 #cae7ff,
        stop:0.8 #b5ddff,
        stop:1.0 #9cd1f7);
    border: 1px solid #72b6ec;
    border-radius: 6px;
    padding: 6px 14px;
    color: #1a1a1a;
    font-weight: bold;
}

QPushButton:hover {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0.0 #ffffff,
        stop:0.3 #def0ff,
        stop:0.6 #bde3ff,
        stop:1.0 #a3d7fa);
    border: 1px solid #55a6e8;
}

QPushButton:pressed {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0   #a3d4f2,
        stop:0.5 #78bde5,
        stop:1.0 #53a3dc);
    border: 1px solid #368fc9;
}

QLineEdit {
    background-color: white;
    border: 1px solid #a0a0a0;
    padding: 4px;
    border-radius: 2px;
}

QMessageBox {
    background-color: #fdfdfd;
}

QLabel {
    color: #1a1a1a;
    font-size: 11pt;
}

QStatusBar {
    background: #e5e5e5;
    border-top: 1px solid #999;
}
"""