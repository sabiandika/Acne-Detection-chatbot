"""
Fuzzy Mamdani untuk FILTER SCOPE (relevansi pertanyaan terhadap skincare)
Input  : skor_keyword (0-10, dari hitungan kata kunci), skor_llm (0-10, penilaian Gemma)
Output : relevansi (0-100) -> luar / ragu / dalam
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
    "makeup", "bedak", "skin barrier",
    "papula", "pustula", "nodul", "kista", "whitehead", "blackhead", "acne",
    "comedone", "rosacea", "eksim", "dermatitis", "melasma", "folikulitis",
    "benjolan kulit", "kondisi kulit", "kesehatan kulit", "perawatan kulit",
    "analisis gejala", "fuzzy mamdani", "chatbot", "aplikasi ini",
]

APPLICATION_KEYWORDS = (
    "aplikasi ini", "chatbot ini", "fitur aplikasi", "cara kerja fuzzy",
    "fuzzy mamdani", "analisis gejala", "hasil analisis", "hasil fuzzy",
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
    "presiden", "python", "anime", "rtx", "harga gpu", "ibu kota", "ibukota",
    "resep nasi", "sepak bola", "bitcoin", "saham",
)
GENERAL_QUESTION_STARTS = (
    "apa itu", "apa penyebab", "bagaimana cara", "apa perbedaan", "apakah",
    "jelaskan", "kenapa jerawat", "mengapa jerawat", "informasi tentang",
)
SYMPTOM_CUES = (
    "merah", "kemerahan", "gatal", "perih", "panas", "nyeri", "sakit", "bengkak",
    "ruam", "bentol", "berminyak", "kering", "mengelupas", "kasar", "tertarik",
    "lengket", "licin", "meradang", "kulitku", "wajahku",
)
PERSONAL_CUES = ("saya", "aku", "kulitku", "wajahku", "muka saya", "kulit saya", "wajah saya")
ACNE_TERMS = ("jerawat", "bruntusan", "komedo", "pimple", "papula", "pustula", "nodul", "kista")


def _has_phrase(text, phrases):
    return any(re.search(rf"(?<!\w){re.escape(phrase)}(?!\w)", text) for phrase in phrases)


def keyword_score(text):
    normalized = bs.normalisasi(text)
    hits = sum(1 for keyword in KEYWORD_SKINCARE if keyword in normalized) + bs.jumlah_kata_kunci(text)
    return 0 if hits == 0 else 5 if hits == 1 else 10


def classify_intent(text):
    """Deterministically route known unsafe, unrelated, app, skin, or symptom asks."""
    normalized = bs.normalisasi(text)
    if any(re.search(pattern, normalized) for pattern in EMERGENCY_PATTERNS):
        return "safety_redirect"
    if _has_phrase(normalized, UNSAFE_KEYWORDS):
        return "unsafe_medical_request"
    if _has_phrase(normalized, OUT_OF_DOMAIN_KEYWORDS):
        return "out_of_scope"
    if _has_phrase(normalized, APPLICATION_KEYWORDS):
        return "application_help"
    if _has_phrase(normalized, KEYWORD_SKINCARE) or bs.jumlah_kata_kunci(text):
        if any(normalized.startswith(start) for start in GENERAL_QUESTION_STARTS):
            return "skincare_education"
        has_symptom = _has_phrase(normalized, SYMPTOM_CUES)
        has_personal_acne = _has_phrase(normalized, PERSONAL_CUES) and _has_phrase(normalized, ACNE_TERMS)
        return "symptom_analysis" if has_symptom or has_personal_acne else "skincare_education"
    return "out_of_scope"


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
