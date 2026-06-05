import socket
# Apply IPv4 monkey patch to bypass DNS timeout
orig_getaddrinfo = socket.getaddrinfo
def ipv4_only_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    return orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = ipv4_only_getaddrinfo

# Apply Pydantic unpickling patch
from langchain_core.documents import Document
def __setstate__(self, state):
    if "__dict__" in state:
        self.__dict__.update(state["__dict__"])
    else:
        self.__dict__.update(state)
    for k in ["__pydantic_extra__", "__pydantic_fields_set__", "__pydantic_private__"]:
        if k in state:
            object.__setattr__(self, k, state[k])
Document.__setstate__ = __setstate__

import os
import json
import time
from pathlib import Path
from typing import List
from dotenv import load_dotenv

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Load environment
load_dotenv()

class KatekeseIndexerAPI:
    def __init__(self, data_dir: str = "data/final", docs_dir: str = "docs", index_dir: str = "data/index"):
        self.data_dir = Path(data_dir)
        self.docs_dir = Path(docs_dir)
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        self.manifest_path = self.index_dir / "indexed_files_api.txt"
        self.index_path = self.index_dir / "katekese_faiss_api"
        
        # Initialize Google Embeddings (API-based)
        print("[*] Initializing Google Embeddings (gemini-embedding-001)...")
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001"
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\n\n", "\n", " ", ""]
        )

    def get_indexed_files(self) -> set:
        if self.manifest_path.exists():
            return set(self.manifest_path.read_text().splitlines())
        return set()

    def save_indexed_files(self, indexed_files: set):
        self.manifest_path.write_text("\n".join(sorted(list(indexed_files))))

    def load_jsonl_file(self, file_path: Path, limit: int = None) -> List[Document]:
        documents = []
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
                    if limit and count >= limit: break
                except: continue
        print(f"    Loaded {count} entries from {file_path.name} -> {len(documents)} chunks.")
        return documents

    def update_index(self, batch_size: int = 20):
        """Only index a SMALL SUBSET of files for evaluation purposes. Saves after every batch."""
        indexed_files = self.get_indexed_files()
        
        target_files = ["katekismus_final.jsonl", "pdf_Seri-Dokumen-Gerejawi-PATRIS-CORDE_final.jsonl"]
        
        jsonl_files = [self.data_dir / f for f in target_files if (self.data_dir / f).exists()]
        new_jsonl = [f for f in jsonl_files if f.name not in indexed_files]
        
        # Limit MD files
        md_files = [f for f in self.docs_dir.rglob("*.md") if ".obsidian" not in str(f)][:2]
        new_md = [f for f in md_files if str(f) not in indexed_files]
        
        if not new_jsonl and not new_md:
            print("[*] No new files to index.")
            return

        print(f"[*] Found {len(new_jsonl)} new JSONL files and {len(new_md)} new MD files.")
        
        all_new_docs = []
        for f in new_jsonl:
            all_new_docs.extend(self.load_jsonl_file(f, limit=100)) # LIMIT entries per file
            indexed_files.add(f.name)
            
        for f in new_md:
            try:
                content = f.read_text(encoding='utf-8')
                doc = Document(
                    page_content=content,
                    metadata={"title": f.stem, "source": "Obsidian Vault", "file_path": str(f)}
                )
                all_new_docs.extend(self.text_splitter.split_documents([doc]))
                indexed_files.add(str(f))
                print(f"    Loaded MD: {f.name}")
            except: pass

        if not all_new_docs:
            return

        print(f"[*] Indexing {len(all_new_docs)} new chunks using Google API...")
        
        # Load existing index or create new
        vector_store = None
        if self.index_path.exists():
            vector_store = FAISS.load_local(str(self.index_path), self.embeddings, allow_dangerous_deserialization=True)
            start_idx = 0
        else:
            first_batch = all_new_docs[:batch_size]
            vector_store = FAISS.from_documents(first_batch, self.embeddings)
            start_idx = batch_size
            vector_store.save_local(str(self.index_path))
            print(f"  [>] Indexed and SAVED first batch (1-{min(batch_size, len(all_new_docs))})")

        for i in range(start_idx, len(all_new_docs), batch_size):
            batch = all_new_docs[i:i + batch_size]
            vector_store.add_documents(batch)
            vector_store.save_local(str(self.index_path))
            print(f"  [>] Indexed and SAVED batch {i//batch_size + 1} ({i+1}-{min(i+batch_size, len(all_new_docs))})")
            time.sleep(5) # Aggressive rate limiting

        self.save_indexed_files(indexed_files)
        print(f"[*] API-based index update complete. Index saved at {self.index_path}")

    def query_test(self, query: str, k: int = 3):
        if not self.index_path.exists(): return
        vector_store = FAISS.load_local(str(self.index_path), self.embeddings, allow_dangerous_deserialization=True)
        results = vector_store.similarity_search(query, k=k)
        print(f"\n[QUERY TEST] '{query}'")
        for i, res in enumerate(results):
            print(f"[{i+1}] {res.metadata.get('title')} ({res.metadata.get('source')}): {res.page_content[:150]}...")

if __name__ == "__main__":
    indexer = KatekeseIndexerAPI()
    indexer.update_index()
    indexer.query_test("Apa saja kategori data?")
