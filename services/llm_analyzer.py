import os, json
from groq import Groq
from dotenv import load_dotenv
from services.validator import validate_resume_object
from services.json_utils import safe_json_loads
from services.LLM_Models import MODEL_NAME_ANALYZER

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

ANALYZER_PROMPT = """
You are a deterministic resume parser and diagnostics engine.

Your task:
Transform the provided resume JSON into a canonical schema_version "1.0" resume object with analysis metadata.

STRICT RULES:
- Return ONLY valid raw JSON.
- No markdown.
- No comments.
- No hallucinations.
- Do NOT invent companies, metrics, skills, projects, or experience.
- Preserve quantified achievements exactly.
- Keep bullets concise and factual.
- Missing values must use empty strings or empty arrays.
- Schema compliance is mandatory.

You MUST use ONLY the exact schema keys specified below.

DO NOT rename fields.

Forbidden examples:
- "name" instead of "title"
- "dates" instead of "duration"
- "achievements" instead of "bullets"
- "description" instead of "type"

Required schema:

{
  "resume_id": "",
  "schema_version": "1.0",

  "identity": {
    "name": "",
    "email": "",
    "phone": "",
    "linkedin": "",
    "github": "",
    "portfolio": "",
    "location": ""
  },

  "experience": [
    {
      "title": "",
      "company": "",
      "location": "",
      "duration": "",
      "type": "",
      "bullets": []
    }
  ],

  "projects": [
    {
      "title": "",
      "type": "",
      "year": "",
      "tech_stack": [],
      "bullets": []
    }
  ],

  "education": [
    {
      "degree": "",
      "major": "",
      "institution": "",
      "location": "",
      "graduation_year": "",
      "gpa": "",
      "relevant_coursework": []
    }
  ],

  "skills": {
    "languages": [],
    "frameworks": [],
    "tools": [],
    "domains": []
  },

  "analysis": {
    "professional_summary": "",
    "strengths": [],
    "improvements": [],
    "score": {},
    "ats_keywords": [],
    "recommended_for": []
  }
}

Analysis rules:

professional_summary:
- 2 concise factual sentences
- no motivational language
- no personality assumptions
- based only on resume evidence

strengths[]:
- technical observations only
- must reference observable evidence
- avoid vague praise

Good:
- "Includes quantified backend API metrics"
- "Demonstrates containerization experience"

Bad:
- "Hardworking engineer"
- "Strong communication skills"

improvements[] format:
{
  "section": "",
  "issue": "",
  "suggestion": "",
  "priority": "low|medium|high"
}

Improvement rules:
- must reference actual resume weaknesses
- must be actionable
- do NOT suggest metrics if metrics already exist
- avoid generic recruiter advice

Scores:
- integers only
- range: 0 to 100
- no decimals

score format:
{
  "overall": 0,
  "breakdown": {
    "content_quality": 0,
    "structure": 0,
    "impact": 0,
    "completeness": 0,
    "formatting": 0
  },
  "explanation": ""
}

ats_keywords[]:
- only explicitly present technical keywords

recommended_for[]:
- realistic technical roles only
- based strictly on demonstrated evidence
"""

def analyze_resume_object(resume_v1):
    # Optionally remove large raw text to save tokens
    payload = dict(resume_v1)
    payload.pop("_raw_text", None)

    resp = client.chat.completions.create(
        model= MODEL_NAME_ANALYZER,
        messages=[
            {"role": "system", "content": ANALYZER_PROMPT},
            {"role": "user", "content": json.dumps(payload)}
        ],
        temperature=0.2
    )
    print(resp.choices[0].message.content)
    resume_v2 = safe_json_loads(resp.choices[0].message.content)
    resume_v2, error = validate_resume_object(resume_v2)
    if error:
        print(f"[Validator] {error}")

    return resume_v2