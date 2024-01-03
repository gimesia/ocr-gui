import cv2
import pytesseract
import pytesseract

# Set the path to the Tesseract executable
# Replace with your Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Load the image
image_path = 'billimg2.jpg'
img = cv2.imread(image_path)

scale_factor = 0.5  # Change this value to scale by a different factor

# Rescale the image
rescaled_img = cv2.resize(img, None, fx=scale_factor,
                          fy=scale_factor, interpolation=cv2.INTER_AREA)

# img = rescaled_img

blurred_img = cv2.GaussianBlur(img, (3, 3), 0)

# Convert the image to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = cv2.cvtColor(blurred_img, cv2.COLOR_BGR2GRAY)

# Perform thresholding to obtain a binary image
_, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
thresh = cv2.adaptiveThreshold(
    gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
ret3, thresh = cv2.threshold(
    gray, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

# Show the image with bounding boxes
cv2.imshow('Image with Bounding Boxes', thresh)
cv2.waitKey(0)
cv2.destroyAllWindows()


# Perform OCR and get bounding boxes
boxes = pytesseract.image_to_boxes(thresh)

# Draw bounding boxes on the original image
for box in boxes.splitlines():
    box = box.split()
    x_start, y_start, x_end, y_end = int(
        box[1]), int(box[2]), int(box[3]), int(box[4])
    cv2.rectangle(img, (x_start, img.shape[0] - y_start),
                  (x_end, img.shape[0] - y_end), (0, 255, 0), 2)

print(boxes)
# Show the image with bounding boxes

# Rescale the image
img = cv2.resize(img, None, fx=scale_factor,
                 fy=scale_factor, interpolation=cv2.INTER_AREA)

cv2.imshow('Image with Bounding Boxes', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
