# 📊 Katalog Data

Dataset saat ini mencakup lebih dari 35.000 entri yang dibagi menjadi beberapa kategori utama. Seluruh data telah disatukan dalam skema seragam (Unified Schema) di folder `data/final/`.

## 📖 Kitab Suci (Alkitab)
- **Sumber**: Alkitab Terjemahan Baru (TB) & Deuterokanonika.
- **Format**: Per ayat (per-verse).
- **Status**: ✅ Lengkap (29.436 baris).
- **Fitur**: Judul otomatis `"Kitab Bab:Ayat"`.
- **File**: `alkitab_final.jsonl`

## ⚖️ Hukum Gereja (Canon Law)
- **Sumber**: Kitab Hukum Kanonik (KHK) 1983.
- **Format**: Per Kanon.
- **Status**: ✅ Lengkap (1.752 baris).
- **Fitur**: Judul otomatis `"KHK Kanon [No]"`.
- **File**: `khk_final.jsonl`

## ⛪ Katekismus & Kompendium
- **KKGK**: Kompendium Katekismus Gereja Katolik (Tanya-Jawab).
- **Katekismus Dasar**: Dokumen dasar pengajaran iman.
- **Status**: ✅ Lengkap (1.597 baris).
- **Fitur**: Judul otomatis `"Katekismus No [No]"`.
- **File**: `kkgk_final.jsonl`, `katekismus_final.jsonl`

## 📜 Dokumen Kepausan (Papal Encyclicals)
- **Sumber**: PapalEncyclicals.net.
- **Cakupan**: Dokumen dari Paus Leo XIII hingga Paus Fransiskus.
- **Bahasa**: Inggris (English).
- **Status**: ✅ Selesai (1.407 baris).
- **File**: `papal_encyclicals_final.jsonl`

## 📄 Seri Dokumen Gerejawi (KWI)
- **Sumber**: Ekstraksi PDF buku Dokumen Gerejawi KWI.
- **Cakupan**: 20+ buku (Amoris Laetitia, Gaudium et Spes, dll).
- **Format**: Per halaman (per-page) untuk menjaga konteks.
- **Status**: ✅ Selesai (1.500+ baris).
- **File**: `pdf_*_final.jsonl`

## 🌐 Artikel & Media
- **Katolisitas.org**: Tanya jawab iman, apologetik, katekese dewasa.
- **Mirifica.net**: Berita dan dokumen Departemen Dokpen KWI.
- **Status**: ✅ Selesai (226 baris).
- **File**: `katolisitas_final.jsonl`, `mirifica_final.jsonl`

## 📝 Obsidian Vault (Project Context)
- **Sumber**: Folder `docs/`.
- **Format**: File Markdown (.md).
- **Kegunaan**: Memberikan konteks internal proyek dan desain arsitektur ke RAG Agent.
- **Status**: 🔄 Terintegrasi ke Indexer.
