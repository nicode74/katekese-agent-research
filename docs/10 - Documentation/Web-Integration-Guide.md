# 🌐 Panduan Integrasi Chatbot (RAG)

Dokumen ini adalah spesifikasi teknis untuk mengintegrasikan sistem RAG Katekese ke dalam fitur chatbot website.

## 🏗️ Komponen Sistem
Sistem ini terdiri dari tiga bagian utama:
1.  **Orchestrator (The Brain):** Script Python yang menggunakan Llama 3 (Groq) dan Gemini.
2.  **API Layer (The Bridge):** Server FastAPI yang menyediakan endpoint HTTP.
3.  **Frontend Widget (The Interface):** UI Chatbot pada website gereja.

## 🔌 Spesifikasi API (FastAPI)
Website akan berkomunikasi dengan Python agent melalui endpoint berikut:

### Endpoint: `POST /v1/chat`
**Request Payload:**
```json
{
  "user_id": "lecturer_001",
  "question": "Apa kewajiban seorang Uskup dalam memelihara iman umat?"
}
```

**Response Payload (JSON):**
```json
{
  "answer": "Berdasarkan Hukum Kanonik, Uskup memiliki kewajiban untuk...",
  "citations": [
    {
      "id": 1,
      "title": "KHK Kanon 386",
      "source": "Kitab Hukum Kanonik",
      "url": "..."
    }
  ],
  "status": "success"
}
```

## 🤖 Orchestration Logic (Multi-Agent)
Proyek ini menggunakan **Model Cascading**:
1.  **Llama 3 (Researcher):** Mencari di FAISS index, melakukan *Self-Correction* jika data tidak relevan.
2.  **Gemini (Front Officer):** Menulis jawaban akhir yang empatis dan formal.

## 🛠️ Roadmap Implementasi Website
Jika Anda sedang membangun website, ikuti langkah ini:

### 1. Backend Setup
- Pastikan server Python memiliki akses ke `data/index/katekese_faiss_local`.
- Jalankan API menggunakan `uvicorn src.api.main:app`.

### 2. Frontend Chat UI
- Buat komponen Chat di website (React/Vue/HTML).
- Pastikan ada "Bibiliography" atau "Source Panel" untuk menampilkan data dari array `citations`.
- **UX Tip:** Tampilkan indikator "Sedang mencari di dokumen Gereja..." saat agent bekerja.

## 🔐 Keamanan & Biaya
- Gunakan **Local Embeddings** (HuggingFace) di server untuk menekan biaya operasional menjadi $0.
- Gunakan **Gemini 2.0 Flash** untuk performa chatbot yang cepat.
- Simpan `GOOGLE_API_KEY` dan `GROQ_API_KEY` di level server (jangan pernah taruh di frontend website).
