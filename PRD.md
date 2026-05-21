# 📋 Project Review Document: AI-Powered Resume Analyzer & Career Intelligence Platform

**Version:** 1.0  
**Date:** 2025  
**Status:** Pre-Development Review  
**Author:** Project Team  

---

## 📑 Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Project Overview](#2-project-overview)
3. [System Architecture](#3-system-architecture)
4. [Core Features](#4-core-features)
5. [Advanced Features](#5-advanced-features)
6. [LLM Integration & Prompts](#6-llm-integration--prompts)
7. [Technical Stack](#7-technical-stack)
8. [Implementation Phases](#8-implementation-phases)
9. [Success Metrics](#9-success-metrics)
10. [Risk Analysis](#10-risk-analysis)

---

## 1. Executive Summary

### 1.1 Project Vision

An intelligent resume analysis platform that combines **multimodal PDF/image extraction**, **selective AI enhancement**, and **proactive career intelligence** to help users create ATS-optimized resumes while discovering personalized career paths.

### 1.2 Key Differentiators

| Feature | Traditional Tools | Our Platform |
|---------|------------------|--------------|
| **Input** | Text/PDF only | PDF, Images (scanned resumes, screenshots) |
| **Enhancement** | Full rewrite | Selective (weak sections only) |
| **Structure** | Template-based | Preserves original LaTeX structure |
| **Career Guidance** | Job matching (user inputs JD) | Proactive path generation (LLM-driven) |
| **Editing** | Static preview | Dual-editable (LaTeX + Visual) |
| **Scoring** | 0-100 arbitrary | Contextual (HIGH/MODERATE/LOW) |

### 1.3 Target Users

- **Primary:** Mid-level professionals (3-7 years experience) seeking career growth
- **Secondary:** Recent graduates building first resume
- **Tertiary:** Career pivoters exploring alternative paths

---

## 2. Project Overview

### 2.1 Problem Statement

Existing resume tools suffer from:
1. **Poor structure preservation** - rewrites destroy original formatting
2. **Token inefficiency** - send entire resume to LLM unnecessarily
3. **Lack of actionable guidance** - generic scores without next steps
4. **Limited editing flexibility** - either raw LaTeX or locked templates

### 2.2 Solution Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER UPLOADS RESUME                   │
│                    (PDF/PNG/JPG/JPEG)                    │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│              MULTIMODAL EXTRACTION LAYER                 │
│  ┌──────────────────┐         ┌──────────────────┐     │
│  │  PDF Extraction  │         │ Image Extraction │     │
│  │  PyMuPDF         │         │ Vision LLM       │     │
│  │  → LaTeX + JSON  │         │ → JSON directly  │     │
│  └──────────────────┘         └──────────────────┘     │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│                  STRUCTURED RESUME JSON                  │
│  { identity, experience, projects, education, skills }  │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│                    RESUME ANALYZER                       │
│  • Flags weak sections (projects, workshops, etc.)      │
│  • Scores each section (quantified metrics, verbs, etc.)│
│  • Identifies gaps and strengths                        │
└────────────────────┬────────────────────────────────────┘
                     ↓
            ┌────────┴────────┐
            ↓                 ↓
┌─────────────────┐  ┌─────────────────────────┐
│ LATEX TEMPLATE  │  │ SELECTIVE ENHANCEMENT   │
│ PREPARATION     │  │ ENGINE                  │
│                 │  │                         │
│ • Remove weak   │  │ • LLM enhances ONLY     │
│   sections      │  │   flagged sections      │
│ • Insert Node   │  │ • JSON → JSON           │
│   IDs           │  │ • Adds metrics, fixes   │
│ • Preserve rest │  │   weak verbs            │
└────────┬────────┘  └──────────┬──────────────┘
         │                      │
         └──────────┬───────────┘
                    ↓
         ┌──────────────────────┐
         │ JSON → LATEX         │
         │ CONVERTER            │
         │                      │
         │ Enhanced sections    │
         │ → LaTeX code         │
         └──────────┬───────────┘
                    ↓
         ┌──────────────────────┐
         │ LATEX INTEGRATION    │
         │                      │
         │ Replace Node IDs     │
         │ with enhanced LaTeX  │
         └──────────┬───────────┘
                    ↓
         ┌──────────────────────┐
         │ HYBRID EDITOR        │
         │ ┌────────┬─────────┐ │
         │ │ LaTeX  │ Visual  │ │
         │ │ Editor │ Preview │ │
         │ └────────┴─────────┘ │
         │   [Compile PDF]      │
         └──────────┬───────────┘
                    ↓
         ┌──────────────────────┐
         │ FINAL ENHANCED       │
         │ RESUME               │
         │ (.tex, .pdf)         │
         └──────────────────────┘
```

---

## 3. System Architecture

### 3.1 Pipeline Components

#### **Stage 1: Multimodal Extraction**

**Input Types:**
- PDF (text-based)
- PDF (scanned/image-based)
- PNG/JPG/JPEG (screenshots, phone photos)

**Extraction Logic:**
```python
def extract_resume(file_path, file_type):
    if file_type == 'pdf':
        # Check if PDF has extractable text
        text_content = quick_text_check(file_path)
        
        if len(text_content) > 100:
            # Text-based PDF → dual extraction
            return extract_pdf_dual(file_path)
        else:
            # Scanned PDF → vision LLM
            return extract_with_vision_llm(file_path)
    
    elif file_type in ['png', 'jpg', 'jpeg']:
        # Image → vision LLM
        return extract_with_vision_llm(file_path)

def extract_pdf_dual(pdf_path):
    """Returns (base_latex, json_content)"""
    # PyMuPDF extraction preserving layout
    base_latex = pdf_to_latex_preserving_structure(pdf_path)
    json_content = pdf_to_canonical_json(pdf_path)
    return base_latex, json_content

def extract_with_vision_llm(file_path):
    """Returns json_content only (no LaTeX preservation)"""
    # Send image to vision LLM with structured output prompt
    json_content = vision_llm.extract_resume_json(file_path)
    return None, json_content  # No base LaTeX for images
```

#### **Stage 2: Resume Analyzer**

**Analysis Criteria:**

| Section | Scoring Factors | Weak Threshold |
|---------|----------------|----------------|
| **Projects** | Quantified metrics, tech stack clarity, impact statements | < 60/100 |
| **Experience** | Action verbs, scope/scale, achievements vs duties | < 65/100 |
| **Workshops** | Descriptions, outcomes, relevance | < 50/100 |
| **Summary** | Conciseness, value prop, specificity | < 70/100 |

**Scoring Algorithm:**
```python
def score_section(section_name, content):
    score = 0
    
    # Factor 1: Quantified Metrics (20 points)
    metrics_found = len(re.findall(r'\d+%|\d+x|\d+\+|improved|reduced', content))
    score += min(metrics_found * 5, 20)
    
    # Factor 2: Strong Action Verbs (20 points)
    strong_verbs = ['architected', 'designed', 'built', 'optimized', 'implemented']
    weak_verbs = ['worked on', 'helped with', 'responsible for']
    
    strong_count = sum(1 for v in strong_verbs if v in content.lower())
    weak_count = sum(1 for v in weak_verbs if v in content.lower())
    
    score += strong_count * 5
    score -= weak_count * 3
    
    # Factor 3: Detail/Length (20 points)
    bullet_count = content.count('\item')
    if bullet_count >= 4: score += 20
    elif bullet_count >= 2: score += 10
    
    # Factor 4: Technical Depth (20 points)
    tech_keywords = ['api', 'database', 'system', 'architecture', 'pipeline']
    tech_count = sum(1 for kw in tech_keywords if kw in content.lower())
    score += min(tech_count * 5, 20)
    
    # Factor 5: Formatting Quality (20 points)
    if r'\begin{itemize}' in content and r'\end{itemize}' in content:
        score += 20
    
    return max(0, min(score, 100))
```

#### **Stage 3: Node ID System**

**Placeholder Generation:**
```latex
% Original LaTeX
\section{Projects}
\noindent\textbf{Project Alpha}
\begin{itemize}
  \item Built a web scraper
  \item Processed data
\end{itemize}

% After removal (weak section detected)
%%NODE_PROJECTS_001%%

% After enhancement (replaced)
\section{Projects}
\noindent\textbf{Project Alpha} \hfill \texttt{\small 2023}
\texttt{\small Python, BeautifulSoup, Pandas}
\begin{itemize}
  \item Built a high-performance web scraper processing 1M records/day
  \item Reduced data processing time by 45% via parallel execution
\end{itemize}
```

**Node ID Mapping:**
```python
class NodeIDManager:
    def __init__(self):
        self.node_map = {}  # {node_id: (section_name, original_content, line_range)}
    
    def create_node(self, section_name, original_latex, start_line, end_line):
        node_id = f"NODE_{section_name.upper()}_{uuid.uuid4().hex[:6]}"
        self.node_map[node_id] = {
            "section": section_name,
            "original": original_latex,
            "lines": (start_line, end_line)
        }
        return f"%%{node_id}%%"
    
    def replace_node(self, node_id, enhanced_latex):
        if node_id not in self.node_map:
            raise ValueError(f"Node {node_id} not found")
        
        return enhanced_latex
```

---

## 4. Core Features

### 4.1 Hybrid Editor System

#### **Architecture:**

```
┌──────────────────────────────────────────────────────────┐
│              Hybrid Resume Editor                        │
├───────────────────────┬──────────────────────────────────┤
│  LaTeX Editor         │  Visual Preview                  │
│  (Monaco Editor)      │  (Structured Contenteditable)    │
├───────────────────────┼──────────────────────────────────┤
│ \documentclass[10pt]  │  ┌────────────────────────────┐  │
│ \begin{document}      │  │ JOHN DOE                   │  │
│                       │  │ john@email.com | GitHub    │  │
│ % Header              │  └────────────────────────────┘  │
│ \section{Experience}  │                                  │
│                       │  EXPERIENCE                      │
│ \textbf{SE II}        │  Software Engineer II            │
│ FakeCorp              │  FakeCorp | 2022 - Present       │
│                       │  [Click company to edit]         │
│ \begin{itemize}       │                                  │
│   \item Built API     │  • Built API serving 50k req/day │
│   \item Reduced...    │    [Click to edit bullet]        │
│ \end{itemize}         │  • Reduced latency by 40%        │
│                       │    [Click to edit bullet]        │
│ [Line 42]             │                                  │
│ [Changes detected]    │  ℹ️ Add sections in LaTeX editor │
└───────────────────────┴──────────────────────────────────┘
   ↑ Full editing power    ↑ Text-only editing             
                                                            
                [Compile to PDF] [↓ Download .tex/.pdf]
```

#### **Editing Rules:**

| Action | LaTeX Editor | Visual Preview |
|--------|-------------|----------------|
| Edit job title | ✅ Direct | ✅ Click to edit |
| Edit bullet text | ✅ Direct | ✅ Click to edit |
| Change formatting (bold/italic) | ✅ Direct | ❌ Use LaTeX |
| Add new section | ✅ Direct | ❌ Use LaTeX |
| Reorder sections | ✅ Cut/paste | ❌ Use LaTeX |
| Change margins/spacing | ✅ Direct | ❌ Use LaTeX |

#### **Sync Mechanism:**

```javascript
// Visual Preview → LaTeX Editor sync
class EditorSync {
  constructor(latexEditor, visualPreview) {
    this.latexEditor = latexEditor;
    this.visualPreview = visualPreview;
    this.nodeMap = {}; // Maps DOM elements to LaTeX line numbers
  }
  
  onVisualEdit(element, newValue) {
    const latexLocation = this.nodeMap[element.dataset.nodeId];
    
    if (!latexLocation) {
      console.error('No LaTeX mapping for element');
      return;
    }
    
    // Update LaTeX at specific line
    const lines = this.latexEditor.getValue().split('\n');
    const { lineNum, pattern } = latexLocation;
    
    lines[lineNum] = lines[lineNum].replace(
      pattern,
      (match) => match.replace(/\{(.*?)\}/, `{${escapeLatex(newValue)}}`)
    );
    
    this.latexEditor.setValue(lines.join('\n'));
    this.markNeedsCompile();
  }
  
  buildNodeMap(latexSource) {
    // Parse LaTeX and create mapping
    const lines = latexSource.split('\n');
    
    lines.forEach((line, idx) => {
      // Map \textbf{...} to editable elements
      if (line.includes('\\textbf{')) {
        const nodeId = `title_${idx}`;
        this.nodeMap[nodeId] = {
          lineNum: idx,
          pattern: /\\textbf\{(.*?)\}/
        };
      }
      
      // Map \item ... to bullet elements
      if (line.trim().startsWith('\\item')) {
        const nodeId = `bullet_${idx}`;
        this.nodeMap[nodeId] = {
          lineNum: idx,
          pattern: /\\item (.*)/
        };
      }
    });
  }
}
```

#### **Compilation Strategy:**

**Manual Compile Button (Not Live)**

```python
# Backend: MiKTeX Compilation
@app.route('/api/compile', methods=['POST'])
def compile_latex():
    latex_code = request.json['latex']
    
    # Create temp directory
    file_id = str(uuid.uuid4())
    temp_dir = f'temp/{file_id}'
    os.makedirs(temp_dir, exist_ok=True)
    
    tex_path = os.path.join(temp_dir, 'resume.tex')
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(latex_code)
    
    # Compile with MiKTeX (local, fast)
    result = subprocess.run(
        ['pdflatex', '-interaction=nonstopmode', 'resume.tex'],
        cwd=temp_dir,
        capture_output=True,
        timeout=15
    )
    
    pdf_path = os.path.join(temp_dir, 'resume.pdf')
    
    if result.returncode == 0 and os.path.exists(pdf_path):
        return send_file(pdf_path, mimetype='application/pdf')
    else:
        # Parse error log
        log_path = os.path.join(temp_dir, 'resume.log')
        error_info = parse_latex_error_log(log_path)
        
        return jsonify({
            'error': 'Compilation failed',
            'line': error_info['line'],
            'message': error_info['message']
        }), 400

def parse_latex_error_log(log_path):
    """Extract error line and message from .log file"""
    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
        log = f.read()
    
    # Pattern: ! Error message \n l.42
    match = re.search(r'! (.*?)\nl\.(\d+) (.*)', log)
    if match:
        return {
            'message': match.group(1),
            'line': int(match.group(2)),
            'context': match.group(3)
        }
    
    return {'message': 'Unknown error', 'line': None, 'context': ''}
```

**Frontend: Compile Button UI**

```javascript
document.getElementById('compileBtn').addEventListener('click', async () => {
  const latexCode = latexEditor.getValue();
  
  // Show loading state
  setCompileState('compiling');
  
  try {
    const response = await fetch('/api/compile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ latex: latexCode })
    });
    
    if (response.ok) {
      const pdfBlob = await response.blob();
      displayPdfPreview(pdfBlob);
      setCompileState('success');
    } else {
      const error = await response.json();
      highlightErrorLine(error.line);
      showErrorMessage(error.message);
      setCompileState('error');
    }
  } catch (err) {
    setCompileState('error');
    showErrorMessage('Compilation failed: ' + err.message);
  }
});

function setCompileState(state) {
  const btn = document.getElementById('compileBtn');
  
  if (state === 'compiling') {
    btn.disabled = true;
    btn.innerHTML = '⏳ Compiling...';
  } else if (state === 'success') {
    btn.disabled = false;
    btn.innerHTML = '✓ Compiled';
    setTimeout(() => {
      btn.innerHTML = '🔄 Compile PDF';
    }, 2000);
  } else if (state === 'error') {
    btn.disabled = false;
    btn.innerHTML = '❌ Error - Fix & Retry';
  }
}

function highlightErrorLine(lineNum) {
  latexEditor.deltaDecorations([], [{
    range: new monaco.Range(lineNum, 1, lineNum, 1),
    options: {
      isWholeLine: true,
      className: 'error-line-highlight',
      glyphMarginClassName: 'error-glyph',
      hoverMessage: { value: 'LaTeX compilation error on this line' }
    }
  }]);
}
```

---

## 5. Advanced Features

### 5.1 Career Paths Dashboard

#### **Overview:**

Proactive career intelligence system that generates 3-5 personalized career paths based on resume analysis **without user input**.

#### **Architecture:**

```
Resume JSON
    ↓
Profile Classifier (LLM)
    ↓
{
  "current_level": "Mid-level",
  "primary_domain": "Backend Engineering",
  "years_experience": 3,
  "key_skills": ["Python", "AWS", "System Design"],
  "education_level": "Bachelor's",
  "project_complexity": "Production-scale",
  "leadership_indicators": "Low"
}
    ↓
Career Path Generator (LLM)
    ↓
Generates 3-5 Paths:
├─ Path 1: Ready Now (90%+ alignment)
├─ Path 2: Growth Path (70-80% alignment)
├─ Path 3: Stretch Goal (60-70% alignment)
├─ Path 4: Pivot Option (40-50% alignment)
└─ Path 5: Alternative Track (specialist vs generalist)
    ↓
For Each Path:
├─ Ideal job requirements
├─ Gap analysis
├─ Actionable next steps
└─ Time-to-ready estimate
```

#### **UI/UX Design:**

```
┌─────────────────────────────────────────────────────────┐
│  🎯 Career Paths for Your Profile                      │
│  Based on 3 years Backend Engineering experience       │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ ✅ READY NOW                                            │
│ Senior Backend Engineer (Python/AWS)                    │
│ Alignment: HIGH (92%)                                   │
│                                                         │
│ ✓ You have:                                             │
│   • 3 years production Python experience                │
│   • AWS cloud deployment knowledge                      │
│   • RESTful API design & optimization                   │
│   • Performance tuning & caching                        │
│                                                         │
│ Minor gaps:                                             │
│   ⚠ Show more system design examples (add 1-2 bullets) │
│   ⚠ Highlight any mentoring/code review                │
│                                                         │
│ Next steps:                                             │
│   1. Emphasize architecture decisions in project bullets│
│   2. Add "Mentored junior developers" if applicable     │
│   3. Ready to apply immediately                         │
│                                                         │
│ [Apply with Confidence] [View Similar Roles]            │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 🎯 GROWTH PATH (6-12 months)                            │
│ Staff Engineer (Individual Contributor Track)          │
│ Alignment: MODERATE (74%)                               │
│                                                         │
│ What you need:                                          │
│   ⚠ 2 more years senior-level experience                │
│   ⚠ Technical leadership examples needed                │
│   ⚠ Cross-team influence / architecture proposals       │
│   ⚠ Published technical writing or talks                │
│                                                         │
│ Transition roadmap:                                     │
│   1. Take ownership of system architecture (3-6 months) │
│   2. Write technical design docs & RFC proposals        │
│   3. Mentor 2-3 engineers, document impact              │
│   4. Publish 1-2 technical blog posts                   │
│   5. Lead cross-team initiative                         │
│                                                         │
│ Time to ready: 8-12 months                              │
│                                                         │
│ [View Detailed Roadmap] [Find Resources]                │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 🚀 STRETCH GOAL (12-18 months)                          │
│ Engineering Manager                                     │
│ Alignment: MODERATE (68%)                               │
│                                                         │
│ Why this is a stretch:                                  │
│   ✗ No management experience shown                      │
│   ✗ Need people leadership track record                 │
│   ⚠ Limited cross-functional collaboration examples     │
│                                                         │
│ Transition strategy:                                    │
│   1. Become tech lead of your team (6 months)           │
│   2. Manage 1-2 interns or junior devs                  │
│   3. Run sprint planning & retrospectives               │
│   4. Take management training course                    │
│   5. Shadow current managers, seek mentorship           │
│                                                         │
│ Time to ready: 12-18 months                             │
│                                                         │
│ [See Management Resources] [Talk to Mentors]            │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 🔄 PIVOT OPTION (18-24 months)                          │
│ Machine Learning Engineer                               │
│ Alignment: LOW (52%)                                    │
│                                                         │
│ Transferable strengths:                                 │
│   ✓ Strong Python foundation                            │
│   ✓ Data pipeline & processing experience               │
│   ✓ System optimization skills                          │
│                                                         │
│ Major gaps:                                             │
│   ✗ No ML/AI project experience                         │
│   ✗ Missing: TensorFlow, PyTorch, Scikit-learn          │
│   ✗ Lacks statistics/linear algebra background          │
│   ✗ No model training or deployment examples            │
│                                                         │
│ Full transition plan:                                   │
│   Phase 1 (0-6 months): Learn fundamentals              │
│     • Complete ML course (Fast.ai or Coursera)          │
│     • Study linear algebra & statistics                 │
│   Phase 2 (6-12 months): Build portfolio                │
│     • 3-4 ML projects (Kaggle, personal datasets)       │
│     • Contribute to open-source ML libraries            │
│   Phase 3 (12-18 months): Transition role               │
│     • Target "ML Engineer (Junior)" or hybrid role      │
│     • Leverage backend experience for MLOps/pipelines   │
│   Phase 4 (18-24 months): Full ML role                  │
│                                                         │
│ Time to ready: 18-24 months                             │
│ Difficulty: HIGH (career pivot)                         │
│                                                         │
│ [Explore Learning Path] [Find Courses] [Join Community] │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 🛤️ ALTERNATIVE TRACK                                    │
│ DevOps/Platform Engineer                                │
│ Alignment: MODERATE (71%)                               │
│                                                         │
│ Why this fits:                                          │
│   ✓ AWS experience (strong foundation)                  │
│   ✓ System design & optimization skills                 │
│   ⚠ Need more infrastructure-as-code examples           │
│                                                         │
│ Skills to add:                                          │
│   • Kubernetes, Docker (containerization)               │
│   • Terraform or Ansible (IaC)                          │
│   • CI/CD pipeline design                               │
│   • Monitoring & observability (Prometheus, Grafana)    │
│                                                         │
│ Quick wins:                                             │
│   1. Dockerize your existing projects                   │
│   2. Set up CI/CD for side project                      │
│   3. Get CKA (Certified Kubernetes Admin)               │
│                                                         │
│ Time to ready: 6-9 months                               │
│                                                         │
│ [View DevOps Roadmap] [Certification Prep]              │
└─────────────────────────────────────────────────────────┘
```

---

### 5.2 Advanced Feature 1: Dynamic Career Graph

#### **Visual Representation:**

```
Current Position: Software Engineer II (Backend)
        │
        ├─────────────────────────────────────────┐
        │                                         │
   [1 Year]                                  [1 Year]
        │                                         │
        ↓                                         ↓
┌───────────────────┐                  ┌──────────────────┐
│ Senior Backend    │  Probability:    │ Full Stack       │
│ Engineer          │  HIGH (85%)      │ Engineer         │
└────────┬──────────┘                  └─────────┬────────┘
         │                                       │
    [2-3 Years]                            [2-3 Years]
         │                                       │
         ├───────────────┬───────────────────────┤
         ↓               ↓                       ↓
┌─────────────┐  ┌──────────────┐     ┌─────────────────┐
│ Staff       │  │ Engineering  │     │ Solutions       │
│ Engineer    │  │ Manager      │     │ Architect       │
│ (IC Track)  │  │ (Mgmt Track) │     │ (Specialist)    │
└─────────────┘  └──────────────┘     └─────────────────┘
  Probability:     Probability:         Probability:
  HIGH (75%)       MODERATE (60%)       MODERATE (65%)
```

#### **Implementation:**

**Data Structure:**
```json
{
  "career_graph": {
    "current_node": {
      "title": "Software Engineer II",
      "level": "Mid",
      "tenure": "3 years"
    },
    "paths": [
      {
        "timeframe": "1 year",
        "options": [
          {
            "title": "Senior Backend Engineer",
            "probability": "HIGH",
            "probability_score": 85,
            "why": "Strong technical foundation, needs minor leadership examples"
          },
          {
            "title": "Full Stack Engineer",
            "probability": "MODERATE",
            "probability_score": 65,
            "why": "Backend strong, need frontend skill development"
          }
        ]
      },
      {
        "timeframe": "3 years",
        "from": "Senior Backend Engineer",
        "options": [
          {
            "title": "Staff Engineer",
            "track": "IC",
            "probability": "HIGH",
            "probability_score": 75
          },
          {
            "title": "Engineering Manager",
            "track": "Management",
            "probability": "MODERATE",
            "probability_score": 60
          }
        ]
      }
    ]
  }
}
```

**Visualization:** Use **D3.js** or **React Flow** for interactive graph.

---

### 5.3 Advanced Feature 2: Market Intelligence (Optional)

#### **Integration Points:**

```python
# Optional: LinkedIn/Indeed API integration
def fetch_market_data(role_title):
    """
    Query job market APIs for:
    - Number of open positions
    - Salary ranges
    - Top hiring companies
    - Trending skills
    - Remote availability %
    """
    
    # Example with hypothetical API
    response = job_market_api.query({
        "title": role_title,
        "region": "United States",
        "time_range": "last_30_days"
    })
    
    return {
        "demand": categorize_demand(response['open_positions']),
        "avg_salary": response['salary_range'],
        "top_companies": response['top_employers'][:5],
        "trending_skills": response['skill_frequency'][:10],
        "remote_pct": response['remote_percentage']
    }

def categorize_demand(position_count):
    if position_count > 5000:
        return "HIGH"
    elif position_count > 1000:
        return "MODERATE"
    else:
        return "LOW"
```

#### **UI Display:**

```
Senior Backend Engineer
├─ 📊 Market Demand: HIGH (8,400 open roles)
├─ 💰 Salary Range: $130k - $180k (median: $155k)
├─ 🏢 Top Hiring: Google, Meta, Stripe, Coinbase, Netflix
├─ 📈 Trending Skills: 
│   • Kubernetes (+52% in job postings)
│   • Go (+38%)
│   • gRPC (+29%)
│   • PostgreSQL (stable)
├─ 🌍 Remote-Friendly: 82% of postings
└─ 📍 Top Locations: SF Bay Area, NYC, Seattle, Austin
```

---

### 5.4 Advanced Feature 3: Competitive Analysis

#### **Concept:**

Compare user's resume against **aggregated anonymous data** from similar profiles.

```
┌─────────────────────────────────────────────────────────┐
│ 📊 Competitive Analysis                                 │
│ Compared to 1,247 Senior Backend Engineers              │
└─────────────────────────────────────────────────────────┘

Your Strengths (Top 20%):
✓ AWS experience & cloud architecture
✓ Data pipeline design
✓ Performance optimization

Common Strengths You Lack (Bottom 40%):
⚠ Kubernetes/container orchestration (68% of peers have this)
⚠ gRPC/protocol buffers (54% of peers)
⚠ Open-source contributions (47% of peers)

Your Unique Differentiators:
🌟 ML pipeline integration (only 12% have this)
🌟 Data engineering hybrid background (rare)

Recommendation:
Focus on Kubernetes to close gap with peers, while emphasizing
your ML+Backend hybrid expertise as a unique positioning.

Consider roles like:
• ML Infrastructure Engineer
• Data Platform Engineer
• Backend Engineer (ML-focused teams)
```

#### **Data Privacy:**

- **No individual data stored** - only aggregate statistics
- **Anonymized comparisons** - no user-to-user matching
- **Opt-in only** - users choose to see competitive analysis

---

## 6. LLM Integration & Prompts

### 6.1 Prompt Architecture

All LLM calls use **structured output** with **canonical JSON schemas** for deterministic parsing.

---

### 6.2 Prompt 1: Vision LLM - Image Resume Extraction

**Model:** GPT-4 Vision / Gemini Vision  
**Purpose:** Extract resume from image (screenshot, photo, scanned PDF)  
**Input:** Image file  
**Output:** Canonical resume JSON  

```python
VISION_EXTRACTION_PROMPT = """
You are a resume extraction specialist. Analyze the provided resume image and extract ALL information into structured JSON.

OUTPUT SCHEMA (strict):
{
  "resume_id": "generated_uuid",
  "schema_version": "1.0",
  "identity": {
    "name": "Full name in original case",
    "email": "email@domain.com",
    "phone": "+1234567890 or original format",
    "linkedin": "linkedin.com/in/username (if visible)",
    "github": "github.com/username (if visible)",
    "portfolio": "website.com (if visible)",
    "location": "City, State/Country (if visible)"
  },
  "summary": "Professional summary text or empty string",
  "experience": [
    {
      "title": "Job Title",
      "company": "Company Name",
      "location": "City, State (if shown)",
      "duration": "Month Year - Month Year or Present",
      "type": "Full-time/Internship/Contract (if shown, else empty)",
      "bullets": [
        "First responsibility/achievement",
        "Second responsibility/achievement"
      ]
    }
  ],
  "projects": [
    {
      "title": "Project Name",
      "type": "Personal/Academic/Research (if shown)",
      "year": "2023 or date range",
      "tech_stack": ["Python", "Flask", "AWS"],
      "bullets": [
        "Project description or achievement"
      ]
    }
  ],
  "education": [
    {
      "degree": "Bachelor of Science",
      "major": "Computer Science",
      "institution": "University Name",
      "location": "City, State (if shown)",
      "graduation_year": "2022",
      "gpa": "3.8/4.0 (if shown, else empty)",
      "relevant_coursework": ["Course 1", "Course 2"] or []
    }
  ],
  "workshops": [
    {
      "title": "Workshop/Training Name",
      "year": "2023",
      "description": "Brief description (if available)"
    }
  ],
  "skills": {
    "languages": ["Python", "JavaScript"],
    "frameworks": ["React", "Flask"],
    "tools": ["Git", "Docker"],
    "domains": ["Backend", "Data Engineering"]
  }
}

EXTRACTION RULES:
1. Extract text EXACTLY as written - preserve capitalization, spelling
2. If information is unclear/illegible, use empty string or empty array
3. Do NOT invent or hallucinate information not visible in image
4. If resume has unusual format, do your best to map to schema
5. For bullet points, preserve original wording
6. Return ONLY valid JSON - no markdown, no explanations

IMAGE PROVIDED: [Resume screenshot/photo]
"""
```

---

### 6.3 Prompt 2: Resume Analyzer - Section Scoring & Gap Detection

**Model:** GPT-4o-mini / Llama 3 70B / Groq  
**Purpose:** Analyze resume JSON, score sections, identify weak areas  
**Input:** Canonical resume JSON  
**Output:** Analysis object with scores and improvements  

```python
ANALYZER_PROMPT = """
You are a professional resume analyst. Evaluate the provided resume and identify strengths, weaknesses, and specific improvements.

INPUT: Resume JSON object

OUTPUT SCHEMA (strict):
{
  "profile_summary": {
    "years_experience": 3,
    "current_level": "Mid-level",
    "primary_domain": "Backend Engineering",
    "key_skills": ["Python", "AWS", "System Design"],
    "education_level": "Bachelor's",
    "project_complexity": "Production-scale",
    "leadership_indicators": "Low/Moderate/High"
  },
  "section_scores": {
    "experience": {
      "score": 75,
      "category": "HIGH/MODERATE/LOW",
      "strengths": [
        "Uses quantified metrics (50k requests/day, 40% improvement)",
        "Strong action verbs (architected, optimized)"
      ],
      "weaknesses": [
        "Some bullets are task-focused, not achievement-focused",
        "Missing scope/team size context"
      ]
    },
    "projects": {
      "score": 58,
      "category": "MODERATE",
      "strengths": [
        "Shows technical depth with specific technologies"
      ],
      "weaknesses": [
        "No quantified metrics in project bullets",
        "Missing impact statements (how was it used?)",
        "Tech stack clarity needed"
      ]
    },
    "workshops": {
      "score": 45,
      "category": "LOW",
      "strengths": [],
      "weaknesses": [
        "Only lists workshop titles, no outcomes or learnings",
        "Missing descriptions of what was built/learned"
      ]
    },
    "summary": {
      "score": 72,
      "category": "MODERATE",
      "strengths": [
        "Concise and focused"
      ],
      "weaknesses": [
        "Generic phrases like 'passionate' or 'hard-working'",
        "Could specify unique value proposition"
      ]
    }
  },
  "weak_sections": ["projects", "workshops"],
  "overall_assessment": {
    "content_quality": "HIGH",
    "structure": "HIGH",
    "impact": "MODERATE",
    "completeness": "MODERATE",
    "ats_readiness": "HIGH"
  },
  "improvement_priority": [
    {
      "section": "projects",
      "issue": "Missing quantified metrics",
      "suggestion": "Add scale/impact metrics (e.g., '1M records/day', '40% faster')",
      "priority": "HIGH",
      "examples": [
        "Before: Built a web scraper",
        "After: Built a high-performance web scraper processing 1M records/day, reducing data collection time by 45%"
      ]
    },
    {
      "section": "workshops",
      "issue": "No descriptions or outcomes",
      "suggestion": "Add bullet points explaining what was built or learned",
      "priority": "MODERATE",
      "examples": [
        "Before: Large Language Models Workshop (2023)",
        "After: Large Language Models Workshop (2023)\n• Built RAG system using Pinecone and Groq\n• Implemented retrieval optimization reducing query time by 30%"
      ]
    },
    {
      "section": "experience",
      "issue": "Some task-focused bullets instead of achievement-focused",
      "suggestion": "Reframe bullets to highlight impact and results",
      "priority": "MODERATE",
      "examples": [
        "Before: Worked on real-time notification system",
        "After: Implemented real-time notification system serving 10k concurrent users, reducing latency by 25%"
      ]
    }
  ],
  "ats_keywords": ["Python", "Flask", "AWS", "REST API", "System Design", "Performance Optimization"],
  "missing_keywords": ["Kubernetes", "Microservices", "CI/CD"]
}

SCORING RUBRIC:
- **90-100 (HIGH)**: Quantified metrics, strong verbs, clear impact, technical depth
- **65-89 (MODERATE)**: Some metrics, decent clarity, room for improvement
- **0-64 (LOW)**: Vague, task-focused, lacks metrics, weak verbs

ANALYSIS RULES:
1. Be specific - provide exact examples of issues
2. Prioritize improvements by impact (HIGH/MODERATE/LOW)
3. Extract ATS keywords actually present in resume
4. Do NOT invent experience or achievements
5. Return ONLY valid JSON
"""
```

---

### 6.4 Prompt 3: Selective Enhancer - Improve Weak Sections Only

**Model:** GPT-4o / Llama 3 70B  
**Purpose:** Enhance ONLY flagged weak sections  
**Input:** Weak sections from resume JSON + improvement suggestions  
**Output:** Enhanced sections in same JSON format  

```python
SELECTIVE_ENHANCEMENT_PROMPT = """
You are a resume enhancement specialist. Improve ONLY the provided weak sections by applying the improvement suggestions.

INPUT:
{
  "sections_to_enhance": {
    "projects": [...original project data...],
    "workshops": [...original workshop data...]
  },
  "improvement_suggestions": [
    {
      "section": "projects",
      "issue": "Missing quantified metrics",
      "suggestion": "Add scale/impact metrics",
      "examples": [...]
    }
  ]
}

OUTPUT SCHEMA (strict - return ONLY enhanced sections):
{
  "projects": [
    {
      "title": "Same as original",
      "type": "Same as original",
      "year": "Same as original",
      "tech_stack": ["Enhanced if needed"],
      "bullets": [
        "ENHANCED bullet with quantified metrics",
        "ENHANCED bullet with stronger action verbs"
      ]
    }
  ],
  "workshops": [
    {
      "title": "Same as original",
      "year": "Same as original",
      "description": "ENHANCED description with outcomes/learnings"
    }
  ]
}

ENHANCEMENT RULES:
1. Apply ALL improvement suggestions from the input
2. Add quantified metrics where missing (be realistic based on project scope):
   - For personal projects: 100s-1000s scale
   - For production systems: 10k-1M+ scale
   - Performance improvements: 20-50% range typical
3. Use strong action verbs:
   - GOOD: Architected, Designed, Built, Implemented, Optimized, Engineered
   - AVOID: Worked on, Helped with, Responsible for
4. Keep bullets concise (under 25 words)
5. Do NOT invent new projects/experiences - only enhance existing ones
6. Do NOT change field names or structure - match input schema exactly
7. Return ONLY valid JSON

EXAMPLE TRANSFORMATIONS:

Input bullet:
"Built a web scraper"

Enhanced bullet:
"Built a high-performance web scraper processing 1M records/day from 5 e-commerce sites, reducing data collection time by 45%"

---

Input bullet:
"Implemented data cleaning scripts"

Enhanced bullet:
"Implemented automated data cleaning and normalization scripts using Pandas, improving data quality scores by 22% and reducing manual processing time"

---

Input workshop (before):
{
  "title": "Large Language Models Workshop",
  "year": "2023",
  "description": ""
}

Enhanced workshop (after):
{
  "title": "Large Language Models Workshop",
  "year": "2023",
  "description": "Built a document-grounded RAG system using Groq and Pinecone with custom dataset creation. Implemented retrieval optimization based on topic frequency, reducing query latency by 30%."
}
"""
```

---

### 6.5 Prompt 4: Career Path Generator

**Model:** GPT-4o / Claude Sonnet 3.5  
**Purpose:** Generate 3-5 personalized career paths  
**Input:** Resume profile summary (from analyzer)  
**Output:** Career paths with alignment scores and roadmaps  

```python
CAREER_PATH_PROMPT = """
You are an expert career strategist. Based on the candidate's profile, generate 3-5 personalized career paths ranging from "ready now" to "pivot options".

INPUT:
{
  "profile": {
    "years_experience": 3,
    "current_role": "Software Engineer II",
    "primary_domain": "Backend Engineering",
    "key_skills": ["Python", "Flask", "AWS", "System Design"],
    "education": "BS Computer Science",
    "project_complexity": "Production-scale",
    "leadership_indicators": "Low",
    "strengths": ["Quantified metrics", "Technical depth"],
    "weaknesses": ["Limited leadership examples", "Missing Kubernetes"]
  }
}

OUTPUT SCHEMA (strict):
{
  "career_paths": [
    {
      "category": "ready_now",
      "role_title": "Senior Backend Engineer (Python/AWS)",
      "seniority": "Senior",
      "alignment_score": 92,
      "alignment_category": "HIGH",
      "ideal_requirements": {
        "years_experience": "4-6",
        "technical_skills": ["Python", "AWS", "System Design", "REST APIs"],
        "soft_skills": ["Code review", "Mentoring"],
        "education": "Bachelor's in CS or equivalent"
      },
      "current_strengths": [
        "3 years production Python experience",
        "AWS cloud deployment & optimization",
        "RESTful API design and performance tuning",
        "Strong system design foundation"
      ],
      "gaps": [
        {
          "category": "experience",
          "description": "1 more year at senior level typically expected",
          "severity": "LOW",
          "how_to_close": "Emphasize scope and impact of current work"
        },
        {
          "category": "leadership",
          "description": "Limited mentoring/code review examples shown",
          "severity": "MODERATE",
          "how_to_close": "Add 1-2 bullets showing knowledge sharing or junior dev guidance"
        }
      ],
      "next_steps": [
        "Add system architecture decision examples to project bullets",
        "Highlight any mentoring, code reviews, or knowledge sharing",
        "Emphasize ownership of production systems",
        "Ready to apply immediately with minor resume tweaks"
      ],
      "time_to_ready": "0-3 months",
      "difficulty": "EASY",
      "probability": "Very High"
    },
    {
      "category": "growth_path",
      "role_title": "Staff Engineer (Individual Contributor Track)",
      "seniority": "Staff",
      "alignment_score": 74,
      "alignment_category": "MODERATE",
      "ideal_requirements": {
        "years_experience": "7-10",
        "technical_skills": ["Advanced system design", "Cross-team architecture", "Technical leadership"],
        "soft_skills": ["Technical mentorship", "Influence without authority", "Written communication"],
        "education": "Bachelor's or higher"
      },
      "current_strengths": [
        "Strong technical foundation in backend systems",
        "Production system ownership experience",
        "Performance optimization skills"
      ],
      "gaps": [
        {
          "category": "experience",
          "description": "Need 4+ more years at senior+ level",
          "severity": "HIGH",
          "how_to_close": "Gain senior-level experience first, then work toward staff"
        },
        {
          "category": "leadership",
          "description": "No technical leadership or cross-team influence shown",
          "severity": "HIGH",
          "how_to_close": "Lead architecture proposals, mentor multiple engineers, drive technical decisions"
        },
        {
          "category": "visibility",
          "description": "No evidence of technical writing, talks, or open-source",
          "severity": "MODERATE",
          "how_to_close": "Publish blog posts, give talks, contribute to OSS"
        }
      ],
      "next_steps": [
        "First, secure Senior Engineer role (see Path 1)",
        "In senior role, take ownership of system architecture (6-12 months)",
        "Write technical design docs and RFC proposals",
        "Mentor 2-3 engineers, document impact",
        "Publish 2-3 technical blog posts or give internal talks",
        "Lead a cross-team technical initiative",
        "Build reputation as subject matter expert"
      ],
      "time_to_ready": "2-3 years",
      "difficulty": "MODERATE",
      "probability": "Moderate (requires sustained growth)"
    },
    {
      "category": "growth_path",
      "role_title": "Engineering Manager",
      "seniority": "Manager",
      "alignment_score": 68,
      "alignment_category": "MODERATE",
      "ideal_requirements": {
        "years_experience": "5-8",
        "technical_skills": ["System architecture understanding", "Technical project management"],
        "soft_skills": ["People management", "1-on-1s", "Performance reviews", "Hiring", "Team building"],
        "education": "Bachelor's"
      },
      "current_strengths": [
        "Strong technical background provides credibility",
        "Understanding of backend systems and challenges"
      ],
      "gaps": [
        {
          "category": "management_experience",
          "description": "No people management experience shown",
          "severity": "HIGH",
          "how_to_close": "Become tech lead, then manage interns/junior devs, then full team"
        },
        {
          "category": "soft_skills",
          "description": "Limited cross-functional collaboration examples",
          "severity": "MODERATE",
          "how_to_close": "Work with product, design, and other teams; document collaboration"
        }
      ],
      "next_steps": [
        "Become tech lead of your current team (6-12 months)",
        "Manage 1-2 interns or new hires as a trial",
        "Run sprint planning, standups, and retrospectives",
        "Take a management fundamentals course",
        "Shadow current managers, find a management mentor",
        "Practice 1-on-1s and feedback conversations",
        "Decide if management track truly fits your interests"
      ],
      "time_to_ready": "2-3 years",
      "difficulty": "MODERATE-HIGH",
      "probability": "Moderate (requires deliberate transition)"
    },
    {
      "category": "pivot_option",
      "role_title": "Machine Learning Engineer",
      "seniority": "Mid-level",
      "alignment_score": 52,
      "alignment_category": "LOW",
      "ideal_requirements": {
        "years_experience": "3-5",
        "technical_skills": ["Python", "TensorFlow/PyTorch", "ML algorithms", "Model deployment", "Data pipelines"],
        "soft_skills": ["Experimentation", "Data analysis"],
        "education": "Bachelor's in CS/Math/Stats or equivalent"
      },
      "current_strengths": [
        "Strong Python foundation",
        "Data pipeline and processing experience",
        "System optimization skills (transferable to model optimization)"
      ],
      "gaps": [
        {
          "category": "technical_skills",
          "description": "No ML/AI project experience or model training",
          "severity": "HIGH",
          "how_to_close": "Build 3-4 ML projects, take courses, gain hands-on experience"
        },
        {
          "category": "knowledge",
          "description": "Missing ML frameworks (TensorFlow, PyTorch, Scikit-learn)",
          "severity": "HIGH",
          "how_to_close": "Learn frameworks through projects and coursework"
        },
        {
          "category": "fundamentals",
          "description": "Statistics and linear algebra background unclear",
          "severity": "MODERATE",
          "how_to_close": "Study ML fundamentals, math prerequisites"
        }
      ],
      "next_steps": [
        "Phase 1 (0-6 months): Learn fundamentals",
        "  • Complete ML course (Fast.ai, Coursera, or Deeplearning.ai)",
        "  • Study linear algebra and statistics basics",
        "  • Read 'Hands-On Machine Learning' book",
        "Phase 2 (6-12 months): Build portfolio",
        "  • Complete 3-4 ML projects (Kaggle competitions, personal datasets)",
        "  • Deploy 1-2 models to production (even small scale)",
        "  • Contribute to open-source ML libraries",
        "Phase 3 (12-18 months): Transition role",
        "  • Target 'ML Engineer (Junior)' or hybrid Backend+ML roles",
        "  • Leverage backend experience for MLOps and data pipelines",
        "  • Emphasize engineering skills over pure research",
        "Phase 4 (18-24 months): Full ML Engineer role",
        "  • Apply to mid-level ML positions"
      ],
      "time_to_ready": "18-24 months",
      "difficulty": "HIGH (career pivot)",
      "probability": "Low-Moderate (requires significant reskilling)"
    },
    {
      "category": "alternative_track",
      "role_title": "DevOps / Platform Engineer",
      "seniority": "Mid-Senior",
      "alignment_score": 71,
      "alignment_category": "MODERATE",
      "ideal_requirements": {
        "years_experience": "3-6",
        "technical_skills": ["AWS/Cloud", "Kubernetes", "Terraform/IaC", "CI/CD", "Monitoring"],
        "soft_skills": ["System reliability", "Automation mindset"],
        "education": "Bachelor's in CS or equivalent"
      },
      "current_strengths": [
        "AWS experience (strong foundation)",
        "Backend system understanding",
        "Performance optimization skills"
      ],
      "gaps": [
        {
          "category": "skills",
          "description": "Missing Kubernetes and container orchestration",
          "severity": "HIGH",
          "how_to_close": "Learn Kubernetes, get CKA certification"
        },
        {
          "category": "skills",
          "description": "Infrastructure-as-Code (Terraform/Ansible) not shown",
          "severity": "MODERATE",
          "how_to_close": "Learn Terraform, automate infrastructure setup"
        },
        {
          "category": "skills",
          "description": "CI/CD pipeline design experience unclear",
          "severity": "MODERATE",
          "how_to_close": "Build CI/CD pipelines for projects"
        }
      ],
      "next_steps": [
        "Dockerize all your existing projects",
        "Set up Kubernetes cluster (local or cloud) and deploy apps",
        "Learn Terraform and automate AWS infrastructure",
        "Build a full CI/CD pipeline (GitHub Actions + Docker + K8s)",
        "Get CKA (Certified Kubernetes Administrator) certification",
        "Add monitoring and alerting to projects (Prometheus, Grafana)",
        "Emphasize infrastructure and reliability work in resume"
      ],
      "time_to_ready": "6-9 months",
      "difficulty": "MODERATE",
      "probability": "High (natural extension of backend skills)"
    }
  ]
}

GENERATION RULES:
1. Generate 3-5 paths covering different categories:
   - At least 1 "ready_now" (90%+ alignment)
   - At least 1 "growth_path" (65-80% alignment)
   - At least 1 "pivot_option" or "alternative_track" (40-70% alignment)

2. Alignment scoring:
   - 90-100: HIGH (ready now or very close)
   - 65-89: MODERATE (achievable with effort)
   - 40-64: LOW (significant gaps, but possible)
   - <40: Don't suggest (too unrealistic)

3. Be realistic about timelines:
   - Ready now: 0-6 months
   - Growth path: 1-3 years
   - Pivot: 1.5-3 years

4. Prioritize actionable next steps - specific, not generic
5. Consider both IC (individual contributor) and management tracks
6. Return ONLY valid JSON

"""
```

---

### 6.6 Prompt 5: Job Requirement Generator (for each career path)

**Model:** GPT-4o-mini  
**Purpose:** Generate ideal job requirements for recommended roles  
**Input:** Career path role title + profile  
**Output:** Detailed job requirements  

```python
JOB_REQUIREMENT_PROMPT = """
You are a technical recruiter. For the given role, generate realistic ideal job requirements.

INPUT:
{
  "role_title": "Senior Backend Engineer",
  "seniority": "Senior",
  "domain": "Backend Engineering"
}

OUTPUT SCHEMA:
{
  "role_title": "Senior Backend Engineer",
  "typical_requirements": {
    "years_experience": "4-7 years in backend development",
    "education": "Bachelor's in Computer Science or equivalent experience",
    "technical_skills": {
      "required": [
        "Proficient in Python, Go, or Java",
        "RESTful API design and development",
        "SQL and NoSQL databases",
        "Cloud platforms (AWS, GCP, or Azure)",
        "System design and architecture",
        "Performance optimization and scaling"
      ],
      "preferred": [
        "Kubernetes and containerization",
        "Microservices architecture",
        "Message queues (Kafka, RabbitMQ)",
        "CI/CD pipeline design",
        "Monitoring and observability tools"
      ]
    },
    "soft_skills": [
      "Code review and mentorship",
      "Cross-functional collaboration",
      "Technical documentation",
      "Problem-solving and debugging",
      "Communication with non-technical stakeholders"
    ],
    "certifications": {
      "helpful": ["AWS Solutions Architect", "CKA (Kubernetes)"],
      "required": []
    }
  },
  "typical_responsibilities": [
    "Design and implement scalable backend services",
    "Lead architecture decisions for new features",
    "Mentor junior and mid-level engineers",
    "Optimize system performance and reliability",
    "Collaborate with product and frontend teams",
    "Participate in on-call rotation and incident response",
    "Write technical design documents"
  ],
  "success_metrics": [
    "System uptime and reliability",
    "API response time and throughput",
    "Code quality and test coverage",
    "Team velocity and delivery",
    "Mentorship impact on junior engineers"
  ]
}

Return ONLY valid JSON.
"""
```

---

## 7. Technical Stack

### 7.1 Backend

```yaml
Language: Python 3.11+
Framework: Flask 3.0

Core Dependencies:
  - PyMuPDF (fitz): PDF extraction with layout preservation
  - groq: LLM API client
  - python-dotenv: Environment variable management
  - werkzeug: Secure filename handling

Storage:
  - File system: Temporary uploads, cache, generated files
  - No database required (stateless architecture)

PDF Compilation:
  - MiKTeX (local installation)
  - subprocess for pdflatex invocation
```

### 7.2 Frontend

```yaml
Core:
  - HTML5
  - CSS3 (custom design system)
  - Vanilla JavaScript (ES6+)

Libraries:
  - Monaco Editor: LaTeX code editor (VS Code engine)
  - PDF.js: PDF preview rendering
  - Custom contenteditable: Visual preview editing

UI Framework:
  - No framework (lightweight, fast)
  - Custom components for resume editor
```

### 7.3 LLM Integration

```yaml
Primary Provider: Groq
Model: llama3-groq-70b-8192-tool-use-preview / openai/gpt-oss-20b

Vision Model (optional):
  - GPT-4 Vision (via OpenAI API)
  - Gemini Vision (via Google AI)

Response Format:
  - JSON mode (structured outputs)
  - Schema validation on client side
```

### 7.4 Deployment

```yaml
Development:
  - Local Flask server (localhost:5000)
  - MiKTeX installed locally
  - Groq API key in .env

Production (future):
  - Gunicorn + Nginx
  - Docker container with TeX Live
  - Redis for caching
  - CDN for static assets
```

---

## 8. Implementation Phases

### Phase 1: Core Pipeline (Weeks 1-3)

**Deliverables:**
- ✅ PDF → Dual extraction (LaTeX + JSON)
- ✅ Resume analyzer with section scoring
- ✅ Selective enhancer (LLM for weak sections only)
- ✅ JSON → LaTeX converter
- ✅ Node ID system for placeholder replacement
- ✅ Basic compilation (MiKTeX integration)

**Success Criteria:**
- Can upload PDF, get analysis, enhance weak sections, download improved .tex

---

### Phase 2: Hybrid Editor (Weeks 4-5)

**Deliverables:**
- ✅ Monaco editor for LaTeX
- ✅ Visual preview with contenteditable fields
- ✅ Bidirectional sync (preview ↔ LaTeX)
- ✅ Manual compile button with error handling
- ✅ PDF preview pane

**Success Criteria:**
- Users can edit in either pane and see changes reflected
- Compilation errors show line numbers and messages

---

### Phase 3: Career Paths Dashboard (Weeks 6-8)

**Deliverables:**
- ✅ Profile classifier (from resume JSON)
- ✅ Career path generator (3-5 paths)
- ✅ Gap analysis and next steps
- ✅ UI cards for each path
- ✅ Interactive path selection

**Success Criteria:**
- Generates realistic, personalized career paths
- Provides actionable next steps
- HIGH/MODERATE/LOW alignment scoring

---

### Phase 4: Advanced Features (Weeks 9-11)

**Deliverables:**
- ✅ Dynamic career graph visualization (D3.js/React Flow)
- ✅ Market intelligence integration (optional API)
- ✅ Competitive analysis (aggregated comparisons)

**Success Criteria:**
- Visual career trajectory graph
- Market data enhances career recommendations
- Competitive insights help positioning

---

### Phase 5: Image Support (Weeks 12-13)

**Deliverables:**
- ✅ Image upload support (.png, .jpg, .jpeg)
- ✅ Vision LLM integration
- ✅ OCR fallback (optional budget mode)

**Success Criteria:**
- Can extract resume from screenshots and scanned docs
- Vision LLM accuracy >90% for clean images

---

### Phase 6: Polish & Optimization (Week 14+)

**Deliverables:**
- ✅ Multi-level caching (v1, v2, v3, rendered files)
- ✅ Error handling and user feedback
- ✅ Loading states and progress indicators
- ✅ Mobile responsiveness
- ✅ Accessibility improvements

**Success Criteria:**
- <2 second response time for cached results
- Graceful error messages
- Works on mobile devices

---

## 9. Success Metrics

### 9.1 Technical Metrics

| Metric | Target |
|--------|--------|
| **Extraction Accuracy** | >95% for text PDFs, >85% for images |
| **Enhancement Quality** | User satisfaction >4/5 rating |
| **Compilation Success Rate** | >98% (valid LaTeX) |
| **Response Time** | <5s for full pipeline, <1s for cached |
| **Token Efficiency** | 50% reduction vs full-resume approach |

### 9.2 User Experience Metrics

| Metric | Target |
|--------|--------|
| **Career Path Relevance** | >80% users find ≥1 relevant path |
| **Actionability** | >70% users understand next steps |
| **Editor Usability** | >4/5 satisfaction with hybrid editor |
| **Completion Rate** | >60% upload → download final resume |

### 9.3 Business Metrics (Future)

| Metric | Target |
|--------|--------|
| **User Retention** | >40% return within 30 days |
| **Resume Improvement** | Avg score increase of 15+ points |
| **Conversion** | >10% free → paid (if monetized) |

---

## 10. Risk Analysis

### 10.1 Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Vision LLM hallucination** | HIGH | MEDIUM | Add user confirmation step, show confidence scores |
| **LaTeX compilation failures** | MEDIUM | HIGH | Robust error parsing, fallback templates, preserve .log files |
| **Token costs exceed budget** | MEDIUM | MEDIUM | Multi-level caching, optimize prompts, monitor usage |
| **PDF extraction fails on complex layouts** | MEDIUM | MEDIUM | Fall back to template-based generation, use OCR |
| **Sync issues between LaTeX ↔ Preview** | MEDIUM | MEDIUM | Comprehensive testing, clear editing rules |

### 10.2 Product Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Career paths too generic** | MEDIUM | HIGH | Fine-tune prompts with user feedback, A/B testing |
| **Users confused by dual editor** | LOW | MEDIUM | Clear onboarding tooltips, tutorial video |
| **Enhancement doesn't preserve voice** | MEDIUM | MEDIUM | Make enhancements opt-in per section, show before/after |

### 10.3 Ethical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Resume inflation/lying** | MEDIUM | HIGH | Disclaimer: "Enhance, don't fabricate", ethical guidelines |
| **Bias in career recommendations** | LOW | HIGH | Test across diverse profiles, avoid demographic assumptions |
| **Privacy concerns (resume data)** | LOW | HIGH | No data retention, client-side processing where possible |

---

## 11. Future Enhancements (Beyond MVP)

### 11.1 Short-term (3-6 months)

- **Multi-language support** (Spanish, French, German resumes)
- **Cover letter generation** (using resume data + job description)
- **ATS simulation** (test resume against common ATS systems)
- **Export formats** (DOCX, Markdown, HTML)

### 11.2 Long-term (6-12 months)

- **Interview prep** (generate interview questions based on resume)
- **Salary negotiation guidance** (based on market data + experience)
- **Job application tracker** (track applications and outcomes)
- **Recruiter mode** (batch resume analysis for hiring teams)

---

## 12. Appendix

### 12.1 Canonical Resume JSON Schema

```json
{
  "resume_id": "uuid-v4",
  "schema_version": "1.0",
  "identity": {
    "name": "string",
    "email": "string",
    "phone": "string",
    "linkedin": "string",
    "github": "string",
    "portfolio": "string",
    "location": "string"
  },
  "summary": "string",
  "experience": [
    {
      "title": "string",
      "company": "string",
      "location": "string",
      "duration": "string",
      "type": "string",
      "bullets": ["string"]
    }
  ],
  "projects": [
    {
      "title": "string",
      "type": "string",
      "year": "string",
      "tech_stack": ["string"],
      "bullets": ["string"]
    }
  ],
  "education": [
    {
      "degree": "string",
      "major": "string",
      "institution": "string",
      "location": "string",
      "graduation_year": "string",
      "gpa": "string",
      "relevant_coursework": ["string"]
    }
  ],
  "workshops": [
    {
      "title": "string",
      "year": "string",
      "description": "string"
    }
  ],
  "skills": {
    "languages": ["string"],
    "frameworks": ["string"],
    "tools": ["string"],
    "domains": ["string"]
  }
}
```

### 12.2 LaTeX Template Structure

```latex
\documentclass[10pt, letterpaper]{article}
% Packages
\usepackage[geometry, titlesec, enumitem, hyperref, fonts...]

% Custom commands
\newcommand{\resumeHeader}[6]{...}
\newcommand{\resumeSection}[1]{...}
\newcommand{\resumeItem}[1]{...}

\begin{document}

%%NODE_HEADER%%

%%NODE_SUMMARY%%

%%NODE_EXPERIENCE%%

%%NODE_PROJECTS%%

%%NODE_EDUCATION%%

%%NODE_WORKSHOPS%%

%%NODE_SKILLS%%

\end{document}
```

---

**Document Status:** Draft  
**Next Review:** After Phase 1 completion  
**Approvals Required:** Technical Lead, Product Owner  

---

**End of Project Review Document**