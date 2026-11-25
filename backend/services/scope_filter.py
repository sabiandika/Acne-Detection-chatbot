"""
Fuzzy Mamdani untuk FILTER SCOPE (relevansi pertanyaan terhadap skincare)
dan Deterministic 10-Class Intent + Context Router.
"""
import re

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

from utils import text_normalizer as bs

x_in = np.arange(0, 10.01, 0.1)
x_out = np.arange(0, 100.01, 1)


def _in(nama):
    v = ctrl.Antecedent(x_in, nama)
    v["rendah"] = fuzz.trapmf(v.universe, [0, 0, 2, 5])
    v["sedang"] = fuzz.trimf(v.universe, [2, 5, 8])
    v["tinggi"] = fuzz.trapmf(v.universe, [5, 8, 10, 10])
    return v


kw = _in("keyword")
llm = _in("llm")

rel = ctrl.Consequent(x_out, "relevansi")
rel["luar"] = fuzz.trimf(rel.universe, [0, 0, 40])
rel["ragu"] = fuzz.trimf(rel.universe, [20, 50, 80])
rel["dalam"] = fuzz.trimf(rel.universe, [60, 100, 100])

R = ctrl.Rule
_rules = [
    R(kw["rendah"] & llm["rendah"], rel["luar"]),
    R(kw["rendah"] & llm["sedang"], rel["ragu"]),
    R(kw["rendah"] & llm["tinggi"], rel["ragu"]),
    R(kw["sedang"] & llm["rendah"], rel["ragu"]),
    R(kw["sedang"] & llm["sedang"], rel["dalam"]),
    R(kw["sedang"] & llm["tinggi"], rel["dalam"]),
    R(kw["tinggi"] & llm["rendah"], rel["ragu"]),
    R(kw["tinggi"] & llm["sedang"], rel["dalam"]),
    R(kw["tinggi"] & llm["tinggi"], rel["dalam"]),
]
_sys = ctrl.ControlSystem(_rules)


def relevansi(skor_keyword, skor_llm):
    sim = ctrl.ControlSystemSimulation(_sys)
    sim.input["keyword"] = float(np.clip(skor_keyword, 0, 10))
    sim.input["llm"] = float(np.clip(skor_llm, 0, 10))
    sim.compute()
    skor = float(sim.output["relevansi"])
    if skor < 35:
        return skor, "luar"
    if skor < 65:
        return skor, "ragu"
    return skor, "dalam"


KEYWORD_SKINCARE = [
    "kulit", "wajah", "skincare", "sunscreen", "serum", "toner", "pelembap",
    "moisturizer", "cleanser", "kemerahan", "merah", "gatal", "perih", "kusam",
    "berminyak", "kering", "iritasi", "ruam", "bruntusan", "jerawat", "komedo",
    "flek", "pori", "vitamin c", "vit c", "niacinamide", "retinol", "spf",
    "sabun", "masker", "alergi", "mengelupas", "bengkak", "bentol", "kosmetik",
    "makeup", "bedak", "skin barrier", "hidrasi", "dehidrasi", "eksfoliasi",
    "salicylic acid", "benzoyl peroxide", "ceramide", "hyaluronic acid",
    "centella", "panthenol", "zinc", "uv", "tabir surya", "pembersih",
    "papula", "pustula", "nodul", "kista", "whitehead", "blackhead", "acne",
    "comedone", "rosacea", "eksim", "dermatitis", "melasma", "folikulitis",
    "benjolan kulit", "kondisi kulit", "kesehatan kulit", "perawatan kulit",
    "analisis gejala", "fuzzy mamdani", "chatbot", "aplikasi ini",
]

APPLICATION_KEYWORDS = (
    "aplikasi ini", "chatbot ini", "fitur aplikasi", "cara kerja fuzzy",
    "fuzzy mamdani", "analisis gejala", "hasil analisis", "hasil fuzzy",
)
SOURCE_CUES = (
    "sumber", "sumbernya", "referensinya", "referensi", "referensi ilmiah",
    "rujukan", "citation", "sitasi", "paper", "jurnal", "source", "bukti ilmiah",
)
PRODUCT_MARKERS = (
    "produk", "product", "products", "toko", "store", "katalog", "catalog",
    "di rijema dira", "bisa saya beli", "item",
)
PRODUCT_CATEGORIES = (
    "cleanser", "pembersih", "moisturizer", "pelembap", "pelembab",
    "serum", "sunscreen", "tabir surya",
)
PRODUCT_RECOMMENDATION_CUES = (
    "rekomendasi", "rekomendasikan", "recommend", "cocok", "suitable",
    "paling sesuai", "paling bagus", "pilihkan", "saran produk",
)
PRODUCT_SEARCH_CUES = (
    "cari", "tampilkan", "ada", "tersedia", "lihat produk", "produk apa", "daftar produk",
)
PRODUCT_COMPARISON_CUES = (
    "bandingkan", "perbandingan", "beda antara", "perbedaan antara",
    "mana yang lebih bagus", "mana yang lebih baik", "mana yang paling",
    "yang lebih bagus", "lebih cocok mana", "mana yang lebih cocok", "vs",
)

CONTEXT_CUES = (
    "masalah itu", "masalah tersebut", "hal tersebut", "hal itu", "kondisi itu",
    "kondisi tersebut", "yang tadi", "bagaimana solusinya", "solusinya",
    "ada saran", "saran gak", "saran tidak", "saran dong", "sarannya",
    "produk tersebut", "produk itu", "produk tadi", "produk apa yang cocok",
    "ada produk", "rekomendasi produknya", "produknya",
    "mana yang lebih bagus", "mana yang lebih baik", "mana yang paling",
    "mana yang lebih cocok", "mana yang cocok", "yang paling cocok",
    "mengatasinya", "merawatnya", "mencegahnya", "penyebabnya", "gejalanya",
    "cirinya", "cara pakainya", "cara menggunakannya", "kandungannya",
    "berikan sumbernya", "berikan sumber", "sumbernya", "referensinya",
    "kenapa bisa begitu", "kenapa begitu", "mengapa demikian",
)
CONTEXT_SUFFIX_PATTERN = re.compile(
    r"^(?:apa|bagaimana|gimana|kenapa|mengapa|kapan|berapa|apakah|ada)\b.*\b"
    r"(?:penyebab|solusi|cara|gejala|ciri|dampak|efek|kandungan|produk|sumber|referensi|saran)nya\b"
)

ADVICE_CUES = (
    "saran", "solusi", "mengatasinya", "mengatasi", "merawatnya", "merawat",
    "cara mengatasinya", "cara merawat", "mencegahnya", "mencegah", "tips",
    "langkah", "penanganan", "perawatan",
)
INFO_QUESTION_STARTS = (
    "apa itu", "apa pengertian", "definisi", "apa penyebab", "penyebab",
    "bagaimana mekanisme", "bagaimana cara", "apa perbedaan", "perbedaan", "bedanya",
    "apakah", "jelaskan", "kenapa", "mengapa", "informasi tentang", "faktor",
)
UNSAFE_KEYWORDS = (
    "dosis", "berapa mg", "berapa ml", "berapa tablet", "resep obat", "resepkan",
    "diagnosis pasti", "diagnosa", "diagnosis saya", "obat resep",
)
EMERGENCY_PATTERNS = (
    r"sesak napas", r"bengkak.{0,25}(?:bibir|kelopak|wajah)",
    r"(?:ruam|bengkak).{0,25}menyebar cepat",
)
OUT_OF_DOMAIN_KEYWORDS = (
    "presiden", "python", "javascript", "java", "coding", "program", "algoritma",
    "anime", "rtx", "gpu", "laptop", "ibu kota", "ibukota", "perang dunia",
    "sejarah", "resep nasi", "masak", "sepak bola", "bitcoin", "saham", "politik",
)
SYMPTOM_CUES = (
    "merah", "kemerahan", "gatal", "perih", "panas", "nyeri", "sakit", "bengkak",
    "ruam", "bentol", "berminyak", "kering", "mengelupas", "kasar", "tertarik",
    "lengket", "licin", "meradang", "kusam",
)
PERSONAL_CUES = (
    "saya", "aku", "kulitku", "wajahku", "mukaku", "muka saya",
    "kulit saya", "wajah saya", "mengalami", "merasa", "keluhan",
)
ACNE_TERMS = ("jerawat", "bruntusan", "komedo", "pimple", "papula", "pustula", "nodul", "kista")


def _has_phrase(text, phrases):
    return any(re.search(rf"(?<!\w){re.escape(phrase)}(?!\w)", text) for phrase in phrases)


def _is_contextual_followup(normalized_text: str) -> bool:
    if _has_phrase(normalized_text, CONTEXT_CUES):
        return True
    if CONTEXT_SUFFIX_PATTERN.search(normalized_text):
        return True
    words = normalized_text.split()
    if len(words) <= 4 and any(w.endswith("nya") for w in words):
        return True
    return False


def keyword_score(text):
    normalized = bs.normalisasi(text)
    hits = sum(1 for keyword in KEYWORD_SKINCARE if keyword in normalized) + bs.jumlah_kata_kunci(text)
    return 0 if hits == 0 else 5 if hits == 1 else 10


def classify_intent(text, has_product_context=False):
    """Route source/catalog/educational requests before skin symptom analysis."""
    normalized = bs.normalisasi(text)
    if any(re.search(pattern, normalized) for pattern in EMERGENCY_PATTERNS):
        return "safety_redirect"
    if _has_phrase(normalized, UNSAFE_KEYWORDS):
        return "unsafe_medical_request"
    if _has_phrase(normalized, OUT_OF_DOMAIN_KEYWORDS):
        return "out_of_scope"
    if _has_phrase(normalized, SOURCE_CUES):
        return "source_request"

    has_product_marker = _has_phrase(normalized, PRODUCT_MARKERS)
    has_product_category = _has_phrase(normalized, PRODUCT_CATEGORIES)
    has_product_request = has_product_marker or has_product_category
    is_comparison = _has_phrase(normalized, PRODUCT_COMPARISON_CUES)

    if is_comparison and (has_product_request or has_product_context):
        return "product_comparison"

    if has_product_request:
        if (_has_phrase(normalized, PRODUCT_RECOMMENDATION_CUES)
                or _has_phrase(normalized, ("cocok untuk", "untuk kulit", "saran"))
                or "beli" in normalized):
            return "product_recommendation"
        if (_has_phrase(normalized, PRODUCT_SEARCH_CUES) or has_product_category
                or has_product_marker):
            return "product_search"

    if has_product_context and _has_phrase(normalized, ("mana yang", "yang paling", "produk tadi", "yang cocok")):
        return "product_recommendation"

    if _has_phrase(normalized, APPLICATION_KEYWORDS):
        return "application_help"

    if _has_phrase(normalized, KEYWORD_SKINCARE) or bs.jumlah_kata_kunci(text):
        is_info_question = any(normalized.startswith(start) for start in INFO_QUESTION_STARTS)
        has_personal = _has_phrase(normalized, PERSONAL_CUES)

        if is_info_question and not any(p in normalized for p in ("saya", "aku", "kulitku", "wajahku")):
            return "skin_information"

        if _has_phrase(normalized, ADVICE_CUES) and not _has_phrase(normalized, SYMPTOM_CUES):
            return "skincare_advice"

        has_symptom = _has_phrase(normalized, SYMPTOM_CUES)
        has_personal_acne = has_personal and _has_phrase(normalized, ACNE_TERMS)
        if has_symptom or has_personal_acne or _has_phrase(normalized, ("analisis kondisi", "analisis kulit", "nilai kondisi")):
            return "skin_analysis"

        if is_info_question:
            return "skin_information"
        return "general_skincare"

    return "out_of_scope"


def resolve_context(text, history):
    """Resolve follow-up utterances from valid prior user turns (ignoring fallback turns)."""
    normalized = bs.normalisasi(text)
    if not _is_contextual_followup(normalized):
        return None

    valid_user_turns = []
    for item in history or []:
        if item.get("is_fallback"):
            continue
        if item.get("role") == "user" and isinstance(item.get("content"), str):
            prior = item["content"].strip()
            prior_intent = classify_intent(prior)
            if prior_intent in {
                "skin_analysis", "skin_information", "skincare_advice",
                "general_skincare", "source_request",
                "product_recommendation", "product_search", "product_comparison",
            }:
                valid_user_turns.append(prior)

    if not valid_user_turns:
        return None
    return " | ".join(valid_user_turns[-2:])


def classify_contextual_intent(text, context, has_product_context=False):
    """Honor safety/domain boundaries first, then route resolved follow-up intents."""
    explicit = classify_intent(text, has_product_context=has_product_context)
    normalized = bs.normalisasi(text)
    is_comparison = _has_phrase(normalized, PRODUCT_COMPARISON_CUES)

    if is_comparison and (has_product_context or _has_phrase(normalized, PRODUCT_MARKERS + PRODUCT_CATEGORIES)):
        return "product_comparison"

    if explicit in {
        "unsafe_medical_request", "safety_redirect", "application_help",
        "source_request", "product_recommendation", "product_search",
        "product_comparison", "skin_analysis", "skin_information",
    }:
        return explicit

    contextual_followup = _is_contextual_followup(normalized)
    if explicit == "out_of_scope" and (not contextual_followup or _has_phrase(normalized, OUT_OF_DOMAIN_KEYWORDS)):
        return "out_of_scope"

    if not context:
        return "clarification_needed" if contextual_followup else explicit

    if _has_phrase(normalized, SOURCE_CUES):
        return "source_request"
    if is_comparison and has_product_context:
        return "product_comparison"
    if _has_phrase(normalized, PRODUCT_MARKERS) or _has_phrase(normalized, ("produk apa", "produk tersebut", "produknya", "ada produk")):
        return "product_recommendation"
    if _has_phrase(normalized, ADVICE_CUES):
        return "skincare_advice"
    if any(normalized.startswith(start) for start in INFO_QUESTION_STARTS) or "penyebab" in normalized or "gejala" in normalized:
        return "skin_information"
    return "general_skincare"


def classify(text):
    """Keep the existing score/label interface without an LLM scope vote."""
    intent = classify_intent(text)
    if intent == "out_of_scope":
        return 0.0, "luar"
    return 100.0, "dalam"


if __name__ == "__main__":
    for k, l in [(0, 0), (0, 5), (0, 9), (5, 1), (5, 5), (10, 9), (10, 1)]:
        s, lab = relevansi(k, l)
        print(f"keyword={k:>2} llm={l} -> {s:5.1f} {lab}")
