# 🐍💻 Python Project for MAIA 8, semester 1 Software Engineering class 
## 🔍👀 Text recognition with GUI 
### __A GUI tool to extract texts from images either taken from the user's webcamera or an uploaded from the file directory.__ 
The development of this program helped me to get familiar and showcase the tools provided by `PyTesseract` and `PyQt5`, 2 popular packages which I have never used before. 

### The tool can be useful for:
- digitalizing the information on grocery receipts
- to digitalize the text on sheets of papers from other classes, where the digital document was not provided (e.g. Applied Mathematics course papers)
- extracting the text from screenshots
- etc...

## Usage:
### 📦 Dependencies:
- numpy
- opencv
- pytesseract
- pyqt5

### 📝Manual:

0. (Make sure all the dependencies are met, change variables in the `config.py` file for the path if needed)

1. run `main.py` -> The main GUI window opens (this can take a couple of seconds, as OpenCV has to access the computer's webcamera)

2. Capture an image via webcamera using the "__Capture Frame__" button or by __pressing \*space\*__ OR by uploading an image from the computer by pressing the "__Upload Image__" button. The image to be analysed will appear on the right side
_(Note: if the webcamera does not have a good enough resolution the OCR might not work as intended)_

3. Press the "__Analyze__" button to open the Analyzer window

4. Cut the ROI. This can be done by clicking on the image. The first click selects the closest corner of the bounding box to the cursor, the second click replaces it to the coordinates of the click. When the bounding box is as desired press the "__Cut__" button.

5. The ROI is cut out from the original image and oriantated to a vertical line. If the orientation is not correct, adjust the rotation with the "__Rotate__" buttons. When the orientation is as desired press the "__OCR__" button.

6. The image with the indicated recognized texts will apper on the left, while on the right the text is extracted into an editable textbox. If the text recognition has made some mistakes, correct them in the textbox, and save the results by pressing the "__Save__" button. The analyzer window closes when the text is saved, and the process returns to __Step 2.__


### 📁 Directory structure:
```
├── test_images
|   └─ images for demonstation purposes
|
├── AnalyserWindow.py
├── main.py
|
├── widgets
|   ├──BBoxEditorWidget.py
|   ├──CutImagePreviewWidget.py
|   └──OCRWidget.py
|
├── utils.py
├── config.py
```

### 💡 Notes:
- PyTesseract works best if the text is vertical and text color is black and the background is white
- PyTesseract engine needs to be downloaded, windows installer available at [UB Mannheim's github](https://github.com/UB-Mannheim/tesseract/wiki)