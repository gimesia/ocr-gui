import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QPoint


class ImageDrawer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Clicker")
        self.setGeometry(100, 100, 800, 600)

        self.points = [(0, 0), (0, 0), (0, 0), (0, 0),]
        self.edited_point_index = None

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Create a QGraphicsScene and QGraphicsView
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.layout.addWidget(self.view)

        # Load an image (replace 'your_image.jpg' with the path to your image)
        self.cv_image = cv2.imread("im/bill0.jpg")
        self.image = self.convert_cv_to_qt(self.cv_image)

        # Add the image to the scene
        self.scene.addPixmap(self.image)

        # Connect mouse click event
        self.view.mousePressEvent = self.mouse_click_event

    def convert_cv_to_qt(self, cv_image):
        height, width, channel = cv_image.shape
        bytes_per_line = 3 * width
        qt_image = QImage(cv_image.data, width, height,
                          bytes_per_line, QImage.Format_RGB888)
        qt_image = qt_image.rgbSwapped()  # Fix color channels
        return QPixmap.fromImage(qt_image)

    def convert_qt_to_cv(self, qt_pixmap):
        qt_image = qt_pixmap.toImage()
        width = qt_image.width()
        height = qt_image.height()
        buffer = qt_image.constBits()
        buffer.setsize(height * width * 4)
        cv_image = np.array(buffer).reshape((height, width, 4))
        return cv2.cvtColor(cv_image, cv2.COLOR_RGBA2RGB)

    def mouse_click_event(self, event):
        # Get the position of the click
        pos = event.pos()
        mapped_pos = self.view.mapToScene(pos)
        x = int(mapped_pos.x())
        y = int(mapped_pos.y())

        img = self.cv_image.copy()

        if self.edited_point_index is not None:
            self.change_point((x, y))
            # Convert the OpenCV image to QPixmap and update the scene
            qt_image = self.convert_cv_to_qt(img)
            self.scene.clear()
            self.scene.addPixmap(qt_image)
            self.edited_point_index = None

        if self.edited_point_index is None:
            self.edited_point_index = self.find_point_to_edit((x, y))

        for i, point in enumerate(self.points):
            rad = 8
            if i == self.edited_point_index:
                rad = 4
            cv2.circle(img, point, rad, (0, 0, 255), -1)
            print(point)

        # Draw a circle on the OpenCV image
        # cv2.circle(img, self.points[0], 5, (0, 0, 255), -1)
        # cv2.circle(img, self.points[1], 5, (0, 255, 0), -1)
        # cv2.circle(img, self.points[2], 5, (255, 0, 0), -1)
        # cv2.circle(img, self.points[3], 5, (0, 255, 255), -1)

    def find_point_to_edit(self, point):
        dists = [dist(point, p) for p in self.points]
        min_dist = dists.index(np.array(dists).min())
        self.edited_point_index = min_dist
        print(min_dist)

    def change_point(self, point):
        self.points[self.edited_point_index] = point


def dist(x, y): return np.linalg.norm(np.array(x)-np.array(y))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageDrawer()
    window.show()
    sys.exit(app.exec_())
