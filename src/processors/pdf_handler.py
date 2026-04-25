import pdfplumber
import json
import os
from typing import Dict

class KWIParser:
    def __init__(self, output_dir: str = "data/processed/"):
        self.output_dir = output_dir

    def extract_pdf(self, file_path: str):
        file_name = os.path.basename(file_path)
        print(f"[*] Parsing: {file_name}")
        
        extracted_data = []
        
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                # Kita ambil teks per halaman
                text = page.extract_text()
                
                if text:
                    entry = {
                        "content": text.strip(),
                        "metadata": {
                            "source": file_name,
                            "page": i + 1,
                            "type": "Dokumen KWI",
                            "category": "Pastoral/Ensiklik"
                        }
                    }
                    extracted_data.append(entry)
        
        return extracted_data

# Cara pakainya (Logic testing)
# parser = KWIParser()
# result = parser.extract_pdf("data/raw/kwi/surat_gembala_2024.pdf")