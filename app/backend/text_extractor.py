"""
Modul Ekstraksi & Pembersihan Teks PDF (FR-04 & Jobdesc Back-End)
Penanggung Jawab: Heyden Alya Syailendra & Ksatrio Dananjaya

Modul ini bertanggung jawab untuk:
1. Membaca berkas PDF dari memori / temporary storage.
2. Mengekstrak teks dari setiap halaman secara efisien.
3. Membersihkan teks dari noise (header/footer berulang, nomor halaman, karakter anomali).
4. Menyusun teks per dokumen menjadi payload terstruktur yang siap dikonsumsi LLM (Gemini 1.5 Flash).
"""

import re
import logging
from typing import Dict, Any, Optional
from pypdf import PdfReader

logger = logging.getLogger("research_gap_api.extractor")

def clean_extracted_text(text: str) -> str:
    """
    Membersihkan teks mentah hasil ekstraksi PDF:
    - Menghapus baris kosong berlebih
    - Menghapus pola nomor halaman mandiri (misal: '--- Page 1 ---' atau angka tunggal di awal/akhir)
    - Normalisasi spasi dan newline
    """
    if not text:
        return ""

    # Ganti carriage returns dan tab
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Hapus baris yang hanya berisi angka (biasanya nomor halaman)
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        # Lewati nomor halaman tunggal
        if stripped.isdigit():
            continue
        cleaned_lines.append(stripped)

    # Gabungkan kembali dan hilangkan multiple newlines
    result = "\n".join(cleaned_lines)
    result = re.sub(r'\n{3,}', '\n\n', result)
    result = re.sub(r'[ \t]{2,}', ' ', result)

    return result.strip()


def extract_text_from_pdf(file_path: str, max_chars_per_doc: int = 120_000) -> Dict[str, Any]:
    """
    Mengekstrak teks dari file PDF lokal menggunakan pypdf.
    
    Returns:
        dict berisi:
        - "success": bool
        - "text": str (teks yang sudah dibersihkan)
        - "page_count": int
        - "char_count": int
        - "is_scanned": bool (jika PDF tidak memiliki teks / berupa hasil scan gambar)
    """
    try:
        reader = PdfReader(file_path)
        page_count = len(reader.pages)
        extracted_pages = []

        for idx, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            if page_text.strip():
                extracted_pages.append(page_text)

        raw_text = "\n\n".join(extracted_pages)
        cleaned_text = clean_extracted_text(raw_text)

        # Deteksi jika berkas kemungkinan berupa scan gambar (teks sangat minim)
        is_scanned = len(cleaned_text.strip()) < 100

        # Batasi panjang karakter jika artikel sangat panjang untuk efisiensi
        if len(cleaned_text) > max_chars_per_doc:
            cleaned_text = cleaned_text[:max_chars_per_doc] + "\n\n[...Konten teks dipotong demi efisiensi context...]"

        return {
            "success": True,
            "text": cleaned_text,
            "page_count": page_count,
            "char_count": len(cleaned_text),
            "is_scanned": is_scanned
        }

    except Exception as e:
        logger.error(f"Gagal mengekstrak PDF {file_path}: {str(e)}")
        return {
            "success": False,
            "text": "",
            "page_count": 0,
            "char_count": 0,
            "is_scanned": False,
            "error": str(e)
        }
