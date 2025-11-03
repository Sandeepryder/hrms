import os
from PIL import Image
import pytesseract
import fitz
from docx import Document
import io

def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == '.pdf':
        text = ""
        pdf = fitz.open(file_path)
        for page in pdf:
            text += page.get_text("text")
        return text

    elif ext == '.docx':
        doc = Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs])

    elif ext in ['.png', '.jpg', '.jpeg']:
        return pytesseract.image_to_string(Image.open(file_path))

    else:
        return "Unsupported file format."

file = r"C:/Users/pc/Desktop/TestAI/assets/im.jpg"  # or .docx or .jpg
print(extract_text(file))
