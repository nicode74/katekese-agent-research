import json
import re
import os
from pathlib import Path
from typing import List, Dict, Optional

class DataCleaner:
    def __init__(self):
        # Noise patterns for different sources
        self.noise_patterns = {
            "imankatolik": [
                r"Benedictus XVI Fransiskus Ensiklik & Surat Paus.*?Honorius III",
                r"Dokumen KV 2 Pilih Dokumen.*?Unitatis Redintegratio",
                r"Ethics in Communications",
                r"No: masukkan no\.\s*yang dikehedaki - 0 \(nol\) untuk melihat daftar isi",
                r"-\(catatan kaki lihat versi Cetak\)",
                r"Kitab Hukum Kanonik CODE OF CANON LAW Kitab Hukum Kanonik www\.imankatolik\.or\.id",
                r"Cari Kata dalam Kitab Hukum Kanonik www\.imankatolik\.or\.id",
                r"Nomor:\s*masukkan no\.\s*kanon.*?untuk menunjukkan no\.\s*kanon",
                r",\s*\(?\s*\d+,\s*\d+\s*/\s*\d+-\d+\s*\)?\s*SEJARAH PAUS.*?Yohanes Paulus II",
                r",\s*misalnya\s*\d+,\s*\d+\s*atau\s*\d+-\d+\s*Kata:\s*masukkan kata yang akan dicari",
                r"masukkan no\..*?dikehendaki",
                r"masukkan kata yang akan dicari",
                r"<<", r">>",
            ],
            "kwi": [
                r"Download\s+eBook\s+SDG.*?\n",
                r"Beli\s+Buku\s+SDG.*?\n",
                r"Harga\s+Rp.*?\n",
                r"Tebal\s+Buku.*?\n",
                r"Ukuran\s+Buku.*?\n",
                r"Penerjemah:.*?\n",
                r"Tanggal\s+Terbit.*?\n",
                r"Deskripsi.*?\n",
                r"Judul\s+Buku:.*?\n",
                r"Stok:.*?\n",
                r"Pemesanan:.*?\n",
                r"Konferensi\s+Waligereja\s+Indonesia\s+\(KWI\).*?\n",
                r"Departemen\s+Dokumentasi\s+dan\s+Penerangan.*?\n",
                r"Jalan\s+Cikini.*?E-mail:.*?\n",
            ],
            "papal": [
                r"Post\s+Navigation.*?Next\s+Post",
                r"This\s+entry\s+was\s+posted\s+in.*?\.",
                r"Select\s+Pope.*?List\s+all\s+available",
                r"Kindle,\s+Nook,\s+EPUB",
            ],
            "hidup": [
                r"Baca\s+Juga:.*?\n",
                r"Silakan\s+baca\s+selengkapnya.*?\n",
                r"Dapatkan\s+informasi\s+terupdate.*?\n",
                r"Klik\s+di\s+sini.*?\n",
                r"Sumber:.*?\n",
            ],
            "komkat": [
                r"SEKRETARIAT\s+KOMISI\s+KATEKETIK\s+KWI.*?\n",
                r"Jl\.\s+Cut\s+Meutia.*?\n",
                r"Telephone:.*?Fax:.*?\n",
                r"Copyright.*?Konfrensi\s+Wali\s+Gereja\s+Indonesia",
                r"Baca\s+Selengkapnya\.\.\.",
            ],
            "lbi": [
                r"Lembaga\s+Biblika\s+Indonesia\s+\(LBI\).*?\n",
                r"Contact\s+us:.*?\n",
                r"&copy;.*?LBI\.or\.id",
                r"Theme:\s+Newspaper\s+by\s+tagDiv\.com",
            ]
        }

    def clean_text(self, text: str, source_type: str = "general") -> str:
        if not text: return ""
        
        # 1. Handle common encoding mess (like â€œ for quotes)
        # This often happens when reading UTF-8 as Latin-1 or similar
        # We can try to fix some common ones manually or just normalize
        text = text.replace('â€œ', '"').replace('â€\x9d', '"').replace('â€\x99', "'")
        text = text.replace('â€\x94', '--').replace('â€”', '--').replace('â€¦', '...')
        
        # 2. Source-specific noise
        patterns = self.noise_patterns.get(source_type, [])
        # Also apply imankatolik patterns to general as they are common web noise
        if source_type == "general":
            patterns = self.noise_patterns["imankatolik"]

        for pattern in patterns:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.DOTALL)
        
        # 3. Standardize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()

    def process_file(self, input_path: str, output_path: str, source_type: str):
        if not os.path.exists(input_path): return
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        count = 0
        with open(input_path, 'r', encoding='utf-8') as fin, \
             open(output_path, 'w', encoding='utf-8') as fout:
            for line in fin:
                try:
                    data = json.loads(line)
                    data['content'] = self.clean_text(data.get('content', ''), source_type)
                    if data['content']:
                        fout.write(json.dumps(data, ensure_ascii=False) + '\n')
                        count += 1
                except: continue
        print(f"[*] Cleaned {count} rows from {os.path.basename(input_path)}")

if __name__ == "__main__":
    cleaner = DataCleaner()
    
    # Define tasks: (input, output, type)
    tasks = [
        ('data/raw/kwi/kwi_articles.jsonl', 'data/processed/kwi/kwi_articles_clean.jsonl', 'kwi'),
        ('data/raw/papal_encyclicals/papal_docs.jsonl', 'data/processed/papal/papal_docs_clean.jsonl', 'papal'),
        ('data/raw/mirifica/mirifica_articles.jsonl', 'data/processed/mirifica/mirifica_articles_clean.jsonl', 'kwi'),
        ('data/raw/hidup/hidup_kekatolikan.jsonl', 'data/processed/hidup/hidup_kekatolikan_clean.jsonl', 'hidup'),
        ('data/raw/hidup/hidup_katekese.jsonl', 'data/processed/hidup/hidup_katekese_clean.jsonl', 'hidup'),
        ('data/raw/komkat/komkat_artikel.jsonl', 'data/processed/komkat/komkat_artikel_clean.jsonl', 'komkat'),
        ('data/raw/lbi/lbi_berita-artikel.jsonl', 'data/processed/lbi/lbi_berita-artikel_clean.jsonl', 'lbi'),
        ('data/raw/lbi/lbi_inspirasi-pagi.jsonl', 'data/processed/lbi/lbi_inspirasi-pagi_clean.jsonl', 'lbi'),
    ]
    
    for inp, out, t in tasks:
        cleaner.process_file(inp, out, t)
