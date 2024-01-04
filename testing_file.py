import cv2
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Load an image using OpenCV
image = cv2.imread('billimg3.jpg')

# Convert the image to grayscale
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Use pytesseract to do OCR on the image
data = pytesseract.image_to_data(
    gray_image, output_type=pytesseract.Output.DICT)

grouped_boxes = {}
boxes = []
# Iterate through each detected text
for i, text in enumerate(data['text']):
    if text:
        x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
        # Draw bounding box around the text
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 1)
        # cv2.putText(image, text, (x, y - 10),
        #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        threshold = 12  # Adjust this value as needed

        # Check if there's a group already near the current box
        found = False
        for key, value in grouped_boxes.items():
            if abs(y - key) < threshold:
                grouped_boxes[key].append((x, y, w, h))
                found = True
                break

        # If no group found nearby, create a new group
        if not found:
            grouped_boxes[y] = [(x, y, w, h)]
        print(text)

print(grouped_boxes)

for key, value in grouped_boxes.items():
    t = 0
    l = 0
    hgh = 0

    print(f"Vertical Position: {key}")

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

    print("----------")

# Display the image with bounding boxes
cv2.imshow('Detected Text with Bounding Boxes', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
