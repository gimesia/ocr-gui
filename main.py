import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget


class NewWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setGeometry(200, 200, 400, 300)
        self.setWindowTitle('New Window')


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setGeometry(100, 100, 400, 300)
        self.setWindowTitle('Main Window')

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.open_new_window_btn = QPushButton('Open New Window', self)
        self.open_new_window_btn.clicked.connect(self.open_new_window)

        self.label = QLabel("This is a label in the main window")

        self.layout.addWidget(self.open_new_window_btn)
        self.layout.addWidget(self.label)

    def open_new_window(self):
        self.setEnabled(False)  # Disable main window
        self.new_window = NewWindow(self)
        self.new_window.show()

        # Re-enable main window when the new window is closed
        self.new_window.installEventFilter(self)

    def eventFilter(self, source, event):
        if event.type() == event.Close:
            # Enable main window when the new window is closed
            self.setEnabled(True)
            return False
        return super().eventFilter(source, event)


def run_app():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run_app()
