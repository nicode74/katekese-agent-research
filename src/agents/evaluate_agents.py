import time
import os
import sys

# Add root to python path to allow importing from src.agents
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.agents.agent_gemini import KatekeseAgentGemini
from src.agents.agent_groq import KatekeseAgentGroq
from src.agents.agent_local_gemma import KatekeseAgentOllamaGemma

def run_evaluation():
    questions = [
        "Apa kewajiban seorang Uskup dalam memelihara iman umat menurut hukum gereja?",
        "Berapa jumlah sakramen dalam Gereja Katolik?",
        "Jelaskan secara singkat apa itu dosa asal berdasarkan Katekismus."
    ]
    
    agents = [
        ("Gemini 2.0 Flash", KatekeseAgentGemini),
        ("Groq (Llama 3)", KatekeseAgentGroq),
        ("Ollama (Gemma 4)", KatekeseAgentOllamaGemma)
    ]
    
    results = []
    
    print("[*] Starting Agent Evaluation Pipeline...")
    
    for agent_name, agent_class in agents:
        print(f"\n--- Testing Agent: {agent_name} ---")
        try:
            # Init agent
            agent = agent_class()
            
            for q_idx, q in enumerate(questions):
                print(f"  -> Q{q_idx+1}: {q}")
                start_time = time.time()
                try:
                    res = agent.ask(q)
                    answer = res['answer'].replace("\n", " ").replace("|", "\\|") # escape pipes for MD table
                    latency = time.time() - start_time
                    results.append({
                        "Agent": agent_name,
                        "Question": f"Q{q_idx+1}",
                        "Latency (s)": f"{latency:.2f}",
                        "Answer": answer,
                        "Status": "Success"
                    })
                    print(f"     [+] Success ({latency:.2f}s)")
                except Exception as e:
                    latency = time.time() - start_time
                    results.append({
                        "Agent": agent_name,
                        "Question": f"Q{q_idx+1}",
                        "Latency (s)": f"{latency:.2f}",
                        "Answer": f"ERROR: {str(e)}".replace("|", "\\|"),
                        "Status": "Failed"
                    })
                    print(f"     [-] Failed ({latency:.2f}s): {e}")
        except Exception as e:
            print(f"[!] Could not initialize {agent_name}: {e}")
            for q_idx, q in enumerate(questions):
                results.append({
                        "Agent": agent_name,
                        "Question": f"Q{q_idx+1}",
                        "Latency (s)": "N/A",
                        "Answer": f"INIT ERROR: {str(e)}".replace("|", "\\|"),
                        "Status": "Failed"
                })
                
    # Generate Markdown Report
    report_path = os.path.join(os.path.dirname(__file__), "../../docs/30 - Research & Experiments/A_B_Test_Results.md")
    report_path = os.path.abspath(report_path)
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# RAG Agent A/B Test Results\n\n")
        f.write("This document contains automated evaluation results comparing different LLM orchestrations.\n\n")
        
        f.write("## Test Questions\n")
        for i, q in enumerate(questions):
            f.write(f"{i+1}. {q}\n")
        f.write("\n")
        
        f.write("## Evaluation Matrix\n\n")
        f.write("| Agent | Question | Latency | Status | Answer Snippet |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- |\n")
        
        for r in results:
            snippet = r['Answer'][:200] + ("..." if len(r['Answer']) > 200 else "")
            f.write(f"| {r['Agent']} | {r['Question']} | {r['Latency (s)']}s | {r['Status']} | {snippet} |\n")
            
    print(f"\n[*] Evaluation complete. Report generated at {report_path}")

if __name__ == "__main__":
    run_evaluation()
