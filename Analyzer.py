
import sys

import numpy as np
import cv2 as cv
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGraphicsView, QGraphicsScene, QPushButton, QMainWindow
from PyQt5.QtGui import QWindow, QPixmap, QImage
from PyQt5.QtCore import Qt, QPoint, QRectF

from utils import BBox, convert_cv_to_qt, cut_straight_bbox_img, rotate_img


class AnalyzerWindow(QMainWindow):
    def __init__(self, img):# Wlcome back
        super().__init__()
        self.setWindowTitle('Extract text')

        self.img = img
        self.cut_img = None

        self.bbox_editor = BBoxEditorWidget(self.img)

        self.control_button = QPushButton("Cut", self)
        self.control_button.clicked.connect(self.cut_image)

        widget = QWidget()

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.bbox_editor)
        self.layout.addWidget(self.control_button)

        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

        self.show()

    def set_image(self, img: np.ndarray):
        self.img = img

    def cut_image(self):
        mask = self.bbox_editor.bbox.create_mask(self.img.shape).astype(bool)

        self.cut_img = self.img * mask

        rotation = self.bbox_editor.bbox.get_rotation_angle(self.img.shape)

        self.cut_img = cut_straight_bbox_img(
            self.cut_img, self.bbox_editor.bbox)




        widget = CutImagePreviewWidget(self.cut_img)

        self.layout = QHBoxLayout()
        self.layout.addWidget(widget)
        self.layout.addWidget(self.control_button)

        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        # cv.imshow("N", self.cut_img)
        # cv.waitKey(0)
        # cv.destroyAllWindows()


class CutImagePreviewWidget(QWidget):
    def __init__(self, img):
        super().__init__()
        self.img = img
        h, w, ch = self.img.shape
        self.resize(w, h)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, w, h)

        self.view = QGraphicsView(self.scene)
        self.layout.addWidget(self.view)

        qt_image = convert_cv_to_qt(self.img.copy())
        self.scene.clear()
        self.scene.addPixmap(qt_image)


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
        qt_image = convert_cv_to_qt(img)
        self.scene.clear()
        self.scene.addPixmap(qt_image)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AnalyzerWindow(cv.imread("im/bill0.jpg"))
    sys.exit(app.exec_())
