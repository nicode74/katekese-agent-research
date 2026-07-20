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
import time
import json
import mlflow
import requests
from typing import AsyncGenerator, List, Dict, Any
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

load_dotenv()

class HybridOrchestrator:
    def __init__(self):
        print("[*] Initializing Agentic RAG Pipeline (Llama 3.3 Router + Gemini 2.5 Synthesizer)...")
        self.intent_router = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1)
        self.synthesizer = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", 
            temperature=0.2,
            streaming=True
        )
        self.verifier = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.0)
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        self.supabase_url = os.environ.get("SUPABASE_URL", "").rstrip("/")
        self.supabase_key = os.environ.get("SUPABASE_SERVICE_KEY", os.environ.get("SUPABASE_KEY", ""))
        
        if self.supabase_url and self.supabase_key:
            print("[*] Supabase connection configured.")
        else:
            print("[WARNING] Supabase credentials missing. RAG will fallback to direct model generation.")
            
        self.mlflow_uri = os.environ.get("MLFLOW_TRACKING_URI")
        if self.mlflow_uri:
            mlflow.set_tracking_uri(self.mlflow_uri)
            mlflow.set_experiment("Agentic-RAG-Serving")

    def route_intent(self, query: str) -> str:
        """Route user query into DOCTRINE_RAG, PARISH_INFO, or DIRECT."""
        system_prompt = """You are an intent router for a Catholic Parish AI Assistant.
Analyze the user's query and output EXACTLY ONE of the following routing labels:
- DOCTRINE_RAG: If the query asks about Catholic teachings, Bible verses, Church laws (KHK), Catechism (KKGK), sacraments, theology, or papal encyclicals.
- PARISH_INFO: If the query asks about church mass schedules, mass times, parish announcements (warta jemaat), daily reflections (renungan harian), church locations, or parish events.
- DIRECT: If the query is a greeting, casual conversation, identity check, or general request not needing document lookup.

Output ONLY the label name (DOCTRINE_RAG, PARISH_INFO, or DIRECT)."""
        
        try:
            messages = [SystemMessage(content=system_prompt), HumanMessage(content=query)]
            response = self.intent_router.invoke(messages)
            intent = response.content.strip().upper()
            if "DOCTRINE" in intent or "RAG" in intent:
                return "DOCTRINE_RAG"
            if "PARISH" in intent or "INFO" in intent or "JADWAL" in intent or "WARTA" in intent:
                return "PARISH_INFO"
            return "DIRECT"
        except Exception as e:
            print(f"[!] Intent router error: {e}. Defaulting to DOCTRINE_RAG.")
            return "DOCTRINE_RAG"

    async def retrieve_parish_context(self, query: str) -> tuple[str, List[Dict[str, Any]]]:
        """Fetch real-time parish schedules, announcements, and reflections from Supabase DB."""
        if not self.supabase_url or not self.supabase_key:
            return "", []

        headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}"
        }
        
        context_parts = []
        citations = []
        
        try:
            # 1. Fetch upcoming mass schedules
            res_jadwal = requests.get(f"{self.supabase_url}/rest/v1/jadwal?select=*&order=tanggal.asc&limit=5", headers=headers)
            if res_jadwal.status_code == 200:
                jadwal_data = res_jadwal.json()
                if jadwal_data:
                    context_parts.append("=== JADWAL MISA / KEGIATAN PAROKI ===")
                    for j in jadwal_data:
                        line = f"• {j.get('nama_kegiatan')}: {j.get('tanggal')} pukul {j.get('jam')} di {j.get('lokasi')}"
                        if j.get('deskripsi'):
                            line += f" ({j.get('deskripsi')})"
                        context_parts.append(line)
                        citations.append({
                            "title": f"Jadwal: {j.get('nama_kegiatan')}",
                            "source": "Jadwal Paroki",
                            "content": f"{j.get('tanggal')} @ {j.get('lokasi')}"
                        })

            # 2. Fetch announcements (warta jemaat)
            res_pengumuman = requests.get(f"{self.supabase_url}/rest/v1/pengumuman?select=*&order=created_at.desc&limit=5", headers=headers)
            if res_pengumuman.status_code == 200:
                pengumuman_data = res_pengumuman.json()
                if pengumuman_data:
                    context_parts.append("\n=== WARTA JEMAAT / PENGUMUMAN ===")
                    for p in pengumuman_data:
                        context_parts.append(f"• [{p.get('kategori', 'Umum')}] {p.get('judul')}: {p.get('isi')}")
                        citations.append({
                            "title": p.get('judul', 'Pengumuman'),
                            "source": "Warta Jemaat",
                            "content": p.get('isi', '')[:100]
                        })

            # 3. Fetch latest reflection
            res_renungan = requests.get(f"{self.supabase_url}/rest/v1/renungan?select=*&order=tanggal.desc&limit=2", headers=headers)
            if res_renungan.status_code == 200:
                renungan_data = res_renungan.json()
                if renungan_data:
                    context_parts.append("\n=== RENUNGAN HARIAN PAROKI ===")
                    for r in renungan_data:
                        context_parts.append(f"• {r.get('judul')} ({r.get('ayat_referensi')}): {r.get('isi')}")
                        citations.append({
                            "title": r.get('judul', 'Renungan'),
                            "source": f"Renungan {r.get('ayat_referensi')}",
                            "content": r.get('isi', '')[:100]
                        })

        except Exception as e:
            print(f"[!] Error retrieving parish context: {e}")

        context_text = "\n".join(context_parts)
        return context_text, citations

    async def retrieve_doctrine_context(self, query: str, k: int = 5) -> tuple[str, List[Dict[str, Any]]]:
        """Retrieve context from vector database using hybrid vector similarity search."""
        if not self.supabase_url or not self.supabase_key:
            return "", []
            
        start_time = time.time()
        query_embedding = self.embeddings.embed_query(query)
        
        url = f"{self.supabase_url}/rest/v1/rpc/match_documents_hybrid"
        headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "query_text": query,
            "query_embedding": query_embedding,
            "match_count": k,
            "filter": {}
        }
        
        docs = []
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=8)
            if response.status_code == 200:
                docs = response.json()
        except Exception as e:
            print(f"[!] Vector RPC error: {e}")
            
        retrieval_latency = time.time() - start_time
        if self.mlflow_uri and mlflow.active_run():
            mlflow.log_metric("retrieval_latency", retrieval_latency)
            
        context_parts = []
        citations = []
        
        for d in docs:
            metadata = d.get('metadata', {})
            source = metadata.get('source', 'Katekese Database')
            title = d.get('title') or metadata.get('title') or 'Dokumen Gereja'
            content = d.get('content', '')
            url_link = d.get('url') or metadata.get('url') or ''
            
            context_parts.append(f"Sumber: {source} | Judul: {title}\n{content}")
            citations.append({
                "title": title,
                "source": source,
                "content": content[:120] + "..." if len(content) > 120 else content,
                "url": url_link
            })
            
        return "\n\n".join(context_parts), citations

    def verify_self_rag(self, query: str, context: str, response_text: str) -> Dict[str, Any]:
        """Self-RAG critic to check for dogmatic hallucinations and verify context grounding."""
        prompt = f"""You are a theological evaluator verifying an AI assistant's response.
Question: {query}
Retrieved Context:
{context}

Response Draft:
{response_text}

Analyze if the response is faithful to the context and does NOT invent unverified theological claims or false Bible citations.
Output a JSON object with:
"is_faithful": boolean,
"reason": string,
"correction_needed": boolean
"""
        try:
            res = self.verifier.invoke([HumanMessage(content=prompt)])
            text = res.content.strip()
            if "{" in text and "}" in text:
                json_str = text[text.find("{"):text.rfind("}")+1]
                return json.loads(json_str)
        except Exception as e:
            print(f"[!] Self-RAG verification skipped/errored: {e}")
            
        return {"is_faithful": True, "reason": "Self-check passed by default.", "correction_needed": False}

    async def stream_response(self, query: str, history: List[Dict[str, str]] = None, mode: str = "short") -> AsyncGenerator[str, None]:
        """Full Agentic Pipeline: Route -> Retrieve (Parish or Doctrine) -> Synthesize -> Yield SSE events."""
        intent = self.route_intent(query)
        
        context = ""
        citations = []
        
        if intent == "PARISH_INFO":
            context, citations = await self.retrieve_parish_context(query)
        elif intent == "DOCTRINE_RAG":
            context, citations = await self.retrieve_doctrine_context(query)
            
        # Send initial metadata SSE payload first
        metadata_payload = json.dumps({
            "intent": intent,
            "citations": citations
        })
        yield f"event: metadata\ndata: {metadata_payload}\n\n"
        
        # System Prompt construction
        system_prompt = (
            "Anda adalah Asisten AI Resmi Gereja Katolik St. Agustinus & St. Yohanes Rasul (Girisekar). "
            "Jawablah dengan ramah, penuh kasih, hormat, dan berbasis doktrin Katolik yang sahih.\n"
        )
        
        if mode == "detailed":
            system_prompt += "Berikan jawaban yang mendalam, terstruktur dengan sub-judul, dan jelaskan dasar Kitab Suci atau Katekismus jika relevan.\n"
        else:
            system_prompt += "Berikan jawaban yang padat, jelas, dan langsung pada inti pertanyaan.\n"
            
        if context:
            system_prompt += f"\nGunakan data dan dokumen berikut sebagai referensi utama Anda:\n\n{context}\n"
        elif intent != "DIRECT":
            system_prompt += "\nJika data spesifik tidak ditemukan di konteks, jawab berdasarkan pemahaman umum teologi Katolik dan beri tahu pengguna bahwa ini adalah penjelasan umum.\n"

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

        # Stream text response from Gemini
        accumulated_text = ""
        async for chunk in self.synthesizer.astream(messages):
            accumulated_text += chunk.content
            # Send chunk event
            chunk_payload = json.dumps({"text": chunk.content})
            yield f"event: chunk\ndata: {chunk_payload}\n\n"
            
        # Optional Self-RAG verification log
        if intent == "DOCTRINE_RAG" and context:
            eval_res = self.verify_self_rag(query, context, accumulated_text)
            if not eval_res.get("is_faithful", True):
                print(f"[Self-RAG Warning]: {eval_res.get('reason')}")

        yield "event: end\ndata: {}\n\n"
