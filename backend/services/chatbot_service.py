"""Orchestrate scope filtering, extraction, fuzzy analysis, and response generation."""

import json
import logging

from fuzzy import inference
from utils import text_normalizer as normalizer
from . import scope_filter, symptom_extraction
from .ollama_service import chat

logger = logging.getLogger(__name__)
DEFAULT_SYMPTOM_SCORE = 2
NEW_PRODUCT_CUES = (
    "baru beli", "baru pakai", "baru aja pakai", "habis pakai", "setelah pakai",
    "baru dicoba", "baru ganti", "baru make", "baru aja make",
)


def process(text):
    _, scope_label = scope_filter.classify(text)
    if scope_label == "luar":
        return "Maaf, aku cuma bisa bantu soal skincare dan masalah kulit ya 🙏 Coba ceritain keluhan kulitmu."
    if scope_label == "ragu":
        return ("Aku belum yakin ini soal skincare/kulit. Kalau iya, ceritain aja keluhan kulitmu "
                "(misal merah, gatal, jerawat, kering) ya 🙏")

    symptoms = symptom_extraction.extract(text)
    feelings = normalizer.deteksi_perasaan(text)
    if all(value is None for value in symptoms.values()):
        return ("Aku ikut kepikiran nih 😟 Boleh ceritain lebih jelas? Misalnya kulitnya merah/gatal, "
                "ada jerawat, atau terasa kering/berminyak, dan sejak kapan?")

    values = {key: DEFAULT_SYMPTOM_SCORE if value is None else value for key, value in symptoms.items()}
    normalized = normalizer.normalisasi(text)
    stop_new_product = any(cue in normalized for cue in NEW_PRODUCT_CUES) and values["iritasi"] >= 3
    score, severity = inference.analyze(
        values["keminyakan"], values["jerawat"], values["iritasi"], values["kekeringan"]
    )
    dominant, _ = inference.recommend(
        values["keminyakan"], values["jerawat"], values["iritasi"], values["kekeringan"]
    )
    facts = {
        "perasaan_user": feelings or ["tidak nyaman"],
        "gejala_terbaca": values,
        "skor_fuzzy": round(score, 1),
        "tingkat_masalah": severity,
        "gejala_dominan": dominant,
        "kemungkinan_penyebab": inference.SOLUSI[dominant]["penyebab_umum"],
        "langkah_solusi": inference.SOLUSI[dominant]["langkah"],
        "hentikan_produk_baru": stop_new_product,
        "kapan_ke_dokter": inference.KAPAN_KE_DOKTER[severity],
        "tanda_darurat": inference.DARURAT,
        "pertanyaan_lanjutan": inference.PERTANYAAN_LANJUT[dominant],
    }
    logger.info("Chat analysis completed: severity=%s dominant=%s", severity, dominant)
    system = (
        "Kamu asisten skincare yang hangat dan peduli, bahasa Indonesia santai (pakai 'kamu'). "
        "Jawab HANYA dari DATA, jangan tambah diagnosis, produk, atau kandungan di luar DATA. "
        "Struktur: 1) satu-dua kalimat empati; 2) jelaskan kemungkinan (bukan diagnosis pasti), tingkat "
        "dan penyebab; 3) langkah solusi bernomor, stop produk baru paling atas jika true; "
        "4) kapan ke dokter dan tanda darurat singkat; 5) tutup dengan satu pertanyaan lanjutan. "
        "Maksimal 180 kata. Akhiri dengan: 'Ini bukan pengganti dokter kulit.'"
    )
    answer = chat([
        {"role": "system", "content": system},
        {"role": "user", "content": f"Ucapan user: {text}\n\nDATA: {json.dumps(facts, ensure_ascii=False)}"},
    ])
    answer_is_relevant = any(
        keyword in normalizer.normalisasi(answer) for keyword in scope_filter.KEYWORD_SKINCARE
    ) or normalizer.jumlah_kata_kunci(answer) > 0
    if not answer_is_relevant:
        return "Maaf, aku cuma bisa bantu soal skincare dan masalah kulit ya 🙏"
    return answer
