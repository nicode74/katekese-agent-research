# 📝 Progress Tracking: Katekese RAG Agent

Dokumen ini mencatat milestone teknis yang telah dicapai dalam pengembangan sistem RAG Katekese.

## 🏁 Milestone Terkini (April 2026)

### ✅ Phase 1: Data Acquisition (ETL)
- [x] **Bible Dataset:** Penyatuan Alkitab TB & Deuterokanonika (29.4k baris).
- [x] **Web Spiders:** Berhasil membangun crawler untuk `dokpenkwi.org`, `katolisitas.org`, `mirifica.net`, dan `papalencyclicals.net`.
- [x] **PDF Intelligence:** Ekstraksi teks dari 20+ dokumen utama KWI menggunakan `pdfplumber`.
- [x] **Consolidation:** Seluruh data (35k+ baris) disatukan ke `data/final/` dengan skema JSONL yang seragam.

### ✅ Phase 2: Data Cleaning & Refinement
- [x] **Noise Removal:** Penghapusan navigasi web, iklan, dan metadata harga secara otomatis.
- [x] **Encoding Fix:** Normalisasi karakter UTF-8 (menghapus artifak seperti `â€œ`).
- [x] **Smart Titles:** Implementasi logic untuk menghasilkan judul otomatis (misal: "Kejadian 1:1", "KHK Kanon 5").

### ✅ Phase 3: Indexing & Vector Store
- [x] **Local Embeddings:** Implementasi HuggingFace `paraphrase-multilingual-MiniLM-L12-v2` (Bypass rate limit & zero cost).
- [x] **Vector DB:** Pembuatan index FAISS lokal dengan **125,432 chunks**.
- [x] **Obsidian Integration:** Indexer secara otomatis menyerap file `.md` di folder `docs/` sebagai konteks tambahan.

### ✅ Phase 4: Agent Orchestration (Current)
- [x] **RAG Agent:** Pengembangan `src/agents/katekese_agent.py`.
- [x] **Citation Logic:** Sistem sitasi otomatis `[1]`, `[2]` untuk keaslian data teologis.
- [x] **LLM Reasoner:** Integrasi Gemini 2.0 Flash sebagai otak penalaran.

---

## 🛠️ Pekerjaan Mendatang (Next Steps)
1. [ ] **API Layer:** Membungkus agent ke dalam FastAPI untuk integrasi website.
2. [ ] **UI Integration:** Membuat panel referensi/sumber pada frontend website gereja.
3. [ ] **Advanced Filtering:** Filter pencarian berdasarkan kategori (misal: "Cari hanya di Hukum Kanonik").
