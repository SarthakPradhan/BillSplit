import argparse
import cv2
import numpy as np
import pytesseract
import nltk
import imutils
from imutils.perspective import four_point_transform
import re
from nltk import word_tokenize, pos_tag, ne_chunk

# Load the Tesseract OCR engine
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Replace with the path to your Tesseract OCR executable

# Load the image

image_path = 'images/bill_image.jpg'  # Replace with the path to your bill image
orig = cv2.imread(image_path)
# load the input image from disk, resize it, and compute the ratio
# of the *new* width to the *old* width
# orig = cv2.imread(args["image"])
image = orig.copy()
# image = imutils.resize(image, width=500)
# ratio = orig.shape[1] / float(image.shape[1])


image = ~image
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Apply thresholding to the image
'''
adaptive = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,81,0)
_, thresh = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU )

k = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]], np.uint8)
closing = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, k)


cv2.imshow("gray",gray)
cv2.imshow("imgpad", closing)
cv2.imshow("thresh", thresh)
cv2.imshow("adaptive", adaptive)
cv2.waitKey(0)
cv2.destroyAllWindows()
'''
# Perform OCR using Tesseract
my_config = r"--psm 6 oem 3"
text = pytesseract.image_to_string(gray, config=my_config)

# Print the extracted text
print("Extracted Text:\n", text)
lines = text.split('\n')

pricePattern = r'([0-9]+\.[0-9]+)'
# show the output of filtering out *only* the line items in the
# receipt
print("[INFO] price line items:")
print("========================")
# loop over each of the line items in the OCR'd receipt
for row in text.split('\n'):
    # check to see if the price regular expression matches the current
    # row
    print(row)
    print(lines)
    if re.search(pricePattern, row) is not None:
        break
    else:
        lines.remove(row)
lines = list(filter(None, lines))
pattern = r"^(.*?)\s+\$?([\d.]+)$"

# Initialize dictionary to store results
result_dict = {}

# Loop through input list
for item in lines:
    # Search for pattern in item
    match = re.search(pattern, item)
    if match:
        text = match.group(1)
        number = float(match.group(2))
        if isinstance(number, int):
            print(number)
            number = number/100
        result_dict[text] = number

# Print the resulting dictionary
print(result_dict)
