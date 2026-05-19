import re

# The ultimate source of truth for section names
SECTION_MAPPING = {
    "education": ["education", "academic background", "academics", "educational qualifications"],
    "projects": ["projects", "personal projects", "academic projects", "key projects"],
    "skills": ["skills", "technical skills", "core competencies", "technologies", "tech stack", "expertise"],
    "experience": ["experience", "work experience", "professional experience", "employment history"],
    "workshops": ["workshops", "certifications", "certificates", "courses", "training"]
}

def normalize_header(raw_header):
    """Translates a wild header into our strict JSON keys."""
    raw_header = raw_header.lower().strip()
    for canonical_key, aliases in SECTION_MAPPING.items():
        if raw_header in aliases:
            return canonical_key
    return raw_header

def parse_identity(preamble, full_text):
    identity = {
        "name": "",
        "email": "",
        "phone": "",
        "links": []
    }
    
    # 1. Extract Name (usually the very first non-empty line of the resume)
    lines = [line.strip() for line in preamble.split('\n') if line.strip()]
    if lines:
        identity["name"] = lines[0] # Assumes first line is the name
        
    # 2. Extract Email using Regex
    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', full_text)
    if email_match:
        identity["email"] = email_match.group(0)
        
    # 3. Extract Phone Number using Regex (Handles standard formats & country codes)
    phone_match = re.search(r'\+?\d[\d\s\-\(\)]{7,14}\d', preamble)
    if phone_match:
        identity["phone"] = phone_match.group(0).strip()
        
    # 4. Extract URLs (LinkedIn, GitHub, Portfolios)
    # This looks for http, https, or www.
    urls = re.findall(r'(https?://[^\s]+|www\.[^\s]+)', full_text)
    
    # Filter out empty strings and clean up the list
    identity["links"] = list(set([url for url in urls if url]))
    
    return identity


def build_local_json(cleaned_text):
    resume_data = {
        "identity": {},
        "education": [],
        "projects": [],
        "skills": [],
        "experience": [],
        "workshops": [],
        "raw_sections": {}
    }
    
    # 1. Extract the Identity (Preamble) before the first header
    # Find where the first ### header starts
    first_header_match = re.search(r'###\s*(.*?)\s*###', cleaned_text)
    
    if first_header_match:
        # Grab everything from the start of the text up to the first header
        preamble = cleaned_text[:first_header_match.start()].strip()
    else:
        preamble = cleaned_text # If no headers exist, the whole text is preamble
        
    # Send the preamble to a new parser function
    resume_data["identity"] = parse_identity(preamble, cleaned_text)

    # Regex Breakdown:
    # ###\s*(.*?)\s*### -> Matches the header (e.g., "### PROJECTS ###") and captures "PROJECTS"
    # \n([\s\S]*?)       -> Captures all the multiline content below it
    # (?=\n###|$)        -> Looks ahead to stop capturing when it sees the next "\n###" OR the end of the string
    pattern = r'###\s*(.*?)\s*###\n([\s\S]*?)(?=\n###|$)'
    
    matches = re.finditer(pattern, cleaned_text)
    
    for match in matches:
        raw_header = match.group(1).strip()
        content = match.group(2).strip()
        
        if not content:
            continue
            
        standardized_header = normalize_header(raw_header)
        
        # Route the extracted data
        if standardized_header == "projects":
            resume_data["projects"] = parse_projects_block(content)
        elif standardized_header == "skills":
            resume_data["raw_sections"]["skills_raw"] = content # Temp placeholder
        elif standardized_header in resume_data:
            resume_data[standardized_header] = content
        else:
            resume_data["raw_sections"][standardized_header] = content

    return resume_data

# Add this temporarily in app.py to debug
def extract_resume_text(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            # DEBUG - print raw text
            # print("=== RAW TEXT ===")
            # print(repr(text))  # repr() shows hidden characters like \n \t etc
            # print("=== END RAW TEXT ===")
            
            return text
    except Exception as e:
        raise Exception(f"Error extracting text: {str(e)}")

def parse_projects_block(content):
    """
    Parse projects based on actual PDF structure:
    - Title line: contains a year (2024, 2025, 2026 etc)
    - Tech line: contains a pipe '|'
    - Bullet: starts with •
    - Wrapped bullet: plain text that continues previous bullet
    """
    
    projects = []
    current_project = None
    current_bullet = None
    
    # Clean and split into lines
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    
    def is_title_line(line):
        """Title lines have a year at the end"""
        return bool(re.search(r'\b(20\d{2})\b', line))
    
    def is_tech_line(line):
        """Tech lines contain a pipe character"""
        return '|' in line
    
    def is_bullet_line(line):
        """Bullet lines start with • or -"""
        return line.startswith('•') or line.startswith('-')
    
    def clean_bullet(line):
        """Remove bullet character and clean"""
        return re.sub(r'^[•\-\s]+', '', line).strip()
    
    def fix_hyphenation(text):
        """Fix broken hyphenated words e.g 'minim ize' -> 'minimize'"""
        # Fix space in middle of word caused by PDF
        text = re.sub(r'(\w+) ize\b', r'\1ize', text)
        text = re.sub(r'(\w+) -based', r'\1-based', text)
        text = re.sub(r'(\w) -', r'\1-', text)
        return text
    
    for line in lines:
        
        # ---- New Project Title Detected ----
        if is_title_line(line) and not is_tech_line(line):
            
            # Save previous bullet before moving on
            if current_bullet and current_project is not None:
                current_project['details'].append(fix_hyphenation(current_bullet))
                current_bullet = None
            
            # Save previous project before starting new one
            if current_project is not None:
                projects.append(current_project)
            
            # Start new project
            current_project = {
                'title': re.sub(r'\s+\d{4}.*$', '', line).strip(),  # Remove year from title
                'year': re.search(r'\b(20\d{2}.*?)$', line).group(1).strip(),
                'type': '',
                'tech_stack': [],
                'details': []
            }
        
        # ---- Tech Stack Line ----
        elif is_tech_line(line) and current_project is not None:
            parts = line.split('|')
            current_project['type'] = parts[0].strip()          # e.g "Academic Project"
            current_project['tech_stack'] = [                   # e.g ["Python", "Flask"]
                t.strip() for t in parts[1].split(',')
            ]
        
        # ---- Bullet Point ----
        elif is_bullet_line(line) and current_project is not None:
            
            # Save previous bullet
            if current_bullet:
                current_project['details'].append(fix_hyphenation(current_bullet))
            
            # Start new bullet
            current_bullet = clean_bullet(line)
        
        # ---- Wrapped Line (continuation of previous bullet) ----
        elif current_bullet is not None and current_project is not None:
            current_bullet += ' ' + line
    
    # ---- Save Last Bullet and Last Project ----
    if current_bullet and current_project is not None:
        current_project['details'].append(fix_hyphenation(current_bullet))
    
    if current_project is not None:
        projects.append(current_project)
    
    return projects