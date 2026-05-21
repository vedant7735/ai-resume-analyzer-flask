from openai import OpenAI
from dotenv import load_dotenv
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "services"))

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL_ROUTER = {
    # "image_extraction": "gpt-4o-mini",
    # "resume_analysis": "gpt-4.1-mini",
    # "resume_enhancement": "gpt-4.1-mini",
    "resume_analyzer_and_enhancer": "gpt-4.1-mini"
}