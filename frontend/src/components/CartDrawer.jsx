import { X, Plus, Minus, Trash2, ShoppingBag } from "lucide-react";
import { useCart } from "../context/CartContext";
import "../styles/Cart.css";

function CartDrawer({ isOpen, onClose, onCheckout }) {
  const { cartItems, removeFromCart, updateQuantity, totalItems, totalPrice } =
    useCart();

  const formatPrice = (price) =>
    new Intl.NumberFormat("id-ID", {
      style: "currency",
      currency: "IDR",
      maximumFractionDigits: 0,
    }).format(price);

  if (!isOpen) return null;

  return (
    <div className="cart-overlay" onClick={onClose}>
      <aside
        className="cart-drawer"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="cart-header">
          <div>
            <span className="cart-eyebrow">RIJEMA DIRA</span>
            <h2>Keranjang Belanja</h2>
            <p>{totalItems} produk dipilih</p>
          </div>

          <button className="cart-close" onClick={onClose}>
            <X size={21} />
          </button>
        </div>

        <div className="cart-body">
          {cartItems.length === 0 ? (
            <div className="cart-empty">
              <ShoppingBag size={48} strokeWidth={1.2} />
              <h3>Keranjangmu masih kosong</h3>
              <p>Yuk, temukan skincare yang sesuai dengan kebutuhan kulitmu.</p>
              <button onClick={onClose}>Mulai Belanja</button>
            </div>
          ) : (
            cartItems.map((item) => (
              <div className="cart-item" key={item.id}>
                <img src={item.image} alt={item.name} />

                <div className="cart-item-info">
                  <h3>{item.name}</h3>

                  <strong>{formatPrice(Number(item.price || 0))}</strong>

                  <div className="cart-item-actions">
                    <div className="quantity-control">
                      <button
                        onClick={() =>
                          updateQuantity(item.id, item.quantity - 1)
                        }
                      >
                        <Minus size={14} />
                      </button>

                      <span>{item.quantity}</span>

                      <button
                        onClick={() =>
                          updateQuantity(item.id, item.quantity + 1)
                        }
                      >
                        <Plus size={14} />
                      </button>
                    </div>

                    <button
                      className="cart-remove"
                      onClick={() => removeFromCart(item.id)}
                      aria-label={`Hapus ${item.name}`}
                    >
                      <Trash2 size={17} />
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        {cartItems.length > 0 && (
          <div className="cart-footer">
            <div className="cart-total">
              <span>Total Belanja</span>
              <strong>{formatPrice(totalPrice)}</strong>
            </div>

            <button className="cart-checkout" onClick={onCheckout}>
              Lanjut Checkout
            </button>

            <p>Terima kasih telah memilih Rijema Dira.</p>
          </div>
        )}
      </aside>
    </div>
  );
}

export default CartDrawer;
