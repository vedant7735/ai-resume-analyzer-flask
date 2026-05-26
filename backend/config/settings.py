import os
import secrets
from pathlib import Path
from dotenv import load_dotenv

# Base Directory: root of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load .env file
load_dotenv(BASE_DIR / '.env')

# Secrets
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Generate secure token fallback dynamically if SECRET_KEY is not defined in env
SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_hex(32)

# Environment setup
FLASK_ENV = os.getenv("FLASK_ENV", "development")
DEBUG = FLASK_ENV == "development"

# CORS configurations
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
