import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Heart, ShoppingCart, Trash2, Loader2, AlertCircle, Star } from 'lucide-react';
import axios from 'axios';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { useAuth } from '../context/AuthContext';
import { useCart } from '../context/CartContext';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const WishlistPage = () => {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  const { addToCart } = useCart();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    fetchWishlist();
  }, [isAuthenticated]);

  const fetchWishlist = async () => {
    try {
      const token = localStorage.getItem('afroToken');
      const response = await axios.get(`${API}/wishlist`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setItems(response.data.items);
    } catch (error) {
      console.error('Error fetching wishlist:', error);
      toast.error('Failed to load wishlist');
    } finally {
      setLoading(false);
    }
  };

  const removeFromWishlist = async (productId) => {
    try {
      const token = localStorage.getItem('afroToken');
      await axios.post(`${API}/wishlist/toggle`, 
        { product_id: productId },
        { headers: { Authorization: `Bearer ${token}` }}
      );
      setItems(items.filter(item => item.product_id !== productId));
      toast.success('Removed from wishlist');
    } catch (error) {
      toast.error('Failed to remove item');
    }
  };

  const handleAddToCart = (item) => {
    addToCart({
      id: item.product_id,
      name: item.name,
      price: item.price,
      image: item.image
    });
    toast.success('Added to cart');
  };

  const moveAllToCart = () => {
    items.forEach(item => {
      if (item.in_stock) {
        addToCart({
          id: item.product_id,
          name: item.name,
          price: item.price,
          image: item.image
        });
      }
    });
    toast.success('All available items added to cart');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-emerald-600" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3" data-testid="wishlist-title">
              <Heart className="w-8 h-8 text-red-500 fill-red-500" />
              My Wishlist
            </h1>
            <p className="text-gray-600 mt-1">{items.length} items saved</p>
          </div>
          
          {items.length > 0 && (
            <Button 
              onClick={moveAllToCart}
              className="bg-emerald-600 hover:bg-emerald-700"
              data-testid="add-all-to-cart"
            >
              <ShoppingCart className="w-4 h-4 mr-2" />
              Add All to Cart
            </Button>
          )}
        </div>

        {items.length === 0 ? (
          <Card className="text-center py-12">
            <CardContent>
              <Heart className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Your wishlist is empty</h3>
              <p className="text-gray-500 mb-4">
                Save items you love by clicking the heart icon on products
              </p>
              <Link to="/products">
                <Button className="bg-emerald-600 hover:bg-emerald-700">
                  Browse Products
                </Button>
              </Link>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {items.map((item) => (
              <Card key={item.id} className="group overflow-hidden" data-testid={`wishlist-item-${item.product_id}`}>
                <div className="relative">
                  <Link to={`/product/${item.product_id}`}>
                    <img 
                      src={item.image} 
                      alt={item.name}
                      className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                  </Link>
                  
                  <button
                    onClick={() => removeFromWishlist(item.product_id)}
                    className="absolute top-3 right-3 p-2 bg-white rounded-full shadow-md hover:bg-red-50 transition-colors"
                    data-testid={`remove-${item.product_id}`}
                  >
                    <Trash2 className="w-4 h-4 text-red-500" />
                  </button>
                  
                  {!item.in_stock && (
                    <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                      <Badge className="bg-red-500 text-white">Out of Stock</Badge>
                    </div>
                  )}
                  
                  {item.original_price && item.original_price > item.price && (
                    <Badge className="absolute top-3 left-3 bg-red-500 text-white">
                      {Math.round((1 - item.price / item.original_price) * 100)}% OFF
                    </Badge>
                  )}
                </div>
                
                <CardContent className="p-4">
                  <Link to={`/product/${item.product_id}`}>
                    <h3 className="font-semibold text-gray-900 hover:text-emerald-600 line-clamp-2 mb-2">
                      {item.name}
                    </h3>
                  </Link>
                  
                  <div className="flex items-center gap-1 mb-3">
                    <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                    <span className="text-sm font-medium">{item.rating?.toFixed(1) || '4.5'}</span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-lg font-bold text-emerald-600">£{item.price?.toFixed(2)}</p>
                      {item.original_price && item.original_price > item.price && (
                        <p className="text-sm text-gray-400 line-through">£{item.original_price?.toFixed(2)}</p>
                      )}
                    </div>
                    
                    <Button 
                      size="sm"
                      onClick={() => handleAddToCart(item)}
                      disabled={!item.in_stock}
                      className="bg-emerald-600 hover:bg-emerald-700"
                      data-testid={`add-to-cart-${item.product_id}`}
                    >
                      <ShoppingCart className="w-4 h-4" />
                    </Button>
                  </div>
                  
                  <p className="text-xs text-gray-400 mt-2">
                    Added {new Date(item.added_at).toLocaleDateString('en-GB')}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      <Footer />
    </div>
  );
};

export default WishlistPage;
