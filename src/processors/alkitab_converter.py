import pandas as pd
import json
import os
from pathlib import Path

def convert_deuterokanonika(input_dir: str = "data/raw/alkitab/deuterokanonika", output_dir: str = "data/processed/alkitab"):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    excel_files = list(input_path.glob("*.xlsx"))
    print(f"[*] Found {len(excel_files)} Excel files to convert.")
    
    for excel_file in excel_files:
        print(f"  [+] Converting: {excel_file.name}")
        try:
            df = pd.read_excel(excel_file)
            
            # Common structure: book, chapter, verse, verse_text
            # We want to keep it consistent
            output_file = output_path / (excel_file.stem + ".jsonl")
            
            records = df.to_dict(orient='records')
            with open(output_file, 'w', encoding='utf-8') as f:
                for record in records:
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
            print(f"    [OK] Saved to {output_file.name}")
        except Exception as e:
            print(f"    [ERR] Failed to convert {excel_file.name}: {e}")

if __name__ == "__main__":
    convert_deuterokanonika()
