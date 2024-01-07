from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt

from utils import image2pixelmap, rotate_img


class CutImagePreviewWidget(QWidget):
    """Widget to check the previously cut image,
    Allows to rotate 90 degrees if the orientation is not correct
    """

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
        """90 degree rotation of the image, and updating of the image label 

        Args:
            clockwise (bool, optional): Direction of rotation. Defaults to clockwise.
        """
        rotated_img = rotate_img(self.img, -90 if clockwise else 90)
        self.img = rotated_img

        qt_image = image2pixelmap(rotated_img)
        self.image_label.setPixmap(qt_image)

    def rotate_l(self):
        self.rotate(False)

    def rotate_r(self):
        self.rotate(True)
