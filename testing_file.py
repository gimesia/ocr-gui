import cv2
import pytesseract
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QTextEdit, QHBoxLayout
from PyQt5.QtGui import QPixmap, QImage, QPainter, QFont
from PyQt5.QtCore import Qt

# Path to Tesseract executable (change this based on your installation)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class ImageWindow(QMainWindow):
    def __init__(self, image_path):
        super().__init__()

        self.image_path = image_path
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Text Extraction with PyQt")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QHBoxLayout()

        # Widget to display the image with bounding boxes
        self.image_label = QLabel(alignment=Qt.AlignCenter)
        layout.addWidget(self.image_label)

        # Widget to display and edit extracted text
        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)

        self.centralWidget().setLayout(layout)

        # Read the image using OpenCV
        img = cv2.imread(self.image_path)

        # Convert the image to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Use pytesseract to extract text from the image
        extracted_text = pytesseract.image_to_string(gray)

        # Get information about bounding boxes and confidences
        boxes = pytesseract.image_to_boxes(gray)
        print(boxes)
        # Draw bounding boxes on the image
        for b in boxes.splitlines():
            b = b.split()
            x, y, w, h = int(b[1]), int(b[2]), int(b[3]), int(b[4])
            cv2.rectangle(
                img, (x, img.shape[0] - y), (w, img.shape[0] - h), (0, 255, 0), 1)

        # Display extracted text in the QTextEdit widget
        self.text_edit.setPlainText(extracted_text)

        # Convert image to display in PyQt
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = img_rgb.shape
        bytes_per_line = ch * w
        q_img = QImage(img_rgb.data, w, h, bytes_per_line,
                       QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)

        self.image_label.setPixmap(pixmap)


def main():
    app = QApplication(sys.argv)
    window = ImageWindow('billimg3.jpg')  # Replace with your image path
    window.setGeometry(100, 100, 1000, 600)
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
