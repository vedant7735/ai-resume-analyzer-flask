# AI Resume Analyzer & Career Intelligence Platform

An AI-powered resume intelligence platform that performs:

- layout-aware resume extraction
- structured semantic parsing
- AI-driven resume enhancement
- ATS optimization
- LaTeX resume generation
- career analysis and role recommendations

Built using Flask, React, Groq-hosted LLMs, PyMuPDF, OCR pipelines, and a modular semantic processing architecture.

---

# Overview

This project is designed as a **document intelligence pipeline**, not just a resume parser.

The platform converts unstructured resumes into structured semantic representations, analyzes weaknesses, selectively enhances content, and generates professionally rendered ATS-friendly resumes.

The system emphasizes:

- structure preservation
- selective enhancement
- deterministic processing
- modular architecture
- reusable semantic layers

---

# Core Capabilities

## Resume Extraction

Supports:

- PDF resumes
- scanned resumes
- image-based resumes

Extraction pipeline includes:

- layout-aware parsing using PyMuPDF
- OCR fallback using Tesseract
- typography-based section detection
- semantic block reconstruction
- structured identity extraction

---

## Structured Resume Schema

The platform converts resumes into canonical JSON objects.

Features:

- schema normalization
- schema validation
- automatic repair utilities
- versioned resume objects
- safe structured LLM outputs

---

## AI Resume Analysis

The analysis engine generates:

- professional summaries
- section-level scoring
- ATS keyword extraction
- strengths and weaknesses
- improvement priorities
- realistic role recommendations

---

## Selective Resume Enhancement

Unlike traditional resume tools, this platform avoids rewriting the entire resume.

The enhancement engine:

- preserves strong content
- rewrites only weak sections
- improves action verbs
- enhances quantified impact
- optimizes ATS phrasing
- maintains factual integrity

---

## Career Intelligence System

The platform includes career guidance capabilities such as:

- role alignment analysis
- realistic career path recommendations
- skill gap detection
- growth trajectory planning
- future extensibility for market intelligence

---

## Rendering Engine

The rendering layer converts structured resume JSON into production-ready LaTeX resumes.

Features:

- ATS-friendly formatting
- automatic LaTeX escaping
- editable `.tex` export
- automatic PDF compilation
- downloadable `.pdf` and `.tex` outputs

---

## Frontend Dashboard

Interactive React dashboard featuring:

- drag-and-drop uploads
- analytics dashboard
- section score visualization
- improvement insights
- resume preview
- downloadable assets

---

# System Pipeline

```text
Resume Upload
(PDF / PNG / JPG)
        ↓
Layout-Aware Extraction
        ↓
Structured Resume JSON (v1)
        ↓
Validation & Repair
        ↓
LLM Analysis + Enhancement
        ↓
Enhanced Resume JSON (v2)
        ↓
Career Intelligence Layer
        ↓
LaTeX Rendering Engine
        ↓
PDF Compilation
        ↓
Downloadable Resume Package
```

---

# Architecture

```text
Frontend (React + Vite)
        ↓
Flask API Layer
        ↓
Extraction Pipeline
        ↓
Semantic Processing Layer
        ↓
LLM Processing Layer
        ↓
Enhancement Engine
        ↓
Rendering Engine
        ↓
Caching Layer
```

---

# Tech Stack

## Backend

- Python 3.11+
- Flask
- Flask-CORS

---

## Frontend

- React
- Vite
- Vanilla CSS

---

## AI & LLM Integration

- Groq API
- `openai/gpt-oss-120b`
- structured JSON prompting
- schema-constrained outputs

---

## PDF & OCR Processing

- PyMuPDF (`fitz`)
- pytesseract
- pdf2image

---

## Rendering

- LaTeX
- pdflatex
- MiKTeX / TeX Live

---

## Validation & Utilities

- jsonschema
- python-dotenv
- werkzeug

---

# Project Structure

```text
project_root/
│
├── app.py
├── requirements.txt
├── README.md
│
├── client/
│   ├── src/
│   ├── public/
│   └── vite.config.js
│
├── services/
│   ├── model_service/
│   │   ├── multimodal_extractor.py
│   │   ├── llm_call.py
│   │   └── prompts/
│   │
│   ├── renderer.py
│   ├── validator.py
│   ├── cache_service.py
│   └── json_utils.py
│
├── uploads/
├── cache/
├── generated/
│
└── images/
```
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

# Installation

## Clone Repository

```bash
git clone https://github.com/vedant7735/ai-resume-analyzer-flask.git

cd ai-resume-analyzer-flask
```

---

## Create Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / macOS

```bash
python -m venv venv

source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_api_key_here
```

---

# Running the Backend

```bash
python app.py
```

Backend runs on:

```text
http://localhost:5000
```

---

# Running the Frontend

```bash
cd client

npm install

npm run dev
```

Frontend runs on:

```text
http://localhost:5173
```

---

# API Endpoints

## `POST /upload`

Uploads and analyzes resume files.

### Supported Formats

- `.pdf`
- `.png`
- `.jpg`
- `.jpeg`

### Returns

- structured analyzed resume JSON
- enhancement data
- scoring information

---

## `POST /enhance`

Generates:

- LaTeX resume
- downloadable PDF
- editable `.tex` file

---

## `GET /download-tex/<file_id>`

Downloads generated LaTeX file.

---

## `GET /download-pdf/<file_id>`

Downloads generated PDF resume.

---

# Caching System

The platform includes multi-layer caching:

- analysis cache
- enhancement cache
- render cache

Benefits:

- lower LLM costs
- reduced latency
- faster repeated processing

---

# Current Features

## Implemented

- PDF extraction
- OCR fallback
- layout-aware parsing
- structured resume schema
- AI analysis
- selective enhancement
- ATS scoring
- LaTeX generation
- PDF compilation
- React dashboard
- render caching
- downloadable assets

---

# Planned Improvements

- Resume ↔ Job Description matching
- Docker deployment
- Redis caching
- async job queues
- PostgreSQL persistence
- multiple LaTeX templates
- market intelligence integration
- competitive analysis
- career graph visualization
- CI/CD pipeline
- observability & monitoring
- Kubernetes deployment

---

# Security Notes

- uploaded files are processed temporarily
- API keys are stored using environment variables
- generated resumes may be cached locally
- LaTeX content is sanitized before rendering

---

# Current Limitations

- DOCX support is limited
- OCR accuracy depends on scan quality
- requires local `pdflatex`
- synchronous processing pipeline
- large resumes may increase latency

---

# Development Direction

This project is evolving toward a modular AI document intelligence platform with:

- multimodal extraction
- structured semantic processing
- AI-assisted enhancement
- career intelligence systems
- scalable rendering architecture

---

# Author

GitHub:

https://github.com/vedant7735

---

# License

This project is intended for:

- educational purposes
- experimentation
- internship projects
- portfolio development

---

# Acknowledgements

- Flask
- React
- Groq
- PyMuPDF
- Tesseract OCR
- LaTeX Project