"""Extract skin symptoms with Ollama and the existing deterministic lexicon."""

import json

from .ollama_service import chat
from utils import text_normalizer as normalizer

SYMPTOMS = ("keminyakan", "jerawat", "iritasi", "kekeringan")


def extract_with_llm(text):
    system = (
        "Kamu ekstraktor data untuk keluhan kulit, paham bahasa gaul Indonesia. "
        "Keluarkan HANYA JSON dengan kunci keminyakan, jerawat, iritasi, kekeringan "
        "(angka 0-10, atau null jika tidak disebut). iritasi mencakup merah, gatal, "
        "perih, panas, bentol. Angka kandungan/SPF BUKAN skor gejala. Skala: 0 tidak "
        "ada, 3 ringan, 5 sedang, 7 cukup parah, 9 sangat parah. Kata banget/parah/sampai "
        "menaikkan skor, dikit/agak menurunkan."
    )
    try:
        raw = json.loads(chat([
            {"role": "system", "content": system},
            {"role": "user", "content": text},
        ], json_mode=True))
    except Exception:
        raw = {}
    result = {}
    for key in SYMPTOMS:
        try:
            value = raw.get(key)
            result[key] = min(max(float(value), 0), 10) if value is not None else None
        except (TypeError, ValueError):
            result[key] = None
    return result


def merge(llm_result, lexicon_result):
    merged = {}
    for key in SYMPTOMS:
        values = [value for value in (llm_result.get(key), lexicon_result.get(key)) if value is not None]
        merged[key] = max(values) if values else None
    return merged


def extract(text):
    return merge(extract_with_llm(text), normalizer.skor_leksikon(text))
