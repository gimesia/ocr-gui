import os
from pathlib import Path
import cv2 as cv
import pytesseract

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel
from PyQt5.QtCore import Qt

from utils import find_available_filename, image2pixelmap
from config import tesseract_path, tesseract_config, save_path

# Setting the tesseract path
pytesseract.pytesseract.tesseract_cmd = tesseract_path


class OCRWidget(QWidget):
    """Widget that performs the carachter recognition and the saving of the results
    """

    def __init__(self, img, close_window_command):
        super().__init__()
        self.close_window_command = close_window_command

        self.img = (img)
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
        """Charachter recognition and displaying of results
        """
        img = self.img.copy()
        
        # extract text
        extracted_text = pytesseract.image_to_string(
            img, config=tesseract_config) 
        self.lines = extracted_text.split("\n")

        # extract text data
        data = pytesseract.image_to_data(
            img, output_type=pytesseract.Output.DICT, config=tesseract_config)

        # draw text bboxes
        for i in range(len(data["text"])):
            x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
            # Filter out low-confidence and empty detections
            if int(data["conf"][i]) >= 0 and data["text"][i].replace(" ", "") != "":
                cv.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 1)

        # show results 
        self.text_edit.setPlainText(extracted_text)
        self.image_label.setPixmap(image2pixelmap(img))

    def save_extracted_text(self):
        """Saving of results and closing of the window
        """
        path = save_path
        file_path = os.path.join(path, "ocr_text")

        file_path = find_available_filename(file_path)

        with open(file_path, "w") as file:
            text = self.text_edit.toPlainText()
            file.writelines(text)

        self.close_window_command()
