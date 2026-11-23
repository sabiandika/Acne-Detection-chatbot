"""
Pemahaman bahasa santai/gaul tanpa LLM:
- normalisasi slang
- leksikon gejala + kata penguat/pelemah -> skor 0-10 (fuzzy-friendly)
- deteksi perasaan user (untuk empati)
"""
import re

SLANG = {
    "gatel": "gatal", "gatelnya": "gatal", "gatelan": "gatal", "ga": "tidak", "gak": "tidak", "nggak": "tidak",
    "ngga": "tidak", "engga": "tidak", "enggak": "tidak", "tdk": "tidak", "gw": "saya", "gue": "saya", "gua": "saya",
    "bgt": "banget", "bngt": "banget", "udh": "sudah", "udah": "sudah", "sampe": "sampai", "sampek": "sampai",
    "kek": "seperti", "kayak": "seperti", "dikit": "sedikit", "dkt": "dekat", "ngelupas": "mengelupas",
    "jerawatan": "jerawat", "bruntus": "bruntusan", "ketarik": "tertarik", "nyut-nyutan": "nyeri",
    "pedes": "perih", "kesel": "kesal", "keselnya": "kesal", "pedih": "perih", "cenut": "nyeri", "minyakan": "berminyak", "mengkilap": "berminyak",
    "kinclong": "berminyak", "muka": "wajah", "mukaku": "wajah", "mukanya": "wajah",
}

def normalisasi(teks):
    t = re.sub(r"[^a-z0-9\s]", " ", teks.lower())
    return " ".join(SLANG.get(w, w) for w in t.split())

# (kata/frasa, skor dasar 0-10)
GEJALA = {
    "iritasi": [("merah", 5), ("kemerahan", 5), ("gatal", 5), ("perih", 5), ("panas", 4), ("nyeri", 5),
                ("bengkak", 6), ("ruam", 6), ("bentol", 6), ("iritasi", 5), ("tidak nyaman", 3), ("risih", 3)],
    "jerawat": [("jerawat", 4), ("bruntusan", 4), ("komedo", 3), ("pimple", 4), ("meradang", 5), ("bisul", 6)],
    "keminyakan": [("berminyak", 5), ("lengket", 3), ("licin", 3), ("oily", 5)],
    "kekeringan": [("kering", 5), ("mengelupas", 6), ("kasar", 4), ("tertarik", 4), ("pecah pecah", 6), ("kusam", 3)],
}
PENGUAT = {"banget": 2, "parah": 2, "sekali": 2, "sangat": 2, "pol": 2, "amat": 2, "sampai": 1, "terus": 0.5, "banyak": 1.5}
PELEMAH = {"sedikit": -2, "agak": -1.5, "rada": -1.5, "lumayan": 0, "tipis": -2, "samar": -2}

PERASAAN = {
    "tidak nyaman": ["tidak nyaman", "risih", "gelisah", "perih", "gatal"],
    "bingung": ["kenapa", "bingung", "heran"],
    "khawatir": ["takut", "khawatir", "cemas", "panik", "serem", "ngeri"],
    "kurang percaya diri": ["malu", "minder", "insecure", "tidak pede", "tidak percaya diri"],
    "kesal/lelah": ["kesal", "sebel", "bete", "capek", "frustrasi", "males", "muak"],
    "sedih/stres": ["sedih", "stres", "stress", "galau", "putus asa"],
}

def _ada(t, frasa):
    return re.search(rf"\b{re.escape(frasa)}\b", t) is not None

def skor_leksikon(teks):
    """Return dict gejala -> skor 0-10 atau None bila tidak disebut."""
    t = normalisasi(teks)
    penyesuaian = sum(v for k, v in PENGUAT.items() if _ada(t, k)) + sum(v for k, v in PELEMAH.items() if _ada(t, k))
    hasil = {}
    for gejala, daftar in GEJALA.items():
        ketemu = [skor for frasa, skor in daftar if _ada(t, frasa)]
        if not ketemu:
            hasil[gejala] = None
            continue
        skor = max(ketemu) + 0.75 * (len(ketemu) - 1) + penyesuaian
        hasil[gejala] = round(min(max(skor, 0), 10), 1)
    return hasil

def deteksi_perasaan(teks):
    t = normalisasi(teks)
    return [p for p, kata in PERASAAN.items() if any(_ada(t, k) for k in kata)]

def jumlah_kata_kunci(teks):
    t = normalisasi(teks)
    n = sum(1 for daftar in GEJALA.values() for frasa, _ in daftar if _ada(t, frasa))
    return n

if __name__ == "__main__":
    for c in ["ini muka gw kenapa dah udah merah sampe gatel dan ga nyaman",
              "muka gw berminyak banget, jerawatan parah, malu banget gw",
              "kulit gw agak kering dikit sih",
              "resep nasi goreng"]:
        print(c, "\n  ", skor_leksikon(c), deteksi_perasaan(c))