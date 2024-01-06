import os
from pathlib import Path
import cv2 as cv

import pytesseract
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel
from PyQt5.QtCore import Qt

from utils import find_available_filename, image2pixelmap

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


class OCRWidget(QWidget):
    def __init__(self, img, close_window_command):
        super().__init__()
        self.close_window_command = close_window_command

        self.img = img
        self.lines = []

        self.text_edit = QTextEdit()
        self.image_label = QLabel(alignment=Qt.AlignCenter)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_extracted_text)

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

        extracted_text = pytesseract.image_to_string(img)
        self.lines = extracted_text.split("\n")

        data = pytesseract.image_to_data(
            img, output_type=pytesseract.Output.DICT)

        for i in range(len(data["text"])):
            x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
            # Filter out low-confidence and empty detections
            if int(data["conf"][i]) >= 0 and data["text"][i].replace(" ", "") != "":
                cv.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 1)

        self.text_edit.setPlainText(extracted_text)
        self.image_label.setPixmap(image2pixelmap(img))

    def save_extracted_text(self):
        download_path = Path.home() / "Downloads"
        file_path = os.path.join(download_path, "ocr_text")

        file_path = find_available_filename(file_path)

        with open(file_path, "w") as file:
            for item in self.lines:
                file.write("%s\n" % item)

        self.close_window_command()
