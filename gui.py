import logging
import sys
import os
import cv2
import numpy as np
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QWidget, QLabel, QMessageBox, QHBoxLayout, QVBoxLayout, QGridLayout, QPushButton
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.webcam_widget = WebcamWidget(self.open_new_window)
        self.init_ui()
        self.show()

    def init_ui(self):
        self.setGeometry(100, 100, 640, 480)
        self.setWindowTitle('Main Window')

        self.setCentralWidget(self.webcam_widget)

    def open_new_window(self):
        self.setEnabled(False)  # Disable main window
        self.new_window = AnlalyzerWindow(self)
        self.new_window.show()

        # Re-enable main window when the new window is closed
        self.new_window.installEventFilter(self)

    def eventFilter(self, source, event):
        if event.type() == event.Close:
            # Enable main window when the new window is closed
            self.setEnabled(True)
            return False
        return super().eventFilter(source, event)


class WebcamWidget(QWidget):
    def __init__(self, open_analyzer):
        super().__init__()
        self.open_analyzer = open_analyzer

        self.video_capture = cv2.VideoCapture(0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(10)  # Update frame every 10 milliseconds
        self.init_ui()
        self.analyzed_img = None
        self.uploaded_img = False

    def capture_frame(self):
        self.uploaded_img = False
        _, self.analyzed_img = self.video_capture.read()

    def upload_file_dialog(self):
        try:
            fname = QFileDialog.getOpenFileName(
                self, 'Open File', '/')
            path, extension = os.path.splitext(str(fname[0]))
            self.analyzed_img = cv2.imread(fname[0])

        except Exception as e:
            print('Something went wrong')
            print(e)

        finally:
            # fname is a tuple where the first element is the file path
            print(f'Selected file: {fname[0]}')
            self.uploaded_img = True

    def init_ui(self):
        # Use QGridLayout to create a 2x2 grid layout
        layout = QGridLayout()

        # Add camera feed labels to the first column
        self.label_normal = QLabel(self)
        self.label_threshold = QLabel(self)
        self.label_masked = QLabel(self)

        # Add buttons to the second column
        # BTN1
        button1 = QPushButton("Capture Frame", self)
        button1.clicked.connect(self.capture_frame)
        # BTN2
        button2 = QPushButton("Upload Image", self)
        button2.clicked.connect(self.upload_file_dialog)
        # BTN3
        button3 = QPushButton("Analyze", self)
        button3.clicked.connect(self.open_analyzer)

        # Create a sub-layout (e.g., QVBoxLayout) for the grid cell
        btn_layout = QVBoxLayout()
        sub_layout1 = QHBoxLayout()
        sub_layout2 = QHBoxLayout()

        sub_layout1.addWidget(button1)
        sub_layout1.addWidget(button2)
        sub_layout2.addWidget(button3)

        # Add normal feed to the top cell of the first column
        layout.addWidget(self.label_normal, 0, 0)
        # Add thresholded feed to the bottom cell of the first column
        layout.addWidget(self.label_threshold, 1, 0)
        layout.addWidget(self.label_masked, 1, 1)

        btn_layout.addLayout(sub_layout1)
        btn_layout.addLayout(sub_layout2)

        # Add buttons to the top-right cell
        layout.addLayout(btn_layout, 0, 1)

        self.setLayout(layout)
        self.setWindowTitle("Webcam Widget")
        self.setGeometry(100, 100, 640, 480)
        self.show()

    def update_frame(self):
        ret, frame = self.video_capture.read()
        if ret:
            # Topleft
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            image = QImage(frame.data, width, height,
                           bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(image)
            self.label_normal.setPixmap(pixmap)

            # Convert frame to grayscale for adaptive thresholding (example processing step)
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            threshold_frame = gray_frame

            # Apply adaptive thresholding (example processing step)
            # cv2.adaptiveThreshold(gray_frame, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)

            # Convert frames to appropriate format for displaying in QLabel
            threshold_frame = cv2.cvtColor(threshold_frame, cv2.COLOR_GRAY2RGB)
            mask_frame = cv2.cvtColor(threshold_frame, cv2.COLOR_RGB2BGR)

            if self.analyzed_img is not None:
                if self.analyzed_img.shape != frame.shape:
                    self.analyzed_img = cv2.resize(
                        self.analyzed_img, (frame.shape[1], frame.shape[0]), cv2.INTER_AREA)

                threshold_frame = cv2.cvtColor(
                    self.analyzed_img, cv2.COLOR_BGR2RGB)
                # mask_white_objects(self.analyzed_img)
                mask_frame = self.analyzed_img

            # Convert frames to QImage
            threshold_image = QImage(
                threshold_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            mask_image = QImage(
                mask_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)

            # Convert QImage to QPixmap for displaying in QLabel
            threshold_pixmap = QPixmap.fromImage(threshold_image)
            masked_pixmap = QPixmap.fromImage(mask_image)

            # Set the QPixmap to the QLabel widgets
            self.label_threshold.setPixmap(threshold_pixmap)
            self.label_masked.setPixmap(masked_pixmap)

            if self.uploaded_img:
                pass


class AnlalyzerWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setGeometry(200, 200, 400, 300)
        self.setWindowTitle('New Window')

    def set_image(self, img: np.ndarray):
        self.__img = img


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
