import os
import json
import asyncio
from pathlib import Path
from typing import List
from dotenv import load_dotenv
import mlflow

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

class SupabaseIndexer:
    def __init__(self, data_dir: str = "data/final", docs_dir: str = "docs"):
        self.data_dir = Path(data_dir)
        self.docs_dir = Path(docs_dir)
        
        # Initialize Google Embeddings
        print("[*] Initializing Google gemini-embedding-2...")
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-2"
        )
        
        # Text Splitter Config from Plan (Chunk: 800, Overlap: 10%)
        self.chunk_size = 800
        self.chunk_overlap = 80
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )

        # Initialize Supabase
        self.supabase_url = os.environ.get("SUPABASE_URL")
        self.supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")
        if not self.supabase_url or not self.supabase_key:
            print("[WARNING] SUPABASE_URL or SUPABASE_SERVICE_KEY not found in env.")
        
        # Configure MLflow Dagshub
        self.mlflow_uri = os.environ.get("MLFLOW_TRACKING_URI")
        if self.mlflow_uri:
            os.environ["MLFLOW_TRACKING_USERNAME"] = os.environ.get("MLFLOW_TRACKING_USERNAME", "")
            os.environ["MLFLOW_TRACKING_PASSWORD"] = os.environ.get("MLFLOW_TRACKING_PASSWORD", "")
            mlflow.set_tracking_uri(self.mlflow_uri)
            mlflow.set_experiment("Agentic-RAG-ETL")

    def load_jsonl_file(self, file_path: Path) -> List[Document]:
        documents = []
        count = 0
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    doc = Document(
                        page_content=data['content'],
                        metadata={
                            "title": data.get('title', ''),
                            "source": data.get('source', str(file_path.name)),
                            "url": data.get('url', ''),
                            "language": data.get('language', 'id'),
                            **data.get('metadata', {})
                        }
                    )
                    chunks = self.text_splitter.split_documents([doc])
                    documents.extend(chunks)
                    count += 1
                except Exception as e:
                    continue
        print(f"    Loaded {count} entries from {file_path.name} -> {len(documents)} chunks.")
        return documents

    async def async_batch_upsert(self, documents: List[Document], batch_size: int = 100):
        if not self.supabase_url:
            print("[ERROR] Cannot upsert: Supabase credentials missing.")
            return

        total_batches = (len(documents) + batch_size - 1) // batch_size
        print(f"[*] Starting async batch upsert of {len(documents)} chunks in {total_batches} batches.")
        
        loop = asyncio.get_event_loop()
        from tenacity import retry, wait_exponential, stop_after_attempt
        import requests
        
        @retry(
            wait=wait_exponential(multiplier=2, min=10, max=60), 
            stop=stop_after_attempt(10),
            before_sleep=lambda retry_state: print(f"  [!] Rate limited, retrying in {retry_state.next_action.sleep}s...")
        )
        def _add_docs_with_retry(batch):
            # 1. Embed documents
            texts = [doc.page_content for doc in batch]
            embeddings = self.embeddings.embed_documents(texts)
            
            # 2. Prepare payload
            payload = []
            for doc, emb in zip(batch, embeddings):
                payload.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "embedding": emb
                })
                
            # 3. Insert via REST API
            url = f"{self.supabase_url.rstrip('/')}/rest/v1/documents"
            headers = {
                "apikey": self.supabase_key,
                "Authorization": f"Bearer {self.supabase_key}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal"
            }
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code not in (200, 201, 204):
                raise Exception(f"Failed to upsert: {response.text}")
            
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            await loop.run_in_executor(None, _add_docs_with_retry, batch)
            print(f"  [>] Upserted batch {i//batch_size + 1}/{total_batches}")

    def run_pipeline(self):
        # 1. Load data
        jsonl_files = list(self.data_dir.glob("*.jsonl"))
        all_docs = []
        
        if self.mlflow_uri:
            mlflow.start_run(run_name="Supabase_ETL_Run")
            mlflow.log_param("chunk_size", self.chunk_size)
            mlflow.log_param("chunk_overlap", self.chunk_overlap)
            mlflow.log_param("embedding_model", "gemini-embedding-001")
        
        try:
            for f in jsonl_files:
                docs = self.load_jsonl_file(f)
                all_docs.extend(docs)
                
            if not all_docs:
                print("[*] No documents found to index.")
                if self.mlflow_uri:
                    mlflow.end_run()
                return

            # 2. Async batch upsert
            asyncio.run(self.async_batch_upsert(all_docs, batch_size=200))
            
            # 3. Log Artifacts
            if self.mlflow_uri:
                for f in jsonl_files:
                    # Log files that have 'master_dataset' in name, or log all
                    if "master_dataset" in f.name:
                        mlflow.log_artifact(str(f), artifact_path="dataset")
                print("[*] MLflow artifacts logged.")
                
            print("[*] ETL Pipeline Complete.")
            
        except Exception as e:
            print(f"[!] Error in ETL Pipeline: {e}")
        finally:
            if self.mlflow_uri and mlflow.active_run():
                mlflow.end_run()

if __name__ == "__main__":
    indexer = SupabaseIndexer()
    indexer.run_pipeline()
