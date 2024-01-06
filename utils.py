import numpy as np
import cv2 as cv
from PyQt5.QtGui import QImage, QPixmap


def bgr2rgb(img): return cv.cvtColor(img, cv.COLOR_BGR2RGB)
def bgr2gray(img): return cv.cvtColor(img, cv.COLOR_BGR2GRAY)
def rgb2gray(img): return cv.cvtColor(img, cv.COLOR_RGB2GRAY)
def norm2int(img): return (img*255).astype(np.uint8)
def norm2float(img): return (img/255.).astype(float)


class BBox():
    def __init__(self, tl, tr, bl, br):
        self.tl = tl
        self.tr = tr
        self.bl = bl
        self.br = br

        self.edited_point_index = None

    def __str__(self) -> str:
        p = self.points()
        print(p, sep="\n")

    def points(self):
        return [self.tl, self.tr, self.bl, self.br]

    def find_point_to_edit(self, point):
        dists = [dist(point, p) for p in self.points()]
        min_dist = np.array(dists).min()
        min_dist_index = dists.index(min_dist)
        self.edited_point_index = min_dist_index

    def change_point(self, point):
        print(point)
        if self.edited_point_index == 0:
            self.tl = point
        elif self.edited_point_index == 1:
            self.tr = point
        elif self.edited_point_index == 2:
            self.bl = point
        elif self.edited_point_index == 3:
            self.br = point

        self.edited_point_index = None
        self.__str__()

    def shrink(self, shrink_pix=10):
        self.tl = (self.tl[0]+shrink_pix, self.tl[1]+shrink_pix)
        self.tr = (self.tr[0]+shrink_pix, self.tr[1]-shrink_pix)
        self.bl = (self.bl[0]-shrink_pix, self.bl[1]+shrink_pix)
        self.br = (self.br[0]-shrink_pix, self.br[1]-shrink_pix)

    def create_mask(self, shape):
        mask = np.zeros(shape, float)
        points = np.array(self.points())

        centroid = np.mean(points, axis=0)

        angles = np.arctan2(points[:, 1] - centroid[1],
                            points[:, 0] - centroid[0])

        sorted_indices = np.argsort(angles)
        sorted_points = points[sorted_indices]

        cv.drawContours(mask, [sorted_points], -1, (1, 1, 1), -1)
        return mask

    def get_rotation_angle(self, shape):
        mask = self.create_mask(shape)
        mask = norm2int(mask)
        mask = rgb2gray(mask)

        cnts, hierarchy = cv.findContours(
            mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        cnt = cnts[0]

        rect = cv.minAreaRect(cnt)
        angle = rect[2]
        return angle


def cut_straight_bbox_img(img: np.ndarray, bbox: BBox):
    mask = bbox.create_mask(img.shape)
    angle = bbox.get_rotation_angle(img.shape)

    rotated_mask = rotate_img(mask, -(90-angle))
    rotated_img = rotate_img(img, -(90-angle))
    rotated_masked_img = rotated_mask.astype(bool)*rotated_img

    cnts, _ = cv.findContours(
        rgb2gray(norm2int(rotated_mask)), cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    cnt = cnts[0]

    x, y, w, h = cv.boundingRect(cnt)

    return rotated_masked_img[y:y+h, x:x+w]


def image2pixelmap(img: np.ndarray, shape=None):
    if shape is None:
        height, width, channel = img.shape
    else:
        height, width = shape

    bytes_per_line = 3 * width

    image = QImage(img, width, height,
                   bytes_per_line, QImage.Format_RGB888)
    image = image.rgbSwapped()  # Fix color channels

    return QPixmap.fromImage(image)


def mask_white_objects(img):
    # Convert the image to grayscale
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # Threshold the grayscale image to create a binary mask for white objects
    _, thresholded = cv.threshold(gray, 200, 255, cv.THRESH_BINARY)

    # Find contours in the binary mask
    contours, _ = cv.findContours(
        thresholded, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    # Create an empty mask
    mask = np.zeros_like(img)

    for contour in contours:
        x, y, w, h = cv.boundingRect(contour)
        cv.rectangle(mask, (x, y), (x+w, y+h),
                     (255, 255, 255), thickness=cv.FILLED)

    # Bitwise AND the original image with the mask to mask out white objects
    masked_image = cv.bitwise_and(img, mask)

    return masked_image


def bbox_of_largest_white_object(img):
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

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


def rotate_img(img, angle):
    height, width = img.shape[:2]
    rotation_matrix = cv.getRotationMatrix2D((width / 2, height / 2), angle, 1)

    new_width = int(
        (np.abs(rotation_matrix[0, 0]) * width) + (np.abs(rotation_matrix[0, 1]) * height))
    new_height = int(
        (np.abs(rotation_matrix[1, 0]) * width) + (np.abs(rotation_matrix[1, 1]) * height))

    # Adjust the rotation matrix to prevent cropping
    rotation_matrix[0, 2] += (new_width / 2) - (width / 2)
    rotation_matrix[1, 2] += (new_height / 2) - (height / 2)

    rotated_img = cv.warpAffine(
        img, rotation_matrix, (new_width, new_height), borderMode=cv.BORDER_CONSTANT)

    return rotated_img


def scale_image_to_min_height(image, min_height=920):
    # Get image dimensions
    height, width = image.shape[:2]

    if height < min_height:
        # Calculate the scaling factor to achieve the minimum height while maintaining aspect ratio
        scale_factor = min_height / height

        # Calculate the new dimensions
        new_height = int(height * scale_factor)
        new_width = int(width * scale_factor)

        # Resize the image while preserving aspect ratio
        scaled_image = cv.resize(image, (new_width, new_height))

        return scaled_image
    else:
        return image
