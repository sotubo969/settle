import React, { createContext, useContext, useState, useEffect } from 'react';
import { getCart, saveCart, addToCart as addToCartMock, removeFromCart as removeFromCartMock, updateCartQuantity as updateCartQuantityMock, clearCart as clearCartMock } from '../mock';

const CartContext = createContext();

export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
};

export const CartProvider = ({ children }) => {
  const [cart, setCart] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const savedCart = getCart();
    setCart(savedCart);
    setIsLoading(false);
  }, []);

  const addToCart = (product, quantity = 1) => {
    const updatedCart = addToCartMock(product, quantity);
    setCart(updatedCart);
  };

  const removeFromCart = (productId) => {
    const updatedCart = removeFromCartMock(productId);
    setCart(updatedCart);
  };

  const updateQuantity = (productId, quantity) => {
    const updatedCart = updateCartQuantityMock(productId, quantity);
    setCart(updatedCart);
  };

  const clearCart = () => {
    const updatedCart = clearCartMock();
    setCart(updatedCart);
  };

  const getCartTotal = () => {
    return cart.reduce((total, item) => total + (item.price * item.quantity), 0);
  };

  const getCartCount = () => {
    return cart.reduce((count, item) => count + item.quantity, 0);
  };

  const value = {
    cart,
    addToCart,
    removeFromCart,
    updateQuantity,
    clearCart,
    getCartTotal,
    getCartCount,
    isLoading,
  };

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
};