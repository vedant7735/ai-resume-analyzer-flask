import os
import uuid
import re
import subprocess
import shutil

LATEX_TEMPLATE = r"""
\documentclass[10pt, letterpaper]{article}
\usepackage[ignoreheadfoot, top={{MARGIN_TOP}}cm, bottom={{MARGIN_BOTTOM}}cm, left={{MARGIN_LEFT}}cm, right={{MARGIN_RIGHT}}cm]{geometry}
\usepackage{titlesec, array, enumitem}
\usepackage[colorlinks=false, hidelinks]{hyperref}
\usepackage[T1]{fontenc}\usepackage[utf8]{inputenc}\usepackage{lmodern}
\pagestyle{empty}\setcounter{secnumdepth}{0}\setlength{\parindent}{0pt}\pagenumbering{gobble}
\titleformat{\section}{\normalsize\bfseries\uppercase}{}{0pt}{}[\vspace{1pt}\titlerule\vspace{4pt}]
\titlespacing{\section}{0pt}{8pt}{4pt}
\setlist[itemize]{leftmargin=*, label=\textbullet, itemsep=1pt, parsep=0pt, topsep=2pt}
\begin{document}

{{HEADER}}

{{SUMMARY}}

{{EXPERIENCE}}

{{PROJECTS}}

{{EDUCATION}}

{{SKILLS}}

\end{document}
"""

def escape_latex(text):
    """
    Escape LaTeX special characters in correct order.
    Order matters: backslash must be replaced LAST to avoid double-escaping.
    """
    if text is None:
        return ""
    
    text = str(text)

    # Normalize Unicode spacing/punctuation that regularly breaks pdflatex.
    text = (
        text.replace("\u00A0", " ")
        .replace("\u2007", " ")
        .replace("\u202F", " ")
        .replace("\u2010", "-")
        .replace("\u2011", "-")
        .replace("\u2012", "-")
        .replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u2015", "-")
        .replace("\u2212", "-")
    )

    # Step 1: Replace everything except backslash
    replacements = [
        ('&',  r'\&'),
        ('%',  r'\%'),
        ('$',  r'\$'),
        ('#',  r'\#'),
        ('_',  r'\_'),
        ('{',  r'\{'),
        ('}',  r'\}'),
        ('~',  r'\textasciitilde{}'),
        ('^',  r'\textasciicircum{}'),
    ]
    
    for char, escaped in replacements:
        text = text.replace(char, escaped)
    
    # Step 2: Handle backslash specially (only if not already part of LaTeX command)
    # Replace standalone backslashes not followed by recognized LaTeX commands
    text = re.sub(
        r'\\(?![&%$#_{}textasciitildetextasciicircum])',
        r'\\textbackslash{}',
        text
    )
    
    return text

def render_to_latex(resume_v3):
    idn = resume_v3.get('identity', {})
    prefs = resume_v3.get('render_preferences', {})
    margins = prefs.get('margins', [1.5,1.5,1.8,1.8])

    # HEADER
    header = [r'\begin{center}', rf'{{\LARGE\bfseries {escape_latex(idn.get("name","").upper())}}} \\[4pt]', r'\small']
    parts = []
    if idn.get('email'): parts.append(rf'\href{{mailto:{idn["email"]}}}{{{idn["email"]}}}')
    if idn.get('phone'): parts.append(escape_latex(idn['phone']))
    if idn.get('linkedin'): parts.append(rf'\href{{https://{idn["linkedin"]}}}{{{idn["linkedin"]}}}')
    if idn.get('github'): parts.append(rf'\href{{https://{idn["github"]}}}{{{idn["github"]}}}')
    if idn.get('portfolio'): parts.append(rf'\href{{https://{idn["portfolio"]}}}{{{idn["portfolio"]}}}')
    header.append(' ' + r' \textbar{} '.join(parts))
    header.append(r'\end{center}\vspace{4pt}')
    header_tex = '\n'.join(header)

    # SUMMARY
    summary_tex = '\n'.join([
        r'\section{Summary}',
        escape_latex(resume_v3.get('analysis', {}).get('professional_summary', ''))
    ])

    # EXPERIENCE
    exp_tex = [r'\section{Experience}']
    for e in resume_v3.get('experience', []):
        exp_tex.append(rf'\noindent\textbf{{{escape_latex(e.get("title",""))}}} \hfill \texttt{{\small {escape_latex(e.get("duration",""))}}} \\')
        exp_tex.append(rf'\textit{{\small {escape_latex(e.get("company",""))}}} \hfill \texttt{{\small {escape_latex(e.get("type",""))}}}')
        exp_tex.append(r'\begin{itemize}')
        for b in e.get('bullets', []):
            exp_tex.append(rf'  \item {escape_latex(b)}')
        exp_tex.append(r'\end{itemize}\vspace{4pt}')
    exp_tex = '\n'.join(exp_tex)

    # PROJECTS
    proj_tex = [r'\section{Projects}']
    for p in resume_v3.get('projects', []):
        proj_tex.append(rf'\noindent\textbf{{{escape_latex(p.get("title",""))}}} \hfill \texttt{{\small {escape_latex(p.get("year",""))}}} \\')
        proj_tex.append(rf'\texttt{{\small {escape_latex(", ".join(p.get("tech_stack",[])))}}}')
        proj_tex.append(r'\begin{itemize}')
        for b in p.get('bullets', []):
            proj_tex.append(rf'  \item {escape_latex(b)}')
        proj_tex.append(r'\end{itemize}\vspace{4pt}')
    proj_tex = '\n'.join(proj_tex)

    # EDUCATION
    edu_tex = [r'\section{Education}']
    for ed in resume_v3.get('education', []):
        edu_tex.append(rf'\noindent\textbf{{{escape_latex(ed.get("degree",""))} in {escape_latex(ed.get("major",""))}}} \hfill \texttt{{\small {escape_latex(ed.get("graduation_year",""))}}} \\')
        edu_tex.append(rf'\textit{{\small {escape_latex(ed.get("institution",""))}}}')
        if ed.get('gpa'):
            edu_tex.append(rf'\\ \texttt{{\small GPA: {escape_latex(ed.get("gpa",""))}}}')
        edu_tex.append(r'\vspace{4pt}')
    edu_tex = '\n'.join(edu_tex)

    # SKILLS
    skills = resume_v3.get('skills', {})
    skill_rows = []
    for cat, items in [
        ('Languages', skills.get('languages',[])),
        ('Frameworks', skills.get('frameworks',[])),
        ('Tools', skills.get('tools',[])),
        ('Domains', skills.get('domains',[])),
    ]:
        if items:
            skill_rows.append(rf'\texttt{{\small\bfseries {escape_latex(cat)}}} & \small {escape_latex(", ".join(items))} \\[2pt]')
    skills_tex = '\n'.join([
        r'\section{Technical Skills}',
        r'\begin{tabular}{@{}p{2.8cm} p{12.5cm}@{}}',
        '\n'.join(skill_rows),
        r'\end{tabular}'
    ])

    # Inject
    latex = LATEX_TEMPLATE
    latex = latex.replace('{{MARGIN_TOP}}', str(margins[0]))
    latex = latex.replace('{{MARGIN_BOTTOM}}', str(margins[1]))
    latex = latex.replace('{{MARGIN_LEFT}}', str(margins[2]))
    latex = latex.replace('{{MARGIN_RIGHT}}', str(margins[3]))
    latex = latex.replace('{{HEADER}}', header_tex)
    latex = latex.replace('{{SUMMARY}}', summary_tex)
    latex = latex.replace('{{EXPERIENCE}}', exp_tex)
    latex = latex.replace('{{PROJECTS}}', proj_tex)
    latex = latex.replace('{{EDUCATION}}', edu_tex)
    latex = latex.replace('{{SKILLS}}', skills_tex)

    return latex

def compile_latex_to_pdf(tex_code, output_dir='generated'):
    """
    Compile LaTeX with validation and error preservation.
    Returns (tex_path, pdf_path, file_id) where pdf_path is None on failure.
    """
    os.makedirs(output_dir, exist_ok=True)
    file_id = str(uuid.uuid4())
    output_dir = os.path.abspath(output_dir)
    tex_path = os.path.join(output_dir, f"resume_{file_id}.tex")
    pdf_path = tex_path.replace('.tex', '.pdf')
    log_path = tex_path.replace('.tex', '.log')
    
    # Write .tex file
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(tex_code)
    
    # Check if pdflatex is available
    if not shutil.which('pdflatex'):
        print("[Compiler] pdflatex not found - skipping PDF generation")
        return tex_path, None, file_id
    
    try:
        # Compile twice (for references)
        for run in range(2):
            result = subprocess.run(
            [
                'pdflatex',
                '-interaction=nonstopmode',
                '-output-directory',
                output_dir,
                tex_path
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30
            )
            print("RETURN CODE:", result.returncode)

            print("STDOUT:")
            print(result.stdout.decode(errors="ignore"))

            print("STDERR:")
            print(result.stderr.decode(errors="ignore"))
            # Check return code
            if result.returncode != 0:
                print(f"[Compiler] pdflatex failed (run {run + 1})")
                # Preserve log for debugging
                if os.path.exists(log_path):
                    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                        print(f"[Compiler] Log preview:\n{f.read()[:500]}")
                return tex_path, None, file_id
        

        print("EXPECTED PDF PATH:", pdf_path)
        print("FILES IN OUTPUT DIR:", os.listdir(output_dir))
        # Verify PDF was created
        if not os.path.exists(pdf_path):
            print("[Compiler] PDF not generated despite success code")
            return tex_path, None, file_id
        
        # Cleanup auxiliary files (keep .log on error above)
        for ext in ['.aux', '.log', '.out']:
            aux_file = tex_path.replace('.tex', ext)
            if os.path.exists(aux_file):
                try:
                    os.remove(aux_file)
                except OSError as cleanup_error:
                    print(f"[Compiler] Skipping cleanup for {aux_file}: {cleanup_error}")
        
        print(f"[Compiler] PDF compiled: {file_id}")
        return tex_path, pdf_path, file_id
        
    except subprocess.TimeoutExpired:
        print("[Compiler] Timeout during compilation")
        return tex_path, None, file_id
    except Exception as e:
        print(f"[Compiler] Error: {e}")
        return tex_path, None, file_id
