import numpy as np
import cv2 as cv

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QGraphicsScene, QGraphicsView

from utils import BBox, image2pixelmap


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

        self.bbox.shrink(75)

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
