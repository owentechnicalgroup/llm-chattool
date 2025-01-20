from docx import Document
from reportlab.pdfgen import canvas
import os

def create_test_docx():
    doc = Document()
    doc.add_paragraph("This is a test Word document for the RAG application.")
    doc.add_paragraph("It demonstrates the ability to load and process Microsoft Word documents.")
    doc.add_paragraph("The loader should handle both .txt and .docx files seamlessly.")
    doc.save("data/test.docx")

def create_test_pdf():
    c = canvas.Canvas("data/test.pdf")
    c.drawString(100, 750, "This is a test PDF document for the RAG application.")
    c.drawString(100, 730, "It demonstrates the ability to load and process PDF files.")
    c.drawString(100, 710, "The loader should handle PDF files along with txt and docx files seamlessly.")
    c.drawString(100, 690, "Each page of a PDF document will be processed as a separate document in the RAG system.")
    c.save()

if __name__ == "__main__":
    create_test_docx()
    create_test_pdf()
    print("Test files created successfully.")
