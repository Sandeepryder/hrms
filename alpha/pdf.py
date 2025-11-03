import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text("text")
    return text

pdf_path = r"C:/Users/pc/Desktop/TestAI/resume.pdf"
print(extract_text_from_pdf(pdf_path))
