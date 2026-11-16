"""
Backend REST API Server - Website Rekomendasi Topik / Judul Artikel Ilmiah
Penanggung Jawab: Heyden Alya Syailendra (Prompt Engineer & API/Back-End Developer)

Fitur Utama:
- FR-01 & FR-02: Menerima & memvalidasi file PDF.
- FR-03: Menegakkan batas beban (maks 10 file, total maks 15 MB).
- FR-04: Ekstraksi dan sanitasi teks PDF menjadi payload AI yang bersih.
- FR-05: Integrasi multimodal & teks dengan Google Gemini API 1.5 Flash.
- FR-06: Structured JSON Schema Enforcement menggunakan Pydantic.
- NFR-01: Performa cepat & efisien.
- NFR-02: Stateless session (membersihkan temporary file segera setelah selesai).
"""

import os
import shutil
import logging
import tempfile
from typing import List
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types

from schemas import (
    AnalysisResponse,
    ValidationSummaryResponse,
    FileValidationResult
)
from prompts import SYSTEM_PROMPT, build_user_prompt
from text_extractor import extract_text_from_pdf

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("research_gap_api")

# Load Environment Variables (.env)
load_dotenv()

app = FastAPI(
    title="API Rekomendasi Topik & Research Gap Artikel Ilmiah",
    description="Backend API untuk memproses dokumen PDF jurnal, sintesis literatur, dan rekomendasi topik skripsi dengan Google Gemini 1.5 Flash.",
    version="1.0.0"
)

# CORS Middleware (Memungkinkan integrasi seamless dengan Front-End React/Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Saat production di Render/Vercel, dapat dibatasi ke domain spesifik
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inisialisasi Google GenAI Client
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = None

def get_genai_client() -> genai.Client:
    global client
    if client is not None:
        return client
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GEMINI_API_KEY belum dikonfigurasi di file .env atau environment variable server."
        )
    client = genai.Client(api_key=api_key)
    return client

# Batasan Beban Sesuai SRS (FR-03)
MAX_FILE_COUNT = 10
MAX_TOTAL_SIZE_BYTES = 15 * 1024 * 1024  # 15 Megabytes


# ==================== ENDPOINT: ROOT & HEALTH ====================
@app.get("/", tags=["General"])
def root_info():
    return {
        "status": "online",
        "service": "Website Rekomendasi Topik API",
        "model_engine": "gemini-1.5-flash",
        "author": "Heyden Alya Syailendra (Prompt Engineer & API/Back-End Developer)",
        "docs_url": "/docs"
    }


@app.get("/api/health", tags=["General"])
def health_check():
    return {"status": "healthy", "service": "ready"}


# ==================== ENDPOINT: JSON SCHEMA HELPER ====================
@app.get(
    "/api/schema",
    tags=["Developer Tools"],
    summary="Mendapatkan skema JSON response untuk referensi tim Front-End (Rifal & Jeremy)"
)
def get_expected_schema():
    """
    Menyediakan skema JSON respon agar tim Front-End dapat dengan mudah
    membuat type definition (TypeScript / PropTypes) atau mock data di React.
    """
    return AnalysisResponse.model_json_schema()


# ==================== ENDPOINT: PRE-FLIGHT VALIDATION (FR-02 & FR-03) ====================
@app.post(
    "/api/validate-files",
    response_model=ValidationSummaryResponse,
    tags=["Validation"],
    summary="Validasi cepat berkas sebelum proses upload analisis dimulai (Pre-Flight Check)"
)
async def validate_files(files: List[UploadFile] = File(...)):
    """
    Membantu modul Front-End (FR-02 & FR-03) untuk memvalidasi:
    - Apakah jumlah berkas <= 10
    - Apakah tipe berkas PDF
    - Apakah total akumulasi ukuran <= 15 MB
    """
    total_size = 0
    file_results = []
    has_error = False

    if len(files) == 0:
        return ValidationSummaryResponse(
            valid=False,
            total_files=0,
            total_size_bytes=0,
            total_size_mb=0.0,
            files=[],
            message="Tidak ada berkas yang diunggah."
        )

    if len(files) > MAX_FILE_COUNT:
        has_error = True

    for file in files:
        content = await file.read()
        size = len(content)
        total_size += size
        filename = file.filename or "unknown.pdf"
        is_pdf = filename.lower().endswith(".pdf") and (file.content_type == "application/pdf" or not file.content_type)

        err_msg = None
        if not is_pdf:
            err_msg = "Format bukan berkas PDF."
            has_error = True

        file_results.append(FileValidationResult(
            filename=filename,
            size_bytes=size,
            size_formatted=f"{size / (1024*1024):.2f} MB",
            is_valid_type=is_pdf,
            status="valid" if (is_pdf and not err_msg) else "invalid",
            error_message=err_msg
        ))
        # Reset pointer pembacaan file
        await file.seek(0)

    total_mb = total_size / (1024 * 1024)
    if total_size > MAX_TOTAL_SIZE_BYTES:
        has_error = True
        general_msg = f"Total ukuran file ({total_mb:.2f} MB) melampaui batas maksimal 15 MB."
    elif len(files) > MAX_FILE_COUNT:
        general_msg = f"Jumlah file ({len(files)}) melampaui batas maksimal {MAX_FILE_COUNT} dokumen."
    elif has_error:
        general_msg = "Terdapat file yang bukan merupakan dokumen PDF yang valid."
    else:
        general_msg = f"Semua {len(files)} berkas valid dan siap untuk dianalisis."

    return ValidationSummaryResponse(
        valid=not has_error,
        total_files=len(files),
        total_size_bytes=total_size,
        total_size_mb=round(total_mb, 2),
        files=file_results,
        message=general_msg
    )


# ==================== ENDPOINT: UTAMA ANALISIS AI (FR-01 s/d FR-06) ====================
@app.post(
    "/api/analyze",
    response_model=AnalysisResponse,
    tags=["Analysis"],
    summary="Eksekusi Ekstraksi, Prompt Engineering, dan Rekomendasi Topik"
)
async def analyze_documents(files: List[UploadFile] = File(...)):
    """
    Arsitektur Pertukaran Data Server Lengkap:
    1. Validasi Batasan Beban (FR-02 & FR-03): Maks 10 File & Total <= 15 MB.
    2. Simpan sementara & ekstrak teks PDF (FR-04).
    3. Jika PDF berbasis teks: kirim teks bersih + Prompt Khusus ke Gemini 1.5 Flash.
       Jika PDF berupa scan/gambar: gunakan multimodal upload Gemini Files API.
    4. Force Structured Output JSON Schema (FR-06).
    5. Stateless Cleanup: Hapus semua file sementara (NFR-02).
    """
    ai_client = get_genai_client()

    # 1. Validasi Jumlah Berkas (FR-03)
    if not files or len(files) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wajib mengunggah minimal 1 dokumen artikel ilmiah/jurnal."
        )
    if len(files) > MAX_FILE_COUNT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Batas maksimal unggahan adalah {MAX_FILE_COUNT} dokumen PDF. Anda mengunggah {len(files)} file."
        )

    # 2. Validasi Tipe File & Akumulasi Ukuran (FR-02 & FR-03)
    total_size = 0
    temp_dir = tempfile.mkdtemp(prefix="research_gap_")
    saved_files = []
    gemini_uploaded_files = []

    try:
        logger.info(f"Menerima {len(files)} file PDF untuk diproses.")

        for file in files:
            filename = file.filename or "dokumen.pdf"
            if not filename.lower().endswith(".pdf"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File '{filename}' ditolak. Sistem hanya menerima format PDF (application/pdf)."
                )

            content = await file.read()
            file_size = len(content)
            total_size += file_size

            if total_size > MAX_TOTAL_SIZE_BYTES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Total akumulasi ukuran file melebihi batas 15 MB (Total: {total_size / (1024*1024):.2f} MB)."
                )

            # Simpan sementara di storage server
            temp_file_path = os.path.join(temp_dir, filename)
            with open(temp_file_path, "wb") as f:
                f.write(content)

            saved_files.append({
                "filename": filename,
                "path": temp_file_path,
                "size": file_size
            })

        logger.info(f"Total ukuran valid: {total_size / (1024*1024):.2f} MB. Memulai ekstraksi teks...")

        # 3. Pemrosesan Data & Ekstraksi Teks (FR-04)
        extracted_documents = []
        has_scanned_pdf = False

        for doc in saved_files:
            extraction = extract_text_from_pdf(doc["path"])
            if extraction["is_scanned"] or not extraction["text"]:
                has_scanned_pdf = True
                logger.warning(f"File {doc['filename']} terdeteksi sebagai scanned/gambar. Beralih ke multimodal upload.")

            extracted_documents.append({
                "filename": doc["filename"],
                "path": doc["path"],
                "text": extraction["text"],
                "is_scanned": extraction["is_scanned"]
            })

        # 4. Integrasi AI & Prompt Engineering (FR-05 & FR-06)
        # Jika ada file hasil scan gambar, kita gunakan Files API multimodal agar Gemini 1.5 Flash membaca visual PDF
        llm_contents = []

        if has_scanned_pdf:
            logger.info("Mengunggah dokumen multimodal ke Google Gemini Files API...")
            for doc in saved_files:
                uploaded = ai_client.files.upload(
                    file=doc["path"],
                    config=dict(mime_type="application/pdf")
                )
                gemini_uploaded_files.append(uploaded)
            llm_contents = [*gemini_uploaded_files, "Analisis seluruh artikel ilmiah terlampir sesuai instruksi sistem."]
        else:
            # Menggunakan payload teks terstruktur (sangat cepat dan hemat bandwidth)
            user_prompt = build_user_prompt(extracted_documents)
            llm_contents = [user_prompt]

        logger.info("Mengirimkan payload ke Gemini 1.5 Flash dengan JSON Schema Enforcement...")

        # Panggilan ke Gemini API dengan Structured JSON Schema
        response = ai_client.models.generate_content(
            model="gemini-1.5-flash",
            contents=llm_contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.3,  # Menjaga respon tetap faktual, akademis, dan konsisten
                response_mime_type="application/json",
                response_schema=AnalysisResponse
            )
        )

        logger.info("Berhasil menerima respon terstruktur dari Gemini API.")

        # 5. Parsing & Validasi Respon JSON (FR-06 & FR-07)
        result_json = AnalysisResponse.model_validate_json(response.text)
        return result_json

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saat analisis AI: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Terjadi kesalahan dalam proses analisis AI: {str(e)}"
        )
    finally:
        # 6. Pembersihan Stateless & Hapus File Sementara (NFR-02)
        # Hapus file dari Gemini Cloud Files API jika sempat diunggah
        for g_file in gemini_uploaded_files:
            try:
                ai_client.files.delete(name=g_file.name)
            except Exception:
                pass

        # Hapus temporary directory di server lokal
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                logger.info("Temporary storage lokal berhasil dibersihkan (Stateless).")
            except Exception as cleanup_err:
                logger.warning(f"Gagal membersihkan temporary folder: {str(cleanup_err)}")


if __name__ == "__main__":
    import uvicorn
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Menjalankan server backend di http://{host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=True)
