import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Star, ShoppingCart, Heart, Share2, MapPin, Package, Shield, ArrowLeft } from 'lucide-react';
import axios from 'axios';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { toast } from 'sonner';
import { useCart } from '../context/CartContext';
import { useAuth } from '../context/AuthContext';
import { productAPI } from '../services/api';
import { useRecentlyViewed } from '../hooks/useRecentlyViewed';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ProductDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [relatedProducts, setRelatedProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { addToCart } = useCart();
  const { isAuthenticated } = useAuth();
  const [quantity, setQuantity] = useState(1);
  const [selectedImage, setSelectedImage] = useState(null);
  const { addToRecentlyViewed } = useRecentlyViewed();

  const fetchProduct = useCallback(async () => {
    if (!id) {
      setError('No product ID provided');
      setLoading(false);
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      console.log('Fetching product with ID:', id);
      const data = await productAPI.getProductById(id);
      
      if (!data) {
        setError('Product not found');
        setLoading(false);
        return;
      }
      
      console.log('Product fetched:', data);
      setProduct(data);
      setSelectedImage(data.image);
      
      // Track this product as recently viewed
      addToRecentlyViewed(data);
      
      // Fetch related products
      if (data.category || data.categoryId) {
        try {
          const relatedData = await productAPI.getProducts({ category: data.category || data.categoryId });
          const filtered = (Array.isArray(relatedData) ? relatedData : []).filter(p => p.id !== id).slice(0, 4);
          setRelatedProducts(filtered);
        } catch (err) {
          console.log('No related products found');
        }
      }
    } catch (error) {
      console.error('Error fetching product:', error);
      setError('Failed to load product');
      toast.error('Failed to load product');
    } finally {
      setLoading(false);
    }
  }, [id, addToRecentlyViewed]);

  useEffect(() => {
    fetchProduct();
  }, [fetchProduct]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="max-w-7xl mx-auto px-4 py-16 text-center">
          <div className="animate-pulse">
            <div className="w-16 h-16 bg-emerald-200 rounded-full mx-auto mb-4"></div>
            <p className="text-xl text-gray-600">Loading product...</p>
          </div>
        </div>
        <Footer />
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="max-w-7xl mx-auto px-4 py-16 text-center">
          <h1 className="text-3xl font-bold mb-4">{error || 'Product Not Found'}</h1>
          <p className="text-gray-600 mb-6">The product you're looking for might have been removed or is temporarily unavailable.</p>
          <Link to="/products">
            <Button className="bg-emerald-600 hover:bg-emerald-700">Browse All Products</Button>
          </Link>
        </div>
        <Footer />
      </div>
    );
  }

  const handleAddToCart = async () => {
    if (!isAuthenticated) {
      toast.error('Please login to add items to cart');
      navigate('/login');
      return;
    }

    try {
      await addToCart(product, quantity);
      toast.success(`${product.name} added to cart!`, {
        description: `Quantity: ${quantity}`,
      });
    } catch (error) {
      toast.error('Failed to add to cart. Please try again.');
    }
  };

  const handleBuyNow = async () => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    try {
      await addToCart(product, quantity);
      navigate('/checkout');
    } catch (error) {
      toast.error('Failed to add to cart. Please try again.');
    }
  };

  const handleAddToWishlist = async () => {
    if (!isAuthenticated) {
      toast.error('Please login to add items to wishlist');
      navigate('/login');
      return;
    }
    
    const token = localStorage.getItem('afroToken');
    try {
      const response = await axios.post(`${API}/wishlist/toggle`, 
        { product_id: product.id },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      if (response.data.in_wishlist) {
        toast.success('Added to wishlist!');
      } else {
        toast.success('Removed from wishlist!');
      }
    } catch (error) {
      console.error('Wishlist error:', error);
      toast.error(error.response?.data?.detail || 'Failed to update wishlist');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <div className="max-w-7xl mx-auto px-4 py-8">
        <Button variant="ghost" onClick={() => navigate(-1)} className="mb-6">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back
        </Button>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-12">
          {/* Product Images */}
          <div className="space-y-4">
            <div className="relative overflow-hidden rounded-xl shadow-lg bg-white p-4">
              <img
                src={selectedImage}
                alt={product.name}
                className="w-full h-[500px] object-contain"
              />
              {product.originalPrice && (
                <Badge className="absolute top-6 left-6 bg-red-500 text-white text-lg px-4 py-2">
                  {Math.round(((product.originalPrice - product.price) / product.originalPrice) * 100)}% OFF
                </Badge>
              )}
            </div>
            <div className="grid grid-cols-4 gap-3">
              {[product.image, product.image, product.image, product.image].map((img, idx) => (
                <button
                  key={idx}
                  onClick={() => setSelectedImage(img)}
                  className={`border-2 rounded-lg overflow-hidden hover:border-emerald-500 transition-colors ${
                    selectedImage === img ? 'border-emerald-500' : 'border-gray-200'
                  }`}
                >
                  <img src={img} alt={`${product.name} ${idx + 1}`} className="w-full h-20 object-cover" />
                </button>
              ))}
            </div>
          </div>

          {/* Product Info */}
          <div className="space-y-6">
            <div>
              <Badge className="mb-3 bg-emerald-100 text-emerald-700 hover:bg-emerald-100">
                {product.category}
              </Badge>
              <h1 className="text-4xl font-bold text-gray-900 mb-3">{product.name}</h1>
              <p className="text-lg text-gray-600">by {product.brand}</p>
            </div>

            {/* Rating */}
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1">
                {[...Array(5)].map((_, i) => (
                  <Star
                    key={i}
                    className={`h-5 w-5 ${
                      i < Math.floor(product.rating)
                        ? 'fill-yellow-400 text-yellow-400'
                        : 'text-gray-300'
                    }`}
                  />
                ))}
              </div>
              <span className="text-lg font-semibold">{product.rating}</span>
              <span className="text-gray-600">({product.reviews} reviews)</span>
            </div>

            {/* Price */}
            <div className="flex items-baseline gap-4 py-4 border-y">
              <span className="text-5xl font-bold text-emerald-600">£{product.price.toFixed(2)}</span>
              {product.originalPrice && (
                <>
                  <span className="text-2xl text-gray-500 line-through">£{product.originalPrice.toFixed(2)}</span>
                  <Badge className="bg-red-500 text-white text-sm">
                    Save £{(product.originalPrice - product.price).toFixed(2)}
                  </Badge>
                </>
              )}
            </div>

            {/* Stock */}
            <div className="flex items-center gap-2">
              {product.stock > 0 ? (
                <>
                  <Badge className="bg-green-100 text-green-700 hover:bg-green-100">In Stock</Badge>
                  {product.stock < 20 && (
                    <span className="text-red-600 font-medium">Only {product.stock} left - order soon!</span>
                  )}
                </>
              ) : (
                <Badge className="bg-red-100 text-red-700 hover:bg-red-100">Out of Stock</Badge>
              )}
            </div>

            {/* Quantity Selector */}
            <div className="flex items-center gap-4">
              <span className="font-semibold text-gray-700">Quantity:</span>
              <div className="flex items-center border-2 rounded-lg">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setQuantity(Math.max(1, quantity - 1))}
                  className="px-4 py-2 text-lg font-bold"
                >
                  -
                </Button>
                <span className="px-6 py-2 font-semibold text-lg border-x-2">{quantity}</span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setQuantity(Math.min(product.stock, quantity + 1))}
                  className="px-4 py-2 text-lg font-bold"
                >
                  +
                </Button>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="space-y-3">
              <Button
                size="lg"
                className="w-full bg-orange-500 hover:bg-orange-600 text-white text-lg py-6 shadow-lg hover:shadow-xl transform hover:scale-105 transition-all"
                onClick={handleBuyNow}
                disabled={product.stock === 0}
              >
                <ShoppingCart className="h-5 w-5 mr-2" />
                Buy Now
              </Button>
              <Button
                size="lg"
                variant="outline"
                className="w-full border-2 border-emerald-600 text-emerald-600 hover:bg-emerald-50 text-lg py-6"
                onClick={handleAddToCart}
                disabled={product.stock === 0}
              >
                Add to Cart
              </Button>
              <div className="flex gap-3">
                <Button variant="outline" className="flex-1" size="lg" onClick={handleAddToWishlist}>
                  <Heart className="h-5 w-5 mr-2" />
                  Wishlist
                </Button>
                <Button variant="outline" className="flex-1" size="lg">
                  <Share2 className="h-5 w-5 mr-2" />
                  Share
                </Button>
              </div>
            </div>

            {/* Vendor Info */}
            <Card className="bg-gradient-to-br from-emerald-50 to-green-50 border-emerald-200">
              <CardContent className="p-6">
                <h3 className="font-semibold text-lg mb-3 flex items-center gap-2">
                  <Store className="h-5 w-5 text-emerald-600" />
                  Sold by {product.vendor?.name || product.vendorName || 'AfroMarket Vendor'}
                </h3>
                <div className="flex items-center gap-4 text-sm text-gray-700">
                  <div className="flex items-center gap-1">
                    <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                    <span className="font-medium">{product.vendor?.rating || product.vendorRating || '4.5'}</span>
                  </div>
                  <span>|</span>
                  <span>{product.vendor?.totalSales || product.vendorSales || '100+'} sales</span>
                  <span>|</span>
                  <div className="flex items-center gap-1">
                    <MapPin className="h-4 w-4" />
                    {product.vendor?.location || product.vendorLocation || 'UK'}
                  </div>
                </div>
                <Button variant="link" className="mt-3 p-0 text-emerald-600">
                  Visit Store
                </Button>
              </CardContent>
            </Card>

            {/* Trust Badges */}
            <div className="grid grid-cols-3 gap-4">
              <div className="flex flex-col items-center text-center p-4 bg-white rounded-lg border">
                <Shield className="h-8 w-8 text-emerald-600 mb-2" />
                <p className="text-xs font-medium">Verified Vendor</p>
              </div>
              <div className="flex flex-col items-center text-center p-4 bg-white rounded-lg border">
                <Package className="h-8 w-8 text-emerald-600 mb-2" />
                <p className="text-xs font-medium">Fast Delivery</p>
              </div>
              <div className="flex flex-col items-center text-center p-4 bg-white rounded-lg border">
                <Star className="h-8 w-8 text-emerald-600 mb-2" />
                <p className="text-xs font-medium">Top Rated</p>
              </div>
            </div>
          </div>
        </div>

        {/* Product Details Tabs */}
        <Card className="mb-12">
          <CardContent className="p-8">
            <Tabs defaultValue="description" className="w-full">
              <TabsList className="grid w-full grid-cols-3 mb-6">
                <TabsTrigger value="description">Description</TabsTrigger>
                <TabsTrigger value="details">Product Details</TabsTrigger>
                <TabsTrigger value="reviews">Reviews ({product.reviews})</TabsTrigger>
              </TabsList>
              <TabsContent value="description" className="space-y-4">
                <h3 className="font-semibold text-xl mb-3">About this product</h3>
                <p className="text-gray-700 leading-relaxed">{product.description}</p>
                <p className="text-gray-700 leading-relaxed">
                  This authentic African grocery item is carefully sourced and quality-checked to ensure you get the best taste and nutritional value. Perfect for preparing traditional dishes and bringing the flavors of home to your kitchen.
                </p>
              </TabsContent>
              <TabsContent value="details" className="space-y-4">
                <h3 className="font-semibold text-xl mb-3">Product Specifications</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex flex-col">
                    <span className="text-gray-600 text-sm">Brand</span>
                    <span className="font-semibold">{product.brand}</span>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-gray-600 text-sm">Weight</span>
                    <span className="font-semibold">{product.weight}</span>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-gray-600 text-sm">Category</span>
                    <span className="font-semibold">{product.category}</span>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-gray-600 text-sm">Availability</span>
                    <span className="font-semibold">{product.stock > 0 ? 'In Stock' : 'Out of Stock'}</span>
                  </div>
                </div>
              </TabsContent>
              <TabsContent value="reviews">
                <h3 className="font-semibold text-xl mb-6">Customer Reviews</h3>
                <div className="space-y-6">
                  {[1, 2, 3].map((review) => (
                    <div key={review} className="border-b pb-6 last:border-b-0">
                      <div className="flex items-start gap-4">
                        <div className="bg-emerald-100 h-12 w-12 rounded-full flex items-center justify-center font-semibold text-emerald-700">
                          U{review}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center justify-between mb-2">
                            <div>
                              <p className="font-semibold">Customer {review}</p>
                              <div className="flex items-center gap-1 mt-1">
                                {[...Array(5)].map((_, i) => (
                                  <Star
                                    key={i}
                                    className="h-4 w-4 fill-yellow-400 text-yellow-400"
                                  />
                                ))}
                              </div>
                            </div>
                            <span className="text-sm text-gray-500">2 days ago</span>
                          </div>
                          <p className="text-gray-700">
                            Excellent product! Exactly what I was looking for. Fast delivery and great quality.
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        {/* Related Products */}
        {relatedProducts.length > 0 && (
          <section>
            <h2 className="text-3xl font-bold mb-6">You May Also Like</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {relatedProducts.map((relatedProduct) => (
                <Link key={relatedProduct.id} to={`/product/${relatedProduct.id}`}>
                  <Card className="group hover:shadow-xl transition-all duration-300 hover:-translate-y-2 h-full">
                    <CardContent className="p-4">
                      <div className="relative mb-4 overflow-hidden rounded-lg">
                        <img
                          src={relatedProduct.image}
                          alt={relatedProduct.name}
                          className="w-full h-48 object-cover group-hover:scale-110 transition-transform duration-500"
                        />
                      </div>
                      <div className="space-y-2">
                        <h3 className="font-semibold text-gray-900 line-clamp-2">{relatedProduct.name}</h3>
                        <div className="flex items-center gap-2">
                          <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                          <span className="text-sm font-medium">{relatedProduct.rating}</span>
                        </div>
                        <span className="text-xl font-bold text-emerald-600">£{relatedProduct.price.toFixed(2)}</span>
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              ))}
            </div>
          </section>
        )}
      </div>

      <Footer />
    </div>
  );
};

const Store = ({ className }) => {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <path d="M3 9h18v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V9Z" />
      <path d="m3 9 2.45-4.9A2 2 0 0 1 7.24 3h9.52a2 2 0 0 1 1.8 1.1L21 9" />
      <path d="M12 3v6" />
    </svg>
  );
};

export default ProductDetail;