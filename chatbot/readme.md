Chatbot skincare yang paham bahasa santai + empati
Alur:
 1. Normalisasi slang -> filter scope (keyword + Gemma -> Fuzzy relevansi)
 2. Ekstraksi gejala: Gemma (JSON) DIGABUNG leksikon santai (jaring pengaman)
 3. Aturan keamanan -> Fuzzy Mamdani tingkat masalah
 4. Gemma merangkai jawaban: empati -> penjelasan -> solusi -> pertanyaan lanjutan
Jalankan: python chatbot.py   (pastikan Ollama aktif)


