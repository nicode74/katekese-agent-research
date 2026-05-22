import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GOOGLE_API_KEY")

def test_model(model_name):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:embedContent?key={api_key}"
    payload = {
        "model": f"models/{model_name}",
        "content": {"parts": [{"text": "Hello"}]}
    }
    res = requests.post(url, json=payload)
    print(f"{model_name}: {res.status_code}")
    if res.status_code != 200:
        print(res.text)

test_model("gemini-embedding-001")
test_model("embedding-001")
test_model("text-embedding-004")
