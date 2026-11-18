"""
Chatbot skincare: Ollama (bahasa) + Fuzzy Mamdani (keputusan)
Alur: filter scope -> ekstrak gejala (Ollama JSON) -> aturan keamanan -> fuzzy -> Ollama rangkai jawaban
Jalankan: python chatbot.py   (pastikan `ollama serve` aktif)
"""
import json
import requests
import fuzzy_skin as fuzzy_skin

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "gemma3:4b"      # GANTI sesuai hasil `ollama list`
DEFAULT_GEJALA = 2         # gejala yang tidak disebut user dianggap tidak ada keluhan (asumsi, tulis di laporan)

KEYWORD_SKINCARE = [
    "kulit", "wajah", "muka", "jerawat", "komedo", "skincare", "sunscreen", "serum", "toner",
    "pelembap", "moisturizer", "cleanser", "kemerahan", "merah", "gatal", "perih", "kusam",
    "berminyak", "kering", "iritasi", "ruam", "bruntusan", "flek", "pori", "vit c", "vitamin c",
    "niacinamide", "retinol", "spf", "sabun muka", "masker", "bekas jerawat", "alergi",
]
PICU_PRODUK_BARU = ["baru beli", "baru pakai", "baru make", "baru aja pake", "baru aja make",
                    "baru aja pakai", "habis pakai", "habis pake", "setelah pakai", "setelah pake", "baru dicoba"]

def dalam_scope(teks):
    t = teks.lower()
    return any(k in t for k in KEYWORD_SKINCARE)

def panggil_ollama(messages, json_mode=False):
    payload = {"model": MODEL, "messages": messages, "stream": False,
               "options": {"temperature": 0.2}}
    if json_mode:
        payload["format"] = "json"
    r = requests.post(OLLAMA_URL, json=payload, timeout=120)
    r.raise_for_status()
    return r.json()["message"]["content"]

def ekstrak_gejala(teks):
    sistem = (
        "Kamu adalah ekstraktor data. Baca keluhan kulit user lalu keluarkan HANYA JSON dengan kunci: "
        "keminyakan, jerawat, iritasi, kekeringan (angka 0-10 atau null jika tidak disebut). "
        "iritasi mencakup kemerahan, gatal, perih. Angka dalam teks seperti kandungan/SPF BUKAN skor gejala. "
        "Skala: 0 tidak ada, 3 ringan, 5 sedang, 8 parah, 10 sangat parah."
    )
    try:
        out = panggil_ollama([{"role": "system", "content": sistem},
                              {"role": "user", "content": teks}], json_mode=True)
        data = json.loads(out)
    except Exception:
        data = {}
    hasil = {}
    for k in ["keminyakan", "jerawat", "iritasi", "kekeringan"]:
        v = data.get(k)
        try:
            v = float(v)
            v = min(max(v, 0), 10)        # validasi rentang di backend
        except (TypeError, ValueError):
            v = None
        hasil[k] = v
    return hasil

def proses(teks):
    # 1. filter scope
    if not dalam_scope(teks):
        return "Maaf, aku cuma bisa bantu soal skincare dan masalah kulit ya 🙏 Coba ceritain keluhan kulitmu."

    # 2. ekstraksi gejala
    g = ekstrak_gejala(teks)
    ada_data = any(v is not None for v in g.values())
    if not ada_data:
        return ("Boleh ceritain lebih detail keluhan kulitmu? Misalnya seberapa merah/gatal, "
                "ada jerawat, atau kulit terasa berminyak/kering.")
    nilai = {k: (DEFAULT_GEJALA if v is None else v) for k, v in g.items()}

    # 3. aturan keamanan (bukan fuzzy)
    t = teks.lower()
    produk_baru = any(p in t for p in PICU_PRODUK_BARU) and nilai["iritasi"] >= 3

    # 4. fuzzy Mamdani
    skor, label = fuzzy_skin.hitung(nilai["keminyakan"], nilai["jerawat"], nilai["iritasi"], nilai["kekeringan"])
    dominan, saran_produk = fuzzy_skin.rekomendasi(nilai["keminyakan"], nilai["jerawat"], nilai["iritasi"], nilai["kekeringan"])

    fakta = {
        "gejala_terbaca": nilai,
        "skor_fuzzy": round(skor, 1),
        "tingkat_masalah": label,
        "gejala_dominan": dominan,
        "saran_produk": saran_produk,
        "hentikan_produk_baru": produk_baru,
        "perlu_ke_dokter": label == "berat" or produk_baru,
    }
    print("\n[DEBUG fuzzy]", json.dumps(fakta, ensure_ascii=False, indent=1))

    # 5. Ollama merangkai jawaban dari fakta fuzzy
    sistem = (
        "Kamu asisten skincare ramah berbahasa Indonesia santai. Jawab HANYA berdasarkan DATA yang diberikan, "
        "jangan menambah diagnosis atau produk/kandungan di luar data. Jawaban singkat (maks 120 kata): "
        "sebutkan tingkat masalah, saran produk, dan jika hentikan_produk_baru=true minta user berhenti memakai produk barunya dulu. "
        "Jika perlu_ke_dokter=true sarankan konsultasi dokter kulit. Akhiri dengan: 'Ini bukan pengganti dokter kulit.'"
    )
    return panggil_ollama([
        {"role": "system", "content": sistem},
        {"role": "user", "content": f"Keluhan user: {teks}\n\nDATA: {json.dumps(fakta, ensure_ascii=False)}"},
    ])

if __name__ == "__main__":
    print("Chatbot Skincare (ketik 'keluar' untuk berhenti)")
    while True:
        u = input("\nKamu : ").strip()
        if u.lower() in ("keluar", "exit", "quit"):
            break
        try:
            print("Bot  :", proses(u))
        except requests.exceptions.ConnectionError:
            print("Bot  : Ollama belum jalan. Jalankan `ollama serve` dulu.")
