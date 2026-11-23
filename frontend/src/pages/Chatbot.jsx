
import { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Send,
  Sparkles,
  Droplet,
  FlaskConical,
  Sun,
  MessageCircle,
  RefreshCw,
  ArrowLeft,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Wifi,
  WifiOff
} from 'lucide-react';

import '../styles/chatbot.css';

const quickTopics = [
  { icon: '✨', label: 'Minyak Berlebih & Jerawat' },
  { icon: '💧', label: 'Kulit Berminyak tapi Dehidrasi' },
  { icon: '🧴', label: 'Pilihan Pelembap Bebas Minyak' },
  { icon: '♙', label: 'Kombinasi BHA & Niacinamide' },
  { icon: '☀️', label: 'Rekomendasi Tabir Surya Matte' }
];

const initialMessage = {
  id: 1,
  sender: 'bot',
  text: (
    <>
      Halo, selamat datang di ruang konsultasi <strong>Rijema Dira.</strong>
      <br /><br />
      Saya siap membantu Anda memahami kondisi kulit wajah,
      mengidentifikasi apakah kulit Anda tergolong berminyak atau
      mengalami dehidrasi, serta memberikan panduan kandungan
      skincare yang cocok. Silakan sampaikan keluhan Anda atau
      pilih topik yang tersedia.
    </>
  )
};

// Kirim pesan ke backend Flask -> chatbot fuzzy Mamdani + Ollama
async function sendToBackend(message) {
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  });

  const data = await res.json();

  if (!res.ok || !data.ok) {
    throw new Error(data.reply || 'Terjadi kesalahan pada server.');
  }

  return data.reply;
}

// Cek status backend & Ollama
async function checkHealth() {
  try {
    const res = await fetch('/api/health');
    const data = await res.json();
    return data;
  } catch {
    return { backend: false, ollama: false };
  }
}

function Chatbot() {
  const [messages, setMessages] = useState([
    { ...initialMessage, time: 'Hari ini' }
  ]);

  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [backendStatus, setBackendStatus] = useState({ backend: null, ollama: null });
  const bottomRef = useRef(null);

  // Cek koneksi backend saat komponen pertama kali dimuat
  useEffect(() => {
    checkHealth().then(setBackendStatus);
    // Cek ulang setiap 30 detik
    const interval = setInterval(() => {
      checkHealth().then(setBackendStatus);
    }, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const sendMessage = async (text) => {
    const message = text.trim();

    if (!message || isTyping) return;

    const now = new Date().toLocaleTimeString('id-ID', {
      hour: '2-digit',
      minute: '2-digit'
    });

    // Tambah pesan user ke daftar
    setMessages(prev => [
      ...prev,
      {
        id: Date.now(),
        sender: 'user',
        text: message,
        time: now
      }
    ]);

    setInput('');
    setIsTyping(true);

    try {
      // Kirim ke backend (chatbot fuzzy + Ollama)
      const reply = await sendToBackend(message);

      setMessages(prev => [
        ...prev,
        {
          id: Date.now() + 1,
          sender: 'bot',
          text: reply,
          time: new Date().toLocaleTimeString('id-ID', {
            hour: '2-digit',
            minute: '2-digit'
          })
        }
      ]);
    } catch (error) {
      // Tampilkan pesan error sebagai pesan bot
      setMessages(prev => [
        ...prev,
        {
          id: Date.now() + 1,
          sender: 'bot',
          isError: true,
          text: error.message || 'Gagal menghubungi server. Pastikan backend sudah berjalan.',
          time: new Date().toLocaleTimeString('id-ID', {
            hour: '2-digit',
            minute: '2-digit'
          })
        }
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  const newConversation = () => {
    setMessages([{ ...initialMessage, id: Date.now(), time: 'Hari ini' }]);
    setInput('');
    setIsTyping(false);
  };

  // Render status koneksi
  const renderStatus = () => {
    if (backendStatus.backend === null) return null;

    if (!backendStatus.backend) {
      return (
        <div className="connection-status offline">
          <WifiOff size={14} />
          <span>Backend belum aktif — jalankan <code>start_backend.bat</code></span>
        </div>
      );
    }

    if (!backendStatus.ollama) {
      return (
        <div className="connection-status warning">
          <AlertCircle size={14} />
          <span>Ollama belum aktif — jalankan <code>ollama serve</code></span>
        </div>
      );
    }

    return (
      <div className="connection-status online">
        <Wifi size={14} />
        <span>Terhubung — Siap konsultasi</span>
      </div>
    );
  };

  return (
    <div className="chatbot-page">

      {/* HEADER */}
      <header className="chatbot-header">
        <Link to="/dashboard" className="chatbot-brand">
          <span className="chatbot-brand-logo">RD</span>
          <span>Rijema <b>Dira</b></span>
        </Link>

        <Link to="/dashboard" className="back-home">
          <ArrowLeft size={16} />
          Kembali ke Beranda
        </Link>
      </header>

      <main className="chatbot-layout">

        {/* LEFT SIDEBAR */}
        <aside className="chatbot-sidebar">

          <div className="assistant-profile">
            <div className="assistant-avatar">RD</div>

            <h2>Asisten Konsultasi</h2>
            <p>Panduan Perawatan Kulit Personal</p>

            <span className="online-status">
              <span></span>
              Aktif 24 Jam
            </span>
          </div>

          <div className="quick-topics">
            <h3>Pilihan Topik Cepat</h3>

            {quickTopics.map((topic, index) => (
              <button
                key={index}
                className="topic-button"
                onClick={() => sendMessage(topic.label)}
                disabled={isTyping}
              >
                <span>{topic.icon}</span>
                {topic.label}
              </button>
            ))}
          </div>

        </aside>

        {/* CHAT AREA */}
        <section className="chat-window">

          {/* CHAT HEADER */}
          <div className="chat-window-header">
            <div className="chat-header-info">
              <div className="small-avatar">RD</div>

              <div>
                <h2>Rijema Dira Assistant</h2>
                <p><span></span> Sedang online & siap membantu</p>
              </div>
            </div>

            <button
              className="new-chat-button"
              onClick={newConversation}
            >
              <RefreshCw size={14} />
              Mulai Percakapan Baru
            </button>
          </div>

          {/* CONNECTION STATUS BAR */}
          {renderStatus()}

          {/* MESSAGES */}
          <div className="chat-messages">

            {messages.map(message => (
              <div
                className={`message-row ${message.sender}${message.isError ? ' error' : ''}`}
                key={message.id}
              >
                {message.sender === 'bot' && (
                  <div className={`message-avatar${message.isError ? ' error-avatar' : ''}`}>
                    {message.isError ? '!' : 'RD'}
                  </div>
                )}

                <div className="message-content">
                  <div className={`message-bubble${message.isError ? ' error-bubble' : ''}`}>
                    {message.title && (
                      <h3>{message.title}</h3>
                    )}

                    <div style={{ whiteSpace: 'pre-wrap' }}>{message.text}</div>
                  </div>

                  <span className="message-time">
                    {message.time}
                  </span>
                </div>
              </div>
            ))}

            {isTyping && (
              <div className="message-row bot">
                <div className="message-avatar">RD</div>
                <div className="message-bubble typing-indicator">
                  <Loader2 size={14} className="spin-icon" />
                  Rijema Dira sedang menganalisis...
                </div>
              </div>
            )}

            <div ref={bottomRef} />
          </div>

          {/* INPUT */}
          <div className="chat-input-area">
            <form
              className="chat-input-form"
              onSubmit={e => {
                e.preventDefault();
                sendMessage(input);
              }}
            >
              <input
                type="text"
                value={input}
                onChange={e => setInput(e.target.value)}
                placeholder="Tuliskan pertanyaan seputar kondisi kulit Anda..."
                disabled={isTyping}
              />

              <button
                type="submit"
                aria-label="Kirim pesan"
                disabled={!input.trim() || isTyping}
              >
                <Send size={19} />
              </button>
            </form>

            <p className="chat-tips">
              💡 Chatbot ini menggunakan Fuzzy Mamdani + AI untuk menganalisis keluhan kulit Anda.
              Ceritakan kondisi kulit dengan bahasa sehari-hari, misalnya "muka gw berminyak banget, jerawatan parah".
            </p>
          </div>

        </section>
      </main>
    </div>
  );
}

export default Chatbot;
