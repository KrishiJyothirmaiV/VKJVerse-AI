
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY", "").strip()

if not api_key:
    raise ValueError("GEMINI_API_KEY is missing from .env")

client = genai.Client(api_key=api_key)

print("\nAvailable Gemini models:\n")

for model in client.models.list():
    name = model.name or ""
    actions = model.supported_actions or []

    if "generateContent" in actions:
        print(name)