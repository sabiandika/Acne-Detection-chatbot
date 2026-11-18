import "../styles/dashboard.css";
import { Link } from "react-router-dom";
import {
  Droplet,
  Search,
  ShieldCheck,
  Leaf,
  Sun,
  Sparkles,
  FlaskConical,
  AlertTriangle,
  ArrowRight,
  MessageCircle,
  Heart,
  CheckCircle2,
  Microscope,
} from "lucide-react";

function Dashboard() {
  const skinProblems = [
    {
      icon: <Droplet />,
      title: "Dehidrasi Lapisan Sawar (Skin Barrier)",
      description:
        "Penggunaan pembersih wajah yang terlalu keras mengikis lipid alami kulit. Akibatnya, kelembapan mudah menguap dan kulit menjadi lebih rentan terhadap iritasi.",
      tag: "Fokus: Hidrasi dan penguatan barrier",
    },
    {
      icon: <Search />,
      title: "Penumpukan Keratin pada Saluran Pori",
      description:
        "Ketika sel kulit mati tidak terlepas secara teratur, sumbatan yang terbentuk di dalam folikel akan mengeras dan membentuk komedo, menjadi pemicu pertumbuhan bakteri penyebab jerawat.",
      tag: "Fokus: Eksfoliasi BHA Teratur",
    },
    {
      icon: <Leaf />,
      title: "Fluktuasi Hormon dan Inflamasi",
      description:
        "Stres fisik, pola tidur, dan siklus bulanan memengaruhi hormon androgen yang memperbesar aktivitas kelenjar sebum, memicu jerawat meradang di garis rahang dan pipi.",
      tag: "Fokus: Bahan Penenang Anti-Inflamasi",
    },
  ];

  const routines = [
    {
      number: "Tahap 1",
      icon: <Search />,
      title: "Pembersih Lembut",
      subtitle: "Pagi & Malam",
      description:
        "Gunakan pembersih bertekstur gel dengan busa ringan dan formula bebas sulfat untuk menjaga kelembapan alami kulit tanpa menyebabkan iritasi.",
      note: "Kondisi: Gel berbasis air dengan pH seimbang 5-6.",
    },
    {
      number: "Tahap 2",
      icon: <Droplet />,
      title: "Serum Penenang",
      subtitle: "Pagi & Malam",
      description:
        "Gunakan 2 hingga 3 tetes serum berbasis air yang mengandung Centella Asiatica untuk meredakan kemerahan dan memperkuat skin barrier.",
      note: "Kandungan: Formula oil-free, cepat meresap.",
    },
    {
      number: "Tahap 3",
      icon: <FlaskConical />,
      title: "Pelembap Gel",
      subtitle: "Pagi & Malam",
      description:
        "Pilih pelembap berbasis air (water-gel) bebas minyak yang memberikan hidrasi tanpa membuat kulit terasa berat.",
      note: "Kondisi: Gel ringan tanpa kandungan minyak berat.",
    },
    {
      number: "Tahap 4",
      icon: <Sun />,
      title: "Tabir Surya Ringan",
      subtitle: "Khusus Pagi Hari",
      description:
        "Lindungi kulit dari sinar ultraviolet dengan SPF minimal 30 agar proses perawatan berjalan lebih optimal.",
      note: "Karakteristik: Tekstur fluid dengan hasil akhir matte.",
    },
  ];

  const benefits = [
    {
      icon: <Droplet />,
      title: "Keseimbangan Hidrasi Lapisan Luar",
      description:
        "Menjaga kelembapan minyak alami kulit dan mencegah hilangnya air berlebihan melalui permukaan kulit.",
    },
    {
      icon: <Leaf />,
      title: "Pembentukan Folikel Pori Mandiri",
      description:
        "Eksfoliasi bertahap guna mengurangi kotoran dan sel kulit mati sebelum memicu komedo atau peradangan.",
    },
    {
      icon: <ShieldCheck />,
      title: "Penguatan Pertahanan Kulit (Barrier)",
      description:
        "Menjaga integritas lapisan pelindung alami agar kulit terlindungi dari masalah hambatan lingkungan.",
    },
  ];

  const ingredients = [
    {
      title: "Kandungan yang Bermanfaat",
      icon: <Sparkles />,
      items: [
        {
          name: "Niacinamide (2% - 5%)",
          description:
            "Regulator Sebum dan Pembantu Skin Barrier. Membantu menyeimbangkan produksi minyak harian, menyamarkan tampilan pori, serta mendukung kelembapan.",
        },
        {
          name: "Salicylic Acid (BHA 1% - 2%)",
          description:
            "Pembersih Pori Lipofilik. Asam larut minyak yang dapat masuk ke saluran folikel untuk mengangkat kotoran dan komedo.",
        },
        {
          name: "Centella Asiatica (Cica)",
          description:
            "Agen Penenang Alami. Membantu meredakan kemerahan dan menjaga kulit tetap nyaman.",
        },
        {
          name: "Ceramide & Hyaluronic Acid",
          description:
            "Pengunci Kelembapan Non-Komedogenik. Memulihkan lapisan pelindung kulit dan mempertahankan hidrasi.",
        },
      ],
    },
    {
      title: "Bahan yang Perlu Dibatasi",
      icon: <AlertTriangle />,
      items: [
        {
          name: "Minyak Kelapa Murni & Minyak Mineral Pekat",
          description:
            "Memiliki risiko terasa berat dan dapat menyebabkan ketidaknyamanan pada sebagian kulit berminyak.",
        },
        {
          name: "Butiran Scrub Berpartikel Tajam",
          description:
            "Gesekan partikel besar dapat memperburuk iritasi pada kulit yang sedang mengalami peradangan.",
        },
        {
          name: "Alkohol Denat. Dosis Tinggi",
          description:
            "Berpotensi menyebabkan kulit terasa kering dan kurang nyaman apabila digunakan berlebihan.",
        },
        {
          name: "Artificial Fragrance",
          description:
            "Sebaiknya diperhatikan terutama jika kulit memiliki sensitivitas terhadap pewangi.",
        },
      ],
    },
  ];

  return (
    <div className="dashboard-page">
      {/* NAVBAR */}
      <header className="main-navbar">
        <Link to="/dashboard" className="navbar-brand">
          <span className="brand-logo">RD</span>
          <span>
            Rijema <b>Dira</b>
          </span>
        </Link>

        <nav className="navbar-links">
          <a href="#karakteristik">Karakteristik Kulit</a>
          <a href="#kandungan">Kandungan Aktif</a>
          <a href="#rutinitas">Rutinitas Harian</a>
        </nav>

        <Link to="/chatbot" className="navbar-consult">
          Konsultasi Kulit <ArrowRight size={16} />
        </Link>
      </header>

      <main>
        {/* HERO SECTION */}
        <section className="hero-section">
          <div className="hero-content">
            <span className="section-label">
              Panduan Perawatan Kulit Personal
            </span>

            <h1>Pahami Kebutuhan Kulitmu, Temukan Skincare yang Tepat.</h1>

            <p>
              Setiap kulit memiliki karakter unik. Identifikasi kondisi minyak
              berlebih, pori tersumbat, dan jerawat melalui pendekatan personal
              bersama Rijema Dira. Dapatkan rekomendasi kandungan aktif yang
              aman dan efektif.
            </p>

            <div className="hero-buttons">
              <Link to="/chatbot" className="button-primary">
                Mulai Konsultasi Kulit
              </Link>

              <a href="#karakteristik" className="button-secondary">
                Pelajari Karakter Kulit
              </a>
            </div>

            <div className="hero-features">
              <span>
                <CheckCircle2 /> Pendekatan berbasis kebutuhan kulit
              </span>
              <span>
                <CheckCircle2 /> Informasi kandungan skincare
              </span>
              <span>
                <CheckCircle2 /> Panduan rutinitas harian
              </span>
            </div>
          </div>

          <div className="hero-card">
            <span className="section-label">Prinsip Kulit Seimbang</span>
            <h3>Karakter Kulit Wajah Sehat</h3>
            <p className="hero-card-description">
              Tiga pilar dasar untuk menyeimbangkan kadar minyak dan memelihara
              integritas sawar kulit.
            </p>

            {benefits.map((item, index) => (
              <div className="benefit-card" key={index}>
                <div className="benefit-icon">{item.icon}</div>
                <div>
                  <h4>{item.title}</h4>
                  <p>{item.description}</p>
                </div>
              </div>
            ))}

            <div className="hero-card-footer">
              Pendekatan Lembut + Non-Komedogenik + Berbasis Kebutuhan Kulit
            </div>
          </div>
        </section>

        {/* SKIN PROBLEMS */}
        <section className="content-section" id="karakteristik">
          <div className="section-heading">
            <span className="section-label">Memahami Masalah Kulit</span>
            <h2>Mengapa Kulit Menjadi Berminyak dan Rentan Berjerawat?</h2>
            <p>
              Kulit berjerawat bukan sekadar masalah minyak berlebih, melainkan
              ketidakseimbangan antara kadar hidrasi, eksfoliasi alami pori, dan
              kebiasaan pembersihan wajah.
            </p>
          </div>

          <div className="problem-grid">
            {skinProblems.map((item, index) => (
              <article className="problem-card" key={index}>
                <div className="problem-icon">{item.icon}</div>
                <h3>{item.title}</h3>
                <p>{item.description}</p>
                <span className="card-tag">{item.tag}</span>
              </article>
            ))}
          </div>
        </section>

        {/* INGREDIENTS */}
        <section className="content-section" id="kandungan">
          <div className="section-heading">
            <span className="section-label">Formula Perawatan</span>
            <h2>Kandungan yang Dianjurkan dan yang Perlu Diwaspadai</h2>
            <p>
              Mengetahui bahan aktif pada produk membantu memilih formula yang
              bekerja efektif tanpa memperparah permasalahan kulit.
            </p>
          </div>

          <div className="ingredient-grid">
            {ingredients.map((group, index) => (
              <article
                className={`ingredient-card ${index === 1 ? "warning-card" : ""}`}
                key={group.title}
              >
                <div className="ingredient-title">
                  <div className="ingredient-icon">{group.icon}</div>
                  <h3>{group.title}</h3>
                </div>

                {group.items.map((item) => (
                  <div className="ingredient-item" key={item.name}>
                    <h4>{item.name}</h4>
                    <p>{item.description}</p>
                  </div>
                ))}
              </article>
            ))}
          </div>
        </section>

        {/* ROUTINE */}
        <section className="content-section" id="rutinitas">
          <div className="section-heading">
            <span className="section-label">Panduan Perawatan Harian</span>
            <h2>Empat Tahapan Rutinitas Esensial</h2>
            <p>
              Perawatan kulit yang konsisten tidak memerlukan banyak produk.
              Cukup terapkan langkah dasar yang bekerja secara sinergis.
            </p>
          </div>

          <div className="routine-grid">
            {routines.map((item, index) => (
              <article className="routine-card" key={index}>
                <span className="routine-number">{item.number}</span>

                <div className="routine-icon">{item.icon}</div>

                <h3>{item.title}</h3>
                <span className="routine-subtitle">{item.subtitle}</span>

                <p>{item.description}</p>

                <div className="routine-note">{item.note}</div>
              </article>
            ))}
          </div>
        </section>

        {/* CONSULTATION CTA */}
        <section className="consultation-banner" id="konsultasi">
          <div>
            <span className="section-label">Layanan Konsultasi Personal</span>
            <h2>Ingin berdiskusi mengenai kondisi spesifik kulitmu?</h2>
            <p>
              Dapatkan penjelasan mengenai penyebab jerawat, kecocokan bahan
              aktif, dan tips memilih pelembap melalui sistem konsultasi Rijema
              Dira.
            </p>

            <Link to="/chatbot" className="button-primary">
              Konsultasi di Bagian Atas <ArrowRight size={16} />
            </Link>
          </div>

          <div className="consultation-illustration">
            <MessageCircle className="chat-decoration" />
            <div className="consultation-avatar">RD</div>
            <Sparkles className="sparkle-decoration" />
          </div>
        </section>
      </main>

      {/* FOOTER */}
      <footer className="main-footer">
        <div className="footer-grid">
          <div className="footer-brand">
            <Link to="/dashboard" className="footer-logo">
              <span className="brand-logo">RD</span>
              <span>Rijema Dira</span>
            </Link>

            <p>
              Pendamping personal untuk memahami karakteristik kulit dan
              membangun rutinitas perawatan yang tepat, aman, dan
              berkesinambungan.
            </p>
          </div>

          <div className="footer-column">
            <h4>Topik Konsultasi</h4>
            <a href="#karakteristik">Pengendalian Minyak T-Zone</a>
            <a href="#karakteristik">Mengatasi Jerawat Aktif</a>
            <a href="#kandungan">Pemilihan Pelembap Gel</a>
            <a href="#kandungan">Bahan yang Non-Komedogenik</a>
          </div>

          <div className="footer-column">
            <h4>Edukasi Perawatan</h4>
            <a href="#kandungan">Pengenalan Niacinamide</a>
            <a href="#kandungan">BHA dan AHA</a>
            <a href="#rutinitas">Identifikasi Bahan Aktif</a>
            <a href="#rutinitas">Panduan Perawatan Pagi dan Malam</a>
          </div>

          <div className="footer-column">
            <h4>Informasi Layanan</h4>
            <a href="#konsultasi">Ketentuan Penggunaan</a>
            <a href="#konsultasi">Kebijakan Privasi</a>
            <a href="#konsultasi">Hubungi Tim Rijema Dira</a>
          </div>
        </div>

        <div className="footer-disclaimer">
          <strong>Pemberitahuan:</strong> Rekomendasi yang diberikan melalui
          Rijema Dira bersifat edukasi perawatan kulit. Konsultasikan
          permasalahan kulit dengan tenaga medis apabila mengalami kondisi yang
          memerlukan pemeriksaan.
        </div>

        <div className="footer-bottom">
          <span>© 2026 Rijema Dira. Semua hak cipta dilindungi.</span>
          <span>Dirancang dengan penuh perhatian untuk kulitmu.</span>
        </div>
      </footer>
    </div>
  );
}

export default Dashboard;
