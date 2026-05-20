This file is a merged representation of the entire codebase, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
app.py
cleaner.py
images/landing.png
images/recommendation.png
images/score.png
images/summary.png
README.md
requirements.txt
services/__init__.py
services/cache_service.py
services/cleaner_service.py
services/latex_service.py
services/llm_service.py
services/pdf_service.py
templates/index.html
templates/script.js
templates/styles.css
```

# Files

## File: services/__init__.py
````python
# Services package initialization
````

## File: services/cache_service.py
````python
# Caching Service
# This service will handle caching and loading analysis results to save on API usage.
import os
import json
import hashlib


def get_file_hash(filepath):
    """Generate SHA256 hash of file"""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for block in iter(lambda: f.read(4096), b""):
            sha256.update(block)
    return sha256.hexdigest()


def get_cached_analysis(file_hash, cache_folder='cache'):
    """Get cached analysis if exists"""
    
    os.makedirs(cache_folder, exist_ok=True)
    cache_file = os.path.join(cache_folder, f"{file_hash}.json")
    
    if os.path.exists(cache_file):
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return None


def save_to_cache(file_hash, data, cache_folder='cache'):
    """Save analysis to cache"""
    
    os.makedirs(cache_folder, exist_ok=True)
    cache_file = os.path.join(cache_folder, f"{file_hash}.json")
    
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
````

## File: services/cleaner_service.py
````python
# Text Cleaning Service
# This service will handle cleaning, encoding fixes, and structure mapping of raw resume text.
from cleaner import clean_resume_text

def clean_text(raw_text):
    """
    Clean raw PDF text using your existing cleaner function.
    Wraps cleaner.clean_resume_text() for service layer.
    """
    return clean_resume_text(raw_text)
````

## File: services/latex_service.py
````python
import os
import uuid
import subprocess
import shutil
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# ===== BASE TEMPLATE (extracted from original PDF structure) =====

BASE_TEMPLATE = r"""
\documentclass[10pt, letterpaper]{article}

\usepackage[
    ignoreheadfoot,
    top=1.5cm,
    bottom=1.5cm,
    left=1.8cm,
    right=1.8cm,
    footskip=0.9cm,
]{geometry}
\usepackage{titlesec}
\usepackage{array}
\usepackage{enumitem}
\usepackage[colorlinks=false, hidelinks]{hyperref}
\usepackage{iftex}

\ifPDFTeX
    \input{glyphtounicode}
    \pdfgentounicode=1
    \usepackage[T1]{fontenc}
    \usepackage[utf8]{inputenc}
    \usepackage{lmodern}
\fi

\pagestyle{empty}
\setcounter{secnumdepth}{0}
\setlength{\parindent}{0pt}
\pagenumbering{gobble}

\titleformat{\section}
    {\normalsize\bfseries\uppercase}
    {}
    {0pt}
    {}
    [\vspace{1pt}\titlerule\vspace{4pt}]
\titlespacing{\section}{0pt}{8pt}{4pt}

\setlist[itemize]{
    leftmargin=*,
    label=\textbullet,
    itemsep=1pt,
    parsep=0pt,
    topsep=2pt,
}

\begin{document}

{{HEADER}}

{{SUMMARY}}

{{EXPERIENCE}}

{{PROJECTS}}

{{EDUCATION}}

{{SKILLS}}

\end{document}
"""


# ===== LLM PROMPT (Section Improvements Only) =====

IMPROVEMENT_PROMPT = """
You are a professional resume writer. You will receive resume sections and improvement suggestions.

Your job is to return ONLY the improved sections in plain text format.

Use this exact format for each section:

[SUMMARY]
Improved 2-3 sentence summary applying all suggestions.

[EXPERIENCE_ITEM]
Job Title
Company Name | Duration | Employment Type
• Improved bullet with quantified metric
• Another improved bullet with metric
• Third improved bullet

[EXPERIENCE_ITEM]
[Repeat for each job]

[PROJECT_ITEM]
Project Title
Tech Stack: Python, Flask | Year: 2024
• Improved bullet with quantified metric
• Another improved bullet

[PROJECT_ITEM]
[Repeat for each project]

[EDUCATION_ITEM]
Degree in Major
Institution | Year | GPA: X.X/4.0

[SKILLS]
Languages: Python, JavaScript, SQL
Frameworks: Flask, Django, React
Tools: Git, Docker, AWS
Domains: Machine Learning, Data Engineering

RULES:
1. Apply ALL improvement suggestions
2. Add quantified metrics to every bullet (numbers, percentages, scale)
3. Use strong action verbs
4. Keep bullets under 20 words
5. Use • for bullets
6. Use | for separators
7. Do NOT change the structure, only improve content
"""


def generate_improved_latex(resume_data, original_extracted_text):
    """
    Strategy:
    1. Extract original LaTeX structure from PDF text
    2. LLM improves ONLY the content
    3. Replace content in original structure
    4. Return improved .tex
    """

    try:
        # Step 1: Get improvements from LLM
        data_str = format_resume_data(resume_data)

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": IMPROVEMENT_PROMPT},
                {"role": "user", "content": f"Improve these sections:\n\n{data_str}"}
            ],
            temperature=0.2
        )

        improved_text = response.choices[0].message.content.strip()

        # Step 2: Parse improvements
        improvements = parse_improvements(improved_text)

        # Step 3: Build LaTeX with improvements
        latex_code = build_improved_latex(resume_data, improvements)

        return latex_code

    except Exception as e:
        raise Exception(f"LaTeX improvement failed: {str(e)}")


def parse_improvements(text):
    """Parse LLM-improved sections"""
    import re

    improvements = {}

    # Extract summary
    summary_match = re.search(r'\[SUMMARY\]\s*\n(.+?)(?=\n\[|\Z)', text, re.DOTALL)
    if summary_match:
        improvements['summary'] = summary_match.group(1).strip()

    # Extract experience items
    improvements['experience'] = []
    exp_items = re.findall(
        r'\[EXPERIENCE_ITEM\]\s*\n(.+?)(?=\n\[EXPERIENCE_ITEM\]|\n\[PROJECT_ITEM\]|\n\[EDUCATION_ITEM\]|\n\[SKILLS\]|\Z)',
        text,
        re.DOTALL
    )
    for item in exp_items:
        lines = [l.strip() for l in item.strip().split('\n') if l.strip()]
        if len(lines) >= 2:
            title = lines[0]
            meta_line = lines[1]
            meta_parts = meta_line.split('|')

            company = meta_parts[0].strip() if len(meta_parts) > 0 else ''
            duration = meta_parts[1].strip() if len(meta_parts) > 1 else ''
            emp_type = meta_parts[2].strip() if len(meta_parts) > 2 else ''

            bullets = [l[2:].strip() for l in lines[2:] if l.startswith('•')]

            improvements['experience'].append({
                'title': title,
                'company': company,
                'duration': duration,
                'type': emp_type,
                'bullets': bullets
            })

    # Extract project items
    improvements['projects'] = []
    proj_items = re.findall(
        r'\[PROJECT_ITEM\]\s*\n(.+?)(?=\n\[PROJECT_ITEM\]|\n\[EDUCATION_ITEM\]|\n\[SKILLS\]|\Z)',
        text,
        re.DOTALL
    )
    for item in proj_items:
        lines = [l.strip() for l in item.strip().split('\n') if l.strip()]
        if len(lines) >= 2:
            title = lines[0]
            meta_line = lines[1]

            tech_match = re.search(r'Tech Stack:\s*(.+?)(?:\s*\||\Z)', meta_line)
            year_match = re.search(r'Year:\s*(.+?)(?:\s*\||\Z)', meta_line)

            tech = tech_match.group(1).strip() if tech_match else ''
            year = year_match.group(1).strip() if year_match else ''

            bullets = [l[2:].strip() for l in lines[2:] if l.startswith('•')]

            improvements['projects'].append({
                'title': title,
                'tech': tech,
                'year': year,
                'bullets': bullets
            })

    # Extract skills
    skills_match = re.search(r'\[SKILLS\]\s*\n(.+?)(?=\n\[|\Z)', text, re.DOTALL)
    if skills_match:
        improvements['skills'] = {}
        for line in skills_match.group(1).split('\n'):
            if ':' in line:
                parts = line.split(':', 1)
                cat = parts[0].strip()
                items = parts[1].strip()
                improvements['skills'][cat] = items

    return improvements


def escape_latex(text):
    """Escape special LaTeX characters.
    
    Order matters: backslash must be handled first via a placeholder
    to prevent double-escaping of braces inserted by other replacements.
    """
    if not text:
        return ''

    # Step 1: Replace literal backslashes with a unique placeholder
    BACKSLASH_PLACEHOLDER = '\x00BACKSLASH\x00'
    text = text.replace('\\', BACKSLASH_PLACEHOLDER)

    # Step 2: Escape all other special characters (order doesn't matter here)
    text = text.replace('&',  r'\&')
    text = text.replace('%',  r'\%')
    text = text.replace('$',  r'\$')
    text = text.replace('#',  r'\#')
    text = text.replace('_',  r'\_')
    text = text.replace('{',  r'\{')
    text = text.replace('}',  r'\}')
    text = text.replace('~',  r'\textasciitilde{}')
    text = text.replace('^',  r'\textasciicircum{}')

    # Step 3: Now replace the placeholder with the final LaTeX backslash command
    # This is done last so the braces in \textbackslash{} are NOT re-escaped
    text = text.replace(BACKSLASH_PLACEHOLDER, r'\textbackslash{}')

    return text


def ensure_url(url):
    """Ensure a URL has a protocol prefix, avoiding double https://"""
    if not url:
        return ''
    if url.startswith('http://') or url.startswith('https://'):
        return url
    return 'https://' + url


def display_url(url):
    """Strip protocol prefix for cleaner display text"""
    if not url:
        return ''
    return url.replace('https://', '').replace('http://', '')


def build_improved_latex(resume_data, improvements):
    """Build LaTeX using original structure + improved content"""

    identity = resume_data.get('identity', {})

    # Build header
    email = identity.get('email', '')
    phone = identity.get('phone', '')
    linkedin = identity.get('linkedin', '')
    github = identity.get('github', '')
    portfolio = identity.get('portfolio', '')

    header = r"""\begin{center}
    {\LARGE\bfseries """ + escape_latex(identity.get('name', '').upper()) + r"""} \\[4pt]
    \small
    \href{mailto:""" + email + r"""}{""" + email + r"""} \textbar{} """ + escape_latex(phone) + r""" \textbar{} \href{""" + ensure_url(linkedin) + r"""}{""" + display_url(linkedin) + r"""}"""

    if github:
        header += r""" \textbar{} \href{""" + ensure_url(github) + r"""}{""" + display_url(github) + r"""}"""

    if portfolio:
        header += r""" \textbar{} \href{""" + ensure_url(portfolio) + r"""}{""" + display_url(portfolio) + r"""}"""

    header += r"""
\end{center}
\vspace{4pt}"""

    # Build summary
    summary = r"""\section{Summary}
""" + escape_latex(improvements.get('summary', '')) + "\n"

    # Build experience
    experience = r"""\section{Experience}
"""
    for exp in improvements.get('experience', []):
        experience += r"""\noindent\textbf{""" + escape_latex(exp['title']) + r"""} \hfill \texttt{\small """ + escape_latex(exp['duration']) + r"""} \\
\textit{\small """ + escape_latex(exp['company']) + r"""} \hfill \texttt{\small """ + escape_latex(exp['type']) + r"""}
\begin{itemize}
"""
        for bullet in exp['bullets']:
            experience += r"""  \item """ + escape_latex(bullet) + "\n"

        experience += r"""\end{itemize}
\vspace{4pt}

"""

    # Build projects
    projects = r"""\section{Projects}
"""
    for proj in improvements.get('projects', []):
        projects += r"""\noindent\textbf{""" + escape_latex(proj['title']) + r"""} \hfill \texttt{\small """ + escape_latex(proj['year']) + r"""} \\
\texttt{\small """ + escape_latex(proj['tech']) + r"""}
\begin{itemize}
"""
        for bullet in proj['bullets']:
            projects += r"""  \item """ + escape_latex(bullet) + "\n"

        projects += r"""\end{itemize}
\vspace{4pt}

"""

    # Build education
    education = r"""\section{Education}
"""
    for edu in resume_data.get('education', []):
        education += r"""\noindent\textbf{""" + escape_latex(edu.get('degree', '') + ' in ' + edu.get('major', '')) + r"""} \hfill \texttt{\small """ + escape_latex(edu.get('graduation_year', '')) + r"""} \\
\textit{\small """ + escape_latex(edu.get('institution', '')) + r"""}"""
        if edu.get('gpa'):
            education += r""" \\ \texttt{\small GPA: """ + escape_latex(edu.get('gpa', '')) + r"""}"""
        education += r"""
\vspace{4pt}

"""

    # Build skills
    skills = r"""\section{Technical Skills}
\begin{tabular}{@{}p{2.8cm} p{12.5cm}@{}}
"""
    for cat, items in improvements.get('skills', {}).items():
        skills += r"""\texttt{\small\bfseries """ + escape_latex(cat).upper() + r"""} & \small """ + escape_latex(items) + r""" \\[2pt]
"""
    skills += r"""\end{tabular}"""

    # Combine all
    latex = BASE_TEMPLATE
    latex = latex.replace('{{HEADER}}', header)
    latex = latex.replace('{{SUMMARY}}', summary)
    latex = latex.replace('{{EXPERIENCE}}', experience)
    latex = latex.replace('{{PROJECTS}}', projects)
    latex = latex.replace('{{EDUCATION}}', education)
    latex = latex.replace('{{SKILLS}}', skills)

    return latex


def compile_latex_to_pdf(tex_filepath):
    """
    Compile .tex to .pdf using pdflatex
    Returns path to generated PDF
    """

    try:
        # Check if pdflatex is available
        if not shutil.which('pdflatex'):
            raise Exception("pdflatex not installed. Install texlive-latex-base")

        # Get directory and filename
        tex_dir = os.path.dirname(tex_filepath)
        tex_filename = os.path.basename(tex_filepath)

        # Run pdflatex twice (for proper references)
        for i in range(2):
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', tex_filename],
                cwd=tex_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=120  # MiKTeX auto-installs packages on first run, needs extra time
            )

        # Check if PDF was actually produced (don't rely on exit code —
        # MiKTeX returns non-zero for warnings like "check for updates")
        pdf_path = tex_filepath.replace('.tex', '.pdf')

        if not os.path.exists(pdf_path):
            raise Exception("PDF not generated")

        # Clean up auxiliary files
        for ext in ['.aux', '.log', '.out']:
            aux_file = tex_filepath.replace('.tex', ext)
            if os.path.exists(aux_file):
                os.remove(aux_file)

        return pdf_path

    except subprocess.TimeoutExpired:
        _cleanup_aux_files(tex_filepath)
        raise Exception("LaTeX compilation timeout")
    except Exception as e:
        _cleanup_aux_files(tex_filepath)
        raise Exception(f"PDF compilation failed: {str(e)}")


def _cleanup_aux_files(tex_filepath):
    """Remove auxiliary files left behind by failed compilations"""
    for ext in ['.aux', '.log', '.out']:
        aux_file = tex_filepath.replace('.tex', ext)
        if os.path.exists(aux_file):
            try:
                os.remove(aux_file)
            except OSError:
                pass


def save_latex_and_pdf(latex_code, output_folder='generated'):
    """
    Save LaTeX and compile to PDF
    Returns both file paths
    """

    os.makedirs(output_folder, exist_ok=True)

    file_id = str(uuid.uuid4())
    tex_filename = f"resume_{file_id}.tex"
    tex_filepath = os.path.join(output_folder, tex_filename)

    # Save .tex
    with open(tex_filepath, 'w', encoding='utf-8') as f:
        f.write(latex_code)

    # Compile to .pdf
    try:
        pdf_filepath = compile_latex_to_pdf(tex_filepath)
        pdf_filename = os.path.basename(pdf_filepath)
    except Exception as e:
        print(f"Warning: PDF compilation failed: {e}")
        pdf_filepath = None
        pdf_filename = None

    return {
        'file_id': file_id,
        'tex_filename': tex_filename,
        'tex_filepath': tex_filepath,
        'pdf_filename': pdf_filename,
        'pdf_filepath': pdf_filepath
    }


def format_resume_data(resume_data):
    """Format resume data for LLM"""

    identity = resume_data.get('identity', {})
    analysis = resume_data.get('analysis', {})

    data_str = f"""
IMPROVEMENTS TO APPLY:
"""

    for imp in analysis.get('improvements', []):
        data_str += f"\n[{imp['section']}] {imp['issue']} -> {imp['suggestion']}"

    data_str += "\n\nCURRENT SUMMARY:\n"
    data_str += analysis.get('professional_summary', '')

    data_str += "\n\nCURRENT EXPERIENCE:\n"
    for exp in resume_data.get('experience', []):
        title = exp.get('title', '')
        company = exp.get('company', '')
        duration = exp.get('duration', '')
        job_type = exp.get('type', '')
        data_str += f"\n{title} at {company} ({duration}) - {job_type}\n"
        for resp in exp.get('responsibilities', []):
            data_str += f"  - {resp}\n"

    data_str += "\n\nCURRENT PROJECTS:\n"
    for proj in resume_data.get('projects', []):
        data_str += f"\n{proj.get('title', '')} ({proj.get('year', '')}) - {', '.join(proj.get('tech_stack', []))}\n"
        for detail in proj.get('details', []):
            data_str += f"  - {detail}\n"

    data_str += "\n\nCURRENT SKILLS:\n"
    skills = resume_data.get('skills', {})
    data_str += f"Languages: {', '.join(skills.get('languages', []))}\n"
    data_str += f"Frameworks: {', '.join(skills.get('frameworks', []))}\n"
    data_str += f"Tools: {', '.join(skills.get('tools', []))}\n"
    data_str += f"Domains: {', '.join(skills.get('domains', []))}\n"

    return data_str
````

## File: services/llm_service.py
````python
# LLM Analysis Service
# This service will manage OpenAI/Groq client API calls for analyzing resume text.
import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

ANALYSIS_PROMPT = """
You are an AI resume analyzer. Your job is to parse resume text and provide a comprehensive analysis in strict JSON format.

## Your Task:
1. **Extract** all structured information (identity, projects, education, experience, workshops, skills)
2. **Analyze** the content quality and completeness
3. **Generate** a professional summary
4. **Suggest** specific improvements
5. **Calculate** an overall resume score

## Output Format (strict JSON):

{
  "identity": {
    "name": "Full Name",
    "email": "email@domain.com",
    "phone": "+1234567890",
    "linkedin": "linkedin.com/in/username",
    "github": "github.com/username",
    "portfolio": "website.com",
    "location": "City, Country"
  },
  
  "projects": [
    {
      "title": "Project Name",
      "type": "Academic Project | Personal Project | Research | Open Source",
      "year": "2024 | 2024 - 2025 | May 2024 - Aug 2024",
      "tech_stack": ["Python", "Flask", "React"],
      "details": [
        "Achievement-focused bullet point with metrics",
        "Another specific accomplishment"
      ]
    }
  ],
  
  "experience": [
    {
      "title": "Job Title",
      "company": "Company Name",
      "location": "City, Country",
      "duration": "May 2024 - Aug 2024 | Jan 2023 - Present",
      "type": "Full-time | Internship | Part-time | Contract",
      "responsibilities": [
        "Quantified achievement with impact",
        "Specific contribution with results"
      ]
    }
  ],
  
  "education": [
    {
      "degree": "Bachelor of Technology | Master of Science",
      "major": "Computer Science",
      "institution": "University Name",
      "location": "City, Country",
      "graduation_year": "2026",
      "gpa": "3.8/4.0",
      "relevant_coursework": ["Course 1", "Course 2"]
    }
  ],
  
  "workshops": [
    {
      "title": "Workshop Name",
      "year": "2024",
      "description": "Brief description of what was learned or built"
    }
  ],
  
  "skills": {
    "languages": ["Python", "C++", "JavaScript"],
    "frameworks": ["React", "Flask", "TensorFlow"],
    "tools": ["Git", "Docker", "AWS"],
    "domains": ["Machine Learning", "Web Development", "IoT"]
  },
  
  "analysis": {
    "professional_summary": "A concise 2-3 sentence summary highlighting the candidate's strongest skills, experience level, and career focus based on the resume content. Written in third person, professional tone.",
    
    "strengths": [
      "Specific strength observed",
      "Another strength with examples"
    ],
    
    "improvements": [
      {
        "section": "Projects | Experience | Education | Skills | Overall",
        "issue": "Specific problem identified",
        "suggestion": "Actionable fix with example",
        "priority": "High | Medium | Low"
      }
    ],
    
    "score": {
      "overall": 75,
      "breakdown": {
        "content_quality": 80,
        "structure": 70,
        "impact": 75,
        "completeness": 70,
        "formatting": 80
      },
      "explanation": "Brief explanation of the overall score"
    },
    
    "missing_sections": ["Certifications", "Publications"],
    
    "ats_keywords": ["Python", "Machine Learning", "REST API"],
    
    "recommended_for": ["Software Engineer", "ML Engineer", "Backend Developer"]
  }
}

## Scoring Criteria:

**Content Quality (0-100):** Strong action verbs, quantified achievements, technical depth
**Structure (0-100):** Logical organization, consistent formatting
**Impact (0-100):** Demonstrates results and problem-solving
**Completeness (0-100):** All essential sections present
**Formatting (0-100):** Professional language and grammar

**Overall Score:** Weighted average with emphasis on Content Quality (30%) and Impact (30%)

## Important Rules:
1. DO NOT invent information - only extract what's present
2. If section missing, use empty array [] or object {}
3. Be specific and actionable in improvements
4. Return ONLY valid JSON
"""


def analyze_resume(cleaned_text):
    """
    Analyze resume using Groq LLM.
    Returns structured JSON data.
    """
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": ANALYSIS_PROMPT},
                {"role": "user", "content": cleaned_text}
            ],
            temperature=0.0
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        raise Exception(f"LLM analysis failed: {str(e)}")
````

## File: services/pdf_service.py
````python
# PDF Extraction Service
# This service will handle extraction of text and hyperlinks from PDF files.
from cleaner import extract_resume_text

def extract_text_from_pdf(pdf_path):
    """
    Extract text from PDF using your existing cleaner function.
    Wraps cleaner.extract_resume_text() for service layer.
    """
    return extract_resume_text(pdf_path)
````

## File: cleaner.py
````python
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
````

## File: requirements.txt
````
Flask==2.3.0
flask-cors==4.0.0
PyPDF2==3.0.0
groq==0.4.0
python-dotenv==1.0.0
werkzeug==2.3.0
````

## File: templates/script.js
````javascript
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadForm = document.getElementById('uploadForm');
const fileInfo = document.getElementById('fileInfo');
const loading = document.getElementById('loading');
const error = document.getElementById('error');
const uploadContainer = document.getElementById('uploadContainer');
const dashboardContainer = document.getElementById('dashboardContainer');
const uploadNewBtn = document.getElementById('uploadNewBtn');
const submitBtn = document.getElementById('submitBtn');
const dashboardPdfBtn = document.getElementById('dashboardPdfBtn');

let resumeData = null;

// Click to upload
uploadArea.addEventListener('click', (e) => {
    if (e.target !== fileInput) {
        fileInput.click();
    }
});

// File selected
fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        fileInfo.textContent = `Selected: ${file.name} (${(file.size / 1024).toFixed(2)} KB)`;
    }
});

// Drag and drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        fileInput.files = files;
        fileInfo.textContent = `Selected: ${files[0].name} (${(files[0].size / 1024).toFixed(2)} KB)`;
    }
});

// Form submission
uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    error.classList.remove('show');
    loading.classList.add('show');
    submitBtn.disabled = true;

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        loading.classList.remove('show');
        submitBtn.disabled = false;

        if (response.ok && data.success) {
            resumeData = data.data;
            showDashboard(resumeData);
        } else {
            error.textContent = data.error || 'An error occurred';
            error.classList.add('show');
        }

    } catch (err) {
        loading.classList.remove('show');
        submitBtn.disabled = false;
        error.textContent = 'Failed to upload file. Please try again.';
        error.classList.add('show');
    }
});

// Upload new resume
uploadNewBtn.addEventListener('click', () => {
    uploadContainer.style.display = 'flex';
    dashboardContainer.style.display = 'none';
    fileInput.value = '';
    fileInfo.textContent = '';
    resumeData = null;
    dashboardPdfBtn.style.display = 'none';
});

// Show dashboard with data
function showDashboard(data) {
    uploadContainer.style.display = 'none';
    dashboardContainer.style.display = 'block';
    dashboardPdfBtn.style.display = 'none';

    // Populate identity
    document.getElementById('candidateName').textContent = data.identity?.name || 'Unknown Candidate';

    // Populate scores
    const analysis = data.analysis || {};
    const score = analysis.score || {};
    const breakdown = score.breakdown || {};

    document.getElementById('overallScore').textContent = score.overall || '--';
    document.getElementById('scoreExplanation').textContent = score.explanation || '';
    document.getElementById('overallScoreBar').style.width = `${score.overall || 0}%`;

    document.getElementById('contentScore').textContent = breakdown.content_quality || '--';
    document.getElementById('contentBar').style.width = `${breakdown.content_quality || 0}%`;

    document.getElementById('structureScore').textContent = breakdown.structure || '--';
    document.getElementById('structureBar').style.width = `${breakdown.structure || 0}%`;

    document.getElementById('impactScore').textContent = breakdown.impact || '--';
    document.getElementById('impactBar').style.width = `${breakdown.impact || 0}%`;

    document.getElementById('completenessScore').textContent = breakdown.completeness || '--';
    document.getElementById('completenessBar').style.width = `${breakdown.completeness || 0}%`;

    document.getElementById('formattingScore').textContent = breakdown.formatting || '--';
    document.getElementById('formattingBar').style.width = `${breakdown.formatting || 0}%`;

    // Professional summary
    document.getElementById('summaryText').textContent = analysis.professional_summary || 'No summary available.';

    // Strengths
    const strengthsList = document.getElementById('strengthsList');
    strengthsList.innerHTML = '';
    (analysis.strengths || []).forEach(strength => {
        const li = document.createElement('li');
        li.textContent = strength;
        strengthsList.appendChild(li);
    });

    // Improvements - Accordion Style
    const improvementsList = document.getElementById('improvementsList');
    improvementsList.innerHTML = '';
    (analysis.improvements || []).forEach((improvement, index) => {
        const div = document.createElement('div');
        div.className = 'improvement-item';
        if (index === 0) div.classList.add('active'); // First one open by default

        div.innerHTML = `
        <div class="improvement-header">
            <div class="improvement-header-left">
                <span class="improvement-section">${improvement.section}</span>
                <div class="improvement-issue">${improvement.issue}</div>
            </div>
            <div class="improvement-header-right">
                <span class="priority-badge priority-${improvement.priority.toLowerCase()}">${improvement.priority}</span>
                <div class="accordion-icon">▼</div>
            </div>
        </div>
        <div class="improvement-content">
            <div class="improvement-suggestion">${improvement.suggestion}</div>
        </div>`;

        // Add click handler for accordion
        const header = div.querySelector('.improvement-header');
        header.addEventListener('click', () => {
            div.classList.toggle('active');
        });

        improvementsList.appendChild(div);
    });

    // Recommended roles
    const roleTags = document.getElementById('roleTags');
    roleTags.innerHTML = '';
    (analysis.recommended_for || []).forEach(role => {
        const span = document.createElement('span');
        span.className = 'role-tag';
        span.textContent = role;
        roleTags.appendChild(span);
    });

    // ATS Keywords
    const keywordCloud = document.getElementById('keywordCloud');
    keywordCloud.innerHTML = '';
    (analysis.ats_keywords || []).forEach(keyword => {
        const span = document.createElement('span');
        span.className = 'keyword-tag';
        span.textContent = keyword;
        keywordCloud.appendChild(span);
    });

    // Populate tabs
    populateProjectsTab(data.projects || []);
    populateExperienceTab(data.experience || []);
    populateEducationTab(data.education || []);
    populateSkillsTab(data.skills || {});
}

// Tab switching
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const targetTab = btn.dataset.tab;

        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));

        btn.classList.add('active');
        document.getElementById(`tab-${targetTab}`).classList.add('active');
    });
});

function populateProjectsTab(projects) {
    const container = document.getElementById('tab-projects');
    container.innerHTML = '';

    projects.forEach(project => {
        const div = document.createElement('div');
        div.className = 'data-item';

        const techTags = project.tech_stack.map(tech =>
            `<span class="data-tag">${tech}</span>`
        ).join('');

        const details = project.details.map(detail =>
            `<li>${detail}</li>`
        ).join('');

        div.innerHTML = `
            <div class="data-item-header">
                <div class="data-title">${project.title}</div>
                <div class="data-meta">${project.type} • ${project.year}</div>
            </div>
            <div class="data-tags">${techTags}</div>
            <ul class="data-details">${details}</ul>
        `;

        container.appendChild(div);
    });
}

function populateExperienceTab(experiences) {
    const container = document.getElementById('tab-experience');
    container.innerHTML = '';

    experiences.forEach(exp => {
        const div = document.createElement('div');
        div.className = 'data-item';

        const responsibilities = exp.responsibilities.map(resp =>
            `<li>${resp}</li>`
        ).join('');

        div.innerHTML = `
            <div class="data-item-header">
                <div class="data-title">${exp.title}</div>
                <div class="data-meta">${exp.company} • ${exp.duration} • ${exp.type}</div>
            </div>
            <ul class="data-details">${responsibilities}</ul>
        `;

        container.appendChild(div);
    });
}

function populateEducationTab(education) {
    const container = document.getElementById('tab-education');
    container.innerHTML = '';

    education.forEach(edu => {
        const div = document.createElement('div');
        div.className = 'data-item';

        const coursework = edu.relevant_coursework?.map(course =>
            `<span class="data-tag">${course}</span>`
        ).join('') || '';

        div.innerHTML = `
            <div class="data-item-header">
                <div class="data-title">${edu.degree} in ${edu.major}</div>
                <div class="data-meta">${edu.institution} • ${edu.graduation_year} • GPA: ${edu.gpa}</div>
            </div>
            ${coursework ? `<div class="data-tags">${coursework}</div>` : ''}
        `;

        container.appendChild(div);
    });
}

function populateSkillsTab(skills) {
    const container = document.getElementById('tab-skills');
    container.innerHTML = '';

    const categories = [
        { title: 'Languages', data: skills.languages || [] },
        { title: 'Frameworks', data: skills.frameworks || [] },
        { title: 'Tools', data: skills.tools || [] },
        { title: 'Domains', data: skills.domains || [] }
    ];

    categories.forEach(cat => {
        if (cat.data.length > 0) {
            const div = document.createElement('div');
            div.className = 'data-item';

            const tags = cat.data.map(item =>
                `<span class="data-tag">${item}</span>`
            ).join('');

            div.innerHTML = `
                <div class="data-title">${cat.title}</div>
                <div class="data-tags">${tags}</div>
            `;

            container.appendChild(div);
        }
    });
}

// ===== LATEX EDITOR FUNCTIONALITY =====

const downloadLatexBtn = document.getElementById('downloadLatexBtn');
const latexModal = document.getElementById('latexModal');
const closeModal = document.getElementById('closeModal');
const latexEditor = document.getElementById('latexEditor');
const resetBtn = document.getElementById('resetBtn');
const downloadEditedBtn = document.getElementById('downloadEditedBtn');
const editorStatus = document.getElementById('editorStatus');
const lineCount = document.getElementById('lineCount');
const charCount = document.getElementById('charCount');

let originalLatexCode = '';
let currentFileId = null;

// Download LaTeX (generates code and opens editor)
downloadLatexBtn.addEventListener('click', async () => {
    if (!resumeData) return;

    downloadLatexBtn.disabled = true;
    downloadLatexBtn.innerHTML = '<span class="btn-text">⏳ GENERATING...</span>';
    editorStatus.textContent = 'Generating LaTeX...';

    try {
        const response = await fetch('/generate-latex', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ resume_data: resumeData })
        });

        const data = await response.json();

        if (data.success) {
            currentFileId = data.file_id;

            // Fetch the generated file content (.tex)
            const fileResponse = await fetch(`/download-latex/${data.file_id}`);
            const latexCode = await fileResponse.text();

            // Store original and show editor
            originalLatexCode = latexCode;
            latexEditor.value = latexCode;
            updateEditorStats();

            // Show modal
            latexModal.classList.add('show');
            editorStatus.textContent = 'Ready to edit';

            // Show/hide PDF download buttons based on availability
            if (data.pdf_available) {
                showPdfDownloadButton(data.file_id);
                dashboardPdfBtn.style.display = 'block';
            } else {
                const pdfBtn = document.getElementById('downloadPdfBtn');
                if (pdfBtn) {
                    pdfBtn.style.display = 'none';
                }
                dashboardPdfBtn.style.display = 'none';
            }

        } else {
            alert('Failed to generate LaTeX: ' + (data.error || 'Unknown error'));
            editorStatus.textContent = 'Generation failed';
        }

    } catch (err) {
        console.error(err);
        alert('Error generating files');
        editorStatus.textContent = 'Error';
    } finally {
        downloadLatexBtn.disabled = false;
        downloadLatexBtn.innerHTML = '<span class="btn-text">↓ DOWNLOAD .TEX</span>';
    }
});

// Download compiled PDF from dashboard
dashboardPdfBtn.addEventListener('click', () => {
    if (currentFileId) {
        window.location.href = `/download-pdf/${currentFileId}`;
    }
});

// Close modal
closeModal.addEventListener('click', () => {
    latexModal.classList.remove('show');
});

// Close on overlay click
latexModal.addEventListener('click', (e) => {
    if (e.target === latexModal) {
        latexModal.classList.remove('show');
    }
});

// Reset to original
resetBtn.addEventListener('click', () => {
    if (confirm('Reset to original generated code?')) {
        latexEditor.value = originalLatexCode;
        updateEditorStats();
        editorStatus.textContent = 'Reset to original';
    }
});

// Download edited version
downloadEditedBtn.addEventListener('click', () => {
    const editedCode = latexEditor.value;

    // Create blob and download
    const blob = new Blob([editedCode], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `resume_edited_${Date.now()}.tex`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    editorStatus.textContent = 'Downloaded';
    setTimeout(() => {
        editorStatus.textContent = 'Ready to edit';
    }, 2000);
});

function showPdfDownloadButton(fileId) {
    // Add PDF download button to toolbar
    const toolbar = document.querySelector('.editor-toolbar');

    let pdfBtn = document.getElementById('downloadPdfBtn');
    if (!pdfBtn) {
        pdfBtn = document.createElement('button');
        pdfBtn.id = 'downloadPdfBtn';
        pdfBtn.className = 'toolbar-btn';
        pdfBtn.innerHTML = '↓ DOWNLOAD PDF';
        pdfBtn.onclick = () => {
            window.location.href = `/download-pdf/${fileId}`;
        };
        toolbar.insertBefore(pdfBtn, toolbar.children[2]);
    } else {
        // Update click handler and ensure it's visible
        pdfBtn.onclick = () => {
            window.location.href = `/download-pdf/${fileId}`;
        };
        pdfBtn.style.display = 'block';
    }
}

// Update editor stats on typing
latexEditor.addEventListener('input', () => {
    updateEditorStats();
    editorStatus.textContent = 'Modified';
});

function updateEditorStats() {
    const text = latexEditor.value;
    const lines = text.split('\n').length;
    const chars = text.length;

    lineCount.textContent = lines;
    charCount.textContent = chars;
}

// Close modal with Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && latexModal.classList.contains('show')) {
        latexModal.classList.remove('show');
    }
});
````

## File: app.py
````python
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os

# Import services
from services.pdf_service import extract_text_from_pdf
from services.cleaner_service import clean_text
from services.llm_service import analyze_resume
from services.latex_service import generate_improved_latex, save_latex_and_pdf
from services.cache_service import get_file_hash, get_cached_analysis, save_to_cache

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
CACHE_FOLDER = 'cache'
GENERATED_FOLDER = 'generated'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Create folders
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CACHE_FOLDER, exist_ok=True)
os.makedirs(GENERATED_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/styles.css')
def style():
    return send_from_directory('templates', 'styles.css')


@app.route('/script.js')
def script():
    return send_from_directory('templates', 'script.js')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle PDF upload and analysis"""
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'}), 400
    
    filepath = None
    
    try:
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Check cache
        file_hash = get_file_hash(filepath)
        cached = get_cached_analysis(file_hash, CACHE_FOLDER)
        
        if cached:
            os.remove(filepath)
            return jsonify({
                'success': True,
                'filename': filename,
                'data': cached,
                'cached': True
            }), 200
        
        # Extract and clean
        raw_text = extract_text_from_pdf(filepath)
        cleaned_text = clean_text(raw_text)
        
        # Analyze with LLM
        result = analyze_resume(cleaned_text)
        
        # Cache result
        save_to_cache(file_hash, result, CACHE_FOLDER)
        
        # Cleanup
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'data': result,
            'cached': False
        }), 200
        
    except Exception as e:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': str(e)}), 500


@app.route('/generate-latex', methods=['POST'])
def generate_latex():
    """Generate improved LaTeX resume and compile PDF if possible"""
    
    try:
        data = request.json
        resume_data = data.get('resume_data')
        
        if not resume_data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Generate LaTeX
        latex_code = generate_improved_latex(resume_data, "")
        
        # Save LaTeX and compile to PDF
        file_info = save_latex_and_pdf(latex_code, GENERATED_FOLDER)
        
        return jsonify({
            'success': True,
            'file_id': file_info['file_id'],
            'filename': file_info['tex_filename'],
            'pdf_available': bool(file_info['pdf_filepath'])
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download-latex/<file_id>')
def download_latex(file_id):
    """Download LaTeX file"""
    filename = f"resume_{file_id}.tex"
    return send_from_directory(GENERATED_FOLDER, filename, as_attachment=True)


@app.route('/download-pdf/<file_id>')
def download_pdf(file_id):
    """Download PDF file"""
    filename = f"resume_{file_id}.pdf"
    return send_from_directory(GENERATED_FOLDER, filename, as_attachment=True)

@app.route('/debug-latex', methods=['POST'])
def debug_latex():
    """Debug route - see raw LLM output"""
    try:
        from services.latex_service import format_resume_data, IMPROVEMENT_PROMPT
        import os
        from groq import Groq

        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        data = request.json
        resume_data = data.get('resume_data')
        data_str = format_resume_data(resume_data)

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": IMPROVEMENT_PROMPT},
                {"role": "user", "content": f"Improve and return this resume content:\n\n{data_str}"}
            ],
            temperature=0.2
        )

        raw = response.choices[0].message.content

        # Return raw so you can inspect it
        return jsonify({
            'raw_output': raw
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
````

## File: templates/index.html
````html
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resume Analyzer</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link
        href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;900&family=Playfair+Display:ital,wght@1,700&family=IBM+Plex+Mono:wght@400;500&display=swap"
        rel="stylesheet">
    <link rel="stylesheet" href="styles.css">
</head>

<body>
    <!-- Upload Section -->
    <div class="upload-container" id="uploadContainer">
        <div class="upload-wrapper">
            <h1 class="hero-title">
                <span class="title-heavy">RESUME</span>
                <span class="title-italic">Analyzer</span>
            </h1>
            <p class="hero-subtitle">INTELLIGENT PARSING & PROFESSIONAL INSIGHTS</p>

            <form id="uploadForm" enctype="multipart/form-data">
                <div class="upload-area" id="uploadArea">
                    <div class="upload-icon">📄</div>
                    <label for="fileInput" class="upload-label">
                        Drop your resume here or <span class="link-text">browse files</span>
                    </label>
                    <input type="file" id="fileInput" name="file" accept=".pdf" required>
                    <div class="file-info" id="fileInfo"></div>
                </div>

                <button type="submit" id="submitBtn" class="btn-primary">
                    <span class="btn-text">ANALYZE RESUME</span>
                    <span class="btn-arrow">→</span>
                </button>
            </form>

            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p class="loading-text">PROCESSING DOCUMENT...</p>
            </div>

            <div class="error" id="error"></div>
        </div>
    </div>

    <!-- Dashboard Section -->
    <div class="dashboard-container" id="dashboardContainer" style="display: none;">

        <!-- Header -->
        <div class="dashboard-header">
            <div class="header-left">
                <h1 class="dashboard-title">
                    <span class="title-heavy">ANALYSIS</span>
                    <span class="title-italic">Report</span>
                </h1>
                <p class="candidate-name" id="candidateName">REESUME FOR</p>
            </div>
            <div class="header-actions">
                <button class="btn-download" id="downloadLatexBtn">
                    <span class="btn-text">↓ DOWNLOAD .TEX</span>
                </button>
                <button class="btn-download" id="dashboardPdfBtn" style="display: none;">
                    <span class="btn-text">↓ DOWNLOAD PDF</span>
                </button>
                <button class="btn-secondary" id="uploadNewBtn">
                    <span class="btn-text">← UPLOAD NEW</span>
                </button>
            </div>
        </div>

        <!-- Score Overview -->
        <div class="score-section">
            <div class="score-card score-main">
                <div class="score-label">OVERALL SCORE</div>
                <div class="score-value" id="overallScore">--</div>
                <div class="score-bar">
                    <div class="score-bar-fill" id="overallScoreBar"></div>
                </div>
                <div class="score-explanation" id="scoreExplanation"></div>
            </div>

            <div class="score-breakdown">
                <div class="breakdown-item">
                    <div class="breakdown-label">CONTENT</div>
                    <div class="breakdown-score" id="contentScore">--</div>
                    <div class="breakdown-bar">
                        <div class="breakdown-bar-fill" id="contentBar"></div>
                    </div>
                </div>
                <div class="breakdown-item">
                    <div class="breakdown-label">STRUCTURE</div>
                    <div class="breakdown-score" id="structureScore">--</div>
                    <div class="breakdown-bar">
                        <div class="breakdown-bar-fill" id="structureBar"></div>
                    </div>
                </div>
                <div class="breakdown-item">
                    <div class="breakdown-label">IMPACT</div>
                    <div class="breakdown-score" id="impactScore">--</div>
                    <div class="breakdown-bar">
                        <div class="breakdown-bar-fill" id="impactBar"></div>
                    </div>
                </div>
                <div class="breakdown-item">
                    <div class="breakdown-label">COMPLETENESS</div>
                    <div class="breakdown-score" id="completenessScore">--</div>
                    <div class="breakdown-bar">
                        <div class="breakdown-bar-fill" id="completenessBar"></div>
                    </div>
                </div>
                <div class="breakdown-item">
                    <div class="breakdown-label">FORMATTING</div>
                    <div class="breakdown-score" id="formattingScore">--</div>
                    <div class="breakdown-bar">
                        <div class="breakdown-bar-fill" id="formattingBar"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Professional Summary -->
        <div class="section-card">
            <h2 class="section-title">
                <span class="section-number">01.</span>
                <span class="section-text">PROFESSIONAL SUMMARY</span>
            </h2>
            <p class="summary-text" id="summaryText"></p>
        </div>

        <!-- Strengths & Improvements -->
        <div class="two-column">
            <div class="section-card">
                <h2 class="section-title">
                    <span class="section-number">02.</span>
                    <span class="section-text">STRENGTHS</span>
                </h2>
                <ul class="list-styled" id="strengthsList"></ul>
            </div>

            <div class="section-card">
                <h2 class="section-title">
                    <span class="section-number">03.</span>
                    <span class="section-text">IMPROVEMENTS</span>
                </h2>
                <div id="improvementsList"></div>
            </div>
        </div>

        <!-- Recommended Roles -->
        <div class="section-card">
            <h2 class="section-title">
                <span class="section-number">04.</span>
                <span class="section-text">RECOMMENDED ROLES</span>
            </h2>
            <div class="role-tags" id="roleTags"></div>
        </div>

        <!-- ATS Keywords -->
        <div class="section-card">
            <h2 class="section-title">
                <span class="section-number">05.</span>
                <span class="section-text">ATS KEYWORDS</span>
            </h2>
            <div class="keyword-cloud" id="keywordCloud"></div>
        </div>

        <!-- Detailed Data Tabs -->
        <div class="section-card">
            <h2 class="section-title">
                <span class="section-number">06.</span>
                <span class="section-text">DETAILED DATA</span>
            </h2>

            <div class="tabs">
                <button class="tab-btn active" data-tab="projects">PROJECTS</button>
                <button class="tab-btn" data-tab="experience">EXPERIENCE</button>
                <button class="tab-btn" data-tab="education">EDUCATION</button>
                <button class="tab-btn" data-tab="skills">SKILLS</button>
            </div>

            <div class="tab-content">
                <div class="tab-pane active" id="tab-projects"></div>
                <div class="tab-pane" id="tab-experience"></div>
                <div class="tab-pane" id="tab-education"></div>
                <div class="tab-pane" id="tab-skills"></div>
            </div>
        </div>
        <div class="modal-overlay" id="latexModal">
            <div class="modal-container">
                <div class="modal-header">
                    <h2 class="modal-title">
                        <span class="title-heavy">EDIT</span>
                        <span class="title-italic">Resume</span>
                    </h2>
                    <button class="modal-close" id="closeModal">×</button>
                </div>
                <div class="modal-body">
                    <div class="editor-toolbar">
                        <button class="toolbar-btn" id="resetBtn" title="Reset to original">
                            ↺ RESET
                        </button>
                        <button class="toolbar-btn" id="downloadEditedBtn" title="Download edited version">
                            ↓ DOWNLOAD EDITED
                        </button>
                        <span class="toolbar-status">
                            <span class="status-label">STATUS:</span>
                            <span class="status-text" id="editorStatus">Ready</span>
                        </span>
                    </div>
                    <textarea class="latex-editor" id="latexEditor" spellcheck="false"></textarea>
                    <div class="editor-footer">
                        <div class="editor-info">
                            <span class="info-label">LINES:</span>
                            <span class="info-value" id="lineCount">0</span>
                            <span class="info-separator">|</span>
                            <span class="info-label">CHARS:</span>
                            <span class="info-value" id="charCount">0</span>
                        </div>
                        <div class="editor-hint">
                            Click "DOWNLOAD EDITED" to save your changes as a new .tex file
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script src="script.js"></script>
</body>

</html>
````

## File: templates/styles.css
````css
/* ===== CSS RESET & BASE ===== */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

:root {
    /* Color Palette */
    --bg-canvas: #F5F1E8;
    --text-primary: #2B2B2B;
    --text-secondary: #5A5A5A;
    --text-muted: #8B8B8B;

    --accent-primary: #5E6B4C;
    --accent-primary-dark: #465039;
    --accent-secondary: #B89B5E;

    --surface-white: #FFFFFF;
    --surface-light: #FDFCF9;
    --border-color: #E5DFD0;
    --border-dark: #D0C7B3;

    /* Typography */
    --font-sans: 'Inter', system-ui, -apple-system, sans-serif;
    --font-serif: 'Playfair Display', Georgia, serif;
    --font-mono: 'IBM Plex Mono', 'Courier New', monospace;

    /* Spacing */
    --spacing-xs: 0.5rem;
    --spacing-sm: 1rem;
    --spacing-md: 1.5rem;
    --spacing-lg: 2rem;
    --spacing-xl: 3rem;
    --spacing-2xl: 4rem;

    /* Shadows */
    --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.08);
    --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.08);
    --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.1);
}

body {
    font-family: var(--font-sans);
    background-color: var(--bg-canvas);
    color: var(--text-primary);
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
}

/* ===== UPLOAD SECTION ===== */
.upload-container {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--spacing-lg);
}

.upload-wrapper {
    max-width: 600px;
    width: 100%;
}

.hero-title {
    font-size: clamp(2.5rem, 8vw, 4.5rem);
    line-height: 1;
    margin-bottom: var(--spacing-xs);
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.title-heavy {
    font-family: var(--font-sans);
    font-weight: 900;
    letter-spacing: -0.04em;
    color: var(--text-primary);
}

.title-italic {
    font-family: var(--font-serif);
    font-weight: 700;
    font-style: italic;
    color: var(--accent-primary);
}

.hero-subtitle {
    font-family: var(--font-mono);
    font-size: 0.75rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: var(--spacing-xl);
}

.upload-area {
    background: var(--surface-white);
    border: 2px dashed var(--border-color);
    border-radius: 12px;
    padding: var(--spacing-xl);
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    margin-bottom: var(--spacing-md);
}

.upload-area:hover,
.upload-area.dragover {
    border-color: var(--accent-primary);
    background: var(--surface-light);
    box-shadow: var(--shadow-md);
}

.upload-icon {
    font-size: 3rem;
    margin-bottom: var(--spacing-sm);
    opacity: 0.5;
}

.upload-label {
    font-size: 1rem;
    color: var(--text-secondary);
    cursor: pointer;
    display: block;
}

.link-text {
    color: var(--accent-primary);
    text-decoration: underline;
    font-weight: 500;
}

input[type="file"] {
    display: none;
}

.file-info {
    margin-top: var(--spacing-sm);
    font-family: var(--font-mono);
    font-size: 0.85rem;
    color: var(--text-muted);
}

.btn-primary {
    width: 100%;
    background: var(--accent-primary);
    color: var(--surface-white);
    border: none;
    padding: var(--spacing-md) var(--spacing-lg);
    border-radius: 8px;
    font-family: var(--font-mono);
    font-size: 0.9rem;
    font-weight: 500;
    letter-spacing: 0.05em;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: var(--shadow-sm);
}

.btn-primary:hover {
    background: var(--accent-primary-dark);
    box-shadow: var(--shadow-md);
    transform: translateY(-1px);
}

.btn-primary:disabled {
    background: var(--border-color);
    color: var(--text-muted);
    cursor: not-allowed;
    transform: none;
}

.btn-arrow {
    font-size: 1.2rem;
    transition: transform 0.3s ease;
}

.btn-primary:hover .btn-arrow {
    transform: translateX(4px);
}

.loading {
    display: none;
    text-align: center;
    margin-top: var(--spacing-lg);
}

.loading.show {
    display: block;
}

.spinner {
    border: 3px solid var(--border-color);
    border-top: 3px solid var(--accent-primary);
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
    margin: 0 auto var(--spacing-sm);
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }

    100% {
        transform: rotate(360deg);
    }
}

.loading-text {
    font-family: var(--font-mono);
    font-size: 0.85rem;
    letter-spacing: 0.1em;
    color: var(--text-muted);
}

.error {
    display: none;
    background: #FEE;
    color: #C33;
    padding: var(--spacing-md);
    border-radius: 8px;
    margin-top: var(--spacing-md);
    font-size: 0.95rem;
}

.error.show {
    display: block;
}

/* ===== DASHBOARD SECTION ===== */
.dashboard-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: var(--spacing-2xl) var(--spacing-lg);
}

.dashboard-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: var(--spacing-2xl);
    flex-wrap: wrap;
    gap: var(--spacing-md);
}

.dashboard-title {
    font-size: clamp(2rem, 5vw, 3rem);
    line-height: 1;
    margin-bottom: var(--spacing-xs);
}

.candidate-name {
    font-size: 1.1rem;
    color: var(--text-secondary);
    font-weight: 500;
}

.btn-secondary {
    background: transparent;
    color: var(--text-primary);
    border: 2px solid var(--border-dark);
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    font-family: var(--font-mono);
    font-size: 0.85rem;
    font-weight: 500;
    letter-spacing: 0.05em;
    cursor: pointer;
    transition: all 0.3s ease;
}

.btn-secondary:hover {
    background: var(--surface-white);
    border-color: var(--accent-primary);
    color: var(--accent-primary);
}

/* Score Section */
.score-section {
    display: grid;
    grid-template-columns: 1fr 2fr;
    gap: var(--spacing-lg);
    margin-bottom: var(--spacing-2xl);
}

.score-card {
    background: var(--surface-white);
    padding: var(--spacing-xl);
    border-radius: 12px;
    box-shadow: var(--shadow-sm);
}

.score-main {
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.score-label {
    font-family: var(--font-mono);
    font-size: 0.75rem;
    letter-spacing: 0.15em;
    color: var(--text-muted);
    margin-bottom: var(--spacing-sm);
}

.score-value {
    font-size: 4rem;
    font-weight: 900;
    color: var(--accent-primary);
    line-height: 1;
    margin-bottom: var(--spacing-sm);
}

.score-bar {
    width: 100%;
    height: 8px;
    background: var(--border-color);
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: var(--spacing-md);
}

.score-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--accent-primary), #84936E);
    border-radius: 4px;
    transition: width 1s ease;
}

.score-explanation {
    font-size: 0.9rem;
    color: var(--text-secondary);
    line-height: 1.5;
}

.score-breakdown {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
}

.breakdown-item {
    background: var(--surface-light);
    padding: var(--spacing-md);
    border-radius: 8px;
    display: grid;
    grid-template-columns: 1fr auto;
    grid-template-rows: auto auto;
    gap: var(--spacing-xs) var(--spacing-md);
}

.breakdown-label {
    font-family: var(--font-mono);
    font-size: 0.7rem;
    letter-spacing: 0.12em;
    color: var(--text-muted);
}

.breakdown-score {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-primary);
    text-align: right;
}

.breakdown-bar {
    grid-column: 1 / -1;
    width: 100%;
    height: 4px;
    background: var(--border-color);
    border-radius: 2px;
    overflow: hidden;
}

.breakdown-bar-fill {
    height: 100%;
    background: var(--accent-primary);
    border-radius: 2px;
    transition: width 0.8s ease;
}

/* Section Cards */
.section-card {
    background: var(--surface-white);
    padding: var(--spacing-xl);
    border-radius: 12px;
    box-shadow: var(--shadow-sm);
    margin-bottom: var(--spacing-lg);
}

.section-title {
    font-size: 1.5rem;
    margin-bottom: var(--spacing-lg);
    display: flex;
    align-items: baseline;
    gap: var(--spacing-sm);
}

.section-number {
    font-family: var(--font-mono);
    font-size: 0.9rem;
    color: var(--accent-primary);
    font-weight: 500;
}

.section-text {
    font-family: var(--font-sans);
    font-weight: 700;
    letter-spacing: -0.02em;
}

.summary-text {
    font-size: 1.1rem;
    line-height: 1.8;
    color: var(--text-secondary);
}

/* Two Column Layout */
.two-column {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--spacing-lg);
    margin-bottom: var(--spacing-lg);
}

.list-styled {
    list-style: none;
}

.list-styled li {
    padding-left: var(--spacing-md);
    margin-bottom: var(--spacing-sm);
    position: relative;
    line-height: 1.6;
}

.list-styled li::before {
    content: "✓";
    position: absolute;
    left: 0;
    color: var(--accent-secondary);
    font-weight: bold;
}

.improvement-item {
    background: var(--surface-light);
    border-radius: 8px;
    margin-bottom: var(--spacing-xs);
    border-left: 3px solid var(--accent-primary);
    overflow: hidden;
    transition: all 0.3s ease;
}

.improvement-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-md);
    cursor: pointer;
    transition: background 0.3s ease;
}

.improvement-header:hover {
    background: var(--bg-canvas);
}

.improvement-header-left {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    flex: 1;
}

.improvement-section {
    font-family: var(--font-mono);
    font-size: 0.75rem;
    letter-spacing: 0.1em;
    color: var(--text-muted);
    text-transform: uppercase;
}

.improvement-issue {
    font-size: 0.95rem;
    font-weight: 500;
    color: var(--text-primary);
}

.improvement-header-right {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
}

.priority-badge {
    font-family: var(--font-mono);
    font-size: 0.7rem;
    padding: 0.25rem 0.5rem;
    border-radius: 6px;
    font-weight: 500;
    white-space: nowrap;
}

.priority-high {
    background: #FFEBEE;
    color: #C62828;
}

.priority-medium {
    background: #FFF8E1;
    color: #F57C00;
}

.priority-low {
    background: #E8F5E9;
    color: #2E7D32;
}

.accordion-icon {
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    color: var(--text-muted);
    transition: transform 0.3s ease;
}

.improvement-item.active .accordion-icon {
    transform: rotate(180deg);
}

.improvement-content {
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.3s ease, padding 0.3s ease;
}

.improvement-item.active .improvement-content {
    max-height: 500px;
    padding: 0 var(--spacing-md) var(--spacing-md) var(--spacing-md);
}

.improvement-suggestion {
    font-size: 0.9rem;
    color: var(--text-secondary);
    line-height: 1.6;
    padding: var(--spacing-sm);
    background: var(--surface-white);
    border-radius: 8px;
}

.priority-badge {
    font-family: var(--font-mono);
    font-size: 0.7rem;
    padding: 0.25rem 0.5rem;
    border-radius: 6px;
    font-weight: 500;
}

.priority-high {
    background: #FFEBEE;
    color: #C62828;
}

.priority-medium {
    background: #FFF8E1;
    color: #F57C00;
}

.priority-low {
    background: #E8F5E9;
    color: #2E7D32;
}

.improvement-issue {
    font-size: 0.95rem;
    margin-bottom: var(--spacing-xs);
    font-weight: 500;
}

.improvement-suggestion {
    font-size: 0.9rem;
    color: var(--text-secondary);
    line-height: 1.5;
}

/* Role Tags */
.role-tags {
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-sm);
}

.role-tag {
    background: var(--surface-light);
    border: 1px solid var(--border-color);
    padding: var(--spacing-sm) var(--spacing-md);
    border-radius: 8px;
    font-family: var(--font-mono);
    font-size: 0.85rem;
    color: var(--text-primary);
    transition: all 0.3s ease;
}

.role-tag:hover {
    background: var(--accent-primary);
    color: var(--surface-white);
    border-color: var(--accent-primary);
}

/* Keyword Cloud */
.keyword-cloud {
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-xs);
}

.keyword-tag {
    background: var(--bg-canvas);
    padding: 0.5rem 0.75rem;
    border-radius: 8px;
    font-size: 0.85rem;
    color: var(--text-secondary);
    font-family: var(--font-mono);
}

/* Tabs */
.tabs {
    display: flex;
    gap: var(--spacing-xs);
    margin-bottom: var(--spacing-lg);
    border-bottom: 2px solid var(--border-color);
}

.tab-btn {
    background: none;
    border: none;
    padding: var(--spacing-sm) var(--spacing-md);
    font-family: var(--font-mono);
    font-size: 0.8rem;
    letter-spacing: 0.1em;
    color: var(--text-muted);
    cursor: pointer;
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
    transition: all 0.3s ease;
}

.tab-btn:hover {
    color: var(--text-primary);
}

.tab-btn.active {
    color: var(--accent-primary);
    border-bottom-color: var(--accent-primary);
}

.tab-pane {
    display: none;
}

.tab-pane.active {
    display: block;
}

.data-item {
    background: var(--surface-light);
    padding: var(--spacing-md);
    border-radius: 8px;
    margin-bottom: var(--spacing-md);
}

.data-item-header {
    margin-bottom: var(--spacing-sm);
}

.data-title {
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 0.25rem;
}

.data-meta {
    font-family: var(--font-mono);
    font-size: 0.8rem;
    color: var(--text-muted);
}

.data-tags {
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-xs);
    margin-bottom: var(--spacing-sm);
}

.data-tag {
    background: var(--bg-canvas);
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-family: var(--font-mono);
}

.data-details {
    list-style: none;
}

.data-details li {
    padding-left: var(--spacing-md);
    margin-bottom: var(--spacing-xs);
    position: relative;
    font-size: 0.9rem;
    line-height: 1.5;
    color: var(--text-secondary);
}

.data-details li::before {
    content: "—";
    position: absolute;
    left: 0;
    color: var(--accent-primary);
}

/* Responsive */
@media (max-width: 768px) {

    .score-section,
    .two-column {
        grid-template-columns: 1fr;
    }

    .dashboard-header {
        flex-direction: column;
    }

    .tabs {
        overflow-x: auto;
    }
}

/* ===== HEADER ACTIONS ===== */
.header-actions {
    display: flex;
    gap: var(--spacing-sm);
    align-items: center;
}

.btn-download {
    background: var(--accent-primary);
    color: var(--surface-white);
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    font-family: var(--font-mono);
    font-size: 0.85rem;
    font-weight: 500;
    letter-spacing: 0.05em;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: var(--shadow-sm);
}

.btn-download:hover {
    background: var(--accent-primary-dark);
    box-shadow: var(--shadow-md);
    transform: translateY(-1px);
}

.btn-download:disabled {
    background: var(--border-color);
    color: var(--text-muted);
    cursor: not-allowed;
    transform: none;
}

.btn-download .btn-text {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* ===== LATEX EDITOR MODAL ===== */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(43, 43, 43, 0.55);
    backdrop-filter: blur(6px);
    -webkit-backdrop-filter: blur(6px);
    display: none;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: var(--spacing-lg);
    transition: all 0.3s ease;
}

.modal-overlay.show {
    display: flex;
    animation: overlayFadeIn 0.3s ease;
}

@keyframes overlayFadeIn {
    from {
        background: rgba(43, 43, 43, 0);
        backdrop-filter: blur(0px);
        -webkit-backdrop-filter: blur(0px);
    }
    to {
        background: rgba(43, 43, 43, 0.55);
        backdrop-filter: blur(6px);
        -webkit-backdrop-filter: blur(6px);
    }
}

.modal-container {
    background: var(--surface-white);
    border-radius: 12px;
    width: 100%;
    max-width: 1000px;
    height: 80vh;
    max-height: 800px;
    min-height: 500px;
    display: flex;
    flex-direction: column;
    box-shadow: var(--shadow-lg);
    animation: modalSlideIn 0.3s ease;
    overflow: hidden; /* Force child elements (header/footer) to respect rounded corners */
}

@keyframes modalSlideIn {
    from {
        opacity: 0;
        transform: translateY(-20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.modal-header {
    padding: var(--spacing-lg);
    border-bottom: 2px solid var(--border-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.modal-title {
    font-size: 1.8rem;
    line-height: 1;
    display: flex;
    gap: 0.5rem;
}

.modal-close {
    background: transparent;
    border: none;
    font-size: 2rem;
    color: var(--text-muted);
    cursor: pointer;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    transition: all 0.3s ease;
}

.modal-close:hover {
    background: var(--bg-canvas);
    color: var(--text-primary);
}

.modal-body {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

/* Editor Toolbar */
.editor-toolbar {
    padding: var(--spacing-md);
    background: var(--bg-canvas);
    border-bottom: 1px solid var(--border-color);
    display: flex;
    gap: var(--spacing-sm);
    align-items: center;
}

.toolbar-btn {
    background: var(--surface-white);
    border: 1px solid var(--border-color);
    padding: 0.5rem 1.2rem;
    border-radius: 8px; /* Consistent corner radius */
    font-family: var(--font-mono);
    font-size: 0.75rem;
    letter-spacing: 0.05em;
    cursor: pointer;
    transition: all 0.2s ease;
    font-weight: 600;
}

.toolbar-btn:hover {
    background: var(--accent-primary);
    color: var(--surface-white);
    border-color: var(--accent-primary);
}

.toolbar-status {
    margin-left: auto;
    display: flex;
    gap: 0.5rem;
    align-items: center;
}

.status-label {
    font-family: var(--font-mono);
    font-size: 0.7rem;
    letter-spacing: 0.1em;
    color: var(--text-muted);
}

.status-text {
    font-family: var(--font-mono);
    font-size: 0.75rem;
    color: var(--accent-primary);
    font-weight: 500;
}

/* LaTeX Editor (IDE-style Theme) */
.latex-editor {
    flex: 1;
    width: 100%;
    padding: var(--spacing-lg);
    border: none;
    font-family: var(--font-mono);
    font-size: 0.95rem;
    line-height: 1.6;
    resize: none;
    background: #1e2219; /* Premium dark-olive canvas matching color palette */
    color: #edf2e8; /* High-contrast ivory text */
    outline: none;
    transition: background 0.3s ease;
}

.latex-editor:focus {
    background: #242a1e;
}

/* Custom Scrollbar for Editor */
.latex-editor::-webkit-scrollbar {
    width: 8px;
}

.latex-editor::-webkit-scrollbar-track {
    background: #1e2219;
}

.latex-editor::-webkit-scrollbar-thumb {
    background: var(--accent-primary);
    border-radius: 4px;
}

.latex-editor::-webkit-scrollbar-thumb:hover {
    background: var(--accent-primary-dark);
}

/* Editor Footer */
.editor-footer {
    padding: var(--spacing-md);
    background: var(--bg-canvas);
    border-top: 1px solid var(--border-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.editor-info {
    display: flex;
    gap: var(--spacing-sm);
    align-items: center;
    font-family: var(--font-mono);
    font-size: 0.75rem;
}

.info-label {
    color: var(--text-muted);
    letter-spacing: 0.1em;
}

.info-value {
    color: var(--text-primary);
    font-weight: 500;
}

.info-separator {
    color: var(--border-color);
}

.editor-hint {
    font-size: 0.8rem;
    color: var(--text-muted);
    font-style: italic;
}

/* Responsive */
@media (max-width: 768px) {
    .header-actions {
        flex-direction: column;
        width: 100%;
    }

    .btn-download,
    .btn-secondary {
        width: 100%;
    }

    .modal-container {
        height: 95vh;
        max-height: 95vh;
        margin: 0;
        border-radius: 0;
    }

    .editor-footer {
        flex-direction: column;
        gap: var(--spacing-sm);
        align-items: flex-start;
    }
}

/* ===== PDF DOWNLOAD ACTIONS ===== */
#downloadPdfBtn,
#dashboardPdfBtn {
    background: var(--accent-secondary) !important;
    color: var(--surface-white) !important;
    border-color: var(--accent-secondary) !important;
}

#downloadPdfBtn:hover,
#dashboardPdfBtn:hover {
    background: #a3874c !important; /* Premium darker ochre for hover state */
    border-color: #a3874c !important;
    color: var(--surface-white) !important;
    transform: translateY(-1px);
}
````

## File: README.md
````markdown
# README

## PROJECT OVERVIEW

This is an AI-powered resume analyzer that extracts text from PDF resumes, cleans the data, and uses a Language Model to provide comprehensive analysis including professional summaries, improvement suggestions, and scoring.

---

## FEATURES

- PDF text extraction using PyPDF2
- Text cleaning and normalization
- LLM-powered resume analysis
- Professional dashboard with scores and insights
- Improvement suggestions with priority levels
- ATS keyword extraction
- Recommended job roles
- Detailed data tabs for projects, experience, education, and skills

---

## TECH STACK

### Backend:
- Python 3.x
- Flask (web framework)
- Flask-CORS (cross-origin support)
- PyPDF2 (PDF text extraction)
- OpenAI API (LLM analysis)
- python-dotenv (environment variables)

### Frontend:
- HTML5
- CSS3 (custom design system)
- Vanilla JavaScript (no frameworks)

---

## INSTALLATION

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate virtual environment:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Mac/Linux:
     ```bash
     source venv/bin/activate
     ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Create a `.env` file in the root directory
6. Add your OpenAI API key to `.env`:
   ```env
   OPENAI_API_KEY=your_api_key_here
   ```

---

## DEPENDENCIES (`requirements.txt`)

```txt
Flask==2.3.0
flask-cors==4.0.0
PyPDF2==3.0.0
openai==1.0.0
python-dotenv==1.0.0
werkzeug==2.3.0
```

---

## PROJECT STRUCTURE

```txt
project_root/
├── app.py                  # Flask application
├── cleaner.py              # Text cleaning functions
├── .env                    # Environment variables (not in git)
├── requirements.txt        # Python dependencies
├── uploads/                # Temporary upload folder (auto-created)
└── templates/
    ├── index.html          # Main HTML file
    ├── styles.css          # Stylesheet
    └── script.js           # Frontend JavaScript
```

## SCREENSHOTS

### Landing Page

![Landing Page](images/landing.png)

### Analysis Dashboard

![Analysis Dashboard](images/score.png)

### Summary

![Analyzed Data](images/summary.png)

### Recommendations

![Analyzed Data](images/recommendation.png)


---

## HOW TO RUN

1. Make sure virtual environment is activated
2. Run:
   ```bash
   python app.py
   ```
3. Open browser and go to:
   ```txt
   http://localhost:5000
   ```
4. Upload a PDF resume
5. Wait for analysis
6. View comprehensive dashboard

---

## USAGE

1. Drag and drop or click to select a PDF resume
2. Click **"ANALYZE RESUME"** button
3. Wait for processing (usually 5–15 seconds)
4. Dashboard appears with:
   - Overall score out of 100
   - Score breakdown (content, structure, impact, completeness, formatting)
   - Professional summary
   - Strengths list
   - Improvement suggestions (accordion style)
   - Recommended job roles
   - ATS keywords
   - Detailed data tabs
5. Click **"UPLOAD NEW"** to analyze another resume

---

## DESIGN SYSTEM

### Color Palette:
- Background: Warm cream/off-white (`#F5F1E8`)
- Text: Soft charcoal (`#2B2B2B`)
- Primary Accent: Muted olive (`#6B7A46`)
- Secondary Accent: Warm ochre (`#B59A52`)

### Typography:
- Headlines: Inter (heavy sans-serif) + Playfair Display (italic serif)
- Body: Inter (geometric sans-serif)
- UI Labels: IBM Plex Mono (monospaced)

---

## CONFIGURATION

You can adjust the LLM model in `app.py`:
- Default: `gpt-4o-mini` (faster, cheaper)
- Premium: `gpt-4o` (better quality)

---

## FEATURES BREAKDOWN

### 1. Text Extraction (`cleaner.py`)
- Fixes encoding issues
- Removes hyphenation artifacts
- Standardizes whitespace
- Normalizes bullet points
- Detects section headers

### 2. LLM Analysis (`app.py`)
- Structured JSON output
- Score calculation with breakdown
- Professional summary generation
- Strength identification
- Improvement suggestions with priority
- ATS keyword extraction
- Role recommendations

### 3. Dashboard (`index.html + styles.css + script.js`)
- Upload interface with drag-and-drop
- Loading states
- Error handling
- Score visualization with progress bars
- Accordion for improvements
- Tab navigation for detailed data
- Responsive design

---

## API ENDPOINTS

### `POST /upload`
- Accepts: `multipart/form-data` with `file` field
- Returns: JSON with analysis data
- Max file size: 16MB

### `GET /`
- Returns: Main HTML page

### `GET /styles.css`
- Returns: Stylesheet

---

## LIMITATIONS

- Only works with text-based PDFs (not scanned images)
- Requires OpenAI API key (costs money)
- File size limit: 16MB
- PDF format only
- Requires internet connection for LLM

---

## FUTURE ENHANCEMENTS

- Support for multiple file formats (DOCX, TXT)
- OCR for scanned PDFs
- Batch processing
- Export analysis as PDF report
- Compare multiple resumes
- Job description matching
- Resume template suggestions
- Version history tracking

---

## TROUBLESHOOTING

### Issue: File upload fails
**Solution:** Check file is PDF and under 16MB

### Issue: LLM analysis fails
**Solution:** Verify OpenAI API key in `.env` file and check API quota

### Issue: Blank dashboard
**Solution:** Check browser console for JavaScript errors

### Issue: CORS errors
**Solution:** Make sure Flask-CORS is installed and `CORS(app)` is in `app.py`

### Issue: Module not found
**Solution:** Activate virtual environment and run:
```bash
pip install -r requirements.txt
```

---

## SECURITY NOTES

- Uploaded files are deleted immediately after processing
- No data is stored permanently
- API keys stored in `.env` (not committed to git)
- Add `.env` to `.gitignore`
- CORS enabled (disable in production or restrict domains)

---

## LICENSE

This project is for educational/personal use.

---

## CREDITS

- PyPDF2 for PDF extraction
- OpenAI for LLM capabilities
- Google Fonts for typography (Inter, Playfair Display, IBM Plex Mono)

---

## CONTACT

For issues or questions, please open an issue in the repository.
````
