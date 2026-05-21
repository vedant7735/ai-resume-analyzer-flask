from groq import Groq
from dotenv import load_dotenv
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "services"))

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL_NAME_ANALYZER = "openai/gpt-oss-120b"
MODEL_NAME_ENHANCER = "openai/gpt-oss-120b"