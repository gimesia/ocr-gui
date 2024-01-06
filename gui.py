import sys
import os
import cv2 as cv
import numpy as np
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QWidget, QLabel, QMessageBox, QHBoxLayout, QVBoxLayout, QGridLayout, QPushButton
from PyQt5.QtCore import QTimer, Qt

from Analyzer import AnalyzerWindow
from utils import image2pixelmap, mask_white_objects, scale_image_to_min_height


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window")

        self.webcam_widget = WebcamWidget(self.open_new_window)
        self.setCentralWidget(self.webcam_widget)

        self.showMaximized()
        # self.show()

    def open_new_window(self):
        if self.webcam_widget.analyzed_img is not None:
            self.new_window = AnalyzerWindow(self.webcam_widget.analyzed_img)
            self.new_window.show()

            self.setEnabled(False)  # Disable main window
            # Re-enable main window when closed
            self.new_window.installEventFilter(self)
        else:
            print("Capture a frame or upload an image first!")

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

        self.analyzed_img = None
        self.uploaded_img = False

        self.video_capture = cv.VideoCapture(0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(10)  # Update frame every 10 milliseconds

        self.init_ui()

    def capture_frame(self):
        self.uploaded_img = False
        _, analyzed_img = self.video_capture.read()
        analyzed_img = scale_image_to_min_height(analyzed_img)
        self.analyzed_img = analyzed_img

    def upload_file_dialog(self):
        try:
            fname = QFileDialog.getOpenFileName(
                self, "Open File", "/")
            path, extension = os.path.splitext(str(fname[0]))
            im = cv.imread(fname[0])
            im = scale_image_to_min_height(im)
            self.analyzed_img = im

        except Exception as e:
            print(f"Something went wrong\n{e}")

        finally:
            # fname is a tuple where the first element is the file path
            print(f"Selected file: {fname[0]}")
            self.uploaded_img = True

    def init_ui(self):
        layout = QVBoxLayout()

        # Add camera feed labels to the first column
        self.label_normal = QLabel(self)
        self.label_normal.setAlignment(Qt.AlignCenter)

        self.label_threshold = QLabel(self)
        self.label_threshold.setAlignment(Qt.AlignCenter)

        self.label_masked = QLabel(self)
        self.label_masked.setAlignment(Qt.AlignCenter)

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

        frames_layout = QHBoxLayout()
        frames_layout.addWidget(self.label_normal)
        frames_layout.addWidget(self.label_threshold)

        btn_layout.addLayout(sub_layout1)
        btn_layout.addLayout(sub_layout2)

        # Add buttons to the top-right cell
        layout.addLayout(frames_layout)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def update_frame(self):
        ret, frame = self.video_capture.read()
        frame = scale_image_to_min_height(frame)
        # Rescale the image
        # scale_factor = 1.75
        # frame = cv.resize(frame, None, fx=scale_factor,
        #                   fy=scale_factor, interpolation=cv.INTER_AREA)

        if ret:
            # Topleft
            frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            self.label_normal.setPixmap(image2pixelmap(frame))

            # Convert frame to grayscale for adaptive thresholding (example processing step)
            gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            threshold_frame = gray_frame

            # Convert frames to appropriate format for displaying in QLabel
            threshold_frame = cv.cvtColor(threshold_frame, cv.COLOR_GRAY2RGB)
            mask_frame = cv.cvtColor(threshold_frame, cv.COLOR_RGB2BGR)

            if self.analyzed_img is not None:
                if self.analyzed_img.shape != frame.shape:
                    resized_analyzed_img = cv.resize(
                        self.analyzed_img, (frame.shape[1], frame.shape[0]), cv.INTER_AREA)

                    threshold_frame = cv.cvtColor(
                        resized_analyzed_img, cv.COLOR_BGR2RGB)
                    mask_frame = resized_analyzed_img
                else:
                    threshold_frame = cv.cvtColor(
                        self.analyzed_img, cv.COLOR_BGR2RGB)
                    mask_frame = self.analyzed_img

            # Set the QPixmap to the QLabel widgets
            self.label_threshold.setPixmap(image2pixelmap(threshold_frame))
            self.label_masked.setPixmap(
                image2pixelmap(mask_white_objects(mask_frame)))

            if self.uploaded_img:
                pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
