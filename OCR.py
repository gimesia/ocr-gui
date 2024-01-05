import numpy as np
import cv2 as cv

import pytesseract
from pytesseract import Output

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class OCR():
    def __init__(self):
        self.lines = []

    def analyze_img(self, img: np.ndarray):
        image = img.copy()
        # Convert the image to grayscale
        gray_image = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        # Use pytesseract to do OCR on the image
        data = pytesseract.image_to_data(
            gray_image, output_type=pytesseract.Output.DICT)

        grouped_boxes = {}
        grouped_texts = {}
        boxes = []

        # Iterate through each detected text
        for i, text in enumerate(data['text']):
            if text:
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                # Draw bounding box around the text
                cv.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 1)

                threshold = 12  # Adjust this value as needed

                # Check if there's a group already near the current box
                found = False
                for key, value in grouped_boxes.items():
                    if abs(y - key) < threshold:
                        grouped_boxes[key].append((x, y, w, h))
                        grouped_texts[key].append(text)
                        found = True
                        break

                # If no group found nearby, create a new group
                if not found:
                    grouped_boxes[y] = [(x, y, w, h)]
                    grouped_texts[y] = [text]

        print(grouped_texts)

        for key, value in grouped_boxes.items():
            x_s = list(map(lambda x: x[0], value))
            y_s = list(map(lambda x: x[1], value))

            min_box = value[x_s.index(min(x_s))]
            max_box = value[x_s.index(max(x_s))]

            min_y_box = value[y_s.index(min(y_s))]
            max_y_box = value[y_s.index(max(y_s))]

            tl = (min_box[0], min_y_box[1])
            br = (max_box[0] + max_box[2], max_y_box[1] + min_y_box[3])

            cv.rectangle(image, tl, br, (0, 255, 0), 1)

            boxes.append((tl, br))

        lines = []

            

        return img
