import numpy as np
import cv2 as cv
from PyQt5.QtWidgets import QMainWindow, QWidget


class AnalyzerWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.img = None
        bbox = None

        self.setGeometry(200, 200, 400, 300)
        self.setWindowTitle('Extract text')
        self.showMaximized()

    def set_image(self, img: np.ndarray):
        self.img = img


class BBoxEditorWidget(QWidget):
    def __init__(self, ):
        pass


class BBox():
    def __init__(self, tl, tr, bl, br):
        self.topleft = tl
        self.topright = tr
        self.bottomleft = bl
        self.bottomright = br

    def points(self):
        return [self.topleft, self.topright, self.bottomleft, self.bottomright]
