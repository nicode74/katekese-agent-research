import os
import json
import random
from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

# Load environment
load_dotenv()

class QAItem(BaseModel):
    question: str = Field(description="A specific question based on the text in Indonesian.")
    answer: str = Field(description="The ground truth answer derived solely from the text in Indonesian.")

def generate_dataset(data_dir="data/final", output_file="data/evaluation_dataset.json", num_samples=20):
    print(f"[*] Starting Evaluation Dataset Generation (Target: {num_samples} samples)...")
    
    data_path = Path(data_dir)
    samples = []
    files_to_sample = list(data_path.glob("*.jsonl"))

    if not files_to_sample:
        print(f"[!] No JSONL files found in {data_dir}")
        return

    for filepath in files_to_sample:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if lines:
                # Take 3 random lines from each file to get diverse topics
                sampled_lines = random.sample(lines, min(3, len(lines)))
                for line in sampled_lines:
                    try:
                        data = json.loads(line)
                        text = data.get("content", "") or data.get("text", "")
                        if len(text.split()) > 50: # Only keep substantial paragraphs
                            samples.append({"source": filepath.name, "text": text})
                    except: continue

    random.shuffle(samples)
    samples = samples[:num_samples]
    print(f"[*] Selected {len(samples)} diverse contexts.")

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.1)
    parser = JsonOutputParser(pydantic_object=QAItem)

    prompt = PromptTemplate(
        template="""Anda adalah ahli Teologi Katolik yang bertugas membuat soal evaluasi.
Berdasarkan teks berikut, buatlah SATU pasang Pertanyaan dan Jawaban yang spesifik.
Jawaban HARUS dapat ditemukan secara eksplisit di dalam teks.
Gunakan Bahasa Indonesia yang baku.

Teks Konteks:
{context}

Format Output:
{format_instructions}""",
        input_variables=["context"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    chain = prompt | llm | parser
    evaluation_data = []

    for i, sample in enumerate(samples):
        try:
            print(f"  [>] Generating Q&A {i+1}/{len(samples)}...")
            result = chain.invoke({"context": sample["text"]})
            evaluation_data.append({
                "question": result["question"],
                "ground_truth": result["answer"],
                "context": sample["text"],
                "source": sample["source"]
            })
        except Exception as e:
            print(f"  [!] Error on sample {i+1}: {e}")

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(evaluation_data, f, ensure_ascii=False, indent=2)
    
    print(f"[*] Successfully saved {len(evaluation_data)} Q&A pairs to {output_file}")

if __name__ == "__main__":
    generate_dataset()
