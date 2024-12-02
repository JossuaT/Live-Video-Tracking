import pytesseract

text = pytesseract.image_to_string('test.jpg')
print(text)
