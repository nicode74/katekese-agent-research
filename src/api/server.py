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

from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from src.orchestrator.agent_logic import HybridOrchestrator
from src.agents.daily_reflection_agent import DailyReflectionAgent
from src.indexer.auto_ingest import AutoIngestionService
from src.agents.analytics_agent import QueryAnalyticsAgent

app = FastAPI(
    title="Katekese Ecclesia-RAG API & Autonomous Agents",
    description="Agentic RAG pipeline & automated parish services",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
orchestrator: Optional[HybridOrchestrator] = None
reflection_agent: Optional[DailyReflectionAgent] = None
ingestion_service: Optional[AutoIngestionService] = None
analytics_agent: Optional[QueryAnalyticsAgent] = None

# Query history buffer for analytics
query_history_log: List[str] = []

@app.on_event("startup")
async def startup_event():
    global orchestrator, reflection_agent, ingestion_service, analytics_agent
    print("[*] Initializing Ecclesia-RAG Services & Agents...")
    orchestrator = HybridOrchestrator()
    reflection_agent = DailyReflectionAgent()
    ingestion_service = AutoIngestionService()
    analytics_agent = QueryAnalyticsAgent()

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, str]]] = []
    mode: Optional[str] = "short"

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator service not initialized.")

    query_history_log.append(request.message)

    async def sse_stream():
        async for sse_chunk in orchestrator.stream_response(request.message, request.history, request.mode):
            yield sse_chunk

    return StreamingResponse(
        sse_stream(), 
        media_type="text/event-stream"
    )

class ReflectionRequest(BaseModel):
    date: Optional[str] = None

@app.post("/agent/reflection")
async def generate_reflection(req: ReflectionRequest = None):
    if not reflection_agent:
        raise HTTPException(status_code=500, detail="Reflection Agent not ready.")
    
    date_val = req.date if req else None
    result = reflection_agent.run_daily_job(date_val)
    return result

class IngestRequest(BaseModel):
    title: str
    content: str
    source: Optional[str] = "Warta Paroki"
    url: Optional[str] = ""
    metadata: Optional[Dict[str, Any]] = None

@app.post("/webhook/ingest")
async def webhook_ingest(req: IngestRequest):
    if not ingestion_service:
        raise HTTPException(status_code=500, detail="Ingestion Service not ready.")
    
    result = ingestion_service.ingest_document(
        title=req.title,
        content=req.content,
        source=req.source,
        url=req.url,
        extra_metadata=req.metadata
    )
    return result

class AnalyticsRequest(BaseModel):
    queries: Optional[List[str]] = None

@app.post("/agent/analytics")
async def run_analytics(req: AnalyticsRequest = None):
    if not analytics_agent:
        raise HTTPException(status_code=500, detail="Analytics Agent not ready.")
    
    queries_to_analyze = (req.queries if req and req.queries else query_history_log)
    result = analytics_agent.analyze_queries(queries_to_analyze)
    return result

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Ecclesia-RAG Autonomous Agentic API",
        "version": "2.0.0"
    }

if __name__ == "__main__":
    uvicorn.run("src.api.server:app", host="0.0.0.0", port=8000, reload=True)
