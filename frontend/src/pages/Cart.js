import { Link, useNavigate } from 'react-router-dom';
import { Trash2, Plus, Minus, ShoppingBag, ArrowRight, Loader2, Tag, TruckIcon, Shield } from 'lucide-react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Separator } from '../components/ui/separator';
import { useCart } from '../context/CartContext';
import { toast } from 'sonner';
import { useState } from 'react';

const Cart = () => {
  const navigate = useNavigate();
  const { cart, removeFromCart, updateQuantity, getCartTotal, clearCart, isLoading } = useCart();
  const [updatingItems, setUpdatingItems] = useState({});

  const handleUpdateQuantity = async (productId, newQuantity) => {
    if (newQuantity < 1) return;
    
    setUpdatingItems(prev => ({ ...prev, [productId]: true }));
    try {
      await updateQuantity(productId, newQuantity);
      toast.success('Quantity updated');
    } catch (error) {
      toast.error('Failed to update quantity. Please try again.');
      console.error('Update error:', error);
    } finally {
      setUpdatingItems(prev => ({ ...prev, [productId]: false }));
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
    if (window.confirm('Are you sure you want to clear your entire cart?')) {
      try {
        await clearCart();
        toast.success('Cart cleared successfully');
      } catch (error) {
        toast.error('Failed to clear cart');
      }
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
        <Header />
        <div className="max-w-7xl mx-auto px-4 py-16">
          <Card className="p-12">
            <div className="flex flex-col items-center justify-center space-y-4">
              <Loader2 className="h-12 w-12 text-emerald-600 animate-spin" />
              <p className="text-lg text-gray-600">Loading your cart...</p>
            </div>
          </Card>
        </div>
      </div>
    );
  }

  if (cart.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
        <Header />
        <div className="max-w-4xl mx-auto px-4 py-16">
          <Card className="border-2 border-dashed border-gray-300 bg-white shadow-lg">
            <CardContent className="text-center py-20">
              <div className="bg-gray-100 rounded-full w-32 h-32 flex items-center justify-center mx-auto mb-6">
                <ShoppingBag className="h-16 w-16 text-gray-400" />
              </div>
              <h2 className="text-3xl font-bold text-gray-900 mb-4">Your Cart is Empty</h2>
              <p className="text-lg text-gray-600 mb-8 max-w-md mx-auto">
                Discover authentic African and Caribbean groceries and start adding items to your cart!
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link to="/products">
                  <Button size="lg" className="bg-emerald-600 hover:bg-emerald-700 shadow-lg hover:shadow-xl transition-all">
                    <ShoppingBag className="mr-2 h-5 w-5" />
                    Start Shopping
                  </Button>
                </Link>
                <Link to="/">
                  <Button size="lg" variant="outline">
                    Back to Home
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  const subtotal = getCartTotal();
  // Free delivery for orders £100+
  const FREE_DELIVERY_THRESHOLD = 100;
  const deliveryFee = subtotal >= FREE_DELIVERY_THRESHOLD ? 0 : subtotal >= 50 ? 4.99 : 6.99;
  const savings = subtotal >= FREE_DELIVERY_THRESHOLD ? deliveryFee : 0;
  const total = subtotal + (subtotal >= FREE_DELIVERY_THRESHOLD ? 0 : deliveryFee);
  const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
  const amountToFreeDelivery = Math.max(0, FREE_DELIVERY_THRESHOLD - subtotal);

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      <Header />

      <div className="max-w-7xl mx-auto px-3 sm:px-4 py-6 sm:py-12">
        {/* Header Section */}
        <div className="mb-8">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-2">
                Shopping Cart
              </h1>
              <p className="text-gray-600">
                <Badge variant="secondary" className="mr-2">
                  {totalItems} {totalItems === 1 ? 'item' : 'items'}
                </Badge>
                in your cart
              </p>
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={() => navigate('/products')}
                className="hover:bg-emerald-50"
              >
                Continue Shopping
              </Button>
              {cart.length > 0 && (
                <Button
                  variant="ghost"
                  onClick={handleClearCart}
                  className="text-red-600 hover:text-red-700 hover:bg-red-50"
                >
                  Clear Cart
                </Button>
              )}
            </div>
          </div>
          
          {/* Progress Bar for Free Delivery */}
          {subtotal < FREE_DELIVERY_THRESHOLD && (
            <Card className="mt-6 bg-gradient-to-r from-emerald-50 to-green-50 border-emerald-200">
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <TruckIcon className="h-5 w-5 text-emerald-600" />
                    <span className="font-medium text-emerald-900">
                      Add £{amountToFreeDelivery.toFixed(2)} more for FREE delivery!
                    </span>
                  </div>
                  <Badge className="bg-emerald-600">Save up to £6.99</Badge>
                </div>
                <div className="w-full bg-emerald-200 rounded-full h-2.5">
                  <div
                    className="bg-emerald-600 h-2.5 rounded-full transition-all duration-500"
                    style={{ width: `${Math.min((subtotal / FREE_DELIVERY_THRESHOLD) * 100, 100)}%` }}
                  ></div>
                </div>
                <p className="text-xs text-emerald-700 mt-2">Free delivery on all orders over £{FREE_DELIVERY_THRESHOLD}</p>
              </CardContent>
            </Card>
          )}
          {subtotal >= FREE_DELIVERY_THRESHOLD && (
            <Card className="mt-6 bg-gradient-to-r from-emerald-100 to-green-100 border-emerald-300">
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <TruckIcon className="h-5 w-5 text-emerald-600" />
                  <span className="font-semibold text-emerald-900">
                    🎉 You qualify for FREE delivery!
                  </span>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 sm:gap-8">
          {/* Cart Items */}
          <div className="lg:col-span-2 space-y-4">
            {cart.map((item) => (
              <Card key={item.id} className="hover:shadow-lg transition-shadow duration-300">
                <CardContent className="p-4 sm:p-6">
                  <div className="flex gap-4">
                    {/* Product Image */}
                    <div className="flex-shrink-0">
                      <img
                        src={item.image}
                        alt={item.name}
                        className="w-20 h-20 sm:w-24 sm:h-24 object-cover rounded-lg border-2 border-gray-200"
                      />
                    </div>

                    {/* Product Details */}
                    <div className="flex-1 min-w-0">
                      <div className="flex justify-between gap-4">
                        <div className="flex-1">
                          <Link to={`/product/${item.id}`}>
                            <h3 className="text-lg font-semibold text-gray-900 hover:text-emerald-600 transition-colors line-clamp-2">
                              {item.name}
                            </h3>
                          </Link>
                          <div className="mt-1 space-y-1">
                            {item.brand && (
                              <p className="text-sm text-gray-600">
                                <span className="font-medium">Brand:</span> {item.brand}
                              </p>
                            )}
                            {item.weight && (
                              <p className="text-sm text-gray-600">
                                <span className="font-medium">Weight:</span> {item.weight}
                              </p>
                            )}
                            {item.vendor && (
                              <p className="text-sm text-gray-600">
                                <span className="font-medium">Seller:</span> {item.vendor.name}
                              </p>
                            )}
                          </div>
                          {item.inStock ? (
                            <Badge className="mt-2 bg-green-100 text-green-800 hover:bg-green-100">
                              In Stock
                            </Badge>
                          ) : (
                            <Badge variant="destructive" className="mt-2">
                              Out of Stock
                            </Badge>
                          )}
                        </div>

                        {/* Price */}
                        <div className="text-right">
                          <p className="text-xl sm:text-2xl font-bold text-emerald-600">
                            £{item.price.toFixed(2)}
                          </p>
                          {item.originalPrice && item.originalPrice > item.price && (
                            <p className="text-sm text-gray-500 line-through">
                              £{item.originalPrice.toFixed(2)}
                            </p>
                          )}
                        </div>
                      </div>

                      {/* Quantity Controls & Remove */}
                      <div className="flex items-center justify-between mt-4">
                        <div className="flex items-center gap-2">
                          <span className="text-sm text-gray-600 mr-2">Quantity:</span>
                          <div className="flex items-center border border-gray-300 rounded-lg">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleUpdateQuantity(item.id, item.quantity - 1)}
                              disabled={item.quantity <= 1 || updatingItems[item.id]}
                              className="h-9 w-9 p-0 hover:bg-gray-100"
                            >
                              {updatingItems[item.id] ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                              ) : (
                                <Minus className="h-4 w-4" />
                              )}
                            </Button>
                            <span className="w-12 text-center font-semibold">{item.quantity}</span>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleUpdateQuantity(item.id, item.quantity + 1)}
                              disabled={updatingItems[item.id]}
                              className="h-9 w-9 p-0 hover:bg-gray-100"
                            >
                              {updatingItems[item.id] ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                              ) : (
                                <Plus className="h-4 w-4" />
                              )}
                            </Button>
                          </div>
                        </div>

                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleRemove(item)}
                          className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        >
                          <Trash2 className="h-4 w-4 mr-1" />
                          Remove
                        </Button>
                      </div>

                      {/* Item Subtotal */}
                      <div className="mt-3 pt-3 border-t border-gray-200">
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">Item subtotal:</span>
                          <span className="text-lg font-bold text-gray-900">
                            £{(item.price * item.quantity).toFixed(2)}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Order Summary */}
          <div className="lg:col-span-1">
            <div className="sticky top-4">
              <Card className="shadow-xl border-2 border-emerald-100">
                <CardHeader className="bg-gradient-to-r from-emerald-50 to-green-50">
                  <CardTitle className="text-2xl">Order Summary</CardTitle>
                </CardHeader>
                <CardContent className="p-6 space-y-4">
                  {/* Subtotal */}
                  <div className="flex justify-between text-base">
                    <span className="text-gray-600">Subtotal ({totalItems} items)</span>
                    <span className="font-semibold">£{subtotal.toFixed(2)}</span>
                  </div>

                  {/* Service Fee */}
                  <div className="flex justify-between text-base">
                    <span className="text-gray-600 flex items-center gap-1">
                      Service Fee
                      <span className="text-xs text-gray-500">(2%)</span>
                    </span>
                    <span className="font-semibold">£{serviceFee.toFixed(2)}</span>
                  </div>

                  {/* Delivery */}
                  <div className="flex justify-between text-base">
                    <span className="text-gray-600 flex items-center gap-1">
                      <TruckIcon className="h-4 w-4" />
                      Delivery
                    </span>
                    <span className={`font-semibold ${deliveryFee === 0 ? 'text-green-600' : ''}`}>
                      {deliveryFee === 0 ? 'FREE' : `£${deliveryFee.toFixed(2)}`}
                    </span>
                  </div>

                  {/* Savings */}
                  {savings > 0 && (
                    <div className="flex justify-between text-base text-green-600">
                      <span className="flex items-center gap-1">
                        <Tag className="h-4 w-4" />
                        You Save
                      </span>
                      <span className="font-semibold">-£{savings.toFixed(2)}</span>
                    </div>
                  )}

                  <Separator className="my-4" />

                  {/* Total */}
                  <div className="flex justify-between text-xl font-bold">
                    <span>Total</span>
                    <span className="text-emerald-600">£{total.toFixed(2)}</span>
                  </div>

                  {/* Checkout Button */}
                  <Button
                    onClick={handleCheckout}
                    className="w-full bg-emerald-600 hover:bg-emerald-700 text-white h-14 text-lg font-semibold shadow-lg hover:shadow-xl transition-all"
                  >
                    Proceed to Checkout
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Button>

                  {/* Trust Badges */}
                  <div className="pt-4 space-y-3 text-sm text-gray-600">
                    <div className="flex items-center gap-2">
                      <Shield className="h-4 w-4 text-emerald-600" />
                      <span>Secure checkout</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <TruckIcon className="h-4 w-4 text-emerald-600" />
                      <span>Fast UK delivery</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Tag className="h-4 w-4 text-emerald-600" />
                      <span>Best price guarantee</span>
                    </div>
                  </div>

                  {/* Accepted Payments */}
                  <div className="pt-4 border-t border-gray-200">
                    <p className="text-xs text-gray-500 mb-2">We accept:</p>
                    <div className="flex gap-2 items-center">
                      <div className="px-3 py-1 border rounded text-xs font-semibold">VISA</div>
                      <div className="px-3 py-1 border rounded text-xs font-semibold">Mastercard</div>
                      <div className="px-3 py-1 border rounded text-xs font-semibold">PayPal</div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Help Card */}
              <Card className="mt-4 bg-blue-50 border-blue-200">
                <CardContent className="p-4">
                  <p className="text-sm text-blue-900 font-medium mb-2">Need Help?</p>
                  <p className="text-xs text-blue-800">
                    Contact our support team for assistance with your order.
                  </p>
                  <Button variant="link" className="text-blue-600 p-0 h-auto mt-2" onClick={() => navigate('/help')}>
                    Get Help →
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default Cart;
