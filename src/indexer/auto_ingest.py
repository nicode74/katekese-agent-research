import os
import requests
from typing import Dict, Any, List
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

class AutoIngestionService:
    def __init__(self):
        print("[*] Initializing Auto-Ingestion Embeddings (all-MiniLM-L6-v2)...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=80,
            separators=["\n\n", "\n", " ", ""]
        )
        self.supabase_url = os.environ.get("SUPABASE_URL", "").rstrip("/")
        self.supabase_key = os.environ.get("SUPABASE_SERVICE_KEY", os.environ.get("SUPABASE_KEY", ""))

    def ingest_document(self, title: str, content: str, source: str = "Warta Paroki", url: str = "", extra_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Split, embed, and upsert a new parish document/announcement into Supabase vector store."""
        if not content or not content.strip():
            return {"status": "error", "message": "Content cannot be empty."}

        if not self.supabase_url or not self.supabase_key:
            return {"status": "error", "message": "Supabase credentials missing."}

        metadata = {
            "title": title,
            "source": source,
            "url": url,
            "language": "id"
        }
        if extra_metadata:
            metadata.update(extra_metadata)

        # 1. Chunk document
        chunks = self.text_splitter.split_text(content)
        
        # 2. Compute embeddings
        embeddings_list = self.embeddings.embed_documents(chunks)
        
        # 3. Prepare payload for Supabase REST API (documents table)
        payload = []
        for chunk_text, emb in zip(chunks, embeddings_list):
            payload.append({
                "content": f"Judul: {title}\n{chunk_text}",
                "metadata": metadata,
                "embedding": emb
            })

        # 4. Upsert into Supabase `documents` table
        headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }

        api_url = f"{self.supabase_url}/rest/v1/documents"
        try:
            res = requests.post(api_url, headers=headers, json=payload)
            if res.status_code in (200, 201, 204):
                return {
                    "status": "success",
                    "message": f"Successfully indexed '{title}' into {len(chunks)} vector chunk(s).",
                    "chunks_count": len(chunks)
                }
            else:
                return {
                    "status": "error",
                    "message": f"Supabase insert error ({res.status_code}): {res.text}"
                }
        except Exception as e:
            return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    service = AutoIngestionService()
    res = service.ingest_document(
        title="Pengumuman Misa Paskah 2026",
        content="Pendaftaran Misa Paskah Paroki St. Agustinus dibuka mulai tanggal 1 April 2026 melalui Sekretariat Paroki.",
        source="Warta Paroki"
    )
    print("Ingest Result:", res)
