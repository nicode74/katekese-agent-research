import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GOOGLE_API_KEY")

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
response = requests.get(url)
models = response.json().get("models", [])
for m in models:
    if "gemini-1.5" in m.get("name", "").lower():
        print(m.get("name"), m.get("supportedGenerationMethods"))
