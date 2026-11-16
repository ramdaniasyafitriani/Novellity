"""
Pydantic Data Models & JSON Schema Definitions (FR-06 & Arsitektur Data)
Penanggung Jawab: Heyden Alya Syailendra (Prompt Engineer & API/Back-End Developer)

Skema ini mendefinisikan kontrak data antara:
1. Google Gemini API (Structured Output enforcement)
2. Backend FastAPI
3. Frontend React.js (Rifal & Jeremy)
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class DocumentOverview(BaseModel):
    nama_dokumen: str = Field(
        ...,
        description="Nama file dokumen atau estimasi judul paper yang diunggah."
    )
    fokus_utama: str = Field(
        ...,
        description="Fokus masalah, domain, atau metode utama yang dibahas dalam paper ini."
    )
    keterbatasan_diakui: str = Field(
        ...,
        description="Batasan metodologis, dataset, atau tantangan yang diakui oleh penulis paper."
    )


class ResearchGapItem(BaseModel):
    aspek: str = Field(
        ...,
        description="Kategori celah riset: 'Metodologis', 'Dataset / Domain', 'Evaluasi & Validasi', atau 'Implementasi Praktis / Efisiensi'."
    )
    deskripsi: str = Field(
        ...,
        description="Penjelasan mendalam mengenai research gap yang belum terselesaikan di antara paper-paper tersebut."
    )
    tingkat_urgensi: str = Field(
        ...,
        description="Urgensi penyelesaian: 'Tinggi', 'Sedang', atau 'Rendah'."
    )
    alasan_urgensi: str = Field(
        ...,
        description="Alasan kritis mengapa research gap ini penting untuk diinvestigasi oleh mahasiswa tingkat akhir."
    )


class TopicRecommendationItem(BaseModel):
    judul: str = Field(
        ...,
        description="Rekomendasi judul penelitian/skripsi yang tajam, akademis, dan terstruktur sesuai kaidah penulisan ilmiah."
    )
    novelty: str = Field(
        ...,
        description="Nilai kebaruan (novelty) yang membedakan judul ini secara signifikan dari artikel-artikel yang dijadikan referensi."
    )
    rumusan_masalah_utama: str = Field(
        ...,
        description="Pertanyaan penelitian (research question) utama yang akan dijawab oleh judul ini."
    )
    metodologi_usulan: str = Field(
        ...,
        description="Metodologi/algoritma/kerangka kerja riset yang disarankan untuk mengeksekusi topik tersebut secara realistis."
    )
    kontribusi_dan_dampak: str = Field(
        ...,
        description="Manfaat teoritis maupun praktis yang diharapkan dapat dihasilkan dari penelitian ini."
    )


class AnalysisResponse(BaseModel):
    """
    Format respon lengkap yang dipaksa keluar dari LLM dan dikirimkan ke Front-End (FR-06 & FR-07)
    """
    ringkasan_sintesis: str = Field(
        ...,
        description="Paragraf deskriptif mendalam yang mensintesis temuan, pola, dan keterhubungan dari seluruh artikel yang diunggah."
    )
    telaah_paper: List[DocumentOverview] = Field(
        ...,
        description="Pemetaan singkat ringkasan fokus dan batasan dari masing-masing artikel yang dianalisis."
    )
    research_gaps: List[ResearchGapItem] = Field(
        ...,
        description="Daftar 2 hingga 4 celah penelitian (research gaps) yang tajam dan belum terpecahkan."
    )
    rekomendasi_judul: List[TopicRecommendationItem] = Field(
        ...,
        description="Daftar 3 hingga 5 rekomendasi topik dan judul penelitian yang siap diajukan ke dosen pembimbing."
    )


# Model untuk Validasi Pre-Flight (Front-End Helper)
class FileValidationResult(BaseModel):
    filename: str
    size_bytes: int
    size_formatted: str
    is_valid_type: bool
    status: str
    error_message: Optional[str] = None


class ValidationSummaryResponse(BaseModel):
    valid: bool
    total_files: int
    total_size_bytes: int
    total_size_mb: float
    max_files_allowed: int = 10
    max_size_allowed_mb: float = 15.0
    files: List[FileValidationResult]
    message: str
