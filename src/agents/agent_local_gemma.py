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
from typing import List, Dict, Any
from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Load environment
load_dotenv()

class KatekeseAgentOllamaGemma:
    def __init__(self, index_path: str = "data/index/katekese_faiss_local"):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        if not os.path.exists(index_path):
            raise FileNotFoundError(f"Index not found at {index_path}. Please run indexer first.")
            
        self.vector_store = FAISS.load_local(
            index_path, 
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        
        # Initialize LLM (Local Ollama Gemma 4)
        self.llm = ChatOllama(
            model="gemma4",
            temperature=0.2
        )
        
        self.retriever = self.vector_store.as_retriever(
            search_kwargs={"k": 5}
        )

    def format_docs(self, docs):
        context = ""
        citations = []
        for i, doc in enumerate(docs):
            source = doc.metadata.get('source', 'Unknown')
            title = doc.metadata.get('title', 'No Title')
            context += f"[{i+1}] Source: {source} ({title})\nContent: {doc.page_content}\n\n"
            citations.append({
                "id": i+1,
                "title": title,
                "source": source,
                "url": doc.metadata.get('url', '')
            })
        return context, citations

    def ask(self, question: str) -> Dict[str, Any]:
        docs = self.retriever.invoke(question)
        context_text, citations = self.format_docs(docs)
        
        template = """
        Anda adalah asisten teologi Katolik yang ahli dan bijaksana. 
        Gunakan potongan konteks di bawah ini untuk menjawab pertanyaan user. 
        
        Aturan Jawaban:
        1. Jawaban harus didasarkan HANYA pada konteks yang diberikan.
        2. Jika informasi tidak ada di konteks, katakan bahwa Anda tidak tahu, jangan mengarang.
        3. Gunakan gaya bahasa formal dan edukatif, cocok untuk pengajar/dosen.
        4. Berikan sitasi di akhir setiap poin atau paragraf menggunakan nomor [1], [2], dst.
        5. Berikan jawaban dalam Bahasa Indonesia yang baik dan benar.

        KONTEKS:
        {context}

        PERTANYAAN: 
        {question}

        JAWABAN:
        """
        
        prompt = ChatPromptTemplate.from_template(template)
        
        chain = (
            {"context": lambda x: context_text, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
        answer = chain.invoke(question)
        
        return {
            "question": question,
            "answer": answer,
            "citations": citations
        }

if __name__ == "__main__":
    try:
        agent = KatekeseAgentOllamaGemma()
        print("[*] Local Gemma Agent Ready. Testing query...")
        result = agent.ask("Apa kewajiban seorang Uskup dalam memelihara iman umat menurut hukum gereja?")
        print(f"\nA: {result['answer']}")
    except Exception as e:
        print(f"[!] Error: {e}")
