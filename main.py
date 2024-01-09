import sys
import os
import cv2 as cv
import numpy as np
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton
from PyQt5.QtCore import QTimer, Qt
from AnalyserWindow import AnalyserWindow

from utils import image2pixelmap, scale_image_to_min_height


class MainWindow(QMainWindow):
    """Main GUI, handles the webcamera and upload dialog,
    AnalyserWindow is opened from here 
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window")

        self.webcam_widget = WebcamWidget(self.open_new_window)
        self.setCentralWidget(self.webcam_widget)

        self.showMaximized()

    def open_new_window(self):
        """Creates analyser window from captured or uploaded image
        """
        if self.webcam_widget.analysed_img is not None:
            self.new_window = AnalyserWindow(
                self.webcam_widget.analysed_img)  # Open analyzer window

            self.setEnabled(False)  # Disable main window

            # Re-enable main window when closed
            self.new_window.installEventFilter(self)
        else:
            print("Capture a frame or upload an image first!")

    def eventFilter(self, source, event):
        """Event filter for QMainWindow, disables MainWindow if Analyser is opened
        """
        if event.type() == event.Close:
            # Enable main window when the new window is closed
            self.setEnabled(True)
            return False
        return super().eventFilter(source, event)


class WebcamWidget(QWidget):
    """Widget handling webcamera feed and displaying

    Args:
        QWidget (_type_): _description_
    """

    def __init__(self, open_analyser_command):
        super().__init__()
        self.open_analyser = open_analyser_command

        self.analysed_img = None
        self.uploaded_img = False

        self.video_capture = cv.VideoCapture(0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(10)  # Update frame every 10 milliseconds

        self.init_ui()

    def init_ui(self):
        """Creation of widget layout
        """
        layout = QVBoxLayout()

        # Label for camera feed
        self.label_camera_feed = QLabel(self)
        self.label_camera_feed.setAlignment(Qt.AlignCenter)

        # Label for captured or uploaded image
        self.label_analysed_img = QLabel(self)
        self.label_analysed_img.setAlignment(Qt.AlignCenter)

        # Buttons
        # BTN1
        button1 = QPushButton("Capture Frame", self)
        button1.clicked.connect(self.capture_frame)
        # BTN2
        button2 = QPushButton("Upload Image", self)
        button2.clicked.connect(self.upload_file_dialog)
        # BTN3
        button3 = QPushButton("Analyse", self)
        button3.clicked.connect(self.open_analyser)

        btn_layout = QVBoxLayout()
        sub_layout1 = QHBoxLayout()
        sub_layout2 = QHBoxLayout()

        sub_layout1.addWidget(button1)
        sub_layout1.addWidget(button2)
        sub_layout2.addWidget(button3)

        frames_layout = QHBoxLayout()
        frames_layout.addWidget(self.label_camera_feed)
        frames_layout.addWidget(self.label_analysed_img)

        btn_layout.addLayout(sub_layout1)
        btn_layout.addLayout(sub_layout2)

        layout.addLayout(frames_layout)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def update_frame(self):
        """Updating the displayed image from webcamera feed
        """
        ret, frame = self.video_capture.read()
        frame = scale_image_to_min_height(frame)

        if ret:
            # set left-side image
            self.label_camera_feed.setPixmap(image2pixelmap(frame))
            capture_frame = frame.copy()

            if self.analysed_img is not None:
                if self.analysed_img.shape != frame.shape:
                    # Making sure that both images have the same dimensions
                    resized_analysed_img = cv.resize(
                        self.analysed_img, (frame.shape[1], frame.shape[0]), cv.INTER_AREA)

                    capture_frame = resized_analysed_img
                else:
                    capture_frame = self.analysed_img
            else:
                # Turnig the right image gray to indicate that capturing is needed
                capture_frame = cv.cvtColor(capture_frame, cv.COLOR_BGR2GRAY)
                capture_frame = cv.cvtColor(capture_frame, cv.COLOR_GRAY2RGB)

            # set right-side image
            self.label_analysed_img.setPixmap(image2pixelmap(capture_frame))

    def capture_frame(self):
        """Capturing of current frame and storing
        """
        self.uploaded_img = False
        _, analysed_img = self.video_capture.read()
        analysed_img = scale_image_to_min_height(analysed_img)
        self.analysed_img = analysed_img

    def upload_file_dialog(self):
        """Open file upload dialog and displaying the selected image
        """
        try:
            fname = QFileDialog.getOpenFileName(
                self, "Open File", "/")
            path, extension = os.path.splitext(str(fname[0]))
            im = cv.imread(fname[0])
            im = scale_image_to_min_height(im)
            self.analysed_img = im

        except Exception as e:
            print(f"Something went wrong\n{e}")

        finally:
            print(f"Selected file: {fname[0]}")
            self.uploaded_img = True


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
