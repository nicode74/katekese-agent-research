import os
from typing import List, Dict, Any
from dotenv import load_dotenv

from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Load environment
load_dotenv()

class KatekeseAgentGroq:
    def __init__(self, index_path: str = "data/index/katekese_faiss_api"):
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004"
        )
        
        if not os.path.exists(index_path):
            raise FileNotFoundError(f"Index not found at {index_path}. Please run indexer first.")
            
        self.vector_store = FAISS.load_local(
            index_path, 
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        
        # Initialize LLM (Groq Cloud Llama 3 8B)
        self.llm = ChatGroq(
            model="llama3-8b-8192",
            temperature=0.2, 
            api_key=os.getenv("GROQ_API_KEY")
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
        agent = KatekeseAgentGroq()
        print("[*] Groq Agent Ready. Testing query...")
        result = agent.ask("Apa kewajiban seorang Uskup dalam memelihara iman umat menurut hukum gereja?")
        print(f"\nA: {result['answer']}")
    except Exception as e:
        print(f"[!] Error: {e}")
