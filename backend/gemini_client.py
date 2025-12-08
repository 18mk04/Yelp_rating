import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config={
        "response_mime_type": "application/json"
    }
)

def generate_text(prompt: str):
    resp = model.generate_content(prompt)
    return resp.text  # already JSON
