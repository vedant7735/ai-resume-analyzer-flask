import os, json
from groq import Groq
from dotenv import load_dotenv
from services.validator import validate_resume_object
from services.json_utils import safe_json_loads
from services.LLM_Models import MODEL_NAME_ENHANCER

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

ENHANCER_PROMPT = """
You are a resume content enhancer. You will receive a resume object with an "analysis" section containing improvement suggestions.

Your task is to return a JSON object with ONLY the fields that need updating, NOT the entire resume.

Return format:
{
  "summary": "improved summary text if needed",
  "experience": [
    {
      "index": 0,  // which experience item
      "bullets": ["improved bullet 1", "improved bullet 2"]  // only improved bullets
    }
  ],
  "projects": [
    {
      "index": 0,
      "bullets": ["improved bullet 1"]
    }
  ]
}

Rules:
- Only include sections that actually need changes
- Add quantified metrics where missing
- Use strong action verbs
- Keep bullets under 20 words
- Do NOT return unchanged content
- Do NOT invent new jobs/projects
"""

def enhance_resume_object(resume_v2):
    """Apply targeted improvements using semantic patches"""
    
    resp = client.chat.completions.create(
        model=MODEL_NAME_ENHANCER,
        messages=[
            {"role": "system", "content": ENHANCER_PROMPT},
            {"role": "user", "content": json.dumps({
                "identity": resume_v2.get("identity"),
                "experience": resume_v2.get("experience"),
                "projects": resume_v2.get("projects"),
                "analysis": resume_v2.get("analysis")
            })}
        ],
        temperature=0.2
    )
    print(resp.choices[0].message.content)
    patches = safe_json_loads(resp.choices[0].message.content)

    resume_v3 = json.loads(json.dumps(resume_v2))

    if "summary" in patches:
        resume_v3.setdefault("analysis", {})
        resume_v3["analysis"]["professional_summary"] = patches["summary"]

    if "experience" in patches:
        for patch in patches["experience"]:
            idx = patch.get("index")

            if (
                isinstance(idx, int)
                and 0 <= idx < len(resume_v3.get("experience", []))
            ):
                if "bullets" in patch:
                    resume_v3["experience"][idx]["bullets"] = patch["bullets"]

    if "projects" in patches:
        for patch in patches["projects"]:
            idx = patch.get("index")

            if (
                isinstance(idx, int)
                and 0 <= idx < len(resume_v3.get("projects", []))
            ):
                if "bullets" in patch:
                    resume_v3["projects"][idx]["bullets"] = patch["bullets"]

    resume_v3, error = validate_resume_object(resume_v3)

    if error:
        print(f"[Validator] {error}")

    return resume_v3