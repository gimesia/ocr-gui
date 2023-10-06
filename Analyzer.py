import numpy as np
import cv2 as cv

import logging as log


class BBox():
    def __init__(self, tl: tuple[int, int], br: tuple[int, int]):
        self._tl = tl
        self._br = br

    def tl(self):
        return self._tl

    def br(self):
        return self._br

    def tr(self):
        return (self.br[0], self._tl[1])

    def bl(self):
        return (self._tl[0], self.br[1])


class Analyzer():
    def __init__(self, img: np.ndarray = None):
        self.img = img
        self.bbox: BBox = None

    def analyze_img(self, img: np.ndarray):
        self.img = img

        if self.img is not None:
            print("Image can be analyzed")
            gray = cv.cvtColor(self.img, cv.COLOR_BGR2GRAY)
            blur = cv.GaussianBlur(gray, (3, 3), 0)

            th = cv.threshold(gray, 0, 255, cv.THRESH_BINARY+cv.THRESH_OTSU)[1]
            img_dilation = cv.dilate(th, np.ones((3, 3)), iterations=2)

            masked = gray * img_dilation

            # Make the masked area *pop*
            dst = cv.addWeighted(masked, 0.65, gray, 0.35, 0)

            cv.imshow("Analyzed", dst)
            cv.imwrite("im.jpg", img)
        else:
            log.error("Image is not set")
