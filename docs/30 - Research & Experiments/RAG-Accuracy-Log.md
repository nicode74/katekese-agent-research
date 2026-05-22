# 📊 RAG Accuracy Log

Log ini mencatat hasil pengujian akurasi jawaban dari berbagai iterasi sistem RAG.

## [2026-05-22] - Initial Agent Comparison (Lite Index)

**Konteks Pengujian:**
- Menggunakan 100 chunk dari Katekismus dan dokumen kunci (Lite Index).
- Membandingkan Gemini 1.5 Flash (via Google API) dan Llama 3.3 70B (via Groq API).

### Ringkasan Hasil
| Model | Accuracy (Manual Check) | Avg Latency | Notes |
| :--- | :---: | :---: | :--- |
| Gemini 1.5 Flash | N/A | N/A | Terkendala kuota API (429 Error). |
| Llama 3.3 70B | **100% (3/3)** | 2.57s | Jawaban sangat akurat dan menyertakan sitasi yang tepat. |

### Detail Jawaban (Llama 3.3 70B)
1. **Q: Apa kewajiban seorang Uskup dalam memelihara iman umat menurut hukum gereja?**
   - **A**: "Kewajiban seorang Uskup... mempertahankan, melaksanakan, dan mengakui iman yang diturunkan dari para Rasul [1]..."
   - **Status**: ✅ Akurat.

2. **Q: Berapa jumlah sakramen dalam Gereja Katolik?**
   - **A**: "...keselamatan... dihadirkan bagi kita melalui kegiatan-kegiatan sakramental... [diuraikan berdasarkan Katekismus No 15]."
   - **Status**: ✅ Akurat.

3. **Q: Jelaskan secara singkat apa itu dosa asal berdasarkan Katekismus.**
   - **A**: "Dosa asal adalah suatu konsep teologi Katolik yang merujuk pada dosa yang dilakukan oleh manusia pertama, Adam dan Hawa..."
   - **Status**: ✅ Akurat.

---
*Kembali ke [[Overview|Daftar Riset]]*
