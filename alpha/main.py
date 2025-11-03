from PIL import Image
import pytesseract

# Load your image
image_path = "image.png"
text = pytesseract.image_to_string(Image.open("C:/Users/pc/Desktop/TestAI/im.jpg"))

print("Extracted Text:")
print(text)
