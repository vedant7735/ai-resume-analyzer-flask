# AI Resume Analyzer & LaTeX Resume Enhancement Platform

An AI-powered resume analysis and enhancement platform built using Flask, Groq-hosted LLMs, and a structured semantic processing pipeline.

The platform extracts resume content from PDFs, converts resumes into structured JSON, performs contextual analysis and enhancement, and generates ATS-friendly LaTeX and PDF outputs.

---

# PROJECT OVERVIEW

This project is designed as a modular resume intelligence pipeline rather than a simple text analyzer.

The system performs:

- Layout-aware PDF parsing
- Structured semantic extraction
- Resume validation
- AI-powered contextual analysis
- Targeted resume enhancement
- LaTeX resume rendering
- PDF compilation
- Editable `.tex` generation

The architecture separates:
- semantic processing
- validation
- enhancement
- rendering

into independent services for scalability and maintainability.

---

# CORE FEATURES

## Resume Extraction
- Layout-aware PDF extraction using PyMuPDF
- OCR fallback support for scanned resumes
- Section detection using font/layout heuristics
- Structured identity extraction
- Experience/project parsing

## Structured Resume Schema
- Canonical JSON resume format
- JSON schema validation
- Automatic schema repair
- Safe LLM JSON parsing utilities

## AI Resume Analysis
- Professional summary generation
- Resume scoring system
- ATS keyword extraction
- Strength identification
- Improvement recommendations
- Role recommendations

## AI Resume Enhancement
- Targeted semantic enhancement
- Selective bullet rewriting
- Quantified achievement optimization
- Resume content patching system

## Rendering Engine
- JSON → LaTeX conversion
- ATS-friendly resume templates
- PDF compilation using `pdflatex`
- Editable LaTeX export
- Downloadable `.tex` and `.pdf` outputs

## Frontend Dashboard
- Drag-and-drop upload UI
- Interactive analytics dashboard
- Improvement accordion system
- Detailed data tabs
- Resume score visualization
- Editable LaTeX modal editor

## Performance Optimization
- Multi-layer caching system
- Cached analysis pipeline
- Cached enhancement pipeline
- Cached render generation

---

# SYSTEM PIPELINE

```text
PDF Resume
    ↓
Layout-Aware Extraction
    ↓
Structured Resume JSON (v1)
    ↓
LLM Analysis + Validation
    ↓
Enhanced Resume Object (v2)
    ↓
Semantic Enhancement Engine
    ↓
Enhanced Resume Object (v3)
    ↓
LaTeX Rendering Engine
    ↓
PDF Compilation
    ↓
Downloadable .tex and .pdf
```

---

# TECH STACK

## Backend
- Python 3.x
- Flask
- Flask-CORS

## AI & LLM Processing
- Groq API
- `openai/gpt-oss-120b`
- Structured JSON prompting

## PDF & OCR Processing
- PyMuPDF (`fitz`)
- pytesseract
- pdf2image

## Rendering
- LaTeX
- pdflatex

## Frontend
- HTML5
- CSS3
- Vanilla JavaScript

## Validation & Utilities
- jsonschema
- dotenv

---

# PROJECT STRUCTURE

```text
project_root/
│
├── app.py
├── requirements.txt
├── README.md
│
├── services/
│   ├── pdf_extractor.py
│   ├── llm_analyzer.py
│   ├── llm_enhancer.py
│   ├── renderer.py
│   ├── validator.py
│   ├── cache_service.py
│   ├── json_utils.py
│   └── LLM_Models.py
│
├── templates/
│   ├── index.html
│   ├── styles.css
│   └── script.js
│
├── images/
│   ├── landing.png
│   ├── score.png
│   ├── summary.png
│   └── recommendation.png
│
└── generated/
```

---

# INSTALLATION

## Clone Repository

```bash
git clone https://github.com/vedant7735/ai-resume-analyzer-flask.git
cd ai-resume-analyzer-flask
```

---

## Create Virtual Environment

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_api_key_here
```

---

# HOW TO RUN

```bash
python app.py
```

Open in browser:

```text
http://localhost:5000
```

---

# CURRENT MODEL CONFIGURATION

Current LLM configuration:

```python
MODEL_NAME_ANALYZER = "openai/gpt-oss-120b"
MODEL_NAME_ENHANCER = "openai/gpt-oss-120b"
```

Models can be modified inside:

```text
services/LLM_Models.py
```

---

# FEATURES BREAKDOWN

## 1. Layout-Aware Resume Extraction

The extraction layer:
- reads PDF layout blocks
- detects sections using typography heuristics
- extracts semantic structure
- builds canonical resume JSON

Supports:
- text-based PDFs
- scanned resumes via OCR fallback

---

## 2. Resume Validation Layer

The validator:
- enforces schema consistency
- repairs missing fields
- validates LLM outputs
- prevents malformed resume objects

---

## 3. LLM Analysis Engine

The analyzer:
- generates structured JSON
- produces factual summaries
- computes score breakdowns
- extracts ATS keywords
- identifies weaknesses
- recommends technical roles

---

## 4. Enhancement Engine

The enhancement layer:
- applies targeted semantic patches
- rewrites weak bullets
- improves action verbs
- optimizes quantified achievements
- avoids rewriting unchanged sections

---

## 5. Rendering Engine

The rendering system:
- converts structured JSON into LaTeX
- escapes unsafe LaTeX characters
- compiles PDFs automatically
- supports editable `.tex` export

---

## 6. Multi-Level Cache System

Caching layers:
- analyzed resume cache
- enhanced resume cache
- rendered file cache

This significantly reduces repeated LLM and rendering costs.

---

# SCREENSHOTS

## Landing Page

![Landing Page](images/v2/landing.png)

---

## Analysis Dashboard

![Dashboard](images/v2/score.png)

---

## LaTeX Editor

![Latex Editor](images/v2/texeditor.png)

---

## Professional Summary

![Summary](images/v2/summary.png)

---

## Recommendations

![Recommendations](images/v2/recommendation.png)

---

# API ENDPOINTS

## `POST /upload`

Accepts:
- PDF resume upload

Returns:
- analyzed resume JSON

---

## `POST /enhance`

Accepts:
- analyzed resume object

Returns:
- enhanced LaTeX + downloadable files

---

## `GET /download-tex/<file_id>`

Downloads generated `.tex` file.

---

## `GET /download-pdf/<file_id>`

Downloads compiled PDF resume.

---

# CURRENT LIMITATIONS

- Limited DOCX support
- OCR quality depends on scan clarity
- Requires installed `pdflatex`
- Requires internet access for LLM inference
- PDF formatting may vary across resume styles

---

# FUTURE IMPROVEMENTS

- Resume ↔ Job Description matching
- Role alignment analytics
- Multiple LaTeX templates
- Resume version tracking
- Batch resume processing
- Skill gap analysis
- Seniority estimation
- Deployment support

---

# SECURITY NOTES

- Uploaded files are processed temporarily
- API keys stored in `.env`
- Resume data is not permanently stored
- Generated files can be cached locally

---

# LICENSE

This project is intended for:
- educational purposes
- experimentation
- internship development
- portfolio projects

---

# AUTHOR

Vedant Vyas

GitHub:
https://github.com/vedant7735

---

# ACKNOWLEDGEMENTS

- Groq
- PyMuPDF
- pytesseract
- Flask
- jsonschema
- LaTeX