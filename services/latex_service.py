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
            model="openai/gpt-oss-20b",
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