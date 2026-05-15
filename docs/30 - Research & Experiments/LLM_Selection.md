# 🧠 Pemilihan Model LLM (LLM Selection Methodology)

Dokumen ini menjelaskan metodologi dan rasionalisasi di balik pemilihan Large Language Model (LLM) untuk **Katekese RAG Agent**.

## 1. What: Model Apa yang Dipilih?

Dalam pengembangan sistem ini, kami mengadopsi pendekatan **Hybrid LLM** dengan mengombinasikan dua model yang memiliki karakteristik berbeda:
1. **Gemma 4 (Local / Open-Source)**: Model *open-weights* dari Google yang dapat dijalankan secara lokal.
2. **Gemini API (Cloud API)**: Model *closed-source* mutakhir dari Google yang diakses melalui API.

## 2. Why: Mengapa Memilih Strategi Hybrid?

Pendekatan hybrid dipilih untuk mengevaluasi dan menyeimbangkan *trade-off* antara privasi, biaya, dan performa komputasi:

- **Alasan Penggunaan Gemma 4 (Local):**
  - **Privasi Data:** Karena beberapa dokumen Gereja mungkin memiliki hak cipta, pemrosesan secara lokal memastikan tidak ada data yang dikirim ke server pihak ketiga selama *inference*.
  - **Efisiensi Biaya:** Tidak ada biaya per token, sangat menguntungkan untuk eksperimen RAG yang terus-menerus.
  - **Kemandirian Infrastruktur:** Sistem tetap berjalan meskipun tanpa akses internet atau jika API provider sedang *down*.

- **Alasan Penggunaan Gemini API (Cloud):**
  - **Pemahaman Bahasa:** Gemini memiliki performa pemahaman Bahasa Indonesia (multilingual) yang superior untuk konteks teologis dan bahasa kiasan dalam dokumen agama.
  - **Kemampuan Konteks (Context Window):** Memiliki *context window* yang sangat besar, memungkinkan sistem RAG mengirimkan jumlah *chunk* dokumen yang jauh lebih banyak sekaligus.
  - **Kecepatan Inferensi:** Waktu respons jauh lebih cepat karena tidak bergantung pada keterbatasan GPU lokal (seperti VRAM yang terbatas).

## 3. How: Bagaimana Implementasinya?

- **Arsitektur Forking:** Aplikasi dibangun menggunakan kerangka kerja `LangChain`. Untuk menjamin integritas eksperimen (A/B testing) dan memastikan *dependency* yang terisolasi, agen RAG dipisahkan menjadi 3 *script* independen:
  - `agent_gemini.py`: Menggunakan `ChatGoogleGenerativeAI` (Gemini 2.0 Flash) untuk performa tingkat atas via Cloud.
  - `agent_groq.py`: Menggunakan `ChatGroq` sebagai *proxy* cloud untuk inferensi Llama 3 8B yang berkecepatan tinggi tanpa beban lokal.
  - `agent_local_gemma.py`: Menggunakan `ChatOllama` untuk Gemma 4 lokal, mengevaluasi kemampuan varian open-weights lainnya.
- **Evaluasi Otomatis:** Kami mengimplementasikan sebuah *pipeline* evaluasi (`evaluate_agents.py`) yang mengeksekusi semua agen tersebut secara berurutan menggunakan daftar pertanyaan teologis standar. *Script* ini otomatis mencatat waktu respons (latensi) dan jawaban yang dihasilkan, lalu mengompilasinya ke dalam laporan komparasi berbentuk tabel Markdown (`A_B_Test_Results.md`).

---
*Dokumen ini dapat dilampirkan sebagai metodologi di dalam paper penelitian.*
