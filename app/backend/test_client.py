"""
Skrip Pengujian API Rekomendasi Topik & Research Gap
Penanggung Jawab: Heyden Alya Syailendra (Prompt Engineer & API/Back-End Developer)

Dapat digunakan bersama Tsabitah Rayendra (QA & Tester) untuk:
1. Uji Validasi Berkas (Pre-Flight Check)
2. Uji Analisis AI & JSON Schema Output
"""

import sys
import os
import requests

BASE_URL = "http://127.0.0.1:8000"

def test_validation(pdf_paths):
    url = f"{BASE_URL}/api/validate-files"
    print(f"\n[*] Menguji Endpoint Validasi: {url}")
    opened_files = []
    files_payload = []
    try:
        for p in pdf_paths:
            f = open(p, "rb")
            opened_files.append(f)
            files_payload.append(("files", (os.path.basename(p), f, "application/pdf")))
        
        res = requests.post(url, files=files_payload)
        print(f"Status Code: {res.status_code}")
        print("Response:", res.json())
    finally:
        for f in opened_files:
            f.close()


def test_analyze(pdf_paths):
    url = f"{BASE_URL}/api/analyze"
    print(f"\n[*] Menguji Endpoint Analisis: {url}")
    opened_files = []
    files_payload = []
    try:
        for p in pdf_paths:
            f = open(p, "rb")
            opened_files.append(f)
            files_payload.append(("files", (os.path.basename(p), f, "application/pdf")))
        
        print(f"[*] Mengirim {len(pdf_paths)} dokumen PDF ke LLM (Gemini 1.5 Flash)...")
        res = requests.post(url, files=files_payload, timeout=90)
        print(f"Status Code: {res.status_code}")
        
        if res.status_code == 200:
            data = res.json()
            print("\n================== 1. RINGKASAN SINTESIS LITERATUR ==================")
            print(data.get("ringkasan_sintesis"))

            print("\n================== 2. TELAAH PAPER ==================")
            for item in data.get("telaah_paper", []):
                print(f"- {item.get('nama_dokumen')}: {item.get('fokus_utama')}")
                print(f"  Keterbatasan: {item.get('keterbatasan_diakui')}")

            print("\n================== 3. RESEARCH GAPS YANG DITEMUKAN ==================")
            for idx, gap in enumerate(data.get("research_gaps", []), 1):
                print(f"\nGap #{idx} [{gap.get('tingkat_urgensi')}] - Aspek: {gap.get('aspek')}")
                print(f"Deskripsi: {gap.get('deskripsi')}")
                print(f"Alasan Urgensi: {gap.get('alasan_urgensi')}")

            print("\n================== 4. REKOMENDASI TOPIK / JUDUL SKRIPSI ==================")
            for idx, rec in enumerate(data.get("rekomendasi_judul", []), 1):
                print(f"\n[Rekomendasi #{idx}]")
                print(f"JUDUL          : {rec.get('judul')}")
                print(f"NOVELTY        : {rec.get('novelty')}")
                print(f"RUMUSAN MASALAH: {rec.get('rumusan_masalah_utama')}")
                print(f"METODE USULAN  : {rec.get('metodologi_usulan')}")
                print(f"KONTRIBUSI     : {rec.get('kontribusi_dan_dampak')}")
        else:
            print("Gagal:", res.text)
    finally:
        for f in opened_files:
            f.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Penggunaan:")
        print("  python test_client.py <path_file1.pdf> <path_file2.pdf> ...")
        sys.exit(1)

    pdf_files = sys.argv[1:]
    test_validation(pdf_files)
    test_analyze(pdf_files)
