import os
import uuid
import pytesseract

from services.pdf_extractor import (
    build_ocr_blocks,
    build_resume_v1,
    extract_resume_object
)

from services.model_service.capability_routing import get_model_name

# =========================================================
# MODEL CONFIGURATION
# =========================================================

VISION_MODEL_KEY = "multimodal_extraction"

# =========================================================
# FILE TYPES
# =========================================================

PDF_EXTENSIONS = {"pdf"}
IMAGE_EXTENSIONS = {"png", "jpg", "jpeg"}
TEXT_EXTENSIONS = {"txt", "md"}

SUPPORTED_EXTENSIONS = (
    PDF_EXTENSIONS |
    IMAGE_EXTENSIONS |
    TEXT_EXTENSIONS
)

# =========================================================
# FILE HELPERS
# =========================================================

def get_file_extension(filename):

    if not filename or "." not in filename:
        return ""

    return filename.rsplit(".", 1)[1].lower()


def get_resume_input_type(filename):

    extension = get_file_extension(filename)

    if extension in PDF_EXTENSIONS:
        return "pdf"

    if extension in IMAGE_EXTENSIONS:
        return "image"

    if extension in TEXT_EXTENSIONS:
        return "text"

    return "unsupported"

# =========================================================
# MAIN EXTRACTION ENTRYPOINT
# =========================================================

def extract_resume(file_path, original_filename=None):

    filename = original_filename or os.path.basename(file_path)

    input_type = get_resume_input_type(filename)

    # =====================================================
    # PDF FLOW
    # =====================================================

    if input_type == "pdf":

        return extract_resume_object(file_path)

    # =====================================================
    # IMAGE FLOW
    # =====================================================

    if input_type == "image":

        print("[ROUTER] Using OCR pipeline for image input")

        return extract_ocr_resume_object(file_path)

    # =====================================================
    # TEXT FLOW
    # =====================================================

    if input_type == "text":
        return extract_text_resume_object(file_path)

    # =====================================================
    # INVALID TYPE
    # =====================================================

    raise ValueError("Unsupported resume file type")

# =========================================================
# MULTIMODAL EXTRACTION
# =========================================================

def extract_multimodal_resume_object(image_path):

    model_name = get_model_name(VISION_MODEL_KEY)

    print(f"[MULTIMODAL] Using model: {model_name}")

    # =====================================================
    # TODO:
    # Add OpenAI multimodal extraction here
    #
    # Future Flow:
    #
    # image
    # ↓
    # gpt-4o-mini
    # ↓
    # structured JSON
    #
    # =====================================================

    return {
        "resume_id": str(uuid.uuid4()),

        "schema_version": "1.0",

        "identity": {},

        "experience": [],

        "projects": [],

        "education": [],

        "skills": {},

        "analysis": {},

        "render_preferences": {
            "template": "classic",
            "font_size": 10,
            "margins": [1.5, 1.5, 1.8, 1.8]
        },

        "_layout_blocks": [],

        "_extraction": {
            "input_type": "image",
            "method": "multimodal_llm",
            "model": model_name
        }
    }

# =========================================================
# OCR EXTRACTION
# =========================================================

def extract_ocr_resume_object(image_path):

    print("[OCR] Starting OCR extraction")

    text = pytesseract.image_to_string(image_path)

    if not text.strip():
        raise ValueError("OCR did not extract readable text from the image")

    return build_resume_v1(
        build_ocr_blocks(text),
        text,
        {
            "input_type": "image",
            "method": "tesseract_ocr"
        }
    )

# =========================================================
# TEXT EXTRACTION
# =========================================================

def extract_text_resume_object(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    
    if not text.strip():
        raise ValueError("Text file is empty")
        
    return build_resume_v1(
        build_ocr_blocks(text),
        text,
        {
            "input_type": "text",
            "method": "raw_text"
        }
    )
