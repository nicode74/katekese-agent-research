# Katekese Agent Research

Project penelitian untuk membangun basis data katekese Katolik yang komprehensif sebagai fondasi sistem **RAG (Retrieval-Augmented Generation)**. Proyek ini mencakup otomatisasi crawling, ekstraksi PDF, pembersihan data, dan konsolidasi ribuan dokumen Gereja.

## 📊 Statistik Dataset (data/final/)
Total dataset saat ini mencakup **~35,000+ baris data** yang telah dibersihkan dan disatukan (unified):

| Kategori | Cakupan Data | Jumlah Baris |
| :--- | :--- | :--- |
| **Kitab Suci** | Alkitab TB & Deuterokanonika (per ayat) | 29,436 |
| **Hukum Gereja** | Kitab Hukum Kanonik (KHK) lengkap | 1,752 |
| **Katekismus** | KKGK & Katekismus Dasar | 1,597 |
| **Dokumen Paus** | Ensiklik & Surat Apostolik (English) | 1,407 |
| **Media & Artikel** | Katolisitas.org & Mirifica.net | 109 |
| **Transkrip PDF** | Seri Dokumen Gerejawi KWI (per halaman) | 1,500+ |

## 🏗️ Arsitektur Proyek
```text
katekese-agent-research/
├── data/
│   ├── raw/          # Data mentah hasil crawling/download
│   ├── processed/    # Data hasil ekstraksi PDF & pembersihan awal
│   └── final/        # Dataset final siap indexing (Unified Schema)
├── src/
│   ├── crawler/      # Spider untuk KWI, Papal Encyclicals, Katolisitas, dll.
│   ├── processors/   # Logic pembersihan, ekstraksi PDF, & konsolidasi
│   └── agents/       # [WIP] Implementasi RAG Agent
├── notebooks/        # Eksperimen data & analisis
└── README.md
```

## 🛠️ Pipeline Data
1.  **Discovery & Research:** Pemetaan sumber data otoritatif (Vatikan, KWI, Katolisitas).
2.  **Automated Crawling:** Spider berbasis Python (BeautifulSoup) untuk ekstraksi artikel secara masif.
3.  **PDF Intelligence:** Ekstraksi teks dari dokumen pindaian (OCR-ready) menggunakan `pdfplumber`.
4.  **Data Refinement:**
    *   Normalisasi karakter & encoding (UTF-8).
    *   Penghapusan noise web (navigasi, harga buku, iklan).
    *   Generasi judul otomatis berbasis metadata & content-first-line.
5.  **Consolidation:** Penyatuan seluruh sumber ke dalam satu format `.jsonl` dengan skema yang konsisten.

## 📋 Skema Data (Unified Schema)
Setiap entri di folder `data/final/` memiliki struktur:
```json
{
  "title": "Judul Dokumen / Ayat",
  "content": "Isi teks bersih",
  "url": "Sumber original (jika ada)",
  "source": "Nama sumber (misal: Alkitab TB)",
  "language": "id / en",
  "metadata": { ... data tambahan ... }
}
```

## 🚀 Cara Menjalankan
1.  **Setup Environment:**
    ```bash
    python -m venv venv
    source venv/Scripts/activate
    pip install -r requirements.txt
    ```
2.  **Crawl Data:**
    ```bash
    python src/crawler/kwi_spider.py
    python src/crawler/katolisitas_spider.py
    ```
3.  **Proses & Konsolidasi:**
    ```bash
    python src/processors/pdf_processor.py
    python src/processors/consolidator.py
    ```

---
*Proyek ini dikembangkan untuk mempermudah umat dan peneliti dalam mengakses ajaran resmi Gereja Katolik melalui bantuan AI.*
