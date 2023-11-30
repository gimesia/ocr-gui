import numpy as np
import cv2 as cv
from PyQt5.QtGui import QImage, QPixmap


def image2pixelmap(img: np.ndarray, shape=None):
    if shape is None:
        height, width, channel = img.shape
    else:
        height, width = shape

    bytes_per_line = 3 * width

    image = QImage(img, width, height,
                   bytes_per_line, QImage.Format_RGB888)

    return QPixmap.fromImage(image)


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

    for contour in contours:
        x, y, w, h = cv.boundingRect(contour)
        cv.rectangle(mask, (x, y), (x+w, y+h),
                     (255, 255, 255), thickness=cv.FILLED)

    # Bitwise AND the original image with the mask to mask out white objects
    masked_image = cv.bitwise_and(image, mask)

    return masked_image


def bbox_of_largest_white_object(image):
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    _, thresholded = cv.threshold(gray, 200, 255, cv.THRESH_BINARY)

    contours, _ = cv.findContours(
        thresholded, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    largest = None

    for contour in contours:
        if largest is None:
            largest = contour
        else:
            if cv.contourArea(largest) > cv.contourArea(contour):
                largest = contour

    rect = cv.minAreaRect(largest)
    return cv.boxPoints(rect)


def dist(point_a, point_b):
    return np.linalg.norm(np.array(point_a)-np.array(point_b))


def convert_qt_to_cv(qt_pixmap):
    qt_image = qt_pixmap.toImage()
    width = qt_image.width()
    height = qt_image.height()
    buffer = qt_image.constBits()
    buffer.setsize(height * width * 4)
    cv_image = np.array(buffer).reshape((height, width, 4))
    return cv.cvtColor(cv_image, cv.COLOR_RGBA2RGB)


def convert_cv_to_qt(cv_image):
    height, width, channel = cv_image.shape
    bytes_per_line = 3 * width
    qt_image = QImage(cv_image.data, width, height,
                      bytes_per_line, QImage.Format_RGB888)
    qt_image = qt_image.rgbSwapped()  # Fix color channels
    return QPixmap.fromImage(qt_image)
