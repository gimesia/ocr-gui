import numpy as np

import pytesseract
from pytesseract import Output

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class OCR():
    def __init__(self, img):
        self.img = img
        self.lines = []

    def analyze_img(self, img: np.ndarray):
        d = pytesseract.image_to_data(img, output_type=Output.DICT)
        n_boxes = len(d['text'])
        recognized_sentences = []

        # Group recognized characters into sentences based on their positions
        for i in range(n_boxes):
            if int(d['conf'][i]) > 60:
                (x, y, w, h) = (d['left'][i], d['top']
                                [i], d['width'][i], d['height'][i])
                recognized_sentences.append((d['text'][i], x, y))

        # Sort the recognized characters by Y-coordinate to group lines
        recognized_sentences.sort(key=lambda x: x[2])

        # Process recognized characters to form sentences based on lines
        lines = []
        current_line = []
        prev_y = recognized_sentences[0][2]
        for text, x, y in recognized_sentences:
            if y - prev_y > 10:  # Separation threshold between lines
                lines.append(' '.join(current_line))
                current_line = []

            current_line.append(text)
            prev_y = y

        lines.append(' '.join(current_line))  # Add the last line

        return lines
