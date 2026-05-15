from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn

from src.orchestrator.agent_logic import HybridOrchestrator

app = FastAPI(
    title="Katekese RAG API",
    description="Agentic RAG pipeline for Catholic Theology",
    version="1.0.0"
)

# Initialize Orchestrator on startup
orchestrator = None

@app.on_event("startup")
async def startup_event():
    global orchestrator
    orchestrator = HybridOrchestrator()

class QueryRequest(BaseModel):
    query: str

@app.post("/ask")
async def ask_question(request: QueryRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized.")

    return StreamingResponse(
        orchestrator.stream_response(request.query), 
        media_type="text/event-stream"
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("src.api.server:app", host="0.0.0.0", port=8000, reload=True)
