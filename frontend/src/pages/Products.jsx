import { useState } from "react";
import { useCart } from "../context/CartContext";
import CartDrawer from "../components/CartDrawer";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import {
  Search,
  ShoppingCart,
  Star,
  X,
  Plus,
  Minus,
  MessageCircle,
  ArrowLeft,
  Check,
} from "lucide-react";

import "../styles/products.css";
import products from "../../../shared/products.json";



const formatPrice = (price) => "Rp" + price.toLocaleString("id-ID");

function Products() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const productParam = searchParams.get("product");
  const [isCartOpen, setIsCartOpen] = useState(false);
  const { totalItems, addToCart: addProductToCart } = useCart();
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("Semua");
  const [selectedProductState, setSelectedProductState] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [notification, setNotification] = useState("");
  const productFromUrl = products.find((product) => product.id === Number(productParam));
  const selectedProduct = productFromUrl || selectedProductState;

  const closeProductDetails = () => {
    setSelectedProductState(null);
    if (productParam) {
      const params = new URLSearchParams(searchParams);
      params.delete("product");
      setSearchParams(params, { replace: true });
    }
  };

  const categories = ["Semua", "Cleanser", "Moisturizer", "Serum", "Sunscreen"];

  const filteredProducts = products.filter((product) => {
    const matchSearch = product.name
      .toLowerCase()
      .includes(search.toLowerCase());
    const matchCategory = category === "Semua" || product.category === category;

    return matchSearch && matchCategory;
  });

  const handleAddToCart = () => {
    addProductToCart(selectedProduct, quantity);

    setNotification(
      `${selectedProduct.name} berhasil dimasukkan ke keranjang!`,
    );

    closeProductDetails();
    setQuantity(1);

    setTimeout(() => setNotification(""), 3000);
  };

  const openDetail = (product) => {
    setSelectedProductState(product);
    setQuantity(1);
  };

  return (
    <div className="products-page">
      <header className="products-navbar">
        <Link to="/dashboard" className="products-brand">
          <div className="products-logo">RD</div>
          <span>
            Rijema <b>Dira</b>
          </span>
        </Link>

        <nav className="products-nav-links">
          <Link to="/dashboard">Beranda</Link>
          <a href="#catalog">Produk</a>
          <Link to="/chatbot">Konsultasi</Link>
        </nav>

        <div className="products-nav-actions">
          <button className="cart-link" onClick={() => setIsCartOpen(true)}>
            <ShoppingCart size={19} />
            <span>Keranjang</span>
            <b>{totalItems}</b>
          </button>
        </div>
      </header>

      <main className="products-container">
        <div className="products-heading">
          <Link to="/dashboard" className="back-products">
            <ArrowLeft size={15} /> Kembali
          </Link>

          <span className="products-label">RIJEMA DIRA COLLECTION</span>
          <h1>Temukan Perawatan Terbaikmu</h1>
          <p>
            Pilih skincare yang sesuai dengan kebutuhan dan karakteristik
            kulitmu.
          </p>
        </div>

        <section className="catalog-section" id="catalog">
          <div className="catalog-toolbar">
            <div className="catalog-search">
              <Search size={18} />
              <input
                type="text"
                placeholder="Cari produk skincare..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>

            <span className="product-total">
              {filteredProducts.length} Produk ditemukan
            </span>
          </div>

          <div className="category-filters">
            {categories.map((item) => (
              <button
                key={item}
                className={category === item ? "category-active" : ""}
                onClick={() => setCategory(item)}
              >
                {item}
              </button>
            ))}
          </div>

          <div className="products-grid">
            {filteredProducts.map((product) => (
              <article className="product-card" key={product.id}>
                <button
                  className="product-image-button"
                  onClick={() => openDetail(product)}
                  aria-label={`Lihat ${product.name}`}
                >
                  <img src={product.image} alt={product.name} />
                  <span className="product-category">{product.category}</span>
                </button>

                <div className="product-card-info">
                  <div className="product-rating">
                    <Star size={13} fill="currentColor" />
                    {product.rating}
                  </div>

                  <h3>{product.name}</h3>
                  <p className="product-skin">{product.skin}</p>

                  <div className="product-card-bottom">
                    <strong>{formatPrice(product.price)}</strong>

                    <button onClick={() => openDetail(product)}>
                      Lihat Detail
                    </button>
                  </div>
                </div>
              </article>
            ))}
          </div>

          {filteredProducts.length === 0 && (
            <div className="empty-products">
              <Search size={35} />
              <h3>Produk tidak ditemukan</h3>
              <p>Coba gunakan kata pencarian atau kategori lain.</p>
            </div>
          )}
        </section>

        <section className="products-consultation">
          <div>
            <span>SKINCARE CONSULTATION</span>
            <h2>Masih bingung memilih skincare?</h2>
            <p>Konsultasikan kebutuhan kulitmu dengan asisten Rijema Dira.</p>
          </div>

          <Link to="/chatbot">
            <MessageCircle size={17} />
            Mulai Konsultasi
          </Link>
        </section>
      </main>

      {/* POPUP DETAIL PRODUK */}

      {selectedProduct && (
        <div
          className="product-modal-overlay"
          onClick={closeProductDetails}
        >
          <div className="product-modal" onClick={(e) => e.stopPropagation()}>
            <button
              className="modal-close"
              onClick={closeProductDetails}
              aria-label="Tutup detail"
            >
              <X size={20} />
            </button>

            <div className="modal-image">
              <img src={selectedProduct.image} alt={selectedProduct.name} />
            </div>

            <div className="modal-details">
              <span className="modal-category">{selectedProduct.category}</span>

              <h2>{selectedProduct.name}</h2>

              <div className="modal-rating">
                <Star size={15} fill="currentColor" />
                {selectedProduct.rating} / 5
              </div>

              <h3 className="modal-price">
                {formatPrice(selectedProduct.price)}
              </h3>

              <div className="modal-description">
                <h4>Deskripsi Produk</h4>
                <p>{selectedProduct.description}</p>
              </div>

              <div className="modal-ingredients">
                <h4>Kandungan Utama</h4>

                <div className="ingredient-tags">
                  {selectedProduct.ingredients.map((item) => (
                    <span key={item}>{item}</span>
                  ))}
                </div>
              </div>

              <div className="modal-skin">
                <h4>Cocok untuk</h4>
                <p>{selectedProduct.skin}</p>
              </div>

              <div className="modal-quantity">
                <span>Jumlah</span>

                <div>
                  <button
                    onClick={() => setQuantity((q) => Math.max(1, q - 1))}
                    aria-label="Kurangi jumlah"
                  >
                    <Minus size={15} />
                  </button>

                  <strong>{quantity}</strong>

                  <button
                    onClick={() => setQuantity((q) => q + 1)}
                    aria-label="Tambah jumlah"
                  >
                    <Plus size={15} />
                  </button>
                </div>
              </div>

              <button className="add-cart-button" onClick={handleAddToCart}>
                <ShoppingCart size={18} />
                Masukkan ke Keranjang
              </button>
              <p className="modal-total">
                Total: {formatPrice(selectedProduct.price * quantity)}
              </p>
            </div>
          </div>
        </div>
      )}

      {notification && (
        <div className="product-notification">
          <Check size={18} />
          {notification}
        </div>
      )}

      <CartDrawer
        isOpen={isCartOpen}
        onClose={() => setIsCartOpen(false)}
        onCheckout={() => {
          setIsCartOpen(false);
          navigate("/checkout");
        }}
      />
    </div>
  );
}

export default Products;
