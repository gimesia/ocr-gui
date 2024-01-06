import sys

import numpy as np
import cv2 as cv

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMainWindow, QTextEdit
from widgets.BBoxEditorWidget import *
from widgets.CutImagePreviewWidget import *
from widgets.OCRWidget import *

from utils import cut_straight_bbox_img


class AnalyzerWindow(QMainWindow):
    def __init__(self, img):
        super().__init__()
        self.setWindowTitle("Extract text")

        self.img = img
        self.cut_img = None
        self.cip_widget = None

        self.bbox_editor = BBoxEditorWidget(self.img)

        self.control_button = QPushButton("Cut", self)
        self.control_button.clicked.connect(self.perform_cut_image)

        self.central_widget = QWidget()

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.bbox_editor)
        self.layout.addWidget(self.control_button)

        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        self.showMaximized()

    def set_image(self, img: np.ndarray):
        self.img = img

    def perform_cut_image(self):
        mask = self.bbox_editor.bbox.create_mask(self.img.shape).astype(bool)

        self.cut_img = self.img * mask

        rotation = self.bbox_editor.bbox.get_rotation_angle(self.img.shape)

        self.cut_img = cut_straight_bbox_img(
            self.cut_img, self.bbox_editor.bbox)

        widget = QWidget()
        cip_widget = CutImagePreviewWidget(self.cut_img)
        self.cip_widget = cip_widget
        btn = QPushButton("OCR!", self)
        btn.clicked.connect(self.perform_ocr)

        layout = QVBoxLayout()
        layout.addWidget(cip_widget)
        layout.addWidget(btn)

        widget.setLayout(layout)

        self.central_widget = widget
        self.setCentralWidget(self.central_widget)

    def perform_ocr(self):
        if self.cip_widget is None or self.cip_widget.img is None:
            return

        ocr_widget = OCRWidget(self.cip_widget.img, self.close_window)
        self.central_widget = ocr_widget
        self.setCentralWidget(self.central_widget)

    def close_window(self):
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AnalyzerWindow(cv.imread("img.jpg"))
    sys.exit(app.exec_())
