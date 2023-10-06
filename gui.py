import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QGridLayout, QPushButton
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer


class WebcamWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.video_capture = cv2.VideoCapture(0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(10)  # Update frame every 10 milliseconds
        self.init_ui()
        self.analyzed_img = None

    def capture_frame(self):
        _, self.analyzed_img = self.video_capture.read()

    def init_ui(self):
        layout = QGridLayout()  # Use QGridLayout to create a 2x2 grid layout

        # Add camera feed labels to the first column
        self.label_normal = QLabel(self)
        self.label_threshold = QLabel(self)
        # Add normal feed to the top cell of the first column
        layout.addWidget(self.label_normal, 0, 0)
        # Add thresholded feed to the bottom cell of the first column
        layout.addWidget(self.label_threshold, 1, 0)

        # Add buttons to the second column
        button1 = QPushButton("Capture Frame", self)
        button1.clicked.connect(self.capture_frame)

        button2 = QPushButton("Analyze", self)

        button3 = QPushButton("Button 3", self)

        button4 = QPushButton("Button 4", self)

        # Create a sub-layout (e.g., QVBoxLayout) for the grid cell
        sub_layout1 = QVBoxLayout()
        sub_layout1.addWidget(button1)
        sub_layout1.addWidget(button2)

        sub_layout2 = QVBoxLayout()
        sub_layout2.addWidget(button3)
        sub_layout2.addWidget(button4)

        # Add button3 to the top cell of the third row in the second column
        layout.addLayout(sub_layout1, 0, 1)
        # Add button4 to the bottom cell of the fourth row in the second column
        layout.addLayout(sub_layout2, 1, 1)

        self.setLayout(layout)
        self.setWindowTitle("Webcam Widget")
        self.setGeometry(100, 100, 640, 480)
        self.show()

    def update_frame(self):
        ret, frame = self.video_capture.read()
        if ret:
            # Convert frame to grayscale for adaptive thresholding (example processing step)
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Apply adaptive thresholding (example processing step)
            threshold_frame = cv2.adaptiveThreshold(gray_frame, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                                    cv2.THRESH_BINARY, 11, 2)

            # Convert frames to appropriate format for displaying in QLabel
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            threshold_frame = cv2.cvtColor(threshold_frame, cv2.COLOR_GRAY2RGB)
            if self.analyzed_img is not None:
                threshold_frame = self.analyzed_img

            # Convert frames to QImage
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            image = QImage(frame.data, width, height,
                           bytes_per_line, QImage.Format_RGB888)
            threshold_image = QImage(
                threshold_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)

            # Convert QImage to QPixmap for displaying in QLabel
            pixmap = QPixmap.fromImage(image)
            threshold_pixmap = QPixmap.fromImage(threshold_image)

            # Set the QPixmap to the QLabel widgets
            self.label_normal.setPixmap(pixmap)
            self.label_threshold.setPixmap(threshold_pixmap)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WebcamWidget()
    sys.exit(app.exec_())
