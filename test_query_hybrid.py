import os
import requests
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings

# Load environment
load_dotenv()

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")

if not supabase_url or not supabase_key:
    print("[!] Error: Supabase credentials missing in .env")
    exit(1)

# Initialize Embeddings (same model as the index)
print("[*] Initializing HuggingFace Embeddings (all-MiniLM-L6-v2)...")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Test query in Indonesian
query = "Apa kewajiban seorang Uskup?"
print(f"[*] Embedding query: '{query}'")
query_embedding = embeddings.embed_query(query)

url = f"{supabase_url.rstrip('/')}/rest/v1/rpc/match_documents_hybrid"
headers = {
    "apikey": supabase_key,
    "Authorization": f"Bearer {supabase_key}",
    "Content-Type": "application/json"
}

payload = {
    "query_text": query,
    "query_embedding": query_embedding,
    "match_count": 5,
    "filter": {}
}

print("[*] Calling match_documents_hybrid on Supabase...")
response = requests.post(url, headers=headers, json=payload)

if response.status_code == 200:
    results = response.json()
    print(f"\n[SUCCESS] Retrieved {len(results)} documents:\n")
    for i, doc in enumerate(results):
        print(f"[{i+1}] Source: {doc.get('metadata', {}).get('source', 'Unknown')} | Title: {doc.get('metadata', {}).get('title', 'No Title')}")
        print(f"    RRF Score: {doc.get('rrf_score'):.5f} | Similarity: {doc.get('similarity'):.5f} | FTS Rank: {doc.get('fts_rank'):.5f}")
        content_snippet = doc.get('content', '').replace('\n', ' ')
        print(f"    Content: {content_snippet[:150]}...")
        print("-" * 80)
else:
    print(f"[!] Error calling RPC: {response.status_code} - {response.text}")
