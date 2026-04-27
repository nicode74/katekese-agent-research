import json
import re
import os
from pathlib import Path
from typing import List, Dict, Any

class DataConsolidator:
    def __init__(self, output_dir: str = "data/final"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Noise patterns (from cleaner.py but consolidated)
        self.general_noise = [
            r"Download\s+eBook.*?\n",
            r"Beli\s+Buku.*?\n",
            r"Harga\s+Rp.*?\n",
            r"Tebal\s+Buku.*?\n",
            r"Ukuran\s+Buku.*?\n",
            r"Penerjemah:.*?\n",
            r"Tanggal\s+Terbit.*?\n",
            r"Deskripsi.*?\n",
            r"Stok:.*?\n",
            r"Pemesanan:.*?\n",
            r"Select\s+Pope.*?List\s+all\s+available",
            r"Kindle,\s+Nook,\s+EPUB",
            r"<<", r">>",
        ]

    def clean_text(self, text: str) -> str:
        if not text: return ""
        # Fix encoding artifacts
        text = text.replace('â€œ', '"').replace('â€\x9d', '"').replace('â€\x99', "'")
        text = text.replace('â€\x94', '--').replace('â€”', '--').replace('â€¦', '...')
        text = text.replace('Ã­', 'i').replace('Ì„', '').replace(' chaÃ­roÌ„ ', ' chairo ') # Specific Katolisitas artifacts
        
        for pattern in self.general_noise:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.DOTALL)
            
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def normalize_entry(self, data: Dict, source_name: str, default_lang: str = "id") -> Dict:
        """Ensure every entry has title, content, url, source, and language."""
        content = self.clean_text(data.get('content', ''))
        
        # IMPROVED TITLE LOGIC
        title = data.get('title')
        if not title or title == "No Title":
            if source_name == "khk":
                idx = data.get('index') or data.get('metadata', {}).get('index', '?')
                title = f"KHK Kanon {idx}"
            elif source_name == "kkgk" or source_name == "katekismus":
                idx = data.get('id') or data.get('metadata', {}).get('id', '?')
                title = f"Katekismus No {idx}"
            elif source_name == "papal_encyclicals":
                # Try to get title from URL or content
                url_part = data.get('url', '').split('/')[-1].replace('.htm', '').replace('-', ' ').title()
                title = url_part if url_part else "Papal Document"
            else:
                title = source_name.replace('_', ' ').title()

        return {
            "title": title,
            "content": content,
            "url": data.get('url', ''),
            "source": data.get('source') or source_name,
            "language": data.get('language') or default_lang,
            "metadata": {k: v for k, v in data.items() if k not in ['title', 'content', 'url', 'source', 'language']}
        }

    def process_file(self, input_path: Path, source_name: str, lang: str = "id"):
        if not input_path.exists():
            print(f"[!] Skip: {input_path} not found.")
            return

        output_file = self.output_dir / f"{source_name}_final.jsonl"
        print(f"[*] Processing {input_path.name} -> {output_file.name}")
        
        # For PDFs, we want to find a consistent title from the first page
        global_title = None
        if source_name.startswith("pdf_"):
            try:
                with open(input_path, 'r', encoding='utf-8') as f:
                    first_line = f.readline()
                    if first_line:
                        first_data = json.loads(first_line)
                        content = first_data.get('content', '')
                        # Take first 5-10 words or first line of first page
                        if content:
                            title_match = content.split('\n')[0].strip()
                            # If it's too long, truncate it
                            if len(title_match) > 100:
                                title_match = " ".join(title_match.split()[:10]) + "..."
                            global_title = title_match
            except: pass
            
            # Fallback to cleaned filename if global_title is still bad/short
            if not global_title or len(global_title) < 3:
                global_title = source_name.replace("pdf_", "").replace("_", " ").replace("-", " ").title()

        count = 0
        with open(input_path, 'r', encoding='utf-8') as fin, \
             open(output_file, 'w', encoding='utf-8') as fout:
            for line in fin:
                try:
                    data = json.loads(line)
                    # Use global_title if we found one
                    if global_title and (not data.get('title') or data.get('title') == "No Title"):
                        data['title'] = global_title
                        
                    normalized = self.normalize_entry(data, source_name, lang)
                    if normalized['content']:
                        fout.write(json.dumps(normalized, ensure_ascii=False) + '\n')
                        count += 1
                except: continue
        print(f"    [OK] Consolidated {count} rows.")

    def process_alkitab(self):
        """Special handling for Alkitab TB (JSON) and Deuterokanonika (JSONL)."""
        alkitab_final = self.output_dir / "alkitab_final.jsonl"
        print(f"[*] Processing Alkitab collection -> {alkitab_final.name}")
        
        count = 0
        with open(alkitab_final, 'w', encoding='utf-8') as fout:
            # 1. Main Alkitab TB
            tb_path = Path("data/raw/alkitab/alkitab-tb.json")
            if tb_path.exists():
                with open(tb_path, 'r', encoding='utf-8') as f:
                    tb_data = json.load(f)
                    for book in tb_data:
                        book_name = book.get('book', 'Unknown')
                        for chapter in book.get('chapters', []):
                            chap_num = chapter.get('chapter', 0)
                            for verse in chapter.get('verses', []):
                                # Skip non-content verses (like section headers)
                                if verse.get('type') != 'content':
                                    continue
                                    
                                entry = {
                                    "title": f"{book_name} {chap_num}:{verse.get('verse')}",
                                    "content": verse.get('content', ''),
                                    "url": f"bible://tb/{book_name}/{chap_num}/{verse.get('verse')}",
                                    "source": "Alkitab TB",
                                    "language": "id",
                                    "metadata": {"book": book_name, "chapter": chap_num, "verse": verse.get('verse')}
                                }
                                fout.write(json.dumps(entry, ensure_ascii=False) + '\n')
                                count += 1

            # 2. Deuterokanonika
            deut_dir = Path("data/processed/alkitab")
            for df in deut_dir.glob("*.jsonl"):
                with open(df, 'r', encoding='utf-8') as f:
                    for line in f:
                        data = json.loads(line)
                        book_name = data.get('book') or data.get('title', 'Unknown')
                        entry = {
                            "title": f"{book_name} {data.get('chapter')}:{data.get('verse')}",
                            "content": data.get('verse_text', ''),
                            "url": f"bible://deut/{book_name}/{data.get('chapter')}/{data.get('verse')}",
                            "source": "Deuterokanonika",
                            "language": "id",
                            "metadata": data
                        }
                        fout.write(json.dumps(entry, ensure_ascii=False) + '\n')
                        count += 1
        print(f"    [OK] Consolidated {count} Alkitab rows.")

if __name__ == "__main__":
    con = DataConsolidator()
    
    # 1. Alkitab
    con.process_alkitab()
    
    # 2. Katekismus & Laws
    con.process_file(Path("data/processed/katekese/khk_clean.jsonl"), "khk")
    con.process_file(Path("data/processed/katekese/kkgk_clean.jsonl"), "kkgk")
    con.process_file(Path("data/processed/katekese/katekese_final_clean.jsonl"), "katekismus")
    
    # 3. KWI & Mirifica
    con.process_file(Path("data/raw/kwi/kwi_articles.jsonl"), "kwi")
    con.process_file(Path("data/raw/mirifica/mirifica_articles.jsonl"), "mirifica")
    
    # 4. Katolisitas & EKatolik
    con.process_file(Path("data/raw/katolisitas/katolisitas_articles.jsonl"), "katolisitas")
    con.process_file(Path("data/raw/ekatolik/ekatolik_prayers.jsonl"), "ekatolik")
    
    # 5. Papal (English)
    con.process_file(Path("data/raw/papal_encyclicals/papal_docs.jsonl"), "papal_encyclicals", lang="en")
    
    # 6. Processed PDFs
    kwi_pdf_dir = Path("data/processed/kwi/pdfs")
    if kwi_pdf_dir.exists():
        for pdf_jsonl in kwi_pdf_dir.glob("*.jsonl"):
            con.process_file(pdf_jsonl, f"pdf_{pdf_jsonl.stem}")
