import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API_BASE = `${BACKEND_URL}/api`;

// Track if we're already redirecting to prevent multiple redirects
let isRedirecting = false;

// Simple in-memory cache for GET requests
const cache = new Map();
const CACHE_TTL = 60000; // 1 minute cache

const getCached = (key) => {
  const item = cache.get(key);
  if (item && Date.now() - item.timestamp < CACHE_TTL) {
    return item.data;
  }
  cache.delete(key);
  return null;
};

const setCache = (key, data) => {
  cache.set(key, { data, timestamp: Date.now() });
};

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000, // 15 second timeout for faster failure
});

// Add auth token to requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('afroToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle response errors - IMPROVED to prevent aggressive logout
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Only handle 401 for specific auth endpoints, not all endpoints
    if (error.response?.status === 401) {
      const url = error.config?.url || '';
      
      // Only force logout for core auth endpoints, not owner-specific ones
      const isAuthEndpoint = url.includes('/auth/me') || url.includes('/auth/verify');
      const isOwnerEndpoint = url.includes('/owner/') || url.includes('/admin/');
      
      // Don't force logout for owner endpoints - just reject the promise
      if (isOwnerEndpoint) {
        console.warn('Owner endpoint 401 - not forcing logout');
        return Promise.reject(error);
      }
      
      // For auth endpoints, clear credentials and redirect (but only once)
      if (isAuthEndpoint && !isRedirecting) {
        console.log('Auth verification failed - logging out');
        isRedirecting = true;
        localStorage.removeItem('afroToken');
        localStorage.removeItem('afroUser');
        setTimeout(() => {
          isRedirecting = false;
          window.location.href = '/login';
        }, 100);
      }
    }
    return Promise.reject(error);
  }
);

// ============ CART API ============
export const cartAPI = {
  getCart: async () => {
    const response = await apiClient.get('/cart');
    return response.data;
  },

  addToCart: async (productId, quantity = 1) => {
    // Backend expects query parameters, not body
    const response = await apiClient.post(`/cart/add?product_id=${productId}&quantity=${quantity}`);
    return response.data;
  },

  updateQuantity: async (productId, quantity) => {
    const response = await apiClient.put(`/cart/update/${productId}?quantity=${quantity}`);
    return response.data;
  },

  removeFromCart: async (productId) => {
    const response = await apiClient.delete(`/cart/remove/${productId}`);
    return response.data;
  },

  clearCart: async () => {
    const response = await apiClient.delete('/cart/clear');
    return response.data;
  },
};

// ============ AUTH API ============
export const authAPI = {
  register: async (name, email, password) => {
    const response = await apiClient.post('/auth/register', {
      name,
      email,
      password,
    });
    return response.data;
  },

  login: async (email, password) => {
    const response = await apiClient.post('/auth/login', {
      email,
      password,
    });
    return response.data;
  },

  googleLogin: async (token) => {
    const response = await apiClient.post('/auth/google', {
      token,
    });
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },
};

// Helper to transform product data from snake_case to camelCase for frontend
const transformProduct = (product) => {
  if (!product) return product;
  return {
    ...product,
    inStock: product.in_stock ?? product.inStock ?? true,
    stock: product.stock_quantity ?? product.stock ?? 100,
    stockQuantity: product.stock_quantity ?? product.stockQuantity ?? 100,
    vendorId: product.vendor_id ?? product.vendorId,
    createdAt: product.created_at ?? product.createdAt,
    updatedAt: product.updated_at ?? product.updatedAt,
    reviewCount: product.review_count ?? product.reviewCount ?? 0,
    originalPrice: product.original_price ?? product.originalPrice,
  };
};

// ============ PRODUCT API (with caching) ============
export const productAPI = {
  getProducts: async (params = {}) => {
    const cacheKey = `products_${JSON.stringify(params)}`;
    const cached = getCached(cacheKey);
    if (cached) return cached;
    
    const response = await apiClient.get('/products', { params });
    // Transform array of products
    const transformedData = Array.isArray(response.data) 
      ? response.data.map(transformProduct)
      : response.data;
    setCache(cacheKey, transformedData);
    return transformedData;
  },

  getProductById: async (id) => {
    const cacheKey = `product_${id}`;
    const cached = getCached(cacheKey);
    if (cached) return cached;
    
    const response = await apiClient.get(`/products/${id}`);
    // Transform single product
    const transformedData = transformProduct(response.data);
    setCache(cacheKey, transformedData);
    return transformedData;
  },
  
  // Clear cache when needed
  clearCache: () => {
    cache.clear();
  }
};

// ============ ORDER API ============
export const orderAPI = {
  createOrder: async (orderData) => {
    const response = await apiClient.post('/orders', orderData);
    return response.data;
  },

  getOrders: async () => {
    const response = await apiClient.get('/orders');
    return response.data;
  },

  getOrderById: async (id) => {
    const response = await apiClient.get(`/orders/${id}`);
    return response.data;
  },
};

// ============ VENDOR API ============
export const vendorAPI = {
  register: async (vendorData) => {
    const response = await apiClient.post('/vendors/register', vendorData);
    return response.data;
  },

  getDashboardStats: async () => {
    const response = await apiClient.get('/vendor/dashboard/stats');
    return response.data;
  },

  getProducts: async () => {
    const response = await apiClient.get('/vendor/products');
    return response.data;
  },

  addProduct: async (productData) => {
    const response = await apiClient.post('/vendor/products', productData);
    return response.data;
  },

  updateProduct: async (productId, productData) => {
    const response = await apiClient.put(`/vendor/products/${productId}`, productData);
    return response.data;
  },

  deleteProduct: async (productId) => {
    const response = await apiClient.delete(`/vendor/products/${productId}`);
    return response.data;
  },
};

export default apiClient;
