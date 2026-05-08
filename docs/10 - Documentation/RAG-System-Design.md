# 🧠 Desain Sistem RAG

Rencana implementasi Retrieval-Augmented Generation (RAG) untuk Katekese Agent.

## 🧱 Komponen Utama

### 1. Vector Database (Indexing)
Untuk menyimpan data dalam bentuk vektor (embeddings) agar bisa dicari berdasarkan makna (semantic search).
- **Rekomendasi**: `ChromaDB` (Local) atau `Pinecone` (Cloud).
- **Strategi Chunking**:
    - Alkitab & KHK: Tetap per ayat/kanon (sudah cukup kecil).
    - Dokumen PDF: Menggunakan *Recursive Character Text Splitter* (chunk size ~1000, overlap ~200).

### 2. Embeddings Model
Model yang mengubah teks menjadi angka (vektor).
- **Pilihan**:
    - `text-embedding-004` (Google Gemini) - *Direkomendasikan karena integrasi mudah.*
    - `multilingual-e5-large` - *Sangat bagus untuk Bahasa Indonesia.*

### 3. Retrieval Strategy
Bagaimana sistem mengambil data yang relevan:
- **Semantic Search**: Mencari arti yang mirip.
- **Hybrid Search**: Kombinasi semantic search + Keyword search (BM25) untuk mencari nomor ayat/kanon yang spesifik.
- **Re-ranking**: Menggunakan model re-ranker untuk memastikan 5 hasil teratas benar-benar yang paling relevan.

### 4. LLM Agent (Generation)
Otak yang menjawab pertanyaan pengguna berdasarkan data yang diambil.
- **Model**: Gemini 1.5 Pro atau Flash.
- **Prompt Engineering**:
    - Instruksi untuk selalu menyertakan referensi (misal: "Menurut Kanon 521...").
    - Menolak menjawab jika tidak ada dalam basis data (untuk menghindari halusinasi).

## 🛠️ Rencana Implementasi (Roadmap)
1. [ ] **Setup Vector Store**: Script untuk membaca `data/final/*.jsonl` dan memasukkannya ke ChromaDB.
2. [ ] **Retrieval Testing**: Menguji pencarian dengan pertanyaan teologis sederhana.
3. [ ] **Agent Development**: Membangun chain dengan LangChain/LangGraph.
4. [ ] **Evaluation**: Menguji akurasi jawaban terhadap pakar/buku asli.

## 🔗 Integrasi Obsidian
Riset ini menggunakan Obsidian sebagai **Knowledge Base**. RAG Agent nantinya bisa:
- Membaca catatan riset di folder `docs/`.
- Menyimpan hasil tanya jawab otomatis ke dalam file markdown baru.
