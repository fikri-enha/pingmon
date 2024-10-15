import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QSystemTrayIcon,
    QMenu,
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon, QPixmap
from ping3 import ping
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class PingMonitor(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Ping Monitor")
        self.setGeometry(300, 300, 250, 150)

        layout = QVBoxLayout()

        self.status_label = QLabel("Monitoring...", self)
        self.ping_label = QLabel("Ping N/A", self)

        layout.addWidget(self.status_label)
        layout.addWidget(self.ping_label)

        self.setLayout(layout)

        # tray icon
        self.tray_icon = QSystemTrayIcon(self)
        self.update_tray_icon("N/A", None)

        # tray menu
        tray_menu = QMenu()
        show_action = tray_menu.addAction("Show")
        quit_action = tray_menu.addAction("Exit")

        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(app.quit)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        # timer pinging
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_ping)
        self.timer.start(1500)

    def update_ping(self):
        try:
            ping_time = ping("google.com")
            print(ping_time)
            if ping_time is not None:
                ping_ms = int(ping_time * 1000)
                ping_str = f"{ping_ms:.0f}"
                print(ping_str)
                self.ping_label.setText(f"Ping: {ping_str} ms")
                color = self.get_color_for_ping(ping_ms)
                self.update_tray_icon(ping_str, ping_ms)
            else:
                self.ping_label.setText("Ping: Timeout")
                self.update_tray_icon("TO", None)
        except Exception as e:
            self.ping_label.setText(f"Error: {str(e)}")
            self.update_tray_icon("ERR", None)

    def get_color_for_ping(self, ping_ms):
        if ping_ms is None:
            return "gray"
        elif ping_ms <= 80:
            return "green"
        elif 81 <= ping_ms <= 110:
            return "yellow"
        else:
            return "red"

    def update_tray_icon(self, text, ping_ms):
        # create a new image with a black background
        img = Image.new("RGBA", (64, 64), color=(0, 0, 0, 0))
        d = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except IOError:
            font = ImageFont.load_default()

        # Determine text color based on ping value
        text_color = self.get_color_for_ping(ping_ms)

        d.text((32, 32), text, fill=text_color, font=font, anchor="mm", stroke_width=1)

        # convert image to a QIcon
        buffer = BytesIO()
        img.save(buffer, "PNG")
        qp = QPixmap()
        qp.loadFromData(buffer.getvalue())
        icon = QIcon(qp)

        # set the icon
        self.tray_icon.setIcon(icon)

    def closeEvent(self, e):
        e.ignore()
        self.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = PingMonitor()
    sys.exit(app.exec_())
