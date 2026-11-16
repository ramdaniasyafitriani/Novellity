# DOKUMENTASI DELIVERABLE SPRINT & JOBDESC
## Proyek: Website Rekomendasi Topik / Judul Artikel Ilmiah
**Mata Kuliah**: Manajemen Proyek TI (ManPro) - Semester 5  
**Pengembang**: Heyden Alya Syailendra  
**Peran**: Prompt Engineer & API / Back-End Developer  

---

## 1. Ringkasan Tugas & Pemenuhan Persyaratan (Jobdesc Mapping)

| Kode SRS | Deskripsi Kebutuhan | Status Implementasi | Modul Terkait |
| :--- | :--- | :---: | :--- |
| **FR-01 & FR-02** | Validasi berkas upload wajib PDF | **Selesai** | `main.py` (`/api/validate-files` & `/api/analyze`) |
| **FR-03** | Pembatasan beban (Maks 10 PDF, Akumulasi maks 15 MB) | **Selesai** | `main.py` (Kalkulasi ukuran byte streaming & count check) |
| **FR-04** | Pemrosesan Data: Ekstraksi dan sanitasi teks PDF | **Selesai** | `text_extractor.py` (pypdf text extraction & cleaning) |
| **FR-05** | Integrasi Google Gemini API 1.5 Flash | **Selesai** | `main.py` & Google GenAI SDK |
| **FR-06** | JSON Schema Enforcement (Structured Output) | **Selesai** | `schemas.py` & Gemini `response_schema` |
| **FR-07** | Kontrak data terstruktur untuk penampil hasil Front-End | **Selesai** | `schemas.py` (`AnalysisResponse`) & `/api/schema` |
| **NFR-01** | Response time efisien (15 - 30 detik) | **Selesai** | Async I/O, optimized payload, low temperature |
| **NFR-02** | Stateless Session & Privasi data (Hapus file pasca-analisis) | **Selesai** | `tempfile` isolasi dan auto-deletion di blok `finally` |

---

## 2. Arsitektur Pertukaran Data Server (Back-End Architecture)

Sistem backend dibangun menggunakan **FastAPI** dengan arsitektur modular:

```text
[ Frontend (React + Vite) ]
          │
          │ 1. Multipart Form-Data (1-10 PDFs, <= 15MB)
          ▼
┌────────────────────────────────────────────────────────┐
│                   FASTAPI BACKEND                      │
│                                                        │
│  [ Router & Middleware ]                               │
│  ├── CORS Middleware (Open to FE)                      │
│  ├── /api/validate-files  (Pre-flight check)           │
│  ├── /api/schema          (Schema introspection)       │
│  └── /api/analyze         (Main Analysis Pipeline)     │
│                                                        │
│  [ Data Processing & Extraction ]                      │
│  ├── Validation Guard (Size & Extension)               │
│  ├── text_extractor.py (Pembersihan Header/Footer)     │
│  └── Stateless Tempdir Management                      │
└────────────────────────────────────────────────────────┘
          │
          │ 2. Text / Multimodal Payload + Structured Output Config
          ▼
┌────────────────────────────────────────────────────────┐
│             GOOGLE GEMINI 1.5 FLASH API                │
│                                                        │
│  ├── System Instruction (prompts.py)                   │
│  │   ├── Cross-Paper Comparative Synthesis             │
│  │   ├── 4-Dimensional Research Gap Framework          │
│  │   └── Standardized Academic Title Formula           │
│  └── Response Schema Enforcement (schemas.py)          │
└────────────────────────────────────────────────────────┘
          │
          │ 3. Validated JSON Object (Pydantic Model)
          ▼
[ Frontend Dashboard ] (Render Hasil Rekomendasi)
```

---

## 3. Desain Prompt Engineering (Framework Analisis Kritis)

Prompt dirancang untuk mengatasi kecenderungan LLM yang sering kali hanya memberikan kesimpulan dangkal (*shallow summarization*). Sistem prompt memandu LLM menggunakan **4 Dimensi Analisis Research Gap**:

1. **Celah Metodologis (Methodological Gap)**:
   - Menemukan kelemahan algoritma, tingginya latensi komputasi, atau ketidakmampuan beroperasi di perangkat terbatas (*edge/mobile*).
2. **Celah Data & Domain (Empirical & Domain Gap)**:
   - Mengidentifikasi batasan dataset yang hanya bersumber dari benchmark standar luar negeri dan belum diuji pada dataset lokal Indonesia.
3. **Celah Evaluasi & Validasi (Evaluation Gap)**:
   - Mengkritisi pengujian yang hanya berfokus pada metrik tunggal (seperti akurasi) tanpa mengevaluasi *explainability*, *fairness*, atau *robustness*.
4. **Celah Penerapan Nyata (Deployment Gap)**:
   - Memetakan kendala transisi dari model eksperimen laboratorium menuju sistem produksi dunia nyata.

### Formula Judul yang Dituntut ke AI:
`[Inovasi Metode / Modifikasi Pendekatan] + [pada Masalah/Objek Spesifik] + [Studi Kasus / Domain Penerapan]`

---

## 4. Format Kontrak Data JSON (Output Schema)

Front-End akan selalu menerima respon dengan format pasti berikut:

```json
{
  "ringkasan_sintesis": "Paragraf deskriptif mendalam mengenai sintesis lintas artikel...",
  "telaah_paper": [
    {
      "nama_dokumen": "jurnal_1.pdf",
      "fokus_utama": "Klasifikasi citra menggunakan CNN konvensional...",
      "keterbatasan_diakui": "Ukuran model besar dan membutuhkan daya komputasi tinggi..."
    }
  ],
  "research_gaps": [
    {
      "aspek": "Metodologis",
      "deskripsi": "Kurangnya optimasi model untuk inferensi real-time pada mobile device...",
      "tingkat_urgensi": "Tinggi",
      "alasan_urgensi": "Banyak aplikasi praktis membutuhkan inferensi on-device tanpa ketergantungan internet."
    }
  ],
  "rekomendasi_judul": [
    {
      "judul": "Kompresi Model MobileNetV3 Menggunakan Knowledge Distillation untuk Deteksi Penyakit Daun Padi pada Perangkat Edge",
      "novelty": "Menggabungkan arsitektur lightweight dengan distillation khusus fitur lokal, meningkatkan FPS sebesar 40% tanpa mengorbankan akurasi.",
      "rumusan_masalah_utama": "Bagaimana merancang pipeline kompresi yang menjaga akurasi deteksi pada perangkat edge berdaya rendah?",
      "metodologi_usulan": "Knowledge distillation dari teacher ResNet-50 ke student MobileNetV3 dengan quantisasi INT8.",
      "kontribusi_dan_dampak": "Solusi praktis offline bagi petani lokal tanpa koneksi internet stabil."
    }
  ]
}
```

---

## 5. Cara Menjalankan & Menguji

```bash
# 1. Pindah ke direktori backend
cd "E:\0 UMY\KULIAH TI\SEM 5\ManPro\website-rekomendasi-topik\app\backend"

# 2. Install dependensi
pip install -r requirements.txt

# 3. Jalankan server backend
python main.py

# 4. Buka dokumentasi interaktif
http://127.0.0.1:8000/docs
```
