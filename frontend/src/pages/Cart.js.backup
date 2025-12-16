import { Link, useNavigate } from 'react-router-dom';
import { Trash2, Plus, Minus, ShoppingBag, ArrowRight } from 'lucide-react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { useCart } from '../context/CartContext';
import { toast } from 'sonner';

const Cart = () => {
  const navigate = useNavigate();
  const { cart, removeFromCart, updateQuantity, getCartTotal, clearCart, isLoading } = useCart();

  const handleUpdateQuantity = async (productId, newQuantity) => {
    if (newQuantity < 1) return;
    try {
      await updateQuantity(productId, newQuantity);
    } catch (error) {
      toast.error('Failed to update quantity');
    }
  };

  const handleRemove = async (product) => {
    try {
      await removeFromCart(product.id);
      toast.success(`${product.name} removed from cart`);
    } catch (error) {
      toast.error('Failed to remove item');
    }
  };

  const handleCheckout = () => {
    navigate('/checkout');
  };

  const handleClearCart = async () => {
    if (window.confirm('Are you sure you want to clear your cart?')) {
      try {
        await clearCart();
        toast.success('Cart cleared');
      } catch (error) {
        toast.error('Failed to clear cart');
      }
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="max-w-7xl mx-auto px-4 py-16 text-center">
          <p>Loading cart...</p>
        </div>
      </div>
    );
  }

  if (cart.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="max-w-7xl mx-auto px-4 py-16">
          <Card className="text-center py-16">
            <CardContent>
              <ShoppingBag className="h-24 w-24 text-gray-300 mx-auto mb-6" />
              <h2 className="text-3xl font-bold text-gray-900 mb-4">Your cart is empty</h2>
              <p className="text-gray-600 mb-8">Add some delicious African groceries to get started!</p>
              <Link to="/products">
                <Button size="lg" className="bg-emerald-600 hover:bg-emerald-700">
                  Start Shopping
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  const subtotal = getCartTotal();
  const delivery = subtotal > 30 ? 0 : 4.99;
  const total = subtotal + delivery;
  const commission = 1 * cart.reduce((sum, item) => sum + item.quantity, 0);

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <div className="max-w-7xl mx-auto px-3 sm:px-4 py-4 sm:py-8">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4 sm:mb-8 gap-2">
          <h1 className="text-2xl sm:text-4xl font-bold text-gray-900">
            Shopping Cart <span className="text-gray-500 text-lg sm:text-2xl">({cart.length} items)</span>
          </h1>
          <Button variant="outline" onClick={() => navigate('/products')} className="text-xs sm:text-sm">
            Continue Shopping
          </Button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-8">
          {/* Cart Items */}
          <div className="lg:col-span-2 space-y-3 sm:space-y-4">
            {cart.map((item) => (
              <Card key={item.id} className="overflow-hidden hover:shadow-lg transition-shadow">
                <CardContent className="p-3 sm:p-6">
                  <div className="flex gap-3 sm:gap-6">
                    <Link to={`/product/${item.id}`} className="flex-shrink-0">
                      <img
                        src={item.image}
                        alt={item.name}
                        className="w-20 h-20 sm:w-32 sm:h-32 object-cover rounded-lg hover:opacity-80 transition-opacity"
                      />
                    </Link>

                    <div className="flex-1 flex flex-col justify-between min-w-0">
                      <div>
                        <Link to={`/product/${item.id}`}>
                          <h3 className="font-semibold text-sm sm:text-xl text-gray-900 hover:text-emerald-600 transition-colors mb-1 line-clamp-2">
                            {item.name}
                          </h3>
                        </Link>
                        <p className="text-xs sm:text-sm text-gray-600 mb-1 truncate">{item.brand} • {item.weight}</p>
                        <p className="text-xs sm:text-sm text-emerald-600 font-medium truncate">Sold by {item.vendor.name}</p>
                      </div>

                      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mt-2 sm:mt-4 gap-2">
                        {/* Quantity Controls */}
                        <div className="flex items-center border-2 rounded-lg">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleUpdateQuantity(item.id, item.quantity - 1)}
                            disabled={item.quantity <= 1}
                            className="px-2 sm:px-3 py-1 hover:bg-gray-100 h-8 sm:h-auto"
                          >
                            <Minus className="h-3 w-3 sm:h-4 sm:w-4" />
                          </Button>
                          <span className="px-3 sm:px-6 py-1 font-semibold border-x-2 text-sm sm:text-base">{item.quantity}</span>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleUpdateQuantity(item.id, item.quantity + 1)}
                            disabled={item.quantity >= item.stock}
                            className="px-2 sm:px-3 py-1 hover:bg-gray-100 h-8 sm:h-auto"
                          >
                            <Plus className="h-3 w-3 sm:h-4 sm:w-4" />
                          </Button>
                        </div>

                        {/* Price */}
                        <div className="text-right">
                          <p className="text-lg sm:text-2xl font-bold text-emerald-600">
                            £{(item.price * item.quantity).toFixed(2)}
                          </p>
                          <p className="text-xs sm:text-sm text-gray-500">£{item.price.toFixed(2)} each</p>
                        </div>
                      </div>
                    </div>

                    {/* Remove Button */}
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleRemove(item)}
                      className="text-red-500 hover:text-red-700 hover:bg-red-50 self-start h-8 w-8 sm:h-10 sm:w-10"
                    >
                      <Trash2 className="h-4 w-4 sm:h-5 sm:w-5" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Order Summary */}
          <div className="lg:col-span-1">
            <Card className="sticky top-24 shadow-xl">
              <CardContent className="p-4 sm:p-6 space-y-4 sm:space-y-6">
                <h2 className="text-xl sm:text-2xl font-bold text-gray-900">Order Summary</h2>

                <div className="space-y-2 sm:space-y-3 py-3 sm:py-4 border-y">
                  <div className="flex justify-between text-sm sm:text-base text-gray-700">
                    <span>Subtotal ({cart.reduce((sum, item) => sum + item.quantity, 0)} items)</span>
                    <span className="font-semibold">£{subtotal.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between text-sm sm:text-base text-gray-700">
                    <span>Delivery Fee</span>
                    <span className="font-semibold">
                      {delivery === 0 ? (
                        <span className="text-green-600">FREE</span>
                      ) : (
                        `£${delivery.toFixed(2)}`
                      )}
                    </span>
                  </div>
                  {delivery > 0 && (
                    <p className="text-xs sm:text-sm text-emerald-600">
                      Add £{(30 - subtotal).toFixed(2)} more for FREE delivery!
                    </p>
                  )}
                </div>

                <div className="flex justify-between text-lg sm:text-xl font-bold text-gray-900 py-2 sm:py-3">
                  <span>Total</span>
                  <span className="text-emerald-600">£{total.toFixed(2)}</span>
                </div>

                <div className="space-y-2 sm:space-y-3">
                  <Button
                    size="lg"
                    className="w-full bg-orange-500 hover:bg-orange-600 text-white text-base sm:text-lg py-4 sm:py-6 shadow-lg hover:shadow-xl transform hover:scale-105 transition-all"
                    onClick={handleCheckout}
                  >
                    Proceed to Checkout
                    <ArrowRight className="ml-2 h-4 w-4 sm:h-5 sm:w-5" />
                  </Button>
                  <Button
                    variant="outline"
                    size="lg"
                    className="w-full border-2 py-4 sm:py-6 text-sm sm:text-base"
                    onClick={handleClearCart}
                  >
                    Clear Cart
                  </Button>
                </div>

                {/* Trust Badges */}
                <div className="bg-emerald-50 rounded-lg p-3 sm:p-4 space-y-1 sm:space-y-2">
                  <p className="text-xs sm:text-sm font-semibold text-emerald-900">✓ Secure checkout</p>
                  <p className="text-xs sm:text-sm font-semibold text-emerald-900">✓ Same-day delivery available</p>
                  <p className="text-xs sm:text-sm font-semibold text-emerald-900">✓ Support local vendors</p>
                  <p className="text-xs sm:text-sm text-gray-600 mt-2 sm:mt-3 pt-2 sm:pt-3 border-t border-emerald-200">
                    Platform commission: £{commission.toFixed(2)} (£1 per item)
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default Cart;