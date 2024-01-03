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

# Iterate through each detected text
for i, text in enumerate(data['text']):
    if text:
        x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
        # Draw bounding box around the text
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        # cv2.putText(image, text, (x, y - 10),
        #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        print(text)

# Display the image with bounding boxes
cv2.imshow('Detected Text with Bounding Boxes', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
