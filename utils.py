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

    # Draw white contours on the mask
    # cv.drawContours(mask, contours, -1, (255, 255, 255), thickness=cv.FILLED)

    for contour in contours:
        x, y, w, h = cv.boundingRect(contour)
        cv.rectangle(mask, (x, y), (x+w, y+h),
                     (255, 255, 255), thickness=cv.FILLED)

    # Bitwise AND the original image with the mask to mask out white objects
    masked_image = cv.bitwise_and(image, mask)

    return masked_image
