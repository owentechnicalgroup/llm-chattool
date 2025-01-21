from docx import Document
from reportlab.pdfgen import canvas
import os

def create_test_docx():
    doc = Document()
    doc.add_paragraph("This is a test Word document for the RAG application. It demonstrates the ability to load and process Microsoft Word documents. The loader should handle both .txt and .docx files seamlessly. Each sentence should be in its own chunk when possible.")
    doc.save("data/test.docx")

def create_test_pdf():
    c = canvas.Canvas("data/test.pdf")
    text = (
        "This is a test PDF document for the RAG application. "
        "It demonstrates the ability to load and process PDF files. "
        "The loader should handle PDF files along with txt and docx files seamlessly. "
        "Each page of a PDF document will be processed as a separate document in the RAG system. "
        "The text splitter will try to break on sentence boundaries."
    )
    c.drawString(100, 750, text)
    c.save()

def create_test_txt():
    text = (
        "The RAG system processes documents efficiently. "
        "It handles multiple document formats seamlessly. "
        "The system breaks text into manageable chunks. "
        "Each chunk is processed independently. "
        "The text splitter prioritizes breaking on periods for natural sentence boundaries. "
        "This helps maintain context and readability. "
        "The chunks can then be used for further processing. "
        "Vector embeddings will be generated in the next phase. "
        "The system logs all operations for monitoring. "
        "Each document is moved to a completed folder after processing."
    )
    with open("data/test.txt", "w") as f:
        f.write(text)

if __name__ == "__main__":
    create_test_docx()
    create_test_pdf()
    create_test_txt()
    print("Test files created successfully.")
