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

        # Use pytesseract to extract text from the image
        extracted_text = pytesseract.image_to_string(img, lang='eng')

        # Split extracted text into lines
        lines = extracted_text.split('\n')

        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        custom_config = r'--oem 3 --psm 6'
        custom_config = r'--oem 3 --psm 6'
        data = pytesseract.image_to_data(
            img, output_type=pytesseract.Output.DICT)

        # Draw bounding boxes around detected text regions
        for i in range(len(data['text'])):
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            # if int(data['conf'][i]) > 0:  # Filter out low-confidence detections
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 1)

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
    window = ImageWindow('img.jpg')  # Replace with your image path
    window.setGeometry(100, 100, 1000, 600)
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
