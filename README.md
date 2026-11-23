# 🌸 Panduan Setup — Rijema Dira Chatbot System

## Arsitektur Sistem

```mermaid
flowchart LR
    A["🖥️ Browser\nhttp://localhost:5173/chatbot"] -->|"POST /api/chat"| B["⚡ Vite Proxy\n:5173"]
    B -->|"Forward"| C["🐍 Flask Backend\n:5000"]
    C -->|"Proses"| D["🧠 Chatbot Engine"]
    D --> E["📊 Fuzzy Mamdani\nscikit-fuzzy"]
    D --> F["🤖 Ollama / Gemma\n:11434"]
    E --> G["Skor Masalah\n+ Rekomendasi"]
    F --> H["Analisis Gejala\n+ Jawaban Empatik"]
    G --> C
    H --> C
    C -->|"JSON Response"| A
```


## Cara Menjalankan

> [!IMPORTANT]
> Ada **3 service** yang harus jalan: **Ollama**, **Backend Flask**, dan **Frontend Vite**.

### Cara Cepat (Satu Klik)

1. **Pastikan Ollama sudah berjalan** — buka terminal, ketik:
   ```
   ollama serve
   ```
   Biarkan terminal ini terbuka.

2. **Double-click** file `start_system.bat` di root folder project.
   - Ini akan otomatis install dependencies dan jalankan backend + frontend.

3. **Buka browser** ke: **http://localhost:5173/chatbot**

### Cara Manual (Step by Step)

**Terminal 1 — Ollama:**
```
ollama serve
```

**Terminal 2 — Backend:**
```
cd backend
pip install flask flask-cors requests scikit-fuzzy numpy
python app.py
```

**Terminal 3 — Frontend:**
```
npx vite
```

## Fitur yang Sudah Berjalan

- ✅ **Status koneksi real-time** — bar hijau/kuning/merah di atas chat menunjukkan apakah backend & Ollama sudah aktif
- ✅ **Error handling** — kalau server mati atau Ollama belum aktif, pesan error ditampilkan langsung di chat (bukan crash)
- ✅ **Loading animation** — icon berputar saat bot sedang memproses (bukan cuma "sedang mengetik")
- ✅ **Quick Topics** — klik topik cepat di sidebar tetap bekerja
- ✅ **Percakapan Baru** — tombol refresh tetap bekerja
- ✅ **Bahasa santai** — chatbot bisa memahami "muka gw merah gatel banget" berkat normalisasi slang

## Alur Chatbot (Diagram)

```mermaid
flowchart TD
    A["User mengetik pesan"] --> B["Normalisasi bahasa santai\n(slang → baku)"]
    B --> C{"Fuzzy Scope Filter\n(relevansi skincare)"}
    C -->|"Luar"| D["❌ Tolak:\nMaaf, saya cuma bisa\nbantu soal skincare"]
    C -->|"Ragu"| E["⚠️ Minta klarifikasi"]
    C -->|"Dalam"| F["Ekstraksi Gejala"]
    F --> G["Gemma LLM\n(analisis konteks)"]
    F --> H["Leksikon Santai\n(jaring pengaman)"]
    G --> I["Gabung nilai tertinggi"]
    H --> I
    I --> J["Fuzzy Mamdani\n4 input → tingkat masalah"]
    J --> K["Skor + Label\n(ringan/sedang/berat)"]
    K --> L["Gemma merangkai\njawaban empatik"]
    L --> M["✅ Jawaban ditampilkan\ndi UI chatbot"]
```

> [!NOTE]
> Chatbot ini membutuhkan **Ollama** dengan model **gemma3:4b** yang sudah terdownload.
> Jika belum punya, jalankan: `ollama pull gemma3:4b`

> [!WARNING]
> Proses analisis membutuhkan waktu **5-15 detik** per pesan (karena memanggil Ollama 3x per pesan).
> Ini normal dan tergantung performa komputer kamu.
