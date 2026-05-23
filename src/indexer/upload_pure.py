import os
import json
import urllib.request
import urllib.error
import time
from pathlib import Path

# Load env manually
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ[k] = v.strip()

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

if not all([GOOGLE_API_KEY, SUPABASE_URL, SUPABASE_KEY]):
    print("Missing credentials! Make sure .env exists in the root folder.")
    exit(1)

def embed_texts(texts):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2:batchEmbedContents?key={GOOGLE_API_KEY}"
    requests_payload = [
        {"model": "models/gemini-embedding-2", "content": {"parts": [{"text": t}]}}
        for t in texts
    ]
    
    req = urllib.request.Request(url, data=json.dumps({"requests": requests_payload}).encode("utf-8"), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            return [item["values"] for item in res_data.get("embeddings", [])]
    except urllib.error.HTTPError as e:
        print(f"Embedding error: {e.read().decode('utf-8')}")
        return []

def upload():
    data_dir = Path(__file__).parent.parent.parent / "data/final"
    files = list(data_dir.glob("*.jsonl"))
    
    docs = []
    for f in files:
        with open(f, 'r', encoding='utf-8') as f_in:
            for line in f_in:
                try:
                    data = json.loads(line)
                    # Text split manually (simplified 800 chars)
                    content = data["content"]
                    for i in range(0, len(content), 800):
                        chunk = content[i:i+800]
                        if len(chunk) > 100: # skip tiny chunks
                            docs.append({
                                "content": chunk,
                                "metadata": {"source": data.get("source", f.name), **data.get("metadata", {})}
                            })
                except Exception:
                    pass
    
    print(f"Total chunks generated: {len(docs)}")
    batch_size = 50
    
    for i in range(0, len(docs), batch_size):
        batch = docs[i:i+batch_size]
        texts = [d["content"] for d in batch]
        
        embeddings = embed_texts(texts)
        if not embeddings:
            print("Rate limit hit, sleeping for 30s...")
            time.sleep(30)
            continue
            
        payload = []
        for d, e in zip(batch, embeddings):
            payload.append({
                "content": d["content"],
                "metadata": d["metadata"],
                "embedding": e
            })
            
        url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/documents"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        try:
            with urllib.request.urlopen(req) as response:
                print(f"Uploaded batch {i//batch_size + 1}/{len(docs)//batch_size + 1}")
        except urllib.error.HTTPError as e:
            print(f"Failed to upload: {e.read().decode('utf-8')}")
        
        time.sleep(1)

if __name__ == "__main__":
    upload()
