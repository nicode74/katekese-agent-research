# 📝 Progress Tracking: Katekese RAG Agent

Dokumen ini mencatat milestone teknis yang telah dicapai dalam pengembangan sistem RAG Katekese.

---

## 🚀 Milestone Terkini (Juli 2026): Agentic AI & Web Integration (Ecclesia-RAG v2.0)

### ✅ Phase 5: Agentic Routing, Autonomous Workflows & Website Integration
- [x] **Multi-Intent Agentic Router:** Implementasi Intent Classifier (`Llama-3.3-70b` via Groq) untuk memilah kueri secara cerdas ke dalam `DOCTRINE_RAG`, `PARISH_INFO`, dan `DIRECT`.
- [x] **Live Parish Knowledge Retrieval:** Integrasi basis data paroki Supabase (`jadwal`, `pengumuman`, `renungan`) untuk menjawab pertanyaan operasional gereja secara real-time.
- [x] **Self-RAG & Hallucination Guard:** Lapisan verifikasi mandiri untuk mengevaluasi fidelitas jawaban terhadap dokumen rujukan dan mencegah halusinasi sitasi.
- [x] **Autonomous Daily Reflection Agent:** Agen otonom (`daily_reflection_agent.py`) yang membuat renungan harian Katolik berbasis Injil menggunakan Gemini 2.5 Flash dan menyimpan otomatis ke Supabase.
- [x] **Real-Time Vector Auto-Sync Webhook:** `AutoIngestionService` (`auto_ingest.py`) untuk chunking, embedding (`all-MiniLM-L6-v2`), dan indexing warta/dokumen baru secara otomatis.
- [x] **Parish Query Analytics Agent:** Agen pengelompokan pertanyaan umat (`analytics_agent.py`) yang menyajikan insight dan rekomendasi aksi untuk dewan paroki.
- [x] **Next.js 16 Web Integration (`church-website`):**
  - **SSE Proxy API Route:** (`/api/chat`) Menyalurkan streaming teks dan event metadata dari backend FastAPI.
  - **Floating Glassmorphic Chat Widget:** Komponen UI interaktif dengan kartu rujukan sitasi dan toggle mode (Ringkas vs Mendalam).
  - **Dedicated AI Research Portal:** Halaman penuh (`/katekese-ai`) untuk riset doktrin teologi Katolik secara mendalam.
  - **Admin AI Control Dashboard:** Panel manajemen (`/admin/ai-agent`) untuk menjalankan job agen otonom dan memantau analitik.

---

## 🏁 Milestone Sebelumnya (April - Mei 2026)

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
- [x] **Local Embeddings:** Implementasi HuggingFace `sentence-transformers/all-MiniLM-L6-v2` (Bypass rate limit & zero cost).
- [x] **Vector DB & Hybrid Search:** Penyimpanan basis data pgvector Supabase dengan dukungan fungsi RPC `match_documents_hybrid`.
- [x] **Obsidian Awareness:** Indexer secara otomatis menyerap file `.md` di folder `docs/` sebagai konteks tambahan.
- [x] **Incremental Indexing:** Script `index_data.py` hanya memproses file baru atau yang berubah.

### ✅ Phase 4: Agent Orchestration & Evaluation
- [x] **Multi-Provider Architecture:** Pemisahan *Agent* menjadi skrip independen untuk A/B testing (`agent_gemini.py`, `agent_groq.py`, `agent_local_gemma.py`).
- [x] **Citation Logic:** Sistem sitasi otomatis untuk menjamin akurasi rujukan teologis.
- [x] **LLM Reasoner:** Integrasi LangChain untuk **Gemini 2.5 Flash**, **Groq (Llama 3.3)**, dan model lokal.
- [x] **Automated Evaluation:** Pembuatan skrip `evaluate_agents.py` untuk mengukur latensi dan membandingkan *output* antar model.

---

## 🚨 API Constraint Discovery & Rollback (Identified 2026-05-23)
**Finding:**
During the attempt to bypass the cross-lingual embedding degradation (documented in `Cross_Lingual_Embedding_Degradation.md`), the architecture was temporarily migrated to `GoogleGenerativeAIEmbeddings` using `gemini-embedding-001` (3072 dimensions). 
While this mathematically resolved the cross-lingual constraints and required 0MB of local RAM, a critical cloud limitation was discovered: Google's Free Tier strictly limits `embedContent` API requests to 1,000 strings per day.

**Impact:**
Because the dataset consists of 131,532 strings, it would mathematically take 131 days to complete the ingestion using the Free Tier, effectively blocking the use of this API for bulk processing.

**Resolution:**
The system was officially rolled back to the `all-MiniLM-L6-v2` local embedding model. The cross-lingual degradation is now accepted as a documented, scientific constraint of the project's free-tier infrastructure.
