import os
import json
import urllib.request
import urllib.error
import time
from pathlib import Path
from sentence_transformers import SentenceTransformer

# Load env manually
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ[k] = v.strip()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

if not all([SUPABASE_URL, SUPABASE_KEY]):
    print("Missing credentials!")
    exit(1)

def upload_batch(payload, batch_index, total_batches):
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
                print(f"Uploaded batch {batch_index}/{total_batches}")
                return True
        except urllib.error.HTTPError as e:
            print(f"Failed to upload batch {batch_index}, retrying... {e.read().decode('utf-8')}")
            retries -= 1
            time.sleep(2)
    return False

def upload():
    print("Loading local embedding model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
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
    
    print("Calculating embeddings using full Ryzen CPU power...")
    texts = [d["content"] for d in docs]
    # batch_size=256 pushes the CPU completely to its limits
    emb_np = model.encode(texts, batch_size=256, show_progress_bar=True)
    embeddings = [e.tolist() for e in emb_np]
    
    print("Building payloads...")
    batch_size = 100
    payloads = []
    for i in range(0, len(docs), batch_size):
        batch_docs = docs[i:i+batch_size]
        batch_embs = embeddings[i:i+batch_size]
        
        payload = []
        for d, e in zip(batch_docs, batch_embs):
            payload.append({
                "content": d["content"],
                "metadata": d["metadata"],
                "embedding": e
            })
        payloads.append(payload)

    total_batches = len(payloads)
    print(f"Launching 20 parallel threads to blast {total_batches} batches to Supabase...")
    
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = []
        for i, payload in enumerate(payloads):
            futures.append(executor.submit(upload_batch, payload, i + 1, total_batches))
        
        concurrent.futures.wait(futures)
    print("Upload complete!")

if __name__ == "__main__":
    upload()
