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
- [x] **Vector DB:** Pembuatan index FAISS lokal yang mendukung pencarian semantik multibahasa.
- [x] **Obsidian Awareness:** Indexer secara otomatis menyerap file `.md` di folder `docs/` sebagai konteks tambahan, memungkinkan Agent "sadar" akan catatan riset sendiri.
- [x] **Incremental Indexing:** Script `index_data.py` hanya memproses file baru atau yang berubah.

### 🏗️ Phase 4: Agent Orchestration (WIP)
- [x] **RAG Agent:** Pengembangan `src/agents/katekese_agent.py` menggunakan LangChain.
- [x] **Citation Logic:** Sistem sitasi otomatis `[1]`, `[2]` untuk menjamin akurasi rujukan teologis.
- [x] **LLM Reasoner:** Integrasi **Gemini 2.0 Flash** untuk performa cepat dan jendela konteks luas.
- [ ] **Hybrid Search:** Menggabungkan BM25 (keyword) dan Vector Search (semantic) untuk presisi rujukan ayat/kanon.
- [ ] **Evaluation:** Implementasi framework evaluasi (seperti RAGAS) untuk mengukur *faithfulness* dan *relevancy*.

---

## 🛠️ Pekerjaan Mendatang (Short-term)
1. [ ] **Hybrid Search Implementation:** Penting untuk pencarian spesifik nomor ayat/kanon.
2. [ ] **Prompt Tuning:** Optimalisasi instruksi agar Agent lebih "rendah hati" jika tidak menemukan jawaban di data.
3. [ ] **UI Integration:** Membuat bot sederhana (Telegram/CLI) untuk pengujian oleh tim internal.
