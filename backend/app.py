"""
Backend API untuk Rijema Dira Skincare Chatbot
Flask server yang membungkus chatbot fuzzy Mamdani + Ollama
"""

import sys
import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

# Tambah folder chatbot ke path supaya bisa import module-nya
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'chatbot'))

import chatbot as cb

app = Flask(__name__)
CORS(app)  # Izinkan request dari frontend (CORS)


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Endpoint utama chatbot.
    Request body: { "message": "teks dari user" }
    Response:     { "reply": "jawaban bot", "ok": true }
    """
    data = request.get_json(silent=True)
    if not data or not data.get('message', '').strip():
        return jsonify({'ok': False, 'reply': 'Pesan tidak boleh kosong.'}), 400

    user_message = data['message'].strip()

    try:
        reply = cb.proses(user_message)
        return jsonify({'ok': True, 'reply': reply})
    except Exception as e:
        # Kalau Ollama belum jalan atau error lain
        error_msg = str(e)
        if 'Connection' in error_msg or 'connection' in error_msg:
            return jsonify({
                'ok': False,
                'reply': 'Ollama belum aktif. Pastikan Ollama sudah berjalan di komputer kamu (jalankan "ollama serve" di terminal).'
            }), 503
        return jsonify({
            'ok': False,
            'reply': f'Terjadi kesalahan: {error_msg}'
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Cek apakah backend hidup dan Ollama bisa dihubungi."""
    ollama_ok = False
    try:
        import requests as req
        r = req.get('http://localhost:11434/api/tags', timeout=3)
        ollama_ok = r.status_code == 200
    except Exception:
        pass

    return jsonify({
        'backend': True,
        'ollama': ollama_ok
    })


if __name__ == '__main__':
    print("=" * 50)
    print("  Rijema Dira Backend - Starting...")
    print("  API berjalan di http://localhost:5000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
