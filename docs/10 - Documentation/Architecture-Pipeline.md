# 🏗️ Arsitektur & Pipeline Data

Proyek ini menggunakan pendekatan **Extract, Transform, Load (ETL)** yang dimodifikasi untuk kebutuhan riset AI, ditambah tahap **Indexing** untuk mendukung RAG.

## 🔄 Alur Data (Data Flow)

### 1. Extraction (Raw Layer)
Data diambil dari berbagai sumber otoritatif menggunakan teknik yang berbeda:
- **Web Crawling**: Menggunakan `BeautifulSoup` (Scrapy-style spiders) untuk situs seperti *Katolisitas.org*, *Mirifica.net*, dan *PapalEncyclicals.net*.
- **Local Files**: Mengolah file mentah seperti `alkitab-tb.json`.
- **PDF Extraction**: Menggunakan `pdfplumber` untuk mengekstrak teks dari Seri Dokumen Gerejawi KWI.

### 2. Processing (Processed Layer)
Langkah ini fokus pada pembersihan dan standarisasi awal:
- **Cleaning**: Menghapus noise navigasi web, iklan, dan format PDF yang rusak.
- **Normalizing**: Konversi encoding karakter yang aneh menjadi UTF-8 bersih.
- **Title Intelligence**: Menghasilkan judul deskriptif secara otomatis untuk ayat Alkitab, nomor kanon, dan halaman PDF.

### 3. Consolidation (Final Layer)
Menyatukan semua data ke dalam **Unified Schema** di folder `data/final/` dalam format `.jsonl`.

### 4. Indexing (Vector Layer)
Tahap akhir untuk membuat data dapat dicari secara semantik oleh AI:
- **Local Multilingual Embeddings**: Menggunakan model `paraphrase-multilingual-MiniLM-L12-v2` dari HuggingFace (Gratis & No Rate Limit).
- **Vector Store**: Menggunakan **FAISS** untuk penyimpanan index lokal yang efisien.
- **Project Knowledge**: Menggabungkan file `.md` dari Obsidian vault sebagai konteks tambahan.

## 📋 Unified Schema (Format Final)
```json
{
  "title": "Judul spesifik",
  "content": "Isi teks bersih",
  "url": "Link sumber",
  "source": "Label sumber",
  "language": "id / en",
  "metadata": { ... }
}
```

## 🛠️ Tooling & Stack
- **Python 3.14+**: Core language.
- **LangChain & FAISS**: RAG & Vector database.
- **HuggingFace**: Embedding models.
- **pdfplumber**: Ekstraksi PDF.
- **Obsidian**: Knowledge Base & Documentation.
