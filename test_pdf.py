from pdf2image import convert_from_path
import pytesseract

print("Testing PDF...")

images = convert_from_path("test.pdf")
print("Pages:", len(images))

text = pytesseract.image_to_string(images[0])
print("OCR length:", len(text))
