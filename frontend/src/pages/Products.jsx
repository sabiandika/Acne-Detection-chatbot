import { useState } from 'react';
import { useCart } from '../context/CartContext';
import CartDrawer from '../components/CartDrawer';
import { Link } from 'react-router-dom';
import {
  Search, ShoppingCart, Star, X, Plus, Minus,
  MessageCircle, ArrowLeft, Check
} from 'lucide-react';

import '../styles/products.css';

const products = [
  {
    id: 1,
    name: 'Gentle Facial Cleanser',
    category: 'Cleanser',
    price: 65000,
    rating: 4.8,
    image: 'https://images.unsplash.com/photo-1556229010-6c3f2c9ca5f8?w=700',
    description: 'Pembersih wajah lembut untuk membersihkan kotoran dan minyak tanpa membuat kulit terasa tertarik.',
    ingredients: ['Centella Asiatica', 'Glycerin', 'Panthenol'],
    skin: 'Semua jenis kulit'
  },
  {
    id: 2,
    name: 'Hydrating Moisturizer',
    category: 'Moisturizer',
    price: 89000,
    rating: 4.9,
    image: 'https://images.unsplash.com/photo-1601049541289-9b1b7bbbfe19?w=700',
    description: 'Pelembap dengan tekstur ringan untuk membantu menjaga hidrasi dan kelembapan kulit.',
    ingredients: ['Hyaluronic Acid', 'Niacinamide', 'Ceramide'],
    skin: 'Normal dan kombinasi'
  },
  {
    id: 3,
    name: 'Daily UV Sunscreen',
    category: 'Sunscreen',
    price: 95000,
    rating: 4.9,
    image: 'https://images.unsplash.com/photo-1556228720-195a672e8a03?w=700',
    description: 'Perlindungan kulit dari paparan sinar UV untuk melengkapi rutinitas skincare harian.',
    ingredients: ['UV Filters', 'Vitamin E', 'Glycerin'],
    skin: 'Semua jenis kulit'
  },
  {
    id: 4,
    name: 'Niacinamide Bright Serum',
    category: 'Serum',
    price: 110000,
    rating: 4.7,
    image: 'https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=700',
    description: 'Serum untuk membantu merawat tampilan warna kulit tidak merata dan menjaga kondisi skin barrier.',
    ingredients: ['Niacinamide', 'Zinc PCA', 'Hyaluronic Acid'],
    skin: 'Berminyak dan kombinasi'
  },
  {
    id: 5,
    name: 'Soothing Gel Moisturizer',
    category: 'Moisturizer',
    price: 78000,
    rating: 4.8,
    image: 'https://images.unsplash.com/photo-1611930022073-b7a4ba5fcccd?w=700',
    description: 'Pelembap gel dengan sensasi ringan untuk membantu memberikan kelembapan pada kulit.',
    ingredients: ['Aloe Vera', 'Centella Asiatica', 'Panthenol'],
    skin: 'Berminyak dan sensitif'
  },
  {
    id: 6,
    name: 'Exfoliating BHA Serum',
    category: 'Serum',
    price: 105000,
    rating: 4.6,
    image: 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=700',
    description: 'Serum eksfoliasi untuk membantu membersihkan pori-pori dan merawat kulit yang rentan berkomedo.',
    ingredients: ['Salicylic Acid', 'Green Tea', 'Glycerin'],
    skin: 'Berminyak dan rentan berjerawat'
  }
];

const formatPrice = (price) =>
  'Rp' + price.toLocaleString('id-ID');

function Products() {
  const [isCartOpen, setIsCartOpen] = useState(false);
  const {
    totalItems,
    addToCart: addProductToCart
  } = useCart();
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('Semua');
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [notification, setNotification] = useState('');

  const categories = [
    'Semua', 'Cleanser', 'Moisturizer', 'Serum', 'Sunscreen'
  ];

  const filteredProducts = products.filter(product => {
    const matchSearch = product.name.toLowerCase().includes(search.toLowerCase());
    const matchCategory = category === 'Semua' || product.category === category;

    return matchSearch && matchCategory;
  });

 const handleAddToCart = () => {
    addProductToCart(selectedProduct, quantity);

    setNotification(
      `${selectedProduct.name} berhasil dimasukkan ke keranjang!`
    );

    setSelectedProduct(null);
    setQuantity(1);

    setTimeout(() => setNotification(''), 3000);
  };

  const openDetail = (product) => {
    setSelectedProduct(product);
    setQuantity(1);
  };

  return (
    <div className="products-page">

      <header className="products-navbar">
        <Link to="/dashboard" className="products-brand">
          <div className="products-logo">RD</div>
          <span>Rijema <b>Dira</b></span>
        </Link>

        <nav className="products-nav-links">
          <Link to="/dashboard">Beranda</Link>
          <a href="#catalog">Produk</a>
          <Link to="/chatbot">Konsultasi</Link>
        </nav>

        <div className="products-nav-actions">
        <button
            className="cart-link"
            onClick={() => setIsCartOpen(true)}
        >
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
            Pilih skincare yang sesuai dengan kebutuhan dan karakteristik kulitmu.
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
                onChange={e => setSearch(e.target.value)}
              />
            </div>

            <span className="product-total">
              {filteredProducts.length} Produk ditemukan
            </span>
          </div>

          <div className="category-filters">
            {categories.map(item => (
              <button
                key={item}
                className={category === item ? 'category-active' : ''}
                onClick={() => setCategory(item)}
              >
                {item}
              </button>
            ))}
          </div>

          <div className="products-grid">
            {filteredProducts.map(product => (
              <article className="product-card" key={product.id}>

                <button
                  className="product-image-button"
                  onClick={() => openDetail(product)}
                  aria-label={`Lihat ${product.name}`}
                >
                  <img src={product.image} alt={product.name} />
                  <span className="product-category">
                    {product.category}
                  </span>
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
          onClick={() => setSelectedProduct(null)}
        >
          <div
            className="product-modal"
            onClick={e => e.stopPropagation()}
          >

            <button
              className="modal-close"
              onClick={() => setSelectedProduct(null)}
              aria-label="Tutup detail"
            >
              <X size={20} />
            </button>

            <div className="modal-image">
              <img
                src={selectedProduct.image}
                alt={selectedProduct.name}
              />
            </div>

            <div className="modal-details">

              <span className="modal-category">
                {selectedProduct.category}
              </span>

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
                  {selectedProduct.ingredients.map(item => (
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
                    onClick={() => setQuantity(q => Math.max(1, q - 1))}
                    aria-label="Kurangi jumlah"
                  >
                    <Minus size={15} />
                  </button>

                  <strong>{quantity}</strong>

                  <button
                    onClick={() => setQuantity(q => q + 1)}
                    aria-label="Tambah jumlah"
                  >
                    <Plus size={15} />
                  </button>
                </div>
              </div>

              <button
              className="add-cart-button"
              onClick={handleAddToCart}
              >
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
            console.log('Menuju checkout');
        }}
        />

        </div>
        );
}

export default Products;
