import os
import json
import time
from pathlib import Path
from typing import List
from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

class KatekeseIndexer:
    def __init__(self, data_dir: str = "data/final", docs_dir: str = "docs", index_dir: str = "data/index"):
        self.data_dir = Path(data_dir)
        self.docs_dir = Path(docs_dir)
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Local Multilingual Embeddings
        print("[*] Initializing Local Multilingual Embeddings (HuggingFace)...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\n\n", "\n", " ", ""]
        )

    def load_jsonl_documents(self, limit_per_file: int = None) -> List[Document]:
        """Load .jsonl files from data/final/."""
        documents = []
        jsonl_files = list(self.data_dir.glob("*.jsonl"))
        
        print(f"[*] Loading data from {len(jsonl_files)} JSONL files...")
        for file_path in jsonl_files:
            count = 0
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        doc = Document(
                            page_content=data['content'],
                            metadata={
                                "title": data['title'],
                                "source": data['source'],
                                "url": data['url'],
                                "language": data['language'],
                                **data.get('metadata', {})
                            }
                        )
                        chunks = self.text_splitter.split_documents([doc])
                        documents.extend(chunks)
                        count += 1
                        if limit_per_file and count >= limit_per_file:
                            break
                    except: continue
            print(f"    Loaded {count} entries from {file_path.name}")
        return documents

    def load_markdown_documents(self) -> List[Document]:
        """Load .md files from Obsidian vault (docs/)."""
        documents = []
        md_files = list(self.docs_dir.rglob("*.md"))
        
        print(f"[*] Loading data from {len(md_files)} Markdown files (Obsidian)...")
        for file_path in md_files:
            # Skip obsidian config
            if ".obsidian" in str(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    doc = Document(
                        page_content=content,
                        metadata={
                            "title": file_path.stem,
                            "source": "Obsidian Vault",
                            "file_path": str(file_path),
                            "language": "id"
                        }
                    )
                    chunks = self.text_splitter.split_documents([doc])
                    documents.extend(chunks)
                    print(f"    Loaded {file_path.name}")
            except Exception as e:
                print(f"    [!] Error loading {file_path.name}: {e}")
        return documents

    def create_index(self, batch_size: int = 1000, test_mode: bool = False):
        """Create FAISS index combining data and documentation."""
        limit = 100 if test_mode else None
        
        all_docs = self.load_jsonl_documents(limit_per_file=limit)
        all_docs.extend(self.load_markdown_documents())
        
        print(f"[*] Creating index for {len(all_docs)} total chunks...")
        start_time = time.time()
        
        vector_store = None
        for i in range(0, len(all_docs), batch_size):
            batch = all_docs[i:i + batch_size]
            print(f"  [>] Indexing batch {i//batch_size + 1}/{(len(all_docs)-1)//batch_size + 1}...")
            
            if vector_store is None:
                vector_store = FAISS.from_documents(batch, self.embeddings)
            else:
                vector_store.add_documents(batch)
            
        if vector_store:
            save_path = self.index_dir / "katekese_faiss_local"
            vector_store.save_local(str(save_path))
            print(f"[*] Index saved successfully to {save_path}")
            print(f"[*] Total indexing time: {time.time() - start_time:.2f} seconds")

    def query_test(self, query: str, k: int = 3):
        """Test the local index."""
        save_path = self.index_dir / "katekese_faiss_local"
        if not (save_path).exists():
            print("[!] Index not found.")
            return

        vector_store = FAISS.load_local(
            str(save_path), 
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        
        results = vector_store.similarity_search(query, k=k)
        print(f"\n[LOCAL QUERY TEST] Results for: '{query}'")
        for i, res in enumerate(results):
            print(f"\n--- Result {i+1} ---")
            print(f"Title: {res.metadata.get('title')}")
            print(f"Source: {res.metadata.get('source')}")
            print(f"Snippet: {res.page_content[:200]}...")

if __name__ == "__main__":
    indexer = KatekeseIndexer()
    
    # Run production indexing (Data + Docs)
    indexer.create_index(test_mode=False)
    
    # Test query about project itself
    indexer.query_test("Apa saja kategori data dalam proyek ini?")
