import numpy as np
import cv2 as cv

import pytesseract
from pytesseract import Output
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel
from PyQt5.QtCore import Qt

from utils import convert_cv_to_qt, image2pixelmap

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class OCR(QWidget):
    def __init__(self, img):
        super().__init__()
        self.img = img
        self.lines = []

        self.text_edit = QTextEdit()
        self.image_label = QLabel(alignment=Qt.AlignCenter)

        save_btn = QPushButton("Save")
        self.analyze_img()

        layout = QHBoxLayout()
        sublayout = QVBoxLayout()

        sublayout.addWidget(self.text_edit)
        sublayout.addWidget(save_btn)

        layout.addWidget(self.image_label)
        layout.addLayout(sublayout)

        self.setLayout(layout)

        self.analyze_img()

    def analyze_img(self):
        img = self.img.copy()
        # gray_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        # _, thresholded = cv.threshold(
        #     gray_img, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)

        extracted_text = pytesseract.image_to_string(img)
        self.lines = extracted_text.split('\n')

        data = pytesseract.image_to_data(
            img, output_type=pytesseract.Output.DICT)

        for i in range(len(data['text'])):
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            # if int(data['conf'][i]) > 0:  # Filter out low-confidence detections
            cv.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 1)

        self.text_edit.setPlainText(extracted_text)
        self.image_label.setPixmap(convert_cv_to_qt(img))
