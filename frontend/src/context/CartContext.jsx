
import { createContext, useContext, useState } from 'react';

const CartContext = createContext();

export function CartProvider({ children }) {
  const [cartItems, setCartItems] = useState([]);

  // Menambahkan produk ke keranjang
const addToCart = (product, quantity = 1) => {
  setCartItems((currentItems) => {
    const existing = currentItems.find(
      (item) => item.id === product.id
    );

    if (existing) {
      return currentItems.map((item) =>
        item.id === product.id
          ? { ...item, quantity: item.quantity + quantity }
          : item
      );
    }

    return [
      ...currentItems,
      { ...product, quantity }
    ];
  });
};

  // Menghapus produk
  const removeFromCart = (id) => {
    setCartItems((items) =>
      items.filter((item) => item.id !== id)
    );
  };

  // Mengubah jumlah produk
  const updateQuantity = (id, quantity) => {
    if (quantity <= 0) {
      removeFromCart(id);
      return;
    }

    setCartItems((items) =>
      items.map((item) =>
        item.id === id ? { ...item, quantity } : item
      )
    );
  };

  // Mengosongkan keranjang
  const clearCart = () => setCartItems([]);

  // Menghitung jumlah seluruh barang
  const totalItems = cartItems.reduce(
    (total, item) => total + item.quantity,
    0
  );

  // Menghitung total harga
  const totalPrice = cartItems.reduce(
    (total, item) => total + Number(item.price || 0) * item.quantity,
    0
  );

  return (
    <CartContext.Provider
      value={{
        cartItems,
        addToCart,
        removeFromCart,
        updateQuantity,
        clearCart,
        totalItems,
        totalPrice,
      }}
    >
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const context = useContext(CartContext);

  if (!context) {
    throw new Error('useCart harus digunakan di dalam CartProvider');
  }

  return context;
}
