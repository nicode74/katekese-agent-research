import os
import time
import mlflow
from typing import AsyncGenerator
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from supabase.client import Client, create_client
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

load_dotenv()

class HybridOrchestrator:
    def __init__(self):
        # 1. Setup Models
        print("[*] Initializing Llama 3 via Groq (Intent Router) & Gemini 1.5 (Synthesizer)...")
        self.intent_router = ChatGroq(model="llama3-8b-8192")
        self.synthesizer = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro-latest", 
            temperature=0.2,
            streaming=True
        )
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")
        
        # 2. Setup Vector Store
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")
        if supabase_url and supabase_key:
            self.supabase: Client = create_client(supabase_url, supabase_key)
            self.vector_store = SupabaseVectorStore(
                embedding=self.embeddings,
                client=self.supabase,
                table_name="documents",
                query_name="match_documents"
            )
            print("[*] Successfully connected to Supabase Vector Store")
        else:
            print("[WARNING] Supabase credentials missing. RAG will not work.")
            self.vector_store = None

        # 3. MLOps Setup
        self.mlflow_uri = os.environ.get("MLFLOW_TRACKING_URI")
        if self.mlflow_uri:
            mlflow.set_tracking_uri(self.mlflow_uri)
            mlflow.set_experiment("Agentic-RAG-Serving")

    def route_intent(self, query: str) -> str:
        """Use Llama 3 to determine the intent of the query."""
        system_prompt = """You are an intent router for a Catholic Theology AI assistant.
Analyze the user's query and output EXACTLY ONE of the following routing labels:
- RAG: If the query asks for Catholic teachings, Bible verses, Church law, or theological concepts requiring document lookup.
- DIRECT: If the query is a simple greeting, conversational pleasantry, or a general question not requiring specific theological documents.

Output only the label (RAG or DIRECT), nothing else."""
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=query)
            ]
            response = self.intent_router.invoke(messages)
            intent = response.content.strip().upper()
            if "RAG" in intent:
                return "RAG"
            return "DIRECT"
        except Exception as e:
            print(f"[!] Router error: {e}, defaulting to RAG.")
            return "RAG"

    async def retrieve_context(self, query: str, k: int = 5) -> str:
        """Retrieve context from Supabase Vector Store and log latency."""
        if not self.vector_store:
            return ""
        
        start_time = time.time()
        docs = self.vector_store.similarity_search(query, k=k)
        retrieval_latency = time.time() - start_time
        
        # Log metric to MLflow if a run is active
        if self.mlflow_uri and mlflow.active_run():
            mlflow.log_metric("retrieval_latency", retrieval_latency)
            
        context = "\n\n".join([f"Source: {d.metadata.get('source', 'Unknown')}\n{d.page_content}" for d in docs])
        return context

    async def stream_response(self, query: str, history: list = None, mode: str = "short") -> AsyncGenerator[str, None]:
        """Full pipeline: route -> retrieve -> synthesize (stream)."""
        run_started_here = False
        if self.mlflow_uri and not mlflow.active_run():
            mlflow.start_run(run_name="Hybrid_RAG_Query")
            mlflow.log_param("model", "gemini-1.5-pro-latest")
            mlflow.log_param("intent_router", "llama3")
            mlflow.log_param("mode", mode)
            run_started_here = True

        try:
            # 1. Route Intent
            intent = self.route_intent(query)
            if self.mlflow_uri and mlflow.active_run():
                mlflow.log_param("intent", intent)

            # 2. Retrieve Context (if RAG)
            context = ""
            if intent == "RAG":
                context = await self.retrieve_context(query)

            # 3. Synthesize Response
            system_prompt = "You are a helpful, respectful, and highly knowledgeable AI assistant specializing in Catholic Theology. "
            if mode == "detailed":
                system_prompt += "Provide a comprehensive, highly detailed response and make sure to include citations to the provided sources if applicable. "
            else:
                system_prompt += "Provide a concise and to-the-point response. "

            if intent == "RAG":
                system_prompt += f"\n\nUse the following retrieved context to answer the user's question accurately. If the answer is not in the context, say you don't know based on the provided documents.\n\nContext:\n{context}"
            else:
                system_prompt += "\n\nAnswer the user's query."

            messages = [SystemMessage(content=system_prompt)]
            
            if history:
                for msg in history:
                    role = msg.get("role", "")
                    content = msg.get("content", "")
                    if role == "user":
                        messages.append(HumanMessage(content=content))
                    elif role == "assistant":
                        messages.append(AIMessage(content=content))

            messages.append(HumanMessage(content=query))

            # Stream from Gemini
            async for chunk in self.synthesizer.astream(messages):
                yield chunk.content

        except Exception as e:
            print(f"[!] Engine error: {e}")
            yield f"\n\n**System Error:** Could not complete the request. Details: {str(e)}"

        finally:
            if run_started_here:
                mlflow.end_run()
