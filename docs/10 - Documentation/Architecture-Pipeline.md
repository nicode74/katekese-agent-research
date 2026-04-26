# 🏗️ Arsitektur & Pipeline Detail

Dokumen ini merinci langkah teknis yang diambil selama fase riset dan pembangunan data.

## 🔄 Tahapan Transformasi Data (Detail)

### 1. Ekstraksi (Crawling & Scraped)
- **Spiders WordPress**: Kami membangun crawler khusus (WP-Theme detection) untuk *Katolisitas* dan *Mirifica*. Kami menargetkan tag `h3.entry-title` dan kontainer `div.td-post-content`.
- **Papal Archive**: Melakukan ekstraksi terhadap 1,407 dokumen dari *PapalEncyclicals.net* dengan filter otomatis untuk membuang link eksternal (vatican.va).
- **Excel Converter**: Mengonversi dataset Deuterokanonika dari `.xlsx` ke `.jsonl` untuk menjaga konsistensi schema.

### 2. Intelejensi PDF (PDF-to-Text)
- Menggunakan library `pdfplumber` untuk menangani PDF berbasis teks.
- **Titling Logic**: Kami mengimplementasikan algoritma untuk membaca baris pertama pada halaman pertama setiap PDF sebagai "Global Title". Jika baris pertama tidak valid, sistem melakukan *fallback* ke pembersihan nama file (Snake-to-Title case).
- **Chunking Strategy**: PDF dipecah per-halaman untuk menjaga referensi halaman tetap akurat dalam sitasi.

### 3. Pembersihan & Normalisasi (Refinement)
- **Encoding Fix**: Menggunakan regex untuk mengganti artifak encoding (Latin-1 vs UTF-8) yang sering muncul di data Gereja lama. Contoh: `â€œ` -> `"`.
- **Schema Unification**: Seluruh sumber (20+ file) disatukan menggunakan `src/processors/consolidator.py` ke dalam skema seragam:
  - `title`, `content`, `url`, `source`, `language`, `metadata`.

### 4. Indexing (Local Vectorization)
- **Problem**: Gemini API Embedding memiliki limit (quota exhausted) untuk 35,000+ baris data.
- **Solusi**: Migrasi ke **Local Embeddings** menggunakan `sentence-transformers` dengan model `paraphrase-multilingual-MiniLM-L12-v2`.
- **Hasil**: Proses vectorization selesai dalam 55 menit tanpa biaya API dan tanpa limitasi kuota.

## 📊 Integrasi Obsidian
Indexer (`index_data.py`) menggunakan `docs_dir.rglob("*.md")` untuk memindai seluruh vault ini. Artinya, catatan riset ini juga menjadi bagian dari pengetahuan yang bisa dicari oleh AI Agent.
