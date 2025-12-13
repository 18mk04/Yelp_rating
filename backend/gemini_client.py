from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("Missing GEMINI_API_KEY in .env")

# Create Gemini client
client = genai.Client(api_key=API_KEY)

def generate_text(prompt: str) -> str:
    """
    Sends a prompt to Gemini and returns plain text output.
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[prompt],   # MUST be a list
    )

    return response.text or ""
