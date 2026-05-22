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
- [x] **Multi-Provider Architecture:** Pemisahan *Agent* menjadi 4 skrip independen (`agent_gemini.py`, `agent_groq.py`, `agent_local_llama.py`, `agent_local_qwen.py`) untuk A/B testing yang bersih.
- [x] **Citation Logic:** Sistem sitasi otomatis `[1]`, `[2]` untuk menjamin akurasi rujukan teologis.
- [x] **LLM Reasoner:** Integrasi LangChain untuk **Gemini 2.0 Flash**, **Groq (Llama 3)**, dan **Ollama (Llama 3 & Qwen)**.
- [x] **Automated Evaluation:** Pembuatan skrip `evaluate_agents.py` untuk mengukur latensi dan membandingkan *output* antar model secara otomatis ke dalam format Markdown.
- [ ] **Hybrid Search:** Menggabungkan BM25 (keyword) dan Vector Search (semantic) untuk presisi rujukan ayat/kanon.
- [ ] **Deep Evaluation:** Implementasi framework RAGAS untuk mengukur metrik *faithfulness* dan *relevancy* secara komprehensif.

---

## 🛠️ Pekerjaan Mendatang (Short-term)
1. [ ] **Hybrid Search Implementation:** Penting untuk pencarian spesifik nomor ayat/kanon.
2. [ ] **Prompt Tuning:** Optimalisasi instruksi agar Agent lebih "rendah hati" jika tidak menemukan jawaban di data.
3. [ ] **UI Integration:** Membuat bot sederhana (Telegram/CLI) untuk pengujian oleh tim internal.

## 🚨 Urgent Technical Fixes (Identified 2026-05-22)
Berdasarkan hasil pengujian dan evaluasi terbaru:
- [ ] **Environment Repair:** Virtual environment lama (`.venv`, `venv`) rusak (broken symlinks). Perlu standarisasi menggunakan `venv_rag` atau pembuatan ulang secara permanen.
- [ ] **Dependency Update:** Python 3.14 memerlukan `protobuf>=5.0.0` (v7.35.0 teruji berhasil) untuk menghindari error metaclass. Perlu update `requirements.txt`.
- [ ] **Model Maintenance:** Update permanen `agent_groq.py` karena model `llama3-8b` telah decommissioned (sudah di-patch sementara ke `llama-3.3-70b-versatile`).
- [ ] **API Quota Management:** Implementasi retry logic dengan exponential backoff pada `index_data_api.py` dan `agent_gemini.py` untuk menangani limitasi Free Tier Google AI Studio (ResourceExhausted 429).
- [ ] **Missing Credentials:** Konfigurasi Supabase di `.env` masih kosong, menghalangi penggunaan remote vector search di `server.py`.
- [ ] **Ollama Setup:** Konfigurasi server Ollama lokal agar agent berbasis `Gemma` dapat dievaluasi secara konsisten.
