import os
import json
import urllib.request
import urllib.error
import time
from pathlib import Path
from dotenv import load_dotenv

# Ensure we use the right Python environment and API keys
load_dotenv()

from langchain_google_genai import GoogleGenerativeAIEmbeddings

def upload():
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
    
    if not all([SUPABASE_URL, SUPABASE_KEY]):
        print("Missing Supabase credentials!")
        return

    print("Initializing Google Gemini Embeddings...")
    embeddings_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    print("Loading chunks for batched upload...")
    data_dir = Path(__file__).parent.parent.parent / "data/final"
    files = list(data_dir.glob("*.jsonl"))
    
    docs = []
    print("Parsing files...")
    for f in files:
        with open(f, 'r', encoding='utf-8') as f_in:
            for line in f_in:
                try:
                    data = json.loads(line)
                    content = data["content"]
                    # chunk text
                    for i in range(0, len(content), 800):
                        chunk = content[i:i+800]
                        if len(chunk) > 100:
                            docs.append({
                                "content": chunk,
                                "metadata": {"source": data.get("source", f.name), **data.get("metadata", {})}
                            })
                except Exception:
                    pass
    
    print(f"Total chunks generated: {len(docs)}")
    batch_size = 100
    
    for i in range(0, len(docs), batch_size):
        batch = docs[i:i+batch_size]
        texts = [d["content"] for d in batch]
        
        try:
            # This calls batchEmbedContents internally and counts as 1 request!
            embeddings = embeddings_model.embed_documents(texts)
                
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
            retries = 3
            while retries > 0:
                try:
                    with urllib.request.urlopen(req) as response:
                        print(f"Uploaded batch {i//batch_size + 1}/{len(docs)//batch_size + 1}")
                        break
                except urllib.error.HTTPError as e:
                    print(f"Failed to upload batch, retrying... {e.read().decode('utf-8')}")
                    retries -= 1
                    time.sleep(2)
            
            # Sleep 1 second to avoid hitting rate limits (1500 per day, but also RPM limits)
            time.sleep(1)
        except Exception as e:
            print(f"Embedding error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    upload()
