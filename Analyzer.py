import numpy as np
import cv2 as cv
from PyQt5.QtWidgets import QMainWindow


class AnalyzerWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.img = None
        bbox = None

        self.setGeometry(200, 200, 400, 300)
        self.setWindowTitle('Extract text')

    def set_image(self, img: np.ndarray):
        self.img = img


class BBox():
    def __init__(self, tl, tr, bl, br):
        self.topleft = tl
        self.topright = tr
        self.bottomleft = bl
        self.bottomright = br

    def points(self):
        return [self.topleft, self.topright, self.bottomleft, self.bottomright]


def mask_white_objects(image):
    # Convert the image to grayscale
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    # Threshold the grayscale image to create a binary mask for white objects
    _, thresholded = cv.threshold(gray, 200, 255, cv.THRESH_BINARY)

    # Find contours in the binary mask
    contours, _ = cv.findContours(
        thresholded, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    # Create an empty mask
    mask = np.zeros_like(image)

    # Draw white contours on the mask
    # cv.drawContours(mask, contours, -1, (255, 255, 255), thickness=cv.FILLED)

    for contour in contours:
        x, y, w, h = cv.boundingRect(contour)
        cv.rectangle(mask, (x, y), (x+w, y+h),
                     (255, 255, 255), thickness=cv.FILLED)

    # Bitwise AND the original image with the mask to mask out white objects
    masked_image = cv.bitwise_and(image, mask)

    return masked_image
