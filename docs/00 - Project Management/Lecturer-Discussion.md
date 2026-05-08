# 🎓 Agenda Diskusi dengan Dosen/Pembimbing

Dokumen ini berisi poin-poin penting yang perlu dikonsultasikan terkait keberlanjutan proyek **Katekese RAG Agent**.

## ⚖️ 1. Hak Cipta & Distribusi Data (Prioritas Utama)
Sebelum mempublikasikan dataset atau aplikasi, poin ini harus jelas:
- **Redistribusi Alkitab TB:** Apakah kita memiliki izin atau batasan dalam menyimpan teks Alkitab TB (milik LAI) dalam database publik/Kaggle?
- **Dokumen KWI:** Sejauh mana kita diizinkan menyebarkan transkrip teks dari *Seri Dokumen Gerejawi* yang telah kita ekstrak dari PDF.
- **Kaggle Upload:** Rekomendasi teknis adalah **Private Dataset**. Perlu konfirmasi apakah dosen setuju jika data ini diunggah sebagai *Public Dataset* untuk komunitas NLP.

## 🏗️ 2. Arsitektur Teknis
Laporkan perubahan strategi yang kita lakukan:
- **Local Embeddings:** Jelaskan alasan kita pindah dari *Google API* ke **HuggingFace Local** (`paraphrase-multilingual-MiniLM-L12-v2`) untuk menghindari biaya dan limit kuota.
- **FAISS vs Cloud DB:** Saat ini kita menggunakan database lokal (FAISS). Tanyakan apakah ada kebutuhan untuk pindah ke Cloud Vector DB (seperti Pinecone atau MongoDB Atlas) untuk skala website yang lebih besar.

## 🚀 3. Implementasi di Website Gereja
- **User Access:** Siapa saja yang boleh mengakses RAG Agent ini? Apakah hanya pengajar (lecturer) atau seluruh umat?
- **Fitur Sitasi:** Tunjukkan bahwa agent kita sudah memiliki sistem referensi `[1]`, `[2]`. Tanyakan apakah dosen memerlukan format sitasi tertentu (misal: gaya APA atau format dokumen gerejawi standar).

## 📊 4. Cakupan Data
- Kita sudah memiliki **35.000+ baris data**. Apakah dosen menyarankan sumber tambahan lain? (Misalnya: Dokumen Sinode lokal atau Buku Doa tertentu).

---
## ✅ 5. Update Feedback Dosen (Mei 2026)
Poin-poin berikut telah diimplementasikan dalam struktur riset:
- **EDA (Exploratory Data Analysis):** Notebook `01_EDA.ipynb` telah dibuat untuk menganalisis distribusi teks dan chunk data.
- **Evaluasi Model (With & Without RAG):** Menggunakan framework **RAGAS** untuk mengukur *Faithfulness* dan *Relevance* pada model Llama 3 dan Gemini.
- **Unit Testing:** Implementasi *whitebox* (retriever/chunker) dan *blackbox* (API testing) di folder `test/`.
- **Pemilihan LLM:** Dokumentasi strategi **Hybrid LLM** (Llama 3 Local & Gemini Cloud) telah disusun untuk membandingkan performa.
- **Bias & Etika:** Kerangka pengujian bias dan *theological alignment* telah disiapkan.

---
*Catatan: Segera perbarui dokumen ini setelah mendapatkan feedback dari pembimbing.*
