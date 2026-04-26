import os
from typing import List, Dict, Any
from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Load environment
load_dotenv()

class KatekeseAgent:
    def __init__(self, index_path: str = "data/index/katekese_faiss_local"):
        # 1. Initialize Embeddings (Must match indexer)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        
        # 2. Load Local Index
        if not os.path.exists(index_path):
            raise FileNotFoundError(f"Index not found at {index_path}. Please run indexer first.")
            
        self.vector_store = FAISS.load_local(
            index_path, 
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        
        # 3. Initialize LLM (Gemini 2.0 Flash is recommended for speed/cost)
        self.llm = ChatGoogleGenerativeAI(
            model="models/gemini-2.0-flash",
            temperature=0.2, # Lower temperature for factual accuracy
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        # 4. Define the Retrieval Chain
        self.retriever = self.vector_store.as_retriever(
            search_kwargs={"k": 5} # Get top 5 relevant chunks
        )

    def format_docs(self, docs):
        """Formats docs for the prompt and prepares citation info."""
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
        """Orchestrate the RAG flow: Retrieve -> Generate -> Cite."""
        
        # A. Retrieve
        docs = self.retriever.invoke(question)
        context_text, citations = self.format_docs(docs)
        
        # B. Prepare Prompt
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
        
        # C. Generate
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
    # Test the Agent
    try:
        agent = KatekeseAgent()
        print("[*] Agent Ready. Testing query...")
        
        test_query = "Apa kewajiban seorang Uskup dalam memelihara iman umat menurut hukum gereja?"
        result = agent.ask(test_query)
        
        print(f"\nQ: {result['question']}")
        print(f"\nA: {result['answer']}")
        print("\n📚 REFERENSI:")
        for cite in result['citations']:
            print(f"- [{cite['id']}] {cite['title']} (Sumber: {cite['source']})")
            
    except Exception as e:
        print(f"[!] Error: {e}")
