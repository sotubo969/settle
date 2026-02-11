import { useState, useEffect, useCallback } from 'react';

const STORAGE_KEY = 'afromarket_recently_viewed';
const MAX_ITEMS = 10;

/**
 * Hook to track and retrieve recently viewed products
 * Persists to localStorage for cross-session retention
 */
export const useRecentlyViewed = () => {
  const [recentlyViewed, setRecentlyViewed] = useState([]);

  // Load from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        setRecentlyViewed(Array.isArray(parsed) ? parsed : []);
      }
    } catch (error) {
      console.error('Error loading recently viewed:', error);
      setRecentlyViewed([]);
    }
  }, []);

  // Save to localStorage when list changes
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(recentlyViewed));
    } catch (error) {
      console.error('Error saving recently viewed:', error);
    }
  }, [recentlyViewed]);

  // Add a product to recently viewed
  const addToRecentlyViewed = useCallback((product) => {
    if (!product || !product.id) return;

    setRecentlyViewed((prev) => {
      // Remove if already exists (to move to front)
      const filtered = prev.filter((item) => item.id !== product.id);
      
      // Create a minimal product object for storage
      const minimalProduct = {
        id: product.id,
        name: product.name,
        price: product.price,
        image: product.image,
        brand: product.brand,
        category: product.category,
        rating: product.rating,
        inStock: product.inStock ?? product.in_stock ?? true,
        viewedAt: new Date().toISOString(),
      };

      // Add to front and limit to MAX_ITEMS
      return [minimalProduct, ...filtered].slice(0, MAX_ITEMS);
    });
  }, []);

  // Remove a product from recently viewed
  const removeFromRecentlyViewed = useCallback((productId) => {
    setRecentlyViewed((prev) => prev.filter((item) => item.id !== productId));
  }, []);

  // Clear all recently viewed
  const clearRecentlyViewed = useCallback(() => {
    setRecentlyViewed([]);
    localStorage.removeItem(STORAGE_KEY);
  }, []);

  return {
    recentlyViewed,
    addToRecentlyViewed,
    removeFromRecentlyViewed,
    clearRecentlyViewed,
  };
};

export default useRecentlyViewed;
