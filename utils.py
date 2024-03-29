import os
import numpy as np
import cv2 as cv
from PyQt5.QtGui import QImage, QPixmap


def bgr2rgb(img): return cv.cvtColor(img, cv.COLOR_BGR2RGB)
def bgr2gray(img): return cv.cvtColor(img, cv.COLOR_BGR2GRAY)
def rgb2gray(img): return cv.cvtColor(img, cv.COLOR_RGB2GRAY)
def norm2int(img): return (img*255).astype(np.uint8)
def norm2float(img): return (img/255.).astype(float)


class BBox():
    """Bounding box class to make it easier to handle than a list
    """

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
        """Summarize points

        Returns:
            list: array of points 
        """
        return [self.tl, self.tr, self.bl, self.br]

    def find_point_to_edit(self, point):
        """Finds the closest corner to a given point

        Args:
            point (tuple(int, int)): input point
        """
        # collect distances for corners
        dists = [dist(point, p) for p in self.points()]
        # select the closest and stored it in obj. var.
        min_dist = np.array(dists).min()
        min_dist_index = dists.index(min_dist)
        self.edited_point_index = min_dist_index

    def change_point(self, point):
        """Chanege the corner prevously selected

        Args:
            point (tuple(int, int)): new point location
        """
        if self.edited_point_index == 0:
            self.tl = point
        elif self.edited_point_index == 1:
            self.tr = point
        elif self.edited_point_index == 2:
            self.bl = point
        elif self.edited_point_index == 3:
            self.br = point

        self.edited_point_index = None
        # self.__str__()

    def shrink(self, shrink_pix=10):
        """Decreases the bbox from all directions

        Args:
            shrink_pix (int, optional): shrink amount. Defaults to 10.
        """
        self.tl = (self.tl[0]+shrink_pix, self.tl[1]+shrink_pix)
        self.tr = (self.tr[0]+shrink_pix, self.tr[1]-shrink_pix)
        self.bl = (self.bl[0]-shrink_pix, self.bl[1]+shrink_pix)
        self.br = (self.br[0]-shrink_pix, self.br[1]-shrink_pix)

    def create_mask(self, shape):
        """Creates mask image from bbox

        Args:
            shape (tuple(int, int)): Shape of output image

        Returns:
            np.ndarray: image of mask 
        """
        mask = np.zeros(shape, float)
        points = np.array(self.points())

        # sort points in clockwise order
        centroid = np.mean(points, axis=0)
        angles = np.arctan2(points[:, 1] - centroid[1],
                            points[:, 0] - centroid[0])
        sorted_indices = np.argsort(angles)
        sorted_points = points[sorted_indices]

        # draw filled white polygon
        cv.drawContours(mask, [sorted_points], -1, (1, 1, 1), -1)
        return mask

    def get_rotation_angle(self, shape):
        """Gets the orientation of the bbox

        Args:
            shape (tuple(int, int)): shape of the image to get the orientation from

        Returns:
            float: orientation angle
        """
        mask = self.create_mask(shape)
        mask = norm2int(mask)
        mask = rgb2gray(mask)

        cnts, hierarchy = cv.findContours(
            mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        cnt = cnts[0]

        # get minimum area bounding rectangle
        rect = cv.minAreaRect(cnt)
        # extracting the rotation angle out
        angle = rect[2]
        return angle


def cut_straight_bbox_img(img: np.ndarray, bbox: BBox):
    """Cuts image in the area of the bbox and rotates it straight

    Args:
        img (np.ndarray): image to cut
        bbox (BBox): bbox to cut out from image

    Returns:
        np.ndarray: staight cut image
    """
    mask = bbox.create_mask(img.shape)
    angle = bbox.get_rotation_angle(img.shape)

    # staightening image and mask
    rotated_mask = rotate_img(mask, -(90-angle))
    rotated_img = rotate_img(img, -(90-angle))
    # masking
    rotated_masked_img = rotated_mask.astype(bool)*rotated_img

    # get mask object
    cnts, _ = cv.findContours(
        rgb2gray(norm2int(rotated_mask)), cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    cnt = cnts[0]
    # get coordinates of mask object
    x, y, w, h = cv.boundingRect(cnt)

    return rotated_masked_img[y:y+h, x:x+w]


def image2pixelmap(img: np.ndarray, shape=None):
    """Converts image from opencv form to pyqt form
    """
    if shape is None:
        height, width, channel = img.shape
    else:
        height, width = shape

    bytes_per_line = 3 * width
    image = QImage(img, width, height,
                   bytes_per_line, QImage.Format_RGB888)
    image = image.rgbSwapped()  # Fix color channels

    return QPixmap.fromImage(image)


def dist(point_a, point_b):
    """Eucledian distance of 2 points
    """
    return np.linalg.norm(np.array(point_a)-np.array(point_b))


def rotate_img(img, angle):
    """Rotates the image with a rotation angle
    """
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
    """If image doesn't have a min height, this scales it up while keeping the aspect ratio
    """
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


def find_available_filename(file_path):
    """Searches for a filename and returns the first available duplicate option
    """
    if not os.path.exists(file_path):
        return file_path  # If the file doesn't exist, return the original filename

    base_name, extension = os.path.splitext(file_path)
    counter = 1

    while os.path.exists(f"{base_name}_{counter}{extension}"):
        counter += 1

    return f"{base_name}_{counter}{extension}"
