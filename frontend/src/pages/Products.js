import { useState, useEffect } from 'react';
import { useSearchParams, Link, useNavigate } from 'react-router-dom';
import { Star, Filter, X, ShoppingCart, Plus } from 'lucide-react';
import axios from 'axios';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { ProductGridSkeleton } from '../components/Skeletons';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Checkbox } from '../components/ui/checkbox';
import { Label } from '../components/ui/label';
import { Input } from '../components/ui/input';
import { Slider } from '../components/ui/slider';
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '../components/ui/sheet';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { categories } from '../mock';
import { useCart } from '../context/CartContext';
import { useAuth } from '../context/AuthContext';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Products = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [allProducts, setAllProducts] = useState([]);
  const [filteredProducts, setFilteredProducts] = useState([]);
  const [selectedCategories, setSelectedCategories] = useState([]);
  const [priceRange, setPriceRange] = useState([0, 100]);
  const [sortBy, setSortBy] = useState('featured');
  const [loading, setLoading] = useState(true);
  const [addingToCart, setAddingToCart] = useState({});
  const { addToCart } = useCart();
  const { user } = useAuth();
  
  // Dynamic page title based on category/search
  useEffect(() => {
    const categorySlug = searchParams.get('category');
    const searchQuery = searchParams.get('search');
    
    let pageTitle = 'All Products';
    if (searchQuery) {
      pageTitle = `Search: "${searchQuery}"`;
    } else if (categorySlug) {
      const category = categories.find(c => c.slug === categorySlug);
      if (category) {
        pageTitle = category.name;
      }
    }
    
    document.title = `${pageTitle} | AfroMarket UK - Authentic African Groceries`;
    
    // Cleanup on unmount
    return () => {
      document.title = 'AfroMarket UK - Authentic African Groceries';
    };
  }, [searchParams]);
  
  const handleAddToCart = async (e, product) => {
    e.preventDefault(); // Prevent navigation
    e.stopPropagation(); // Stop event bubbling
    
    // Check if user is logged in
    if (!user) {
      toast.info('Please sign in to add items to your cart', {
        action: {
          label: 'Sign In',
          onClick: () => navigate('/login')
        }
      });
      return;
    }
    
    setAddingToCart(prev => ({ ...prev, [product.id]: true }));
    try {
      await addToCart(product);
      toast.success(`${product.name} added to cart!`);
    } catch (error) {
      toast.error('Failed to add to cart');
      console.error('Add to cart error:', error);
    } finally {
      setAddingToCart(prev => ({ ...prev, [product.id]: false }));
    }
  };

  // Helper to transform product data from snake_case to camelCase
  const transformProduct = (product) => {
    if (!product) return product;
    return {
      ...product,
      inStock: product.in_stock ?? product.inStock ?? true,
      stock: product.stock_quantity ?? product.stock ?? 100,
      stockQuantity: product.stock_quantity ?? product.stockQuantity ?? 100,
      vendorId: product.vendor_id ?? product.vendorId,
      reviewCount: product.review_count ?? product.reviewCount ?? 0,
    };
  };

  // Fetch products from backend
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await axios.get(`${API}/products`);
        // Transform products from snake_case to camelCase
        const products = Array.isArray(response.data) 
          ? response.data.map(transformProduct) 
          : [];
        setAllProducts(products);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching products:', error);
        setLoading(false);
      }
    };
    fetchProducts();
  }, []);

  useEffect(() => {
    let filtered = [...allProducts];

    // Search filter
    const searchQuery = searchParams.get('search');
    if (searchQuery) {
      filtered = filtered.filter(p =>
        p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.brand.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.category.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Category filter from URL
    const categorySlug = searchParams.get('category');
    if (categorySlug) {
      const category = categories.find(c => c.slug === categorySlug);
      if (category) {
        filtered = filtered.filter(p => p.categoryId === category.id);
      }
    }

    // Category filter from checkboxes
    if (selectedCategories.length > 0) {
      filtered = filtered.filter(p => selectedCategories.includes(p.categoryId));
    }

    // Price filter
    filtered = filtered.filter(p => p.price >= priceRange[0] && p.price <= priceRange[1]);

    // Sorting
    switch (sortBy) {
      case 'price-low':
        filtered.sort((a, b) => a.price - b.price);
        break;
      case 'price-high':
        filtered.sort((a, b) => b.price - a.price);
        break;
      case 'rating':
        filtered.sort((a, b) => b.rating - a.rating);
        break;
      case 'newest':
        filtered.sort((a, b) => b.id - a.id);
        break;
      default:
        break;
    }

    setFilteredProducts(filtered);
  }, [searchParams, selectedCategories, priceRange, sortBy, allProducts]);

  const toggleCategory = (categoryId) => {
    setSelectedCategories(prev =>
      prev.includes(categoryId)
        ? prev.filter(id => id !== categoryId)
        : [...prev, categoryId]
    );
  };

  const clearFilters = () => {
    setSelectedCategories([]);
    setPriceRange([0, 50]);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-8">
            <div className="h-10 bg-gray-200 rounded w-1/4 animate-pulse"></div>
            <div className="h-5 bg-gray-200 rounded w-1/6 mt-2 animate-pulse"></div>
          </div>
          <div className="flex flex-col lg:flex-row gap-8">
            {/* Sidebar skeleton */}
            <aside className="hidden lg:block w-64 flex-shrink-0">
              <div className="bg-white rounded-xl shadow-lg p-6 space-y-4 animate-pulse">
                <div className="h-6 bg-gray-200 rounded w-1/2"></div>
                {Array.from({ length: 6 }).map((_, i) => (
                  <div key={i} className="h-5 bg-gray-200 rounded w-3/4"></div>
                ))}
                <div className="h-6 bg-gray-200 rounded w-1/2 mt-6"></div>
                <div className="h-8 bg-gray-200 rounded w-full"></div>
              </div>
            </aside>
            {/* Products grid skeleton */}
            <div className="flex-1">
              <ProductGridSkeleton count={8} />
            </div>
          </div>
        </div>
      </div>
    );
  }

  const FilterSection = () => (
    <div className="space-y-6">
      {/* Categories */}
      <div>
        <h3 className="font-semibold text-lg mb-3">Categories</h3>
        <div className="space-y-2">
          {categories.map(category => (
            <div key={category.id} className="flex items-center space-x-2">
              <Checkbox
                id={`cat-${category.id}`}
                checked={selectedCategories.includes(category.id)}
                onCheckedChange={() => toggleCategory(category.id)}
              />
              <Label htmlFor={`cat-${category.id}`} className="text-sm cursor-pointer">
                {category.name}
              </Label>
            </div>
          ))}
        </div>
      </div>

      {/* Price Range */}
      <div>
        <h3 className="font-semibold text-lg mb-3">Price Range</h3>
        <div className="space-y-4">
          <Slider
            value={priceRange}
            onValueChange={setPriceRange}
            max={100}
            step={1}
            className="w-full"
          />
          <div className="flex justify-between items-center gap-2">
            <div className="flex-1">
              <Label className="text-xs">Min</Label>
              <Input
                type="number"
                value={priceRange[0]}
                onChange={(e) => setPriceRange([Number(e.target.value), priceRange[1]])}
                min={0}
                max={priceRange[1]}
                className="h-9"
              />
            </div>
            <span className="text-gray-400 mt-5">-</span>
            <div className="flex-1">
              <Label className="text-xs">Max</Label>
              <Input
                type="number"
                value={priceRange[1]}
                onChange={(e) => setPriceRange([priceRange[0], Number(e.target.value)])}
                min={priceRange[0]}
                max={50}
                className="h-9"
              />
            </div>
          </div>
          <div className="text-center text-sm text-gray-600">
            £{priceRange[0]} - £{priceRange[1]}
          </div>
        </div>
      </div>

      <Button onClick={clearFilters} variant="outline" className="w-full">
        <X className="h-4 w-4 mr-2" />
        Clear Filters
      </Button>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <div className="max-w-7xl mx-auto px-3 sm:px-4 py-4 sm:py-8">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4 sm:mb-6 gap-2 sm:gap-4">
          <div>
            <h1 className="text-xl sm:text-3xl font-bold text-gray-900 mb-1 sm:mb-2">
              {searchParams.get('search') 
                ? `Search results for "${searchParams.get('search')}"` 
                : searchParams.get('category')
                  ? categories.find(c => c.slug === searchParams.get('category'))?.name || 'All Products'
                  : 'All Products'}
            </h1>
            <p className="text-sm sm:text-base text-gray-600">{filteredProducts.length} products found</p>
          </div>

          <div className="flex items-center gap-2 sm:gap-4 w-full sm:w-auto">
            {/* Mobile Filter */}
            <Sheet>
              <SheetTrigger asChild>
                <Button variant="outline" className="lg:hidden">
                  <Filter className="h-4 w-4 mr-2" />
                  Filters
                </Button>
              </SheetTrigger>
              <SheetContent side="left" className="w-80">
                <SheetHeader>
                  <SheetTitle>Filters</SheetTitle>
                </SheetHeader>
                <div className="mt-6">
                  <FilterSection />
                </div>
              </SheetContent>
            </Sheet>

            {/* Sort Dropdown */}
            <Select value={sortBy} onValueChange={setSortBy}>
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue placeholder="Sort by" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="featured">Featured</SelectItem>
                <SelectItem value="price-low">Price: Low to High</SelectItem>
                <SelectItem value="price-high">Price: High to Low</SelectItem>
                <SelectItem value="rating">Customer Rating</SelectItem>
                <SelectItem value="newest">Newest First</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="flex gap-4 sm:gap-8">
          {/* Desktop Filters */}
          <aside className="hidden lg:block w-64 flex-shrink-0">
            <Card className="sticky top-24">
              <CardContent className="p-6">
                <FilterSection />
              </CardContent>
            </Card>
          </aside>

          {/* Products Grid */}
          <div className="flex-1">
            {filteredProducts.length === 0 ? (
              <div className="text-center py-16">
                <p className="text-xl text-gray-600 mb-4">No products found</p>
                <Button onClick={clearFilters} variant="outline">
                  Clear Filters
                </Button>
              </div>
            ) : (
              <div className="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-3 gap-2 sm:gap-6">
                {filteredProducts.map((product) => (
                  <Card key={product.id} className="group hover:shadow-xl transition-all duration-300 hover:-translate-y-1 h-full flex flex-col">
                    <Link to={`/product/${product.id}`} className="flex-1">
                      <CardContent className="p-2 sm:p-4">
                        <div className="relative mb-2 sm:mb-4 overflow-hidden rounded-lg">
                          {product.originalPrice && (
                            <Badge className="absolute top-1 left-1 sm:top-2 sm:left-2 bg-red-500 text-white z-10 text-xs px-1 sm:px-2">
                              {Math.round(((product.originalPrice - product.price) / product.originalPrice) * 100)}% OFF
                            </Badge>
                          )}
                          {!product.inStock && (
                            <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                              <Badge variant="destructive" className="text-sm">Out of Stock</Badge>
                            </div>
                          )}
                          <img
                            src={product.image}
                            alt={product.name}
                            className="w-full h-32 sm:h-56 object-cover group-hover:scale-110 transition-transform duration-500"
                          />
                        </div>
                        <div className="space-y-1 sm:space-y-2">
                          <p className="text-xs sm:text-sm text-emerald-600 font-medium truncate">{product.brand}</p>
                          <h3 className="font-semibold text-xs sm:text-base text-gray-900 line-clamp-2 group-hover:text-emerald-600 transition-colors leading-tight">
                            {product.name}
                          </h3>
                          <div className="flex items-center gap-1">
                            <div className="flex items-center gap-0.5">
                              <Star className="h-3 w-3 sm:h-4 sm:w-4 fill-yellow-400 text-yellow-400" />
                              <span className="text-xs sm:text-sm font-medium">{product.rating}</span>
                            </div>
                            <span className="text-xs text-gray-500">({product.reviews})</span>
                          </div>
                          <div className="flex items-baseline gap-1 sm:gap-2">
                            <span className="text-base sm:text-2xl font-bold text-emerald-600">£{product.price.toFixed(2)}</span>
                            {product.originalPrice && (
                              <span className="text-xs sm:text-sm text-gray-500 line-through">£{product.originalPrice.toFixed(2)}</span>
                            )}
                          </div>
                          <p className="text-xs text-gray-600 truncate">by {product.vendor?.name || product.vendorName || 'AfroMarket Vendor'}</p>
                          {product.stock < 20 && product.inStock && (
                            <Badge variant="outline" className="text-red-600 border-red-300 text-xs px-1">
                              Only {product.stock} left
                            </Badge>
                          )}
                        </div>
                      </CardContent>
                    </Link>
                    {/* Add to Cart Button - Outside Link */}
                    <div className="p-2 sm:p-4 pt-0">
                      <Button
                        onClick={(e) => handleAddToCart(e, product)}
                        disabled={!product.inStock || addingToCart[product.id]}
                        className="w-full bg-emerald-600 hover:bg-emerald-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
                        size="sm"
                      >
                        {addingToCart[product.id] ? (
                          <>
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                            Adding...
                          </>
                        ) : product.inStock ? (
                          <>
                            <ShoppingCart className="h-4 w-4 mr-2" />
                            Add to Cart
                          </>
                        ) : (
                          'Out of Stock'
                        )}
                      </Button>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default Products;