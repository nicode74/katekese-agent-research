import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

try:
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    texts = ["hello world"] * 100
    res = embeddings.embed_documents(texts)
    print(f"Success! Batched {len(res)} embeddings.")
except Exception as e:
    print(f"Error: {e}")
