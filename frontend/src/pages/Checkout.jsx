import { Link, Navigate } from "react-router-dom";
import { ArrowLeft, ShoppingBag } from "lucide-react";
import { useCart } from "../context/CartContext";
import "../styles/Checkout.css";

const formatPrice = (price) =>
  new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    maximumFractionDigits: 0,
  }).format(price);

function Checkout() {
  const { cartItems, totalItems, totalPrice } = useCart();

  if (!cartItems.length) return <Navigate to="/produk" replace />;

  return (
    <main className="checkout-page">
      <header className="checkout-header">
        <Link to="/produk" className="checkout-back">
          <ArrowLeft size={17} /> Kembali ke produk
        </Link>
        <Link to="/dashboard" className="checkout-brand">
          Rijema <b>Dira</b>
        </Link>
      </header>

      <div className="checkout-content">
        <section className="checkout-form-section">
          <span className="checkout-eyebrow">RIJEMA DIRA</span>
          <h1>Selesaikan Pesanan</h1>
          <p className="checkout-intro">
            Isi alamat pengiriman untuk melanjutkan pesananmu.
          </p>

          <form
            className="checkout-form"
            onSubmit={(event) => event.preventDefault()}
          >
            <h2>Informasi Pengiriman</h2>
            <label>
              Nama penerima
              <input
                name="name"
                autoComplete="name"
                required
                placeholder="Nama lengkap"
              />
            </label>
            <label>
              Email
              <input
                name="email"
                type="email"
                autoComplete="email"
                required
                placeholder="nama@email.com"
              />
            </label>
            <label>
              Nomor telepon
              <input
                name="phone"
                type="tel"
                autoComplete="tel"
                required
                placeholder="08xxxxxxxxxx"
              />
            </label>
            <label>
              Alamat lengkap
              <textarea
                name="address"
                autoComplete="street-address"
                required
                rows="3"
                placeholder="Jalan, nomor rumah, RT/RW"
              />
            </label>
            <div className="checkout-location-fields">
              <label>
                Kota
                <input name="city" autoComplete="address-level2" required />
              </label>
              <label>
                Kode pos
                <input name="postalCode" autoComplete="postal-code" required />
              </label>
            </div>
            <label>
              Metode pembayaran
              <select name="payment" defaultValue="transfer">
                <option value="transfer">Transfer bank</option>
                <option value="cod">Bayar di tempat (COD)</option>
              </select>
            </label>
            <button className="checkout-submit" type="submit">
              Buat Pesanan · {formatPrice(totalPrice)}
            </button>
            <p className="checkout-note">
              Form pesanan siap diisi. Pemrosesan pembayaran belum terhubung.
            </p>
          </form>
        </section>

        <aside className="checkout-summary">
          <h2>
            <ShoppingBag size={19} /> Ringkasan Pesanan
          </h2>
          <p className="checkout-count">{totalItems} produk</p>
          <div className="checkout-items">
            {cartItems.map((item) => (
              <article className="checkout-item" key={item.id}>
                <img src={item.image} alt={item.name} />
                <div>
                  <h3>{item.name}</h3>
                  <p>
                    {item.quantity} × {formatPrice(Number(item.price || 0))}
                  </p>
                </div>
                <strong>
                  {formatPrice(Number(item.price || 0) * item.quantity)}
                </strong>
              </article>
            ))}
          </div>
          <div className="checkout-total">
            <span>Total pembayaran</span>
            <strong>{formatPrice(totalPrice)}</strong>
          </div>
        </aside>
      </div>
    </main>
  );
}

export default Checkout;
