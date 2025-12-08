from google import genai
import os
from dotenv import load_dotenv

print("Loading .env...")
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
print("API KEY LOADED:", repr(API_KEY))  # show the raw value

client = genai.Client(api_key=API_KEY)

def generate_text(prompt: str):
    response = client.models.generate_content(
        model="gemini-3-pro-preview",
        contents=prompt
    )
    return response.text
