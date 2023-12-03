
import sys

import numpy as np
import cv2 as cv
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGraphicsView, QGraphicsScene, QPushButton, QMainWindow
from PyQt5.QtGui import QWindow, QPixmap, QImage
from PyQt5.QtCore import Qt, QPoint, QRectF

from utils import mask_white_objects, bbox_of_largest_white_object, convert_cv_to_qt, convert_qt_to_cv, dist


class AnalyzerWindow(QMainWindow):
    def __init__(self, img):
        super().__init__()
        self.img = img
        self.cut_img = None
        self.bbox_editor = BBoxEditorWidget(self.img)

        self.setWindowTitle('Extract text')

        self.central_widget = QWidget()

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.bbox_editor)

        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        button1 = QPushButton("Cut", self)
        self.layout.addWidget(button1)
        button1.clicked.connect(self.cut_image)

        self.show()

    def set_image(self, img: np.ndarray):
        self.img = img

    def cut_image(self):
        mask = self.bbox_editor.bbox.create_mask(self.img.shape).astype(bool)
        self.cut_img = self.img * mask

        cv.imshow("N", self.cut_img)
        cv.waitKey(0)
        cv.destroyAllWindows()


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


class BBox():
    def __init__(self, tl, tr, bl, br):
        self.tl = tl
        self.tr = tr
        self.bl = bl
        self.br = br

        self.edited_point_index = None

    def __str__(self) -> str:
        p = self.points()

    def points(self):
        return [self.tl, self.tr, self.bl, self.br]

    def find_point_to_edit(self, point):
        dists = [dist(point, p) for p in self.points()]
        min_dist = np.array(dists).min()
        min_dist_index = dists.index(min_dist)
        self.edited_point_index = min_dist_index

    def change_point(self, point):
        print(point)
        if self.edited_point_index == 0:
            self.tl = point
        elif self.edited_point_index == 1:
            self.tr = point
        elif self.edited_point_index == 2:
            self.bl = point
        elif self.edited_point_index == 3:
            self.br = point

        self.edited_point_index = None
        self.__str__()

    def create_mask(self, shape):
        mask_img = np.zeros(shape, float)
        points = np.array(self.points())

        centroid = np.mean(points, axis=0)

        # Calculate angles
        angles = np.arctan2(points[:, 1] - centroid[1],
                            points[:, 0] - centroid[0])

        # Sort points based on angles
        sorted_indices = np.argsort(angles)
        sorted_points = points[sorted_indices]

        cv.drawContours(mask_img, [sorted_points], -1, (1, 1, 1), -1)
        return mask_img


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AnalyzerWindow(cv.imread("im/bill0.jpg"))
    sys.exit(app.exec_())
