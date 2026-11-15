# SOFTWARE REQUIREMENTS SPECIFICATION (SRS)

**Nama Proyek**: Website Rekomendasi Topik / Judul Artikel Ilmiah  
**Target Pengguna**: Mahasiswa Tingkat Akhir  
**Dokumen Referensi**: WBS, Jadwal Sprint (Jira), dan Project Charter  

---

## 1. Pendahuluan

### 1.1 Tujuan Sistem
Aplikasi berbasis web ini dirancang sebagai asisten cerdas bagi mahasiswa tingkat akhir untuk mengotomatisasi proses sintesis literatur dari berbagai artikel ilmiah. Sistem ini memetakan celah penelitian (*research gap*) yang belum terselesaikan dan merumuskan rekomendasi judul penelitian yang tajam, orisinal, dan relevan agar terhindar dari penolakan dosen pembimbing akibat kurangnya nilai kebaruan.

### 1.2 Ruang Lingkup (Scope)
Sistem berfokus pada pemrosesan teks menggunakan Large Language Model (LLM) yang diintegrasikan melalui API pihak ketiga (Google Gemini API). Batasan spesifik sistem mencakup:
- Menerima masukan berupa artikel ilmiah/jurnal **wajib berformat PDF**.
- Batas maksimal jumlah unggahan adalah **10 dokumen PDF**.
- Batas maksimal akumulasi total ukuran seluruh berkas yang diunggah adalah **15 MB**.
- Sistem menyajikan luaran dalam bentuk teks terstruktur yang berisi paragraf deskriptif *research gap* serta daftar rekomendasi judul penelitian.

---

## 2. Persyaratan Fungsional (Functional Requirements)
- **FR-01 (Modul Unggah Dokumen)**: Sistem harus menyediakan antarmuka unggah (*upload*) dengan dukungan fitur drag-and-drop untuk file PDF.
- **FR-02 (Validasi Front-End)**: Sistem harus memvalidasi format file (MIME type `application/pdf`). Sistem wajib menolak file selain PDF dan menampilkan pesan galat (*error*).
- **FR-03 (Validasi Batasan Beban)**: Sistem harus menghitung total akumulasi ukuran file sebelum proses unggah dimulai. Jika lebih dari 10 file atau total melampaui 15 MB, sistem akan mencegah proses unggah dan memunculkan peringatan.
- **FR-04 (Pemrosesan Data)**: Sistem Back-End harus mampu menerima paket PDF dari Front-End, mengekstrak teks, dan mempersiapkannya menjadi format masukan (*payload*) untuk AI.
- **FR-05 (Integrasi AI)**: Sistem Back-End harus mengirimkan teks jurnal beserta *system prompt* khusus ke endpoint Gemini API 1.5 Flash untuk analisis *research gap* dan penyusunan judul.
- **FR-06 (Format Luaran)**: Sistem Back-End harus memaksa LLM mengembalikan data dalam format JSON terstruktur (*JSON Schema Enforcement*) untuk mencegah teks basa-basi yang tidak diperlukan.
- **FR-07 (Modul Penampil Hasil)**: Sistem harus menampilkan hasil JSON dari API ke dalam antarmuka web secara rapi dan mudah dibaca oleh pengguna.

---

## 3. Persyaratan Non-Fungsional (Non-Functional Requirements)
- **NFR-01 (Performance / Response Time)**: Proses analisis AI maksimal memakan waktu 15 - 30 detik. Sistem harus menampilkan animasi loading yang komunikatif selama menunggu respons.
- **NFR-02 (Security & Privacy)**: Sesi bersifat *stateless*. File PDF yang diunggah hanya disimpan sementara di server Back-End untuk dikirim ke Gemini API, lalu **wajib langsung dihapus** setelah pemrosesan selesai agar hak cipta terjaga.
- **NFR-03 (Usability)**: Antarmuka web harus bersifat *responsive* (Desktop, Tablet, Smartphone) dan dapat diakses menggunakan browser modern.
- **NFR-04 (Cost Efficiency)**: Sistem dikonfigurasi untuk berjalan secara ekonomis menggunakan infrastruktur *free-tier* pada masa development dan pengujian (*testing*).

---

## 4. Arsitektur Sistem & Stack Teknologi
| Komponen | Teknologi yang Digunakan | Penjelasan |
| :--- | :--- | :--- |
| **Front-End** | React.js + Vite | Pustaka antarmuka pengguna berbasis komponen. Cepat saat development berkat Vite. |
| **Styling (UI)** | Tailwind CSS | Kerangka kerja CSS berbasis utilitas untuk mempercepat pembuatan desain responsif dan konsisten. |
| **Back-End** | Python (FastAPI / Flask) | Mengelola REST API, menerima PDF, menangani komunikasi API ke Google AI Studio, dan menjaga backend tetap ringan. |
| **AI / LLM** | Google Gemini API (1.5 Flash) | Dipilih karena kapabilitas *Context Window* raksasa (mampu membaca 10 PDF sekaligus), integrasi multimodal, dan performa cepat. |
| **Deployment** | Vercel / GitHub Pages (FE) & Render (BE) | Hosting cloud server gratis yang memadai untuk fase pengerjaan proyek akademis (Sprint 5). |

---

## 5. Struktur & Penugasan Tim Pengembang
- **Muhamad Irfan Al Arib** (*Project Manager*): Mengawal keseluruhan proses pengembangan, memastikan timeline (5 Sprint di Jira) dipatuhi, mengatasi hambatan tim, dan menyatukan dokumentasi proyek akhir.
- **Muhammad Rifal Ardi Mustofa** (*UI/UX Designer & Front-End Developer*): Merancang antarmuka awal dan *user flow*, serta mengubah desain Figma menjadi komponen React dan Tailwind CSS.
- **Jeremy Adrean** (*UI/UX Designer & Front-End Developer*): Membantu mengembangkan antarmuka, membangun fungsi validasi pengunggahan dokumen di sisi klien, dan mendesain dasbor penampil hasil.
- **Heyden Alya Syailendra** (*Prompt Engineer & API/Back-End Developer*): Mengoptimalkan instruksi (*prompt*) untuk Gemini API agar selalu menemukan *research gap* yang tajam, serta membangun arsitektur pertukaran data server.
- **Ksatrio Dananjaya** (*Prompt Engineer & API/Back-End Developer*): Mengimplementasikan kode integrasi SDK Google Generative AI di Python, memastikan logika pembersihan teks berjalan baik, dan memaksa keluaran menjadi format JSON.
- **Ramdania Syafitriani** (*Database Specialist & DevOps Engineer*): Mengonfigurasi lingkungan penyimpanan sementara di Back-End, mengatur manajemen versi di GitHub, serta mengeksekusi *deployment* aplikasi ke peladen publik.
- **Tsabitah Rayendra** (*Quality Assurance & AI Tester*): Mengeksekusi pengujian kualitas perangkat lunak, membombardir sistem dengan uji tekanan batas maksimal ukuran (15 MB), serta mengevaluasi validitas jurnal luaran AI.
