import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QGridLayout, QPushButton
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer


def mask_white_objects(image):
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Threshold the grayscale image to create a binary mask for white objects
    _, thresholded = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

    # Find contours in the binary mask
    contours, _ = cv2.findContours(
        thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Create an empty mask
    mask = np.zeros_like(image)

    # Draw white contours on the mask
    # cv2.drawContours(mask, contours, -1, (255, 255, 255), thickness=cv2.FILLED)

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(mask, (x, y), (x+w, y+h),
                      (255, 255, 255), thickness=cv2.FILLED)

    # Bitwise AND the original image with the mask to mask out white objects
    masked_image = cv2.bitwise_and(image, mask)

    return masked_image


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
        self.label_masked = QLabel(self)
        # Add normal feed to the top cell of the first column
        layout.addWidget(self.label_normal, 0, 0)
        # Add thresholded feed to the bottom cell of the first column
        layout.addWidget(self.label_threshold, 1, 0)
        layout.addWidget(self.label_masked, 1, 1)

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
        # layout.addLayout(sub_layout2, 1, 1)

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
            mask_frame = cv2.cvtColor(threshold_frame, cv2.COLOR_RGB2BGR)
            if self.analyzed_img is not None:
                threshold_frame = cv2.cvtColor(
                    self.analyzed_img, cv2.COLOR_BGR2RGB)
                mask_frame = mask_white_objects(self.analyzed_img)

            # Convert frames to QImage
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            image = QImage(frame.data, width, height,
                           bytes_per_line, QImage.Format_RGB888)
            threshold_image = QImage(
                threshold_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            mask_image = QImage(
                mask_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)

            # Convert QImage to QPixmap for displaying in QLabel
            pixmap = QPixmap.fromImage(image)
            threshold_pixmap = QPixmap.fromImage(threshold_image)
            masked_pixmap = QPixmap.fromImage(mask_image)

            # Set the QPixmap to the QLabel widgets
            self.label_normal.setPixmap(pixmap)
            self.label_threshold.setPixmap(threshold_pixmap)
            self.label_masked.setPixmap(masked_pixmap)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WebcamWidget()
    sys.exit(app.exec_())
