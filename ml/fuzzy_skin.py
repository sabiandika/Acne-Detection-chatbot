import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# 1. Variabel & fungsi keanggotaan 
x_in = np.arange(0, 10.01, 0.1)
x_out = np.arange(0, 100.01, 1)

def _buat_input(nama):
    v = ctrl.Antecedent(x_in, nama)
    v["rendah"] = fuzz.trapmf(v.universe, [0, 0, 2, 5])
    v["sedang"] = fuzz.trimf(v.universe, [2, 5, 8])
    v["tinggi"] = fuzz.trapmf(v.universe, [5, 8, 10, 10])
    return v

minyak = _buat_input("keminyakan")
jerawat = _buat_input("jerawat")
iritasi = _buat_input("iritasi")
kering = _buat_input("kekeringan")

masalah = ctrl.Consequent(x_out, "tingkat_masalah")
masalah["ringan"] = fuzz.trimf(masalah.universe, [0, 0, 40])
masalah["sedang"] = fuzz.trimf(masalah.universe, [20, 50, 80])
masalah["berat"] = fuzz.trimf(masalah.universe, [60, 100, 100])

#  2. Rule base (AND = min, komposisi = max) 
R = ctrl.Rule
rules = [
    R(iritasi["tinggi"], masalah["berat"]),
    R(jerawat["tinggi"] & minyak["tinggi"], masalah["berat"]),
    R(jerawat["tinggi"] & iritasi["sedang"], masalah["berat"]),
    R(kering["tinggi"] & iritasi["sedang"], masalah["berat"]),
    R(iritasi["sedang"], masalah["sedang"]),
    R(jerawat["sedang"], masalah["sedang"]),
    R(jerawat["tinggi"], masalah["sedang"]),
    R(minyak["tinggi"], masalah["sedang"]),
    R(kering["tinggi"], masalah["sedang"]),
    R(minyak["sedang"] & kering["sedang"], masalah["sedang"]),
    R(iritasi["rendah"] & jerawat["rendah"] & minyak["rendah"] & kering["rendah"], masalah["ringan"]),
    R(iritasi["rendah"] & jerawat["rendah"] & minyak["sedang"], masalah["ringan"]),
    R(iritasi["rendah"] & jerawat["rendah"] & kering["sedang"], masalah["ringan"]),
    R(iritasi["rendah"] & jerawat["rendah"] & minyak["rendah"], masalah["ringan"]),
]
_sistem = ctrl.ControlSystem(rules)

# 3. Inferensi + defuzzifikasi (centroid) 
def hitung(keminyakan, jerawat_, iritasi_, kekeringan):
    sim = ctrl.ControlSystemSimulation(_sistem)
    sim.input["keminyakan"] = float(np.clip(keminyakan, 0, 10))
    sim.input["jerawat"] = float(np.clip(jerawat_, 0, 10))
    sim.input["iritasi"] = float(np.clip(iritasi_, 0, 10))
    sim.input["kekeringan"] = float(np.clip(kekeringan, 0, 10))
    sim.compute()
    skor = float(sim.output["tingkat_masalah"])
    if skor < 35:
        label = "ringan"
    elif skor < 65:
        label = "sedang"
    else:
        label = "berat"
    return skor, label

#  4. Mapping rekomendasi (berdasarkan gejala dominan) 
REKOMENDASI = {
    "iritasi": "Produk menenangkan & perbaikan skin barrier (ceramide, panthenol, centella). Hindari dulu vitamin C, retinol, AHA/BHA.",
    "jerawat": "Produk anti-jerawat lembut (salicylic acid, niacinamide), non-comedogenic.",
    "keminyakan": "Pembersih gel & pelembap ringan oil-free, niacinamide untuk kontrol minyak.",
    "kekeringan": "Pelembap kaya (hyaluronic acid, ceramide, glycerin) dan pembersih tanpa sabun keras.",
    "normal": "Rutinitas dasar: pembersih lembut, pelembap, dan sunscreen.",
}

def rekomendasi(keminyakan, jerawat_, iritasi_, kekeringan):
    gejala = {"keminyakan": keminyakan, "jerawat": jerawat_, "iritasi": iritasi_, "kekeringan": kekeringan}
    dominan, nilai = max(gejala.items(), key=lambda kv: kv[1])
    if nilai < 3:
        dominan = "normal"
    return dominan, REKOMENDASI[dominan]

# 5. Basis solusi (dipilih berdasarkan gejala dominan + tingkat masalah)
SOLUSI = {
    "iritasi": {
        "penyebab_umum": "kulit sensitif/skin barrier terganggu, bisa dipicu produk baru, kandungan aktif terlalu kuat (vit C, retinol, AHA/BHA), panas, atau pembersih yang keras",
        "langkah": [
            "Stop dulu produk baru dan semua produk aktif (vit C, retinol, AHA/BHA, scrub)",
            "Cuci muka pakai pembersih lembut tanpa wangi dengan air biasa, jangan digosok",
            "Kompres dingin pakai kain bersih 5-10 menit untuk redakan panas dan gatal",
            "Pakai pelembap barrier repair (ceramide, panthenol, centella)",
            "Jangan digaruk, dan pakai sunscreen lembut kalau keluar rumah",
        ],
    },
    "jerawat": {
        "penyebab_umum": "pori tersumbat minyak dan sel kulit mati, bisa dipicu stres, hormon, atau produk yang menyumbat pori",
        "langkah": [
            "Cuci muka 2x sehari dengan pembersih lembut",
            "Pakai produk dengan salicylic acid atau niacinamide secara bertahap",
            "Pilih pelembap dan sunscreen non-comedogenic",
            "Jangan dipencet supaya tidak meradang atau bekasnya membandel",
        ],
    },
    "keminyakan": {
        "penyebab_umum": "produksi sebum berlebih, bisa dipicu hormon, cuaca lembap, atau pelembap yang terlalu berat",
        "langkah": [
            "Pakai pembersih gel yang lembut, jangan terlalu sering cuci muka",
            "Pakai pelembap ringan oil-free, kulit berminyak tetap butuh pelembap",
            "Niacinamide bisa bantu mengontrol minyak",
            "Pilih sunscreen tekstur gel atau ringan",
        ],
    },
    "kekeringan": {
        "penyebab_umum": "kelembapan kulit kurang atau barrier kulit lemah, bisa dipicu AC, cuci muka terlalu keras, atau cuaca kering",
        "langkah": [
            "Ganti pembersih jadi yang lembut tanpa sabun keras",
            "Pakai pelembap dengan hyaluronic acid, glycerin, atau ceramide setelah cuci muka saat kulit masih lembap",
            "Kurangi scrub dan produk aktif dulu",
            "Pakai sunscreen setiap pagi",
        ],
    },
    "normal": {
        "penyebab_umum": "tidak ada tanda masalah yang jelas",
        "langkah": ["Rutinitas dasar: pembersih lembut, pelembap, dan sunscreen setiap pagi"],
    },
}

KAPAN_KE_DOKTER = {
    "ringan": "Kalau 1 minggu tidak membaik atau malah memburuk, periksa ke dokter kulit.",
    "sedang": "Kalau 3-5 hari tidak membaik, atau makin parah, periksa ke dokter kulit.",
    "berat": "Sebaiknya segera konsultasi ke dokter kulit, terutama kalau keluhannya tidak reda dalam 1-2 hari.",
}
DARURAT = "Kalau muncul bengkak di bibir/kelopak mata/wajah, sesak napas, atau ruam menyebar cepat, segera ke IGD/dokter."

PERTANYAAN_LANJUT = {
    "iritasi": "Kemerahan dan gatalnya mulai muncul setelah pakai produk baru atau kena sesuatu (panas, makeup, dll)?",
    "jerawat": "Jerawatnya lebih banyak di area mana, dan terasa nyeri atau tidak?",
    "keminyakan": "Wajahmu mulai berminyak di jam berapa biasanya, dan tipe pelembap apa yang dipakai sekarang?",
    "kekeringan": "Kulitnya sampai mengelupas atau terasa perih, atau cuma terasa tertarik?",
    "normal": "Ada keluhan kulit tertentu yang ingin kamu atasi?",
}

if __name__ == "__main__":
    # tes manual tanpa chatbot
    for kasus in [(2, 1, 7, 3), (8, 8, 2, 2), (1, 0, 0, 1), (3, 2, 9, 6), (2, 9, 1, 1)]:
        s, l = hitung(*kasus)
        print(kasus, "->", round(s, 1), l, "|", rekomendasi(*kasus)[0])