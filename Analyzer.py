import numpy as np
import cv2 as cv

import logging as log


class Analyzer():
    def __init__(self, img=None):
        self.img = img

    def analyze_img(self, img: np.ndarray):
        self.img = img

        if self.img is not None:
            print("Image can be analyzed")
            cv.imshow("Analyzed", img)
        else:
            log.error("Image is not set")
