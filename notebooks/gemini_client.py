# notebooks/gemini_client.py
from google import genai
import os
from dotenv import load_dotenv
import json
from pathlib import Path

# Load .env from project root
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError(f"GEMINI_API_KEY not found. Check {env_path}")

client = genai.Client(api_key=API_KEY)
MODEL = "gemini-2.5-flash"


def generate_text(prompt: str) -> dict:
    """Generate JSON response from Gemini and parse it."""
    response = client.models.generate_content(
        model=MODEL,
        contents=[prompt],
        config={"response_mime_type": "application/json"}
    )
    try:
        return json.loads(response.text)
    except:
        return {}


def generate_text_raw(prompt: str) -> str:
    """Generate plain text response from Gemini."""
    response = client.models.generate_content(
        model=MODEL,
        contents=[prompt]
    )
    return response.text or ""
