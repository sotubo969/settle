// Mock data for African Grocery Marketplace

export const categories = [
  { id: 1, name: 'Fresh Produce', slug: 'fresh-produce', icon: '🌿', image: 'https://images.unsplash.com/photo-1610348725531-843dff563e2c?w=400' },
  { id: 2, name: 'Grains & Flours', slug: 'grains-flours', icon: '🌾', image: 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400' },
  { id: 3, name: 'Condiments & Seasonings', slug: 'condiments', icon: '🌶️', image: 'https://images.unsplash.com/photo-1596040033229-a0b1e2e89a7d?w=400' },
  { id: 4, name: 'Frozen Foods & Meats', slug: 'frozen-meats', icon: '🥩', image: 'https://images.unsplash.com/photo-1607623814075-e51df1bdc82f?w=400' },
  { id: 5, name: 'Snacks & Confectionery', slug: 'snacks', icon: '🍿', image: 'https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=400' },
  { id: 6, name: 'Drinks & Beverages', slug: 'drinks', icon: '🥤', image: 'https://images.unsplash.com/photo-1544145945-35cd6b44be0b?w=400' },
  { id: 7, name: 'Dried & Preserved Foods', slug: 'dried-foods', icon: '🐟', image: 'https://images.unsplash.com/photo-1599639957043-f4520e1a5586?w=400' },
  { id: 8, name: 'Beauty & Household', slug: 'beauty-household', icon: '💄', image: 'https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=400' },
];

export const vendors = [
  { id: 1, name: 'Surulere Foods London', rating: 4.8, totalSales: 1250, location: 'London', verified: true },
  { id: 2, name: 'Niyis African Store', rating: 4.9, totalSales: 2100, location: 'Manchester', verified: true },
  { id: 3, name: 'Owino Supermarket', rating: 4.7, totalSales: 890, location: 'Birmingham', verified: true },
  { id: 4, name: '4Way Foods Market', rating: 4.6, totalSales: 1560, location: 'Leeds', verified: true },
  { id: 5, name: 'Wosiwosi Groceries', rating: 4.9, totalSales: 1980, location: 'London', verified: true },
];

export const products = [
  {
    id: 1,
    name: 'Ayoola Poundo Yam Flour',
    brand: 'Ayoola',
    price: 8.99,
    originalPrice: 10.99,
    image: 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=600',
    category: 'Grains & Flours',
    categoryId: 2,
    vendor: vendors[0],
    vendorId: 1,
    rating: 4.7,
    reviews: 124,
    stock: 45,
    description: 'Premium quality poundo yam flour, perfect for making traditional pounded yam. 100% natural, no additives.',
    weight: '1.5kg',
    inStock: true,
    featured: true,
  },
  {
    id: 2,
    name: 'Fresh Plantains (Bundle)',
    brand: 'Fresh Farms',
    price: 3.49,
    image: 'https://images.unsplash.com/photo-1610348725531-843dff563e2c?w=600',
    category: 'Fresh Produce',
    categoryId: 1,
    vendor: vendors[1],
    vendorId: 2,
    rating: 4.9,
    reviews: 89,
    stock: 120,
    description: 'Fresh ripe plantains, hand-selected for quality. Perfect for frying or boiling.',
    weight: '1kg (4-5 pieces)',
    inStock: true,
    featured: true,
  },
  {
    id: 3,
    name: 'Tropical Sun Nigerian Curry Powder',
    brand: 'Tropical Sun',
    price: 4.99,
    originalPrice: 6.49,
    image: 'https://images.unsplash.com/photo-1596040033229-a0b1e2e89a7d?w=600',
    category: 'Condiments & Seasonings',
    categoryId: 3,
    vendor: vendors[2],
    vendorId: 3,
    rating: 4.8,
    reviews: 256,
    stock: 78,
    description: 'Authentic Nigerian curry powder blend. Rich flavor perfect for jollof rice, stews, and soups.',
    weight: '400g',
    inStock: true,
    featured: true,
  },
  {
    id: 4,
    name: 'Rombis Roasted Groundnuts',
    brand: 'Rombis',
    price: 2.99,
    image: 'https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=600',
    category: 'Snacks & Confectionery',
    categoryId: 5,
    vendor: vendors[3],
    vendorId: 4,
    rating: 4.6,
    reviews: 67,
    stock: 95,
    description: 'Crunchy roasted groundnuts with authentic African flavor. Perfect snack any time of day.',
    weight: '250g',
    inStock: true,
    featured: false,
  },
  {
    id: 5,
    name: 'Golden Morn Cereal',
    brand: 'Nestle',
    price: 6.49,
    image: 'https://images.unsplash.com/photo-1525385133512-2f3bdd039054?w=600',
    category: 'Grains & Flours',
    categoryId: 2,
    vendor: vendors[4],
    vendorId: 5,
    rating: 4.9,
    reviews: 198,
    stock: 62,
    description: 'Nutritious maize-based breakfast cereal fortified with vitamins. A family favorite!',
    weight: '500g',
    inStock: true,
    featured: true,
  },
  {
    id: 6,
    name: 'Fresh Okra',
    brand: 'Fresh Farms',
    price: 2.49,
    image: 'https://images.unsplash.com/photo-1589621316382-008455f857cd?w=600',
    category: 'Fresh Produce',
    categoryId: 1,
    vendor: vendors[0],
    vendorId: 1,
    rating: 4.7,
    reviews: 45,
    stock: 88,
    description: 'Fresh okra vegetables, carefully selected. Essential for soups and stews.',
    weight: '500g',
    inStock: true,
    featured: false,
  },
  {
    id: 7,
    name: 'Frozen Tilapia Fish',
    brand: 'Ocean Fresh',
    price: 12.99,
    originalPrice: 14.99,
    image: 'https://images.unsplash.com/photo-1544943910-4c1dc44aab44?w=600',
    category: 'Frozen Foods & Meats',
    categoryId: 4,
    vendor: vendors[1],
    vendorId: 2,
    rating: 4.8,
    reviews: 132,
    stock: 34,
    description: 'Premium frozen tilapia fish, cleaned and ready to cook. Rich in protein and omega-3.',
    weight: '1kg',
    inStock: true,
    featured: true,
  },
  {
    id: 8,
    name: 'Dark & Lovely Hair Relaxer Kit',
    brand: 'Dark & Lovely',
    price: 9.99,
    image: 'https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=600',
    category: 'Beauty & Household',
    categoryId: 8,
    vendor: vendors[2],
    vendorId: 3,
    rating: 4.5,
    reviews: 87,
    stock: 56,
    description: 'Professional hair relaxer system for smooth, manageable hair. Includes all essentials.',
    weight: '1 Kit',
    inStock: true,
    featured: false,
  },
  {
    id: 9,
    name: 'Garri White (Cassava Flakes)',
    brand: 'Rombis',
    price: 5.49,
    image: 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=600',
    category: 'Grains & Flours',
    categoryId: 2,
    vendor: vendors[3],
    vendorId: 4,
    rating: 4.9,
    reviews: 215,
    stock: 71,
    description: 'Premium white garri, finely processed cassava flakes. Perfect for eba or soaking.',
    weight: '1kg',
    inStock: true,
    featured: true,
  },
  {
    id: 10,
    name: 'Suya Spice Mix',
    brand: 'Tropical Sun',
    price: 3.99,
    image: 'https://images.unsplash.com/photo-1596040033229-a0b1e2e89a7d?w=600',
    category: 'Condiments & Seasonings',
    categoryId: 3,
    vendor: vendors[4],
    vendorId: 5,
    rating: 4.8,
    reviews: 143,
    stock: 92,
    description: 'Authentic suya spice blend with groundnuts and African spices. Perfect for grilled meats.',
    weight: '200g',
    inStock: true,
    featured: false,
  },
  {
    id: 11,
    name: 'Dried Crayfish',
    brand: 'Ocean Harvest',
    price: 7.99,
    image: 'https://images.unsplash.com/photo-1599639957043-f4520e1a5586?w=600',
    category: 'Dried & Preserved Foods',
    categoryId: 7,
    vendor: vendors[0],
    vendorId: 1,
    rating: 4.7,
    reviews: 98,
    stock: 43,
    description: 'Premium dried crayfish, essential for authentic Nigerian soups and stews.',
    weight: '200g',
    inStock: true,
    featured: false,
  },
  {
    id: 12,
    name: 'Plantain Chips (Spicy)',
    brand: 'Afri Snacks',
    price: 2.49,
    image: 'https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=600',
    category: 'Snacks & Confectionery',
    categoryId: 5,
    vendor: vendors[1],
    vendorId: 2,
    rating: 4.6,
    reviews: 76,
    stock: 104,
    description: 'Crispy spicy plantain chips, made from fresh plantains. Addictively delicious!',
    weight: '150g',
    inStock: true,
    featured: false,
  },
];

export const banners = [
  {
    id: 1,
    title: 'Authentic African Groceries',
    subtitle: 'Fresh from trusted vendors across the UK',
    image: 'https://images.unsplash.com/photo-1604719312566-8912e9227c6a?w=1200',
    cta: 'Shop Now',
    link: '/products',
  },
  {
    id: 2,
    title: 'Support Local African Businesses',
    subtitle: 'Connect with verified vendors in your community',
    image: 'https://images.unsplash.com/photo-1542838132-92c53300491e?w=1200',
    cta: 'Explore Vendors',
    link: '/vendors',
  },
  {
    id: 3,
    title: 'Fresh Produce Delivered Daily',
    subtitle: 'Get your favorite ingredients delivered to your door',
    image: 'https://images.unsplash.com/photo-1488459716781-31db52582fe9?w=1200',
    cta: 'Order Now',
    link: '/products?category=fresh-produce',
  },
];

// Mock cart stored in localStorage
export const getCart = () => {
  const cart = localStorage.getItem('afroCart');
  return cart ? JSON.parse(cart) : [];
};

export const saveCart = (cartItems) => {
  localStorage.setItem('afroCart', JSON.stringify(cartItems));
};

export const addToCart = (product, quantity = 1) => {
  const cart = getCart();
  const existingItem = cart.find(item => item.id === product.id);
  
  if (existingItem) {
    existingItem.quantity += quantity;
  } else {
    cart.push({ ...product, quantity });
  }
  
  saveCart(cart);
  return cart;
};

export const removeFromCart = (productId) => {
  const cart = getCart().filter(item => item.id !== productId);
  saveCart(cart);
  return cart;
};

export const updateCartQuantity = (productId, quantity) => {
  const cart = getCart();
  const item = cart.find(item => item.id === productId);
  if (item) {
    item.quantity = quantity;
  }
  saveCart(cart);
  return cart;
};

export const clearCart = () => {
  localStorage.removeItem('afroCart');
  return [];
};

// Mock user authentication
export const mockLogin = (email, password) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const user = {
        id: 1,
        name: 'John Doe',
        email: email,
        role: 'customer',
        avatar: 'https://ui-avatars.com/api/?name=John+Doe',
      };
      localStorage.setItem('afroUser', JSON.stringify(user));
      resolve({ success: true, user });
    }, 1000);
  });
};

export const mockRegister = (name, email, password) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const user = {
        id: Date.now(),
        name: name,
        email: email,
        role: 'customer',
        avatar: `https://ui-avatars.com/api/?name=${name.replace(' ', '+')}`,
      };
      localStorage.setItem('afroUser', JSON.stringify(user));
      resolve({ success: true, user });
    }, 1000);
  });
};

export const getUser = () => {
  const user = localStorage.getItem('afroUser');
  return user ? JSON.parse(user) : null;
};

export const logout = () => {
  localStorage.removeItem('afroUser');
};

// Mock vendor registration
export const mockVendorRegister = (vendorData) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const vendor = {
        id: Date.now(),
        ...vendorData,
        verified: false,
        createdAt: new Date().toISOString(),
      };
      resolve({ success: true, vendor });
    }, 1500);
  });
};

// Mock orders
export const mockOrders = [
  {
    id: 'ORD-2024-001',
    date: '2024-01-15',
    total: 45.67,
    status: 'Delivered',
    items: 3,
  },
  {
    id: 'ORD-2024-002',
    date: '2024-01-20',
    total: 23.45,
    status: 'In Transit',
    items: 2,
  },
];