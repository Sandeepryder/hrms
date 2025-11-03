from docx import Document

def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

docx_path = r"C:/Users/pc/Desktop/TestAI/sample.docx"
print(extract_text_from_docx(docx_path))
