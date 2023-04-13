"""
Author: Sarthak Pradhan
Date: 04/04/2023
Description: function to scan and bill and create elements that can be put into buckets for the convenience of splitting
"""
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
def img_processing():
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
    return gray
def main():
    image = img_processing()

    # Perform OCR using Tesseract
    my_config = r"--psm 6 oem 3"
    text = pytesseract.image_to_string(image, config=my_config)

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
        try:
            match = re.search(pattern, item)
            if match:
                text = match.group(1)
                if "." in match.group(2):
                    # If the string contains a dot, it's a float
                    number = float(match.group(2))
                else:
                    # If the string doesn't contain a dot, it's an integer
                    number = int(match.group(2))/100
                result_dict[text] = number
        except Exception:
            pass

    # Print the resulting dictionary
    return(result_dict)

if __name__ == "__main__":
    print(main())