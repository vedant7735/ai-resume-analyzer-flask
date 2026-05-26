# AI Resume Analyzer — Project Deep Dive

## What This Project Does

A Flask web app that lets users upload a PDF resume, runs it through an LLM (via Groq API) to produce a structured analysis (scores, strengths, improvements, ATS keywords, recommended roles), displays the results on a polished dashboard, and offers a **LaTeX resume generator** that takes the analysis improvements and produces an enhanced `.tex` file with an in-browser editor.

---

## Current File Structure (Actual on Disk)

```
ai-resume-analyzer-flask/
├── app.py                          ← Main Flask app (routes)
├── cleaner.py                      ← Original PDF extraction + text cleaning (LEGACY ROOT FILE)
├── pt_to_json.py                   ← Local regex parser / debug tool (ORPHANED)
├── requirements.txt
├── .env                            ← GROQ_API_KEY
├── .gitignore
├── README.md
│
├── services/
│   ├── __init__.py
│   ├── pdf_service.py              ← Thin wrapper → imports from root cleaner.py
│   ├── cleaner_service.py          ← Thin wrapper → imports from root cleaner.py
│   ├── llm_service.py              ← Groq analysis (client #1)
│   ├── latex_service.py            ← LaTeX generation + PDF compilation (client #2)
│   └── cache_service.py            ← SHA256 hash-based JSON caching
│
├── templates/
│   ├── index.html
│   ├── styles.css
│   └── script.js
│
├── uploads/                        ← Temp PDF storage (cleaned after use)
├── cache/                          ← Cached analysis JSON by file hash
├── generated/                      ← .tex and .log output files
└── images/                         ← Reference screenshots
```

---

## 🔴 Active Bugs & Errors

### 1. `FILLER_PROMPT` does not exist — `/debug-latex` route will crash

In [app.py:154](file:///c:/Intern/Project/ai-resume-analyzer-flask/app.py#L154):
```python
from services.latex_service import format_resume_data, FILLER_PROMPT
```
The variable `FILLER_PROMPT` **does not exist** in `latex_service.py`. The old prompt was renamed to `IMPROVEMENT_PROMPT` during the refactor. Hitting the `/debug-latex` endpoint will throw an `ImportError`.

> [!CAUTION]
> **Fix:** Either remove the `/debug-latex` route entirely (it's a debug tool) or change the import to `IMPROVEMENT_PROMPT`.

---

### 2. `escape_latex` double-corrupts backslashes

In [latex_service.py:252-253](file:///c:/Intern/Project/ai-resume-analyzer-flask/services/latex_service.py#L252-L253):
```python
replacements = [
    ('\\', r'\textbackslash{}'),   # ← This runs FIRST
    ('&',  r'\&'),                 # ← These insert new backslashes
    ...
]
```
Because `\\` → `\textbackslash{}` runs first, and then subsequent replacements insert new `\` characters, those new backslashes are **not** re-escaped. However, the **real problem** is the opposite: if any resume content genuinely contains `\`, it gets converted to `\textbackslash{}`, and then the `{` and `}` in that result get escaped again by later rules into `\{` and `\}`, producing `\textbackslash\{\}` — broken LaTeX.

> [!WARNING]
> **Fix:** Process backslash escaping last, or use a single-pass approach. The standard pattern is to escape `\` → `\textbackslash{}` **last**, not first.

---

### 3. No `.pdf` files are being generated — `.log` files left behind

Looking at the `generated/` directory, there are `.log` files present (compilation was attempted) but **zero `.pdf` files**. This means `pdflatex` is installed on your system but compilation is failing. The `.log` files are not being cleaned up on failure because the cleanup only runs on success.

> [!IMPORTANT]
> Check `generated/resume_3aa22e13-cd2e-4a79-b6cd-2846523c2889.log` for the actual compilation errors. Most likely causes: escaped characters producing invalid LaTeX, or missing packages.

---

### 4. Model mismatch across services

| Service | Model |
|---------|-------|
| [llm_service.py:151](file:///c:/Intern/Project/ai-resume-analyzer-flask/services/llm_service.py#L151) | `openai/gpt-oss-20b` |
| [latex_service.py:144](file:///c:/Intern/Project/ai-resume-analyzer-flask/services/latex_service.py#L144) | `openai/gpt-oss-120b` (just changed) |
| [app.py:164](file:///c:/Intern/Project/ai-resume-analyzer-flask/app.py#L164) (debug route) | `openai/gpt-oss-20b` |

The debug route uses a stale model name and a non-existent prompt constant. If you intended to test the 120b model, the debug route won't reflect that.

---

## 🟡 Architectural Concerns

### 5. Two independent Groq clients at module load time

Both [llm_service.py:10](file:///c:/Intern/Project/ai-resume-analyzer-flask/services/llm_service.py#L10) and [latex_service.py:9](file:///c:/Intern/Project/ai-resume-analyzer-flask/services/latex_service.py#L9) create their own `Groq(api_key=...)` client at import time with their own `load_dotenv()` call. This means:
- Two separate `load_dotenv()` calls racing at import
- Two independent clients that can't share rate limiting or config
- If the API key is wrong, **both** fail silently until the first request

**Recommendation:** Create a single shared client in `services/__init__.py` or a dedicated `services/config.py`.

---

### 6. `cleaner.py` still lives at root — services are just pass-through wrappers

[pdf_service.py](file:///c:/Intern/Project/ai-resume-analyzer-flask/services/pdf_service.py) and [cleaner_service.py](file:///c:/Intern/Project/ai-resume-analyzer-flask/services/cleaner_service.py) are 10-line files that simply `from cleaner import ...` and re-export. The actual logic is still in the root-level [cleaner.py](file:///c:/Intern/Project/ai-resume-analyzer-flask/cleaner.py). This is a half-completed refactor:

```
services/pdf_service.py  →  from cleaner import extract_resume_text  →  cleaner.py (root)
services/cleaner_service.py  →  from cleaner import clean_resume_text  →  cleaner.py (root)
```

**Recommendation:** Move the actual code from `cleaner.py` into the service files and delete the root file.

---

### 7. `pt_to_json.py` is orphaned dead code

[pt_to_json.py](file:///c:/Intern/Project/ai-resume-analyzer-flask/pt_to_json.py) (216 lines) is a local regex-based resume parser that was your **original approach** before switching to LLM-based parsing. It:
- Has its own `extract_resume_text()` function (duplicate of `cleaner.py`)
- Imports `PyPDF2` but it's not in `requirements.txt` as a separate dep
- Is already in `.gitignore`
- Is **never imported by anything**

**Recommendation:** Delete it, or move to a `scripts/` folder if you want to keep it for reference.

---

### 8. Hardcoded `http://localhost:5000` in all fetch calls

[script.js](file:///c:/Intern/Project/ai-resume-analyzer-flask/templates/script.js) has **6 hardcoded** `http://localhost:5000` URLs. This will break immediately if you:
- Deploy to any server
- Change the port
- Use HTTPS

**Recommendation:** Use relative URLs (`/upload`, `/generate-latex`, etc.) since the frontend is served by the same Flask app.

---

### 9. `app.py` never calls `load_dotenv()`

The main [app.py](file:///c:/Intern/Project/ai-resume-analyzer-flask/app.py) does not import or call `load_dotenv()`. It works by accident because the service modules call it at import time. But the debug route at line 158 does `Groq(api_key=os.getenv("GROQ_API_KEY"))` — if `load_dotenv()` hasn't been called yet by the service imports, `os.getenv` would return `None`.

---

### 10. `generate_improved_latex` ignores its second argument

In [app.py:121](file:///c:/Intern/Project/ai-resume-analyzer-flask/app.py#L121):
```python
latex_code = generate_improved_latex(resume_data, "")
```
The `original_extracted_text` parameter is passed as `""` and is **never used** inside the function body at [latex_service.py:130](file:///c:/Intern/Project/ai-resume-analyzer-flask/services/latex_service.py#L130). It's a vestige from the planned "extract original LaTeX structure from PDF text" strategy described in the docstring, which was never implemented.

---

## 🟠 Robustness & Quality Issues

### 11. LLM parsing is fragile

The `parse_improvements()` function in [latex_service.py:166-244](file:///c:/Intern/Project/ai-resume-analyzer-flask/services/latex_service.py#L166-L244) relies on the LLM returning output in an **exact text format** with `[SUMMARY]`, `[EXPERIENCE_ITEM]`, etc. markers. Unlike the analysis endpoint (which uses `response_format={"type": "json_object"}`), the LaTeX improvement endpoint uses **freeform text** — the LLM can easily:
- Add markdown formatting (`**bold**`, ```code blocks```)
- Rearrange sections
- Use different bullet characters
- Skip section markers entirely

**Recommendation:** Consider using JSON mode for the improvement endpoint too, or add robust fallback handling.

---

### 12. No file cleanup for `generated/` directory

The `generated/` folder accumulates `.tex`, `.log`, and eventually `.pdf` files forever. There's no:
- Scheduled cleanup
- TTL-based expiration
- Max file count limit

With each "DOWNLOAD .TEX" click generating a new UUID-named file, this will grow unbounded.

---

### 13. No input validation on `file_id` route parameters

[app.py:137-148](file:///c:/Intern/Project/ai-resume-analyzer-flask/app.py#L137-L148) — The `download-latex` and `download-pdf` routes accept arbitrary `file_id` strings and construct filenames with `f"resume_{file_id}.tex"`. While `send_from_directory` has some built-in path traversal protection, there's no UUID format validation.

---

## 📋 File-by-File Status

| File | Status | Notes |
|------|--------|-------|
| [app.py](file:///c:/Intern/Project/ai-resume-analyzer-flask/app.py) | ⚠️ Has bugs | `FILLER_PROMPT` import error, missing `load_dotenv`, debug route stale |
| [cleaner.py](file:///c:/Intern/Project/ai-resume-analyzer-flask/cleaner.py) | 🟡 Legacy | Should be absorbed into services |
| [pt_to_json.py](file:///c:/Intern/Project/ai-resume-analyzer-flask/pt_to_json.py) | ❌ Dead code | Orphaned, never imported |
| [services/pdf_service.py](file:///c:/Intern/Project/ai-resume-analyzer-flask/services/pdf_service.py) | 🟡 Thin wrapper | Just re-exports from root `cleaner.py` |
| [services/cleaner_service.py](file:///c:/Intern/Project/ai-resume-analyzer-flask/services/cleaner_service.py) | 🟡 Thin wrapper | Just re-exports from root `cleaner.py` |
| [services/llm_service.py](file:///c:/Intern/Project/ai-resume-analyzer-flask/services/llm_service.py) | ✅ Solid | Clean prompt, JSON mode, good error handling |
| [services/latex_service.py](file:///c:/Intern/Project/ai-resume-analyzer-flask/services/latex_service.py) | ⚠️ Fragile | `escape_latex` bug, freeform LLM parsing, unused param |
| [services/cache_service.py](file:///c:/Intern/Project/ai-resume-analyzer-flask/services/cache_service.py) | ✅ Solid | Simple, correct implementation |
| [templates/index.html](file:///c:/Intern/Project/ai-resume-analyzer-flask/templates/index.html) | ✅ Good | Clean semantic HTML |
| [templates/script.js](file:///c:/Intern/Project/ai-resume-analyzer-flask/templates/script.js) | ⚠️ Hardcoded URLs | 6× `localhost:5000` |
| [templates/styles.css](file:///c:/Intern/Project/ai-resume-analyzer-flask/templates/styles.css) | ✅ Premium | Well-organized design system |
| [requirements.txt](file:///c:/Intern/Project/ai-resume-analyzer-flask/requirements.txt) | 🟡 Pinned tight | May cause install issues with strict versions |

---

## 🎯 Prioritized Recommendations

### Immediate Fixes (do now)

1. **Fix or remove `/debug-latex` route** — it will crash on `FILLER_PROMPT` import
2. **Replace hardcoded URLs** in `script.js` — use relative paths (`/upload` instead of `http://localhost:5000/upload`)
3. **Fix `escape_latex` ordering** — move backslash escaping to the end, or exclude `{}` from escaping after backslash conversion
4. **Check `.log` files** in `generated/` to diagnose why PDF compilation fails

### Short-term Cleanup (this week)

5. **Complete the refactor** — move `cleaner.py` logic into `services/pdf_service.py` and `services/cleaner_service.py`, delete root file
6. **Centralize Groq client** — single `load_dotenv()` + single `Groq()` instance shared across services
7. **Delete `pt_to_json.py`** — it's dead code
8. **Remove unused `original_extracted_text` parameter** from `generate_improved_latex`
9. **Add `load_dotenv()` to `app.py`** top-level for safety

### Medium-term Improvements (next sprint)

10. **Add generated file cleanup** — cron job or on-request cleanup for files older than 1 hour
11. **Switch LaTeX improvement to JSON mode** — same approach as `llm_service.py` for reliability
12. **Add `file_id` UUID validation** on download routes
13. **Loosen `requirements.txt` versions** — use `>=` instead of `==` for minor versions, or remove versions entirely for dev
14. **Add proper error pages** — currently errors are `alert()` popups; consider toast notifications

### Nice-to-haves (polish)

15. **Add a loading state to the LaTeX editor** — show a skeleton/shimmer while the LLM generates
16. **Add syntax highlighting** to the LaTeX editor (CodeMirror or Monaco)
17. **Add `.env.example`** with `GROQ_API_KEY=your_key_here` for onboarding
18. **Move `images/` to `.gitignore`** or a docs folder — reference screenshots shouldn't ship in prod
