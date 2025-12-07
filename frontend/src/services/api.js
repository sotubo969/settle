import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API_BASE = `${BACKEND_URL}/api`;

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
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

// Handle response errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear user data and redirect to login
      localStorage.removeItem('afroUser');
      window.location.href = '/login';
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
    const response = await apiClient.post('/cart/add', {
      productId,
      quantity,
    });
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

// ============ PRODUCT API ============
export const productAPI = {
  getProducts: async (params = {}) => {
    const response = await apiClient.get('/products', { params });
    return response.data;
  },

  getProductById: async (id) => {
    const response = await apiClient.get(`/products/${id}`);
    return response.data;
  },
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
