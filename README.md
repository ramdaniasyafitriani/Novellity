# Proyek: Website Rekomendasi Topik / Judul Artikel Ilmiah

**Mata Kuliah**: Manajemen Proyek TI (ManPro) - Semester 5  
**Institusi**: Universitas Muhammadiyah Yogyakarta  
Sistem berbasis kecerdasan buatan (Google Gemini 1.5 Flash) untuk membantu mahasiswa tingkat akhir memetakan *research gap* dari berbagai artikel ilmiah (PDF) dan menghasilkan rekomendasi topik/judul penelitian yang orisinal.

---

## 📁 Struktur Direktori Proyek

```text
E:\0 UMY\KULIAH TI\SEM 5\ManPro\website-rekomendasi-topik/
├── docs/                                                # 📄 Dokumentasi Proyek & Referensi
│   ├── SRS-Website-Rekomendasi-Topik.md                 # Spesifikasi Kebutuhan Perangkat Lunak (SRS)
│   ├── Software Requirements Specification (SRS).pdf    # Berkas Asli SRS PDF
│   ├── Jobdesc-Heyden-Prompt-Engineering-dan-Backend-API.md # Laporan Deliverable Jobdesc Heyden
│   ├── proposal/                                        # Berkas proposal tim
│   └── referensi-jurnal/                                # Contoh paper PDF untuk uji coba
│
└── app/                                                 # 💻 Source Code Aplikasi
    ├── backend/                                         # [Bagian Heyden & Ksatrio] REST API & Prompt Engineering
    │   ├── main.py                                      # Server FastAPI, validasi file, & endpoint /api/analyze
    │   ├── prompts.py                                   # System Prompt & framework analisis 4 dimensi research gap
    │   ├── schemas.py                                   # Pydantic JSON schema enforcement (FR-06)
    │   ├── text_extractor.py                            # Ekstraksi dan sanitasi teks PDF (FR-04)
    │   ├── test_client.py                               # Skrip pengujian API upload PDF
    │   ├── requirements.txt                             # Dependensi Python
    │   └── .env.example                                 # Template API Key Gemini
    │
    └── frontend/                                        # [Bagian Rifal & Jeremy] Antarmuka React.js + Vite + Tailwind CSS
```

---

## 🚀 Panduan Menjalankan Back-End (Heyden Alyas)

### 1. Masuk ke direktori backend
```powershell
cd "E:\0 UMY\KULIAH TI\SEM 5\ManPro\website-rekomendasi-topik\app\backend"
```

### 2. Buat Virtual Environment & Install Dependensi
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Konfigurasi API Key
Salin `.env.example` menjadi `.env` lalu masukkan API Key Google Gemini Anda:
```powershell
Copy-Item .env.example .env
```
Isi nilai di dalam `.env`:
```env
GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxx
```

### 4. Jalankan Server
```powershell
python main.py
```
Server akan aktif di `http://127.0.0.1:8000`.  
Buka Swagger UI di browser: **`http://127.0.0.1:8000/docs`** untuk mencoba upload file secara interaktif!
