import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ANALYZER_ENHANCER_PROMPT = """
You are a resume quality engine. You will receive a resume and return a single improved version of it.

You have two jobs:

FIRST: Read the entire resume and identify what is genuinely weak.
SECOND: Fix only what is weak. Return the complete resume with those fixes applied.

You decide what is weak. You decide how to fix it. The only constraints are below.

---

WHAT COUNTS AS WEAK:

A bullet is weak if it describes a task without stating outcome or scale.
A bullet is strong if it states what was done, how, and what changed as a result.

A workshop is weak if it has no description of what was built or learned.
A summary is weak if it uses generic language with no domain specifics.
A skills section is weak if it lists tools with no context of how they were used.

If something is already specific and impactful, leave it exactly as it is.

---

WHAT YOU MUST NOT DO:

Do not invent metrics that cannot be reasonably inferred from context.
Do not add technologies not mentioned in the original.
Do not change the core claim of any bullet.
Do not use passive voice.
Do not use: worked on, helped with, assisted, responsible for, involved in.
Do not rewrite bullets that are already strong.
Do not fabricate company size or user counts with no contextual basis.

---

SCALE INFERENCE:

You may add scale when it is reasonable to infer from context.
Use these as reference:

Personal or student project → prototype scale, coursework context
Small company or startup → thousands of users, moderate data volumes
Production API at unnamed company → tens of thousands of requests per day
Data pipeline → records per run or per day depending on project description
Performance improvement → express as before and after when possible

If context gives no signal for scale, improve the framing without adding numbers.

---

OUTPUT:

Return the resume with all weak content replaced by improved content.
Preserve all strong content exactly.
Return only the resume object.
No explanations.
No analysis section.
No list of what you changed.
Valid JSON only.
"""


def run_single_pass(raw_text: str) -> dict:
    """
    Single LLM pass.
    Receives clean extracted resume text.
    Returns enhanced resume as parsed dict.
    """

    try:
        response = client.chat.completions.create(
            model=MODEL_ROUTER["resume_analyzer_and_enhancer"],
            messages=[
                {
                    "role": "system",
                    "content": ANALYZER_ENHANCER_PROMPT
                },
                {
                    "role": "user",
                    "content": raw_text
                }
            ],
            temperature=0.2
        )

        usage = response.usage

        print(f"Prompt Tokens: {usage.prompt_tokens}")
        print(f"Completion Tokens: {usage.completion_tokens}")
        print(f"Total Tokens: {usage.total_tokens}")
        print("\n\n")

        raw_output = response.choices[0].message.content.strip()
        print(raw_output)
        print("\n\n")

        # Strip markdown code fences if model wraps output
        if raw_output.startswith("```"):
            raw_output = raw_output.split("```")[1]
            if raw_output.startswith("json"):
                raw_output = raw_output[4:]
            raw_output = raw_output.strip()

        enhanced_resume = json.loads(raw_output)
        return enhanced_resume

    except json.JSONDecodeError as e:
        raise ValueError(f"LLM returned invalid JSON: {str(e)}")

    except Exception as e:
        raise RuntimeError(f"LLM call failed: {str(e)}")