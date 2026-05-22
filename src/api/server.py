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

if __name__ == "__main__":
    uvicorn.run("src.api.server:app", host="0.0.0.0", port=8000, reload=True)
