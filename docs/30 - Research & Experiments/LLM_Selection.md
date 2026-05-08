# 🧠 Pemilihan Model LLM (LLM Selection Methodology)

Dokumen ini menjelaskan metodologi dan rasionalisasi di balik pemilihan Large Language Model (LLM) untuk **Katekese RAG Agent**.

## 1. What: Model Apa yang Dipilih?

Dalam pengembangan sistem ini, kami mengadopsi pendekatan **Hybrid LLM** dengan mengombinasikan dua model yang memiliki karakteristik berbeda:
1. **Llama 3 (Local / Open-Source)**: Model *open-weights* dari Meta (khususnya varian 8B) yang dapat dijalankan secara lokal.
2. **Gemini API (Cloud API)**: Model *closed-source* mutakhir dari Google yang diakses melalui API.

## 2. Why: Mengapa Memilih Strategi Hybrid?

Pendekatan hybrid dipilih untuk mengevaluasi dan menyeimbangkan *trade-off* antara privasi, biaya, dan performa komputasi:

- **Alasan Penggunaan Llama 3 (Local):**
  - **Privasi Data:** Karena beberapa dokumen Gereja mungkin memiliki hak cipta, pemrosesan secara lokal memastikan tidak ada data yang dikirim ke server pihak ketiga selama *inference*.
  - **Efisiensi Biaya:** Tidak ada biaya per token, sangat menguntungkan untuk eksperimen RAG yang terus-menerus.
  - **Kemandirian Infrastruktur:** Sistem tetap berjalan meskipun tanpa akses internet atau jika API provider sedang *down*.

- **Alasan Penggunaan Gemini API (Cloud):**
  - **Pemahaman Bahasa:** Gemini memiliki performa pemahaman Bahasa Indonesia (multilingual) yang superior untuk konteks teologis dan bahasa kiasan dalam dokumen agama.
  - **Kemampuan Konteks (Context Window):** Memiliki *context window* yang sangat besar, memungkinkan sistem RAG mengirimkan jumlah *chunk* dokumen yang jauh lebih banyak sekaligus.
  - **Kecepatan Inferensi:** Waktu respons jauh lebih cepat karena tidak bergantung pada keterbatasan GPU lokal (seperti VRAM yang terbatas).

## 3. How: Bagaimana Implementasinya?

- **Routing:** Aplikasi dibangun menggunakan kerangka kerja `LangChain` dan `LangGraph`. Terdapat parameter konfigurasi (melalui file `.env`) di mana administrator dapat memilih mode operasi LLM: `local` atau `cloud`.
- **Eksekusi Llama 3:** Dijalankan secara lokal menggunakan **Ollama** atau **vLLM** sebagai backend untuk memberikan titik akhir (endpoint) yang kompatibel dengan API OpenAI lokal, atau dijalankan via `HuggingFacePipeline`.
- **Eksekusi Gemini API:** Diintegrasikan menggunakan `langchain-google-genai` dengan model `gemini-1.5-pro` atau `gemini-1.5-flash`.
- **Evaluasi Perbandingan:** Kedua model ini akan dievaluasi secara terpisah (A/B testing) pada *dataset* pertanyaan evaluasi yang sama, untuk menentukan seberapa signifikan perbedaan akurasinya.

---
*Dokumen ini dapat dilampirkan sebagai metodologi di dalam paper penelitian.*
