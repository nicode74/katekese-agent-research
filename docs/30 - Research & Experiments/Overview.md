# 🧪 Riset & Eksperimen

Folder ini digunakan untuk mencatat hasil uji coba model, prompt, dan evaluasi sistem RAG.

## 🔬 Eksperimen Aktif
- **[2026-05-04] LLM Selection Strategy**: Dokumentasi pemilihan strategi [[LLM_Selection|Hybrid LLM (Llama 3 & Gemini)]].
- **[2026-05-04] Bias & Ethics Framework**: Kerangka pengujian [[Bias_Evaluation|Red Teaming dan Evaluasi Bias]].
- **[2026-04-25] Embedding Benchmark**: Membandingkan akurasi pencarian antara Gemini Embedding dan Multilingual-E5.
- **[WIP] Prompt System Instruction**: Menyusun instruksi agar Agent selalu merujuk pada Katekismus.

## 📈 Evaluasi
- [[RAG-Accuracy-Log|Log Akurasi]]: Catatan seberapa tepat jawaban Agent terhadap pertanyaan user.
- **RAGAS Framework**: Evaluasi otomatis menggunakan metrik *Faithfulness* dan *Relevance* (Lihat `notebooks/03_RAG_Evaluation.ipynb`).
- **Synthetic Q&A**: Pembuatan dataset ground truth otomatis (Lihat `notebooks/02_QA_Generation.ipynb`).
- **EDA**: Analisis statistik dataset awal (Lihat `notebooks/01_EDA.ipynb`).
