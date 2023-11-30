import numpy as np
import cv2 as cv
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGraphicsView, QGraphicsScene, QPushButton, QMainWindow
from PyQt5.QtGui import QWindow, QPixmap, QImage
from PyQt5.QtCore import Qt, QPoint, QRectF

from utils import mask_white_objects, bbox_of_largest_white_object, convert_cv_to_qt, convert_qt_to_cv, dist


class AnalyzerWindow(QMainWindow):
    def __init__(self, img):
        super().__init__()
        self.img = img
        self.cut_img = None

        self.setWindowTitle('Extract text')
        self.setCentralWidget(BBoxEditorWidget(self.img))
        self.showMaximized()

    def set_image(self, img: np.ndarray):
        self.img = img


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

        self.view.mousePressEvent = self.mouse_click_event

        bb = bbox_of_largest_white_object(self.img)
        self.bbox = BBox(
            (0, 0), (0, h), (w, 0), (w, h))
        bb.__str__()

        self.layout.addWidget(self.view)
        button1 = QPushButton("Get BBox", self)

        self.layout.addWidget(button1)

        self.refresh_img()

    def mouse_click_event(self, event):
        # Get the position of the click
        pos = event.pos()
        mapped_pos = self.view.mapToScene(pos)
        x = int(mapped_pos.x())
        y = int(mapped_pos.y())

        print((x, y))
        if self.bbox.edited_point_index is None:
            self.bbox.find_point_to_edit((x, y))
        else:
            self.bbox.change_point((x, y))

        self.refresh_img()

    def refresh_img(self, img=None):
        if img is None:
            img = self.img.copy()

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

        def mouse_click_event(self, event):
            # Get the position of the click
            pos = event.pos()
            mapped_pos = self.view.mapToScene(pos)
            x = int(mapped_pos.x())
            y = int(mapped_pos.y())

            if self.bbox.edited_point_index is None:
                self.bbox.find_point_to_edit((x, y))
            else:
                self.bbox.change_point((x, y))

            self.refresh_img()


class BBox():
    def __init__(self, tl, tr, bl, br):
        self.topleft = tl
        self.topright = tr
        self.bottomleft = bl
        self.bottomright = br

        self.edited_point_index = None

    def __str__(self) -> str:
        p = self.points()
        print(f"tl: {p[0]}\ntr{p[1]}\nbl{p[2]}\nbr{p[3]}")

    def points(self):
        return [self.topleft, self.topright, self.bottomleft, self.bottomright]

    def find_point_to_edit(self, point):
        dists = [dist(point, p) for p in self.points()]
        min_dist = np.array(dists).min()
        min_dist_index = dists.index(min_dist)
        self.edited_point_index = min_dist_index

    def change_point(self, point):
        if self.edited_point_index == 0:
            self.tl = point
        elif self.edited_point_index == 1:
            self.tr = point
        elif self.edited_point_index == 2:
            self.bl = point
        elif self.edited_point_index == 3:
            self.br = point

        self.edited_point_index = None
