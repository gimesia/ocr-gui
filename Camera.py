import cv2 as cv
import threading
import time

from Analyzer import Analyzer


class Camera():
    def __init__(self):
        self.frame = None
        self.cap = cv.VideoCapture(0)
        # self.__capturing = False
        self.capturing = False
        self.analyzer = Analyzer()

    def capture(self):
        # self.__capturing = True
        self.capturing = True

        # while self.__capturing:
        while self.capturing:
            # Capture frame-by-frame
            ret, self.frame = self.cap.read()

            # if frame is read correctly ret is True
            if not ret:
                raise Exception(
                    "Can't receive frame (stream end?). Exiting ...")
                break

            # Our operations on the frame come here
            modified_frame = cv.cvtColor(self.frame, cv.COLOR_BGR2GRAY)
            modified_frame = cv.adaptiveThreshold(
                modified_frame, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV, 11, 2)
            modified_frame = cv.Canny(modified_frame, 90, 210)

            # Display the resulting frame
            cv.imshow('frame', modified_frame)

            pressed_key = cv.waitKey(1)
            if pressed_key == ord('q'):
                # self.__capturing = False
                self.capturing = False
            elif pressed_key == 32:
                self.analyzer.analyze_img(self.frame)

        return self.frame

    def start_capture(self):
        capture = threading.Thread(target=self.capture, args=())
        capture.start()


if __name__ == '__main__':
    c = Camera()
    c.start_capture()
