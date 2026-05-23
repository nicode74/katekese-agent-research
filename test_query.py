import os
import requests
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
query = "what happen after God created adam?"
query_embedding = embeddings.embed_query(query)

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")

url = f"{supabase_url.rstrip('/')}/rest/v1/rpc/match_documents"
headers = {
    "apikey": supabase_key,
    "Authorization": f"Bearer {supabase_key}",
    "Content-Type": "application/json"
}

# Test 1: Without match_threshold
payload1 = {
    "query_embedding": query_embedding,
    "match_count": 5,
    "filter": {}
}
resp1 = requests.post(url, headers=headers, json=payload1)
if resp1.status_code == 200:
    for doc in resp1.json():
        print(f"Match: {doc.get('content')[:100]}...")
else:
    print("Error:", resp1.text)

# Test 2: With match_threshold = 0.0
payload2 = {
    "query_embedding": query_embedding,
    "match_threshold": 0.0,
    "match_count": 5
}
resp2 = requests.post(url, headers=headers, json=payload2)
print("Response 2 (threshold 0.0):", resp2.status_code, len(resp2.json()) if resp2.status_code == 200 else resp2.text)

