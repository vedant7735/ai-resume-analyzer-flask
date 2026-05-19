import PyPDF2
import re

def extract_resume_text(pdf_path):
    """Extract text and hyperlinks from resume PDF, with raw debug logging."""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                
                # Extract Hyperlinks
                links = []
                if '/Annots' in page:
                    for annot in page['/Annots']:
                        obj = annot.get_object()
                        if '/A' in obj and '/URI' in obj['/A']:
                            url = obj['/A']['/URI']
                            links.append(url)
                
                text += page_text + "\n"
                if links:
                    text += "\n### EXTRACTED LINKS ###\n"
                    for link in links:
                        text += f"- {link}\n"
                        
            # DEBUG - print raw text to terminal
            # print("\n" + "="*20 + " RAW TEXT (REPR) " + "="*20)
            # print(repr(text))
            # print("="*57 + "\n")
            
            return text
            
    except Exception as e:
        raise Exception(f"Error extracting text: {str(e)}")

def clean_resume_text(raw_text):
    """Clean and structure raw PDF text for LLM processing"""
    
    text = raw_text
    
    # ---- Fix Encoding Issues ----
    text = fix_encoding(text)
    
    # ---- Fix Broken Words ----
    text = fix_hyphenation(text)
    
    # ---- Fix Whitespace ----
    text = fix_whitespace(text)
    
    # ---- Fix Bullets ----
    text = fix_bullets(text)
    
    # ---- Fix Section Headers ----
    text = fix_sections(text)
    
    return text.strip()


def fix_encoding(text):
    """Fix common encoding issues"""
    
    replacements = {
        'â€™': "'",
        'â€œ': '"',
        'â€':  '"',
        'â€"': '-',
        'â€"': '--',
        'Â·':  '-',
        '\x00': '',        # Null bytes
        '\uf0b7': '-',     # Common bullet in PDFs
        '\uf0a7': '-',
        '\u2022': '-',     # Bullet •
        '\u2019': "'",     # Right single quote
        '\u2018': "'",     # Left single quote
        '\u201c': '"',     # Left double quote
        '\u201d': '"',     # Right double quote
        '\u2013': '-',     # En dash
        '\u2014': '--',    # Em dash
        '\u00a0': ' ',     # Non-breaking space
    }
    
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    
    return text


def fix_hyphenation(text):
    """Fix words broken across lines by hyphenation"""
    
    # e.g., "man-\nagement" -> "management"
    text = re.sub(r'-\n(\w)', r'\1', text)
    
    return text


def fix_whitespace(text):
    """Fix spacing and newline issues"""
    
    # Remove carriage returns
    text = text.replace('\r', '\n')
    
    # Fix lines that are just spaces
    text = re.sub(r'^\s+$', '', text, flags=re.MULTILINE)
    
    # Collapse more than 2 newlines into 2
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Fix multiple spaces into one
    text = re.sub(r' {2,}', ' ', text)
    
    # Fix space before punctuation
    text = re.sub(r' ([.,;:!?])', r'\1', text)
    
    return text


def fix_bullets(text):
    """Standardize bullet points"""
    
    # Replace all bullet symbols with a standard dash
    text = re.sub(r'^[\s]*[●•◦▪▸➢✓✔*]\s*', '- ', text, flags=re.MULTILINE)
    
    return text


def fix_sections(text):
    """Detect and normalize section headers"""
    
    # Common resume section headers
    common_sections = [
        'experience', 'work experience', 'professional experience',
        'education', 'academic background',
        'skills', 'technical skills', 'core competencies',
        'projects', 'personal projects',
        'certifications', 'certificates',
        'summary', 'objective', 'profile', 'about',
        'languages', 'interests', 'hobbies',
        'awards', 'achievements', 'accomplishments',
        'volunteer', 'volunteering',
        'publications', 'references'
    ]
    
    # If a line matches a section header, make it uppercase and add separator
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        stripped = line.strip()
        if stripped.lower() in common_sections:
            cleaned_lines.append(f"\n\n### {stripped.upper()} ###\n")
        else:
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)