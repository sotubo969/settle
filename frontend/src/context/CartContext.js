import React, { createContext, useContext, useState, useEffect } from 'react';
import { cartAPI } from '../services/api';
import { useAuth } from './AuthContext';

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
  const { isAuthenticated } = useAuth();

  // Fetch cart from backend
  const fetchCart = async () => {
    if (!isAuthenticated) {
      setCart([]);
      setIsLoading(false);
      return;
    }

    try {
      setIsLoading(true);
      const response = await cartAPI.getCart();
      // Flatten product data onto cart items for easier access in components
      const items = (response.items || []).map(item => ({
        ...item,
        // Spread product properties directly onto item for backward compatibility
        ...(item.product || {}),
        // Keep original item properties that shouldn't be overridden
        id: item.product_id || item.id,
        quantity: item.quantity,
        cartItemId: item.id,
      }));
      setCart(items);
    } catch (error) {
      console.error('Error fetching cart:', error);
      setCart([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCart();
  }, [isAuthenticated]);

  const addToCart = async (product, quantity = 1) => {
    if (!isAuthenticated) {
      throw new Error('Please login to add items to cart');
    }

    try {
      await cartAPI.addToCart(product.id, quantity);
      await fetchCart(); // Refresh cart from backend
    } catch (error) {
      console.error('Error adding to cart:', error);
      throw error;
    }
  };

  const removeFromCart = async (productId) => {
    if (!isAuthenticated) {
      throw new Error('Please login to modify cart');
    }

    try {
      await cartAPI.removeFromCart(productId);
      await fetchCart(); // Refresh cart from backend
    } catch (error) {
      console.error('Error removing from cart:', error);
      throw error;
    }
  };

  const updateQuantity = async (productId, quantity) => {
    if (!isAuthenticated) {
      throw new Error('Please login to modify cart');
    }

    try {
      await cartAPI.updateQuantity(productId, quantity);
      await fetchCart(); // Refresh cart from backend
    } catch (error) {
      console.error('Error updating quantity:', error);
      throw error;
    }
  };

  const clearCart = async () => {
    if (!isAuthenticated) {
      throw new Error('Please login to clear cart');
    }

    try {
      await cartAPI.clearCart();
      setCart([]);
    } catch (error) {
      console.error('Error clearing cart:', error);
      throw error;
    }
  };

  const getCartTotal = () => {
    return cart.reduce((total, item) => {
      const price = item.price || 0;
      const quantity = item.quantity || 0;
      return total + (price * quantity);
    }, 0);
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
    refreshCart: fetchCart,
  };

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
};