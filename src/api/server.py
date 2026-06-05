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

from typing import List, Optional, Dict
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from src.orchestrator.agent_logic import HybridOrchestrator

app = FastAPI(
    title="Katekese RAG API",
    description="Agentic RAG pipeline for Catholic Theology",
    version="1.0.0"
)

# Add CORS middleware to allow requests from the website
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Orchestrator on startup
orchestrator = None

@app.on_event("startup")
async def startup_event():
    global orchestrator
    orchestrator = HybridOrchestrator()

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, str]]] = []
    mode: Optional[str] = "short"

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized.")

    async def sse_stream():
        async for chunk in orchestrator.stream_response(request.message, request.history, request.mode):
            # Format as Server-Sent Events (SSE)
            yield f"data: {chunk}\n\n"

    return StreamingResponse(
        sse_stream(), 
        media_type="text/event-stream"
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/upload")
async def trigger_upload():
    try:
        import threading
        from src.indexer.upload_in_memory import upload_with_embeddings
        
        if not orchestrator or not orchestrator.embeddings:
            return {"status": "error", "message": "Embeddings model not initialized!"}
            
        def run_upload():
            try:
                print("Starting background in-memory upload on Railway...")
                upload_with_embeddings(orchestrator.embeddings)
                print("Background upload finished!")
            except Exception as e:
                print(f"Background upload failed: {e}")
                
        threading.Thread(target=run_upload).start()
        return {"status": "success", "message": "In-memory HF Upload started in background on Railway!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run("src.api.server:app", host="0.0.0.0", port=8000, reload=True)
