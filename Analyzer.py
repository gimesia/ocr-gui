import sys

import numpy as np
import cv2 as cv

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGraphicsView, QGraphicsScene, QPushButton, QMainWindow, QTextEdit, QLabel
from PyQt5.QtCore import Qt

from OCR import OCR
from utils import BBox, cut_straight_bbox_img, image2pixelmap, rotate_img


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

        ocr_widget = OCR(self.cip_widget.img)
        self.central_widget = ocr_widget
        self.setCentralWidget(self.central_widget)


class CutImagePreviewWidget(QWidget):
    def __init__(self, img):
        super().__init__()
        self.img = img
        h, w, ch = self.img.shape
        self.resize(w, h)

        self.layout = QVBoxLayout()
        btn_layout = QHBoxLayout()
        self.setLayout(self.layout)

        btn1 = QPushButton("Rotate left", self)
        btn1.clicked.connect(self.rotate_l)

        btn2 = QPushButton("Rotate right", self)
        btn2.clicked.connect(self.rotate_r)

        self.image_label = QLabel(alignment=Qt.AlignCenter)

        btn_layout.addWidget(btn1)
        btn_layout.addWidget(btn2)

        self.layout.addWidget(self.image_label)
        self.layout.addLayout(btn_layout)

        qt_image = image2pixelmap(self.img.copy())
        self.image_label.setPixmap(qt_image)

    def rotate(self, clockwise=True):
        rotated_img = rotate_img(self.img, -90 if clockwise else 90)
        self.img = rotated_img

        qt_image = image2pixelmap(rotated_img)
        self.image_label.setPixmap(qt_image)

    def rotate_l(self):
        self.rotate(False)

    def rotate_r(self):
        self.rotate(True)


class BBoxEditorWidget(QWidget):
    def __init__(self, img):
        super().__init__()
        self.img = img
        h, w, ch = self.img.shape

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.resize(w, h)

        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, w, h)

        self.view = QGraphicsView(self.scene)
        self.layout.addWidget(self.view)

        self.view.mousePressEvent = self.mouse_click_event

        self.bbox = BBox(
            (0, 0), (0, h), (w, 0), (w, h))

        self.bbox.shrink(100)

        self.refresh_img()

    def mouse_click_event(self, event):
        # Get the position of the click
        pos = event.pos()
        mapped_pos = self.view.mapToScene(pos)
        x = int(mapped_pos.x())
        y = int(mapped_pos.y())

        if self.bbox.edited_point_index is None:
            self.bbox.find_point_to_edit((x, y))
            self.refresh_img()
        else:
            self.bbox.change_point((x, y))
            mask = self.bbox.create_mask(self.img.shape)

            self.refresh_img(mask)

    def refresh_img(self, mask=None):
        img = self.img.copy()

        if mask is not None:
            alpha = 0.5
            beta = (1.0 - alpha)

            img = cv.addWeighted(
                img, alpha, mask.astype(np.uint8)*255, beta, 0.0)

        for i, point in enumerate(self.bbox.points()):
            rad = 4
            thickness = -1
            if i == self.bbox.edited_point_index:
                rad = 8
                thickness = 2
            cv.circle(img, point, rad, (0, 0, 255), thickness)

        # Convert the OpenCV image to QPixmap and update the scene
        qt_image = image2pixelmap(img)
        self.scene.clear()
        self.scene.addPixmap(qt_image)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AnalyzerWindow(cv.imread("img.jpg"))
    sys.exit(app.exec_())
