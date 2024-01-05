import cv2
import pytesseract
import numpy as np

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Load an image using OpenCV
image = cv2.imread('billimg3.jpg')

# Convert the image to grayscale
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

_, thresholded = cv2.threshold(
    gray_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

cv2.imshow('Detected Text with Bounding Boxes', thresholded)
cv2.waitKey(0)
cv2.destroyAllWindows()

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
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 1)

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


for key, value in grouped_boxes.items():
    t = 0
    l = 0
    hgh = 0

    x_s = list(map(lambda x: x[0], value))
    y_s = list(map(lambda x: x[1], value))

    min_box = value[x_s.index(min(x_s))]
    max_box = value[x_s.index(max(x_s))]
    max_height = max(list(map(lambda x: x[3], value)))

    min_y_box = value[y_s.index(min(y_s))]
    max_y_box = value[y_s.index(max(y_s))]

    tl = (min_box[0], min_y_box[1])
    br = (max_box[0] + max_box[2], max_y_box[1] + min_y_box[3])

    cv2.rectangle(image, tl, br, (0, 255, 0), 1)

    boxes.append((tl, br))


lines = []
lines_dic = {}

for key, val in grouped_texts.items():
    price = val[-1]
    rest = val[0:-2]

    price = price.replace("¢", "€")
    price = price.replace(",", ".")

    if price[-1] != "€":
        price = f"{price}€"
    # if price[-1] == "¢":

    lines.append([" ".join(rest), price])

print(lines, sep="\n")

# Display the image with bounding boxes
cv2.imshow('Detected Text with Bounding Boxes', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
