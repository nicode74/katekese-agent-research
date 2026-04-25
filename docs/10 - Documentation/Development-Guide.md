# 🛠️ Panduan Pengembangan

Panduan teknis untuk menjalankan pipeline data dan mengembangkan Katekese Agent.

## ⚙️ Persiapan Lingkungan
1. Pastikan Python 3.14+ terinstall.
2. Buat virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # atau venv\Scripts\activate di Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 🕷️ Menjalankan Crawler
Crawler berada di `src/crawler/`. Contoh menjalankan spider untuk Katolisitas:
```bash
python src/crawler/katolisitas_spider.py
```
*Catatan: Hasil crawler akan masuk ke `data/raw/`.*

## 📄 Memproses PDF
Jika ada file PDF baru di `data/raw/kwi/pdfs/`, jalankan processor:
```bash
python src/processors/pdf_processor.py
```
*Hasil ekstraksi teks per halaman akan masuk ke `data/processed/kwi/pdfs/`.*

## 🧹 Konsolidasi Data (Penting!)
Setelah data mentah (raw) atau data processed diperbarui, jalankan consolidator untuk memperbarui file di `data/final/`:
```bash
python src/processors/consolidator.py
```
File di `data/final/` inilah yang akan menjadi input utama untuk indexing ke Vector Database.

## 🧪 Pengujian Data
Gunakan script `debug_save.py` atau Jupyter Notebooks di folder `notebooks/` untuk melakukan inspeksi data secara cepat.

## 📜 Aturan Kontribusi
1. **Keaslian Data**: Selalu sertakan `url` atau `source` yang jelas.
2. **Pembersihan**: Pastikan teks bersih dari watermark, iklan, atau metadata sampah.
3. **Commit**: Jangan mem-push file besar (seperti PDF atau JSONL hasil crawling massal) ke Git. Gunakan `.gitignore`.
