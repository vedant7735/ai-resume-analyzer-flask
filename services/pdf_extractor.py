import fitz  # PyMuPDF
import uuid
import re

def extract_resume_object(pdf_path):

    doc = fitz.open(pdf_path)
    try: 
        first_page_text = doc[0].get_text("text")

        if len(first_page_text.strip()) < 50:
            return extract_with_ocr(pdf_path)
        return extract_with_layout(doc)
    finally: 
        doc.close()

def detect_sections(blocks):
    """Detect sections using font size/bold heuristics"""
    sections = {
        "experience": [],
        "projects": [],
        "education": [],
        "skills": {}
    }
    
    # Find headers (larger font, bold, uppercase)
    headers = []
    for i, block in enumerate(blocks):
        text = block["text"].strip().upper()
        is_bold = block.get("is_bold", False)
        is_large = block.get("font_size", 10) > 11
        
        if (is_bold or is_large) and any(kw in text for kw in [
            "EXPERIENCE", "PROJECTS", "EDUCATION", "SKILLS", 
            "WORK", "EMPLOYMENT"
        ]):
            headers.append((i, text, block))
    
    # Extract content between headers
    for idx, (start_i, header_text, _) in enumerate(headers):
        end_i = headers[idx + 1][0] if idx + 1 < len(headers) else len(blocks)
        content_blocks = blocks[start_i + 1:end_i]
        
        if "EXPERIENCE" in header_text or "WORK" in header_text:
            sections["experience"] = parse_experience_blocks(content_blocks)
        elif "PROJECT" in header_text:
            sections["projects"] = parse_project_blocks(content_blocks)
        elif "EDUCATION" in header_text:
            sections["education"] = parse_education_blocks(content_blocks)
        elif "SKILL" in header_text:
            sections["skills"] = parse_skills_blocks(content_blocks)
    
    return sections


def extract_identity(blocks):
    """Extract contact info from first page header"""
    # Name is usually first large/bold text
    name = ""
    email = ""
    phone = ""
    linkedin = ""
    github = ""
    
    for block in blocks[:20]:  # check first 20 blocks
        text = block["text"]
        
        if not name and block.get("font_size", 10) > 14:
            name = text.strip()
        
        if not email and "@" in text:
            match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
            if match:
                email = match.group(0)
        
        if not phone:
            match = re.search(r'(\+?\d{1,3}[\s-]?)?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{4}', text)
            if match:
                phone = match.group(0)
        
        if not linkedin and "linkedin.com" in text.lower():
            match = re.search(r'linkedin\.com/in/[\w-]+', text.lower())
            if match:
                linkedin = match.group(0)
        
        if not github and "github.com" in text.lower():
            match = re.search(r'github\.com/[\w-]+', text.lower())
            if match:
                github = match.group(0)
    
    return {
        "name": name,
        "email": email,
        "phone": phone,
        "linkedin": linkedin,
        "github": github,
        "portfolio": "",
        "location": ""
    }


def parse_experience_blocks(blocks):
    """Parse experience using layout hints"""
    experiences = []
    current = None
    
    for block in blocks:
        text = block["text"].strip()
        is_bold = block.get("is_bold", False)

        if is_bold and block.get("font_size", 10) > 10 and not text.startswith("•"):
            if current:
                experiences.append(current)
            current = {
                "title": text,
                "company": "",
                "duration": "",
                "type": "",
                "bullets": []
            }
        # Company/duration line
        elif current and not current["company"] and "|" in text:
            parts = text.split("|")
            current["company"] = parts[0].strip()
            current["duration"] = parts[1].strip() if len(parts) > 1 else ""
        # Bullet point
        elif current and (text.startswith("•") or text.startswith("-")):
            current["bullets"].append(text.lstrip("•- ").strip())
    
    if current:
        experiences.append(current)
    
    return experiences


def parse_project_blocks(blocks):
    """Similar to experience parsing"""
    projects = []
    current = None
    
    for block in blocks:
        text = block["text"].strip()
        is_bold = block.get("is_bold", False)

        if is_bold and block.get("font_size", 10) > 10 and not text.startswith("•"):
            if current:
                projects.append(current)
            current = {
                "title": text,
                "type": "",
                "year": "",
                "tech_stack": [],
                "bullets": []
            }
        elif current and not current["tech_stack"] and ("," in text or ":" in text):
            # Parse tech stack
            tech_text = text.split(":")[-1] if ":" in text else text
            current["tech_stack"] = [t.strip() for t in tech_text.split(",")]
        elif current and (text.startswith("•") or text.startswith("-")):
            current["bullets"].append(text.lstrip("•- ").strip())
    
    if current:
        projects.append(current)
    
    return projects


def parse_education_blocks(blocks):
    """Parse education entries"""
    education = []
    # Simplified for now - LLM will refine
    return education


def parse_skills_blocks(blocks):
    """Parse skills section"""
    skills = {
        "languages": [],
        "frameworks": [],
        "tools": [],
        "domains": []
    }
    # Simplified - LLM will categorize
    return skills

def extract_with_layout(doc):
    """
    Layout-aware extraction using PyMuPDF blocks.
    """

    blocks = []

    for page_num, page in enumerate(doc):

        page_data = page.get_text("dict")

        for block in page_data["blocks"]:

            if "lines" not in block:
                continue

            block_text = []
            block_fonts = []
            block_bbox = block["bbox"]

            for line in block["lines"]:

                line_parts = []

                for span in line["spans"]:

                    text = span["text"].strip()

                    if not text:
                        continue

                    line_parts.append(text)
                    block_fonts.append(span.get("font_size", 10))

                if line_parts:
                    block_text.append(" ".join(line_parts))

            full_text = "\n".join(block_text).strip()

            if not full_text:
                continue

            avg_font_size = (
                sum(block_fonts) / len(block_fonts)
                if block_fonts else 10
            )

            blocks.append({
                "page": page_num,
                "text": full_text,
                "bbox": block_bbox,
                "font_size": avg_font_size,
                "is_bold": avg_font_size >= 12,
                "line_count": len(block_text)
            })

    sections = detect_sections(blocks)
    identity = extract_identity(blocks)

    return {
        "resume_id": str(uuid.uuid4()),
        "schema_version": "1.0",
        "identity": identity,
        "experience": sections.get("experience", []),
        "projects": sections.get("projects", []),
        "education": sections.get("education", []),
        "skills": sections.get("skills", {}),
        "analysis": {},
        "render_preferences": {
            "template": "classic",
            "font_size": 10,
            "margins": [1.5, 1.5, 1.8, 1.8]
        },
        "_layout_blocks": blocks
    }

def extract_with_ocr(pdf_path):
    """
    OCR fallback pipeline for scanned resumes.
    Produces a minimal resume_v1 object.
    """

    from pdf2image import convert_from_path
    import pytesseract

    images = convert_from_path(pdf_path)

    text = "\n".join(
        pytesseract.image_to_string(img)
        for img in images
    )

    # Minimal fake block structure
    blocks = []

    for idx, line in enumerate(text.splitlines()):
        cleaned = line.strip()

        if cleaned:
            blocks.append({
                "page": 0,
                "text": cleaned,
                "bbox": [0, idx * 10, 100, (idx + 1) * 10],
                "font": "ocr",
                "size": 10,
                "flags": 0,
                "color": 0
            })

    sections = detect_sections(blocks)
    identity = extract_identity(blocks)

    return {
        "resume_id": str(uuid.uuid4()),
        "schema_version": "1.0",
        "identity": identity,
        "experience": sections.get("experience", []),
        "projects": sections.get("projects", []),
        "education": sections.get("education", []),
        "skills": sections.get("skills", {}),
        "analysis": {},
        "render_preferences": {
            "template": "classic",
            "font_size": 10,
            "margins": [1.5, 1.5, 1.8, 1.8]
        },
        "_layout_blocks": blocks
    }