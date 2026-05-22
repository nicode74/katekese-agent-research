import os
import mlflow
import pandas as pd
from dotenv import load_dotenv

# Ensure we can import src modules
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

class RAGModelWrapper(mlflow.pyfunc.PythonModel):
    def load_context(self, context):
        from src.orchestrator.agent_logic import HybridOrchestrator
        self.orchestrator = HybridOrchestrator()
        
    def predict(self, context, model_input):
        import asyncio
        # We assume model_input is a DataFrame with 'query' column, or dictionary
        if isinstance(model_input, pd.DataFrame):
            queries = model_input['query'].tolist()
        elif isinstance(model_input, dict) and 'query' in model_input:
            queries = [model_input['query']]
        else:
            queries = [str(model_input)]
            
        results = []
        for q in queries:
            # We collect all streamed chunks to return a full string (since pyfunc expects sync response by default)
            async def get_full_response():
                chunks = []
                async for chunk in self.orchestrator.stream_response(q):
                    chunks.append(chunk)
                return "".join(chunks)
            
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
            response = loop.run_until_complete(get_full_response())
            results.append(response)
            
        return results

def main():
    load_dotenv()
    
    mlflow_uri = os.environ.get("MLFLOW_TRACKING_URI")
    if mlflow_uri:
        mlflow.set_tracking_uri(mlflow_uri)
    mlflow.set_experiment("Agentic-RAG-Serving")
    
    with mlflow.start_run(run_name="Model_Registration") as run:
        print("[*] Logging HybridOrchestrator model to MLflow...")
        
        # Define the requirements file path
        requirements = os.path.join(os.path.dirname(__file__), '..', 'requirements.txt')
        
        # Ensure we just pass a string array if requirements file doesn't exist 
        if not os.path.exists(requirements):
            requirements = ["langchain_google_genai", "langchain_groq", "supabase", "pydantic", "fastapi"]

        mlflow.pyfunc.log_model(
            artifact_path="katekese_rag_model",
            python_model=RAGModelWrapper(),
            registered_model_name="Ecclesia-RAG-Hybrid",
            pip_requirements=requirements
        )
        print(f"[*] Model registered successfully! Run ID: {run.info.run_id}")
        print("[*] Use 'mlflow ui' to view the model artifact.")

if __name__ == "__main__":
    main()
