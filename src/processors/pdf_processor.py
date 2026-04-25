import pdfplumber
import os
import json
import re
from pathlib import Path
from typing import List, Dict, Optional

class PDFProcessor:
    def __init__(self, input_dir: str = "data/raw/kwi/pdfs", output_dir: str = "data/processed/kwi/pdfs"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        
        # Remove common PDF artifacts
        # 1. Fix broken words due to line breaks (hyphenation)
        text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
        
        # 2. Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # 3. Remove common footers/headers if possible (generic patterns)
        # Often page numbers like "Patris Corde 4"
        text = re.sub(r'Patris Corde \d+', '', text)
        text = re.sub(r'Seri Dokumen Gerejawi', '', text, flags=re.IGNORECASE)
        
        return text.strip()

    def process_all_pdfs(self):
        pdf_files = list(self.input_dir.glob("*.pdf"))
        print(f"[*] Found {len(pdf_files)} PDFs to process.")
        
        for pdf_path in pdf_files:
            print(f"  [+] Processing: {pdf_path.name}")
            output_file = self.output_dir / (pdf_path.stem + ".jsonl")
            
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    pages_data = []
                    for i, page in enumerate(pdf.pages):
                        raw_text = page.extract_text()
                        cleaned_text = self.clean_text(raw_text)
                        
                        if cleaned_text:
                            page_entry = {
                                "source": pdf_path.name,
                                "page": i + 1,
                                "content": cleaned_text
                            }
                            pages_data.append(page_entry)
                    
                    if pages_data:
                        with open(output_file, 'w', encoding='utf-8') as f:
                            for entry in pages_data:
                                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                        print(f"    [OK] Saved {len(pages_data)} pages to {output_file.name}")
                    else:
                        print(f"    [!] No text extracted from {pdf_path.name}")
                        
            except Exception as e:
                print(f"    [ERR] Failed to process {pdf_path.name}: {e}")

if __name__ == "__main__":
    processor = PDFProcessor()
    processor.process_all_pdfs()
