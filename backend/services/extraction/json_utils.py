import json
import re


def extract_json(text):
    """
    Extract first valid JSON object.
    """

    text = text.strip()

    # Remove markdown fences
    text = text.replace("```json", "")
    text = text.replace("```", "")

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("No JSON object found")

    return text[start:end + 1]


def safe_json_loads(text):
    """
    Safely parse LLM JSON responses.
    """

    try:
        return json.loads(text)

    except json.JSONDecodeError:
        cleaned = extract_json(text)

        try:
            return json.loads(cleaned)

        except json.JSONDecodeError as e:
            print("[RAW LLM OUTPUT]")
            print(cleaned)
            raise ValueError(f"Failed to parse JSON: {e}")