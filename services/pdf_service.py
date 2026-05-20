# PDF Extraction Service
# This service will handle extraction of text and hyperlinks from PDF files.
from cleaner import extract_resume_text

def extract_text_from_pdf(pdf_path):
    """
    Extract text from PDF using your existing cleaner function.
    Wraps cleaner.extract_resume_text() for service layer.
    """
    return extract_resume_text(pdf_path)