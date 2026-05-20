# Text Cleaning Service
# This service will handle cleaning, encoding fixes, and structure mapping of raw resume text.
from cleaner import clean_resume_text

def clean_text(raw_text):
    """
    Clean raw PDF text using your existing cleaner function.
    Wraps cleaner.clean_resume_text() for service layer.
    """
    return clean_resume_text(raw_text)