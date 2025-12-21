import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { CreditCard, MapPin, Package, CheckCircle, Lock, Shield, Truck, AlertCircle } from 'lucide-react';
import { loadStripe } from '@stripe/stripe-js';
import { Elements, CardElement, useStripe, useElements } from '@stripe/react-stripe-js';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { RadioGroup, RadioGroupItem } from '../components/ui/radio-group';
import { Separator } from '../components/ui/separator';
import { toast } from 'sonner';
import { useCart } from '../context/CartContext';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;
const STRIPE_PUBLISHABLE_KEY = process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY;

// Initialize Stripe
const stripePromise = loadStripe(STRIPE_PUBLISHABLE_KEY);

// Stripe Card Element Styles
const cardElementOptions = {
  style: {
    base: {
      fontSize: '16px',
      color: '#1f2937',
      fontFamily: '"Inter", system-ui, sans-serif',
      '::placeholder': {
        color: '#9ca3af',
      },
      iconColor: '#10b981',
    },
    invalid: {
      color: '#ef4444',
      iconColor: '#ef4444',
    },
  },
};

// Stripe Payment Form Component
const StripePaymentForm = ({ onSuccess, onError, total, shippingInfo, cart, loading, setLoading }) => {
  const stripe = useStripe();
  const elements = useElements();
  const [cardError, setCardError] = useState(null);
  const [processing, setProcessing] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!stripe || !elements) {
      return;
    }

    setProcessing(true);
    setCardError(null);

    try {
      // Get token from localStorage
      const token = localStorage.getItem('afroToken');
      
      // Create payment intent on backend
      const { data: intentData } = await axios.post(
        `${API_URL}/api/payment/stripe/create-intent`,
        {
          amount: total,
          currency: 'gbp',
          metadata: {
            customerEmail: shippingInfo.email,
            customerName: shippingInfo.fullName
          }
        },
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      // Confirm payment with Stripe
      const { error, paymentIntent } = await stripe.confirmCardPayment(
        intentData.clientSecret,
        {
          payment_method: {
            card: elements.getElement(CardElement),
            billing_details: {
              name: shippingInfo.fullName,
              email: shippingInfo.email,
              phone: shippingInfo.phone,
              address: {
                line1: shippingInfo.address,
                city: shippingInfo.city,
                postal_code: shippingInfo.postcode,
                country: 'GB',
              },
            },
          },
        }
      );

      if (error) {
        setCardError(error.message);
        onError(error.message);
      } else if (paymentIntent.status === 'succeeded') {
        onSuccess(paymentIntent.id);
      }
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Payment failed. Please try again.';
      setCardError(errorMessage);
      onError(errorMessage);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="p-4 border-2 border-gray-200 rounded-xl bg-white focus-within:border-emerald-500 transition-colors">
        <CardElement options={cardElementOptions} />
      </div>
      
      {cardError && (
        <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          {cardError}
        </div>
      )}
      
      <div className="flex items-center gap-2 text-sm text-gray-500">
        <Lock className="w-4 h-4" />
        <span>Your payment is secured with 256-bit SSL encryption</span>
      </div>
      
      <Button 
        type="submit" 
        size="lg" 
        className="w-full bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 h-14 text-lg font-semibold shadow-lg shadow-emerald-500/30" 
        disabled={!stripe || processing || loading}
      >
        {processing ? (
          <span className="flex items-center gap-2">
            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            Processing Payment...
          </span>
        ) : (
          <span className="flex items-center gap-2">
            <Lock className="w-5 h-5" />
            Pay £{total.toFixed(2)}
          </span>
        )}
      </Button>
    </form>
  );
};

// PayPal Button Component
const PayPalButton = ({ total, onSuccess, onError, shippingInfo }) => {
  const [processing, setProcessing] = useState(false);

  const handlePayPalClick = async () => {
    setProcessing(true);
    
    // For now, simulate PayPal redirect
    // In production, you would integrate with PayPal SDK
    try {
      // Simulate PayPal payment
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Generate mock PayPal transaction ID
      const transactionId = `PAYPAL-${Date.now()}`;
      onSuccess(transactionId);
    } catch (err) {
      onError('PayPal payment failed. Please try again.');
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="space-y-4">
      <Button 
        type="button" 
        onClick={handlePayPalClick}
        size="lg" 
        className="w-full bg-[#0070ba] hover:bg-[#003087] h-14 text-lg font-semibold"
        disabled={processing}
      >
        {processing ? (
          <span className="flex items-center gap-2">
            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            Connecting to PayPal...
          </span>
        ) : (
          <span className="flex items-center gap-2">
            <span className="font-bold italic">Pay</span>
            <span className="font-bold italic text-[#003087]">Pal</span>
            <span className="ml-2">£{total.toFixed(2)}</span>
          </span>
        )}
      </Button>
      <p className="text-center text-sm text-gray-500">
        You will be redirected to PayPal to complete your payment securely.
      </p>
    </div>
  );
};

// Main Checkout Component
const CheckoutContent = () => {
  const navigate = useNavigate();
  const { cart, getCartTotal, clearCart } = useCart();
  const { user, isAuthenticated } = useAuth();
  const [step, setStep] = useState(1);
  const [paymentMethod, setPaymentMethod] = useState('stripe');
  const [loading, setLoading] = useState(false);
  const [orderId, setOrderId] = useState(null);
  
  const [shippingInfo, setShippingInfo] = useState({
    fullName: user?.name || '',
    email: user?.email || '',
    phone: '',
    address: '',
    city: '',
    postcode: '',
  });

  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    if (cart.length === 0 && step !== 3) {
      navigate('/cart');
    }
  }, [cart, step, navigate]);

  if (!isAuthenticated || (cart.length === 0 && step !== 3)) {
    return null;
  }

  const subtotal = getCartTotal();
  const delivery = subtotal > 30 ? 0 : 4.99;
  const total = subtotal + delivery;

  const handleInputChange = (e) => {
    setShippingInfo({ ...shippingInfo, [e.target.name]: e.target.value });
    // Clear error when user types
    if (errors[e.target.name]) {
      setErrors({ ...errors, [e.target.name]: null });
    }
  };

  const validateShippingInfo = () => {
    const newErrors = {};
    
    if (!shippingInfo.fullName.trim()) newErrors.fullName = 'Full name is required';
    if (!shippingInfo.email.trim()) newErrors.email = 'Email is required';
    if (!shippingInfo.phone.trim()) newErrors.phone = 'Phone number is required for delivery';
    if (!shippingInfo.address.trim()) newErrors.address = 'Street address is required';
    if (!shippingInfo.city.trim()) newErrors.city = 'City is required';
    if (!shippingInfo.postcode.trim()) newErrors.postcode = 'Postcode is required';
    
    // Basic postcode validation for UK
    const postcodeRegex = /^[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][A-Z]{2}$/i;
    if (shippingInfo.postcode && !postcodeRegex.test(shippingInfo.postcode.trim())) {
      newErrors.postcode = 'Please enter a valid UK postcode';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleContinueToPayment = (e) => {
    e.preventDefault();
    
    if (!validateShippingInfo()) {
      toast.error('Please fill in all required shipping details');
      return;
    }
    
    setStep(2);
    window.scrollTo(0, 0);
  };

  const createOrder = async (transactionId) => {
    const token = localStorage.getItem('afroToken');
    
    const orderData = {
      items: cart.map(item => ({
        productId: item.id,
        name: item.name,
        brand: item.brand,
        image: item.image,
        price: item.price,
        quantity: item.quantity,
        vendorId: item.vendor?.id || item.vendorId,
        vendorName: item.vendor?.name || 'Unknown Vendor'
      })),
      shippingInfo: shippingInfo,
      paymentInfo: {
        method: paymentMethod,
        transactionId: transactionId,
        status: 'completed'
      },
      subtotal: subtotal,
      deliveryFee: delivery,
      total: total
    };

    const response = await axios.post(`${API_URL}/api/orders`, orderData, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    return response.data;
  };

  const handlePaymentSuccess = async (transactionId) => {
    setLoading(true);
    
    try {
      const order = await createOrder(transactionId);
      setOrderId(order.orderId);
      await clearCart();
      setStep(3);
      toast.success('Payment successful! Order confirmed.');
    } catch (error) {
      console.error('Order creation error:', error);
      toast.error(error.response?.data?.detail || 'Failed to create order. Please contact support.');
    } finally {
      setLoading(false);
    }
  };

  const handlePaymentError = (errorMessage) => {
    toast.error(errorMessage);
  };

  // Success Step
  if (step === 3) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-green-50">
        <Header />
        <div className="max-w-3xl mx-auto px-4 py-16 text-center">
          <div className="bg-white rounded-3xl shadow-2xl p-12">
            <div className="w-24 h-24 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-8">
              <CheckCircle className="h-14 w-14 text-emerald-600" />
            </div>
            <h1 className="text-4xl font-bold text-gray-900 mb-4">Order Confirmed!</h1>
            <p className="text-xl text-gray-600 mb-2">Thank you for your purchase.</p>
            {orderId && (
              <p className="text-lg font-mono text-emerald-600 mb-8">
                Order ID: #{orderId}
              </p>
            )}
            
            <div className="bg-emerald-50 rounded-xl p-6 mb-8 text-left">
              <h3 className="font-semibold text-emerald-800 mb-3">What happens next?</h3>
              <ul className="space-y-2 text-emerald-700">
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-5 h-5" />
                  Order confirmation email has been sent to {shippingInfo.email}
                </li>
                <li className="flex items-center gap-2">
                  <Package className="w-5 h-5" />
                  Your items will be prepared for shipping
                </li>
                <li className="flex items-center gap-2">
                  <Truck className="w-5 h-5" />
                  You'll receive tracking info once shipped
                </li>
              </ul>
            </div>
            
            <div className="flex gap-4 justify-center">
              <Button size="lg" onClick={() => navigate('/profile')} className="bg-emerald-600 hover:bg-emerald-700">
                View Order Details
              </Button>
              <Button size="lg" variant="outline" onClick={() => navigate('/products')}>
                Continue Shopping
              </Button>
            </div>
          </div>
        </div>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <div className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Secure Checkout</h1>

        {/* Progress Steps */}
        <div className="flex items-center justify-center mb-12">
          <div className="flex items-center">
            <div className={`flex items-center justify-center h-12 w-12 rounded-full font-semibold ${step >= 1 ? 'bg-emerald-600 text-white' : 'bg-gray-200 text-gray-500'}`}>
              <MapPin className="w-5 h-5" />
            </div>
            <span className={`mx-2 text-sm font-medium ${step >= 1 ? 'text-emerald-600' : 'text-gray-400'}`}>Shipping</span>
            <div className={`h-1 w-16 md:w-24 ${step >= 2 ? 'bg-emerald-600' : 'bg-gray-200'}`} />
            <div className={`flex items-center justify-center h-12 w-12 rounded-full font-semibold ${step >= 2 ? 'bg-emerald-600 text-white' : 'bg-gray-200 text-gray-500'}`}>
              <CreditCard className="w-5 h-5" />
            </div>
            <span className={`mx-2 text-sm font-medium ${step >= 2 ? 'text-emerald-600' : 'text-gray-400'}`}>Payment</span>
            <div className={`h-1 w-16 md:w-24 ${step >= 3 ? 'bg-emerald-600' : 'bg-gray-200'}`} />
            <div className={`flex items-center justify-center h-12 w-12 rounded-full font-semibold ${step >= 3 ? 'bg-emerald-600 text-white' : 'bg-gray-200 text-gray-500'}`}>
              <CheckCircle className="w-5 h-5" />
            </div>
            <span className={`mx-2 text-sm font-medium ${step >= 3 ? 'text-emerald-600' : 'text-gray-400'}`}>Complete</span>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Step 1: Shipping */}
            {step === 1 && (
              <form onSubmit={handleContinueToPayment}>
                <Card className="shadow-lg border-0">
                  <CardHeader className="bg-gradient-to-r from-emerald-500 to-emerald-600 text-white rounded-t-lg">
                    <CardTitle className="flex items-center gap-2">
                      <MapPin className="h-5 w-5" />
                      Shipping Information
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="p-6 space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="md:col-span-2">
                        <Label htmlFor="fullName">Full Name *</Label>
                        <Input
                          id="fullName"
                          name="fullName"
                          value={shippingInfo.fullName}
                          onChange={handleInputChange}
                          className={`h-12 ${errors.fullName ? 'border-red-500' : ''}`}
                          placeholder="John Doe"
                        />
                        {errors.fullName && <p className="text-red-500 text-sm mt-1">{errors.fullName}</p>}
                      </div>
                      <div>
                        <Label htmlFor="email">Email *</Label>
                        <Input
                          id="email"
                          name="email"
                          type="email"
                          value={shippingInfo.email}
                          onChange={handleInputChange}
                          className={`h-12 ${errors.email ? 'border-red-500' : ''}`}
                          placeholder="john@example.com"
                        />
                        {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email}</p>}
                      </div>
                      <div>
                        <Label htmlFor="phone">Phone Number *</Label>
                        <Input
                          id="phone"
                          name="phone"
                          type="tel"
                          value={shippingInfo.phone}
                          onChange={handleInputChange}
                          className={`h-12 ${errors.phone ? 'border-red-500' : ''}`}
                          placeholder="07123 456789"
                        />
                        {errors.phone && <p className="text-red-500 text-sm mt-1">{errors.phone}</p>}
                      </div>
                      <div className="md:col-span-2">
                        <Label htmlFor="address">Street Address *</Label>
                        <Input
                          id="address"
                          name="address"
                          value={shippingInfo.address}
                          onChange={handleInputChange}
                          className={`h-12 ${errors.address ? 'border-red-500' : ''}`}
                          placeholder="123 High Street"
                        />
                        {errors.address && <p className="text-red-500 text-sm mt-1">{errors.address}</p>}
                      </div>
                      <div>
                        <Label htmlFor="city">City *</Label>
                        <Input
                          id="city"
                          name="city"
                          value={shippingInfo.city}
                          onChange={handleInputChange}
                          className={`h-12 ${errors.city ? 'border-red-500' : ''}`}
                          placeholder="London"
                        />
                        {errors.city && <p className="text-red-500 text-sm mt-1">{errors.city}</p>}
                      </div>
                      <div>
                        <Label htmlFor="postcode">Postcode *</Label>
                        <Input
                          id="postcode"
                          name="postcode"
                          value={shippingInfo.postcode}
                          onChange={handleInputChange}
                          className={`h-12 ${errors.postcode ? 'border-red-500' : ''}`}
                          placeholder="SW1A 1AA"
                        />
                        {errors.postcode && <p className="text-red-500 text-sm mt-1">{errors.postcode}</p>}
                      </div>
                    </div>
                    
                    <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mt-4">
                      <p className="text-amber-800 text-sm flex items-center gap-2">
                        <AlertCircle className="w-4 h-4" />
                        All fields marked with * are required for delivery
                      </p>
                    </div>
                    
                    <Button type="submit" size="lg" className="w-full mt-6 h-14 text-lg bg-emerald-600 hover:bg-emerald-700">
                      Continue to Payment
                    </Button>
                  </CardContent>
                </Card>
              </form>
            )}

            {/* Step 2: Payment */}
            {step === 2 && (
              <Card className="shadow-lg border-0">
                <CardHeader className="bg-gradient-to-r from-emerald-500 to-emerald-600 text-white rounded-t-lg">
                  <CardTitle className="flex items-center gap-2">
                    <CreditCard className="h-5 w-5" />
                    Payment Method
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-6 space-y-6">
                  {/* Payment Method Selection */}
                  <RadioGroup value={paymentMethod} onValueChange={setPaymentMethod} className="space-y-4">
                    <div className={`flex items-center space-x-3 border-2 rounded-xl p-4 cursor-pointer transition-all ${paymentMethod === 'stripe' ? 'border-emerald-500 bg-emerald-50' : 'border-gray-200 hover:border-gray-300'}`}
                         onClick={() => setPaymentMethod('stripe')}>
                      <RadioGroupItem value="stripe" id="stripe" />
                      <Label htmlFor="stripe" className="flex-1 cursor-pointer">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="font-semibold text-gray-900">Credit/Debit Card</p>
                            <p className="text-sm text-gray-500">Pay securely with Stripe</p>
                          </div>
                          <div className="flex items-center gap-2">
                            <img src="https://upload.wikimedia.org/wikipedia/commons/5/5e/Visa_Inc._logo.svg" alt="Visa" className="h-6" />
                            <img src="https://upload.wikimedia.org/wikipedia/commons/2/2a/Mastercard-logo.svg" alt="Mastercard" className="h-6" />
                          </div>
                        </div>
                      </Label>
                    </div>
                    
                    <div className={`flex items-center space-x-3 border-2 rounded-xl p-4 cursor-pointer transition-all ${paymentMethod === 'paypal' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'}`}
                         onClick={() => setPaymentMethod('paypal')}>
                      <RadioGroupItem value="paypal" id="paypal" />
                      <Label htmlFor="paypal" className="flex-1 cursor-pointer">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="font-semibold text-gray-900">PayPal</p>
                            <p className="text-sm text-gray-500">Pay with your PayPal account</p>
                          </div>
                          <img src="https://upload.wikimedia.org/wikipedia/commons/b/b5/PayPal.svg" alt="PayPal" className="h-6" />
                        </div>
                      </Label>
                    </div>
                  </RadioGroup>

                  <Separator />

                  {/* Payment Forms */}
                  {paymentMethod === 'stripe' && (
                    <div className="pt-4">
                      <h3 className="font-semibold text-gray-900 mb-4">Enter Card Details</h3>
                      <Elements stripe={stripePromise}>
                        <StripePaymentForm
                          onSuccess={handlePaymentSuccess}
                          onError={handlePaymentError}
                          total={total}
                          shippingInfo={shippingInfo}
                          cart={cart}
                          loading={loading}
                          setLoading={setLoading}
                        />
                      </Elements>
                    </div>
                  )}

                  {paymentMethod === 'paypal' && (
                    <div className="pt-4">
                      <PayPalButton
                        total={total}
                        onSuccess={handlePaymentSuccess}
                        onError={handlePaymentError}
                        shippingInfo={shippingInfo}
                      />
                    </div>
                  )}

                  <Button type="button" variant="ghost" onClick={() => setStep(1)} className="w-full">
                    ← Back to Shipping
                  </Button>
                </CardContent>
              </Card>
            )}

            {/* Security Notice */}
            <div className="flex items-center gap-4 p-4 bg-gray-100 rounded-xl">
              <Shield className="w-10 h-10 text-emerald-600" />
              <div>
                <p className="font-semibold text-gray-900">Secure Payment</p>
                <p className="text-sm text-gray-600">Your payment information is encrypted and secure. We never store your card details.</p>
              </div>
            </div>
          </div>

          {/* Order Summary Sidebar */}
          <div className="lg:col-span-1">
            <Card className="sticky top-24 shadow-xl border-0">
              <CardHeader className="bg-gray-900 text-white rounded-t-lg">
                <CardTitle className="flex items-center gap-2">
                  <Package className="w-5 h-5" />
                  Order Summary
                </CardTitle>
              </CardHeader>
              <CardContent className="p-6 space-y-4">
                {/* Cart Items */}
                <div className="space-y-3 max-h-64 overflow-y-auto">
                  {cart.map((item) => (
                    <div key={item.id} className="flex gap-3">
                      <img src={item.image} alt={item.name} className="w-16 h-16 object-cover rounded-lg" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold line-clamp-1">{item.name}</p>
                        <p className="text-xs text-gray-500">{item.brand}</p>
                        <p className="text-sm">Qty: {item.quantity}</p>
                      </div>
                      <p className="font-semibold">£{(item.price * item.quantity).toFixed(2)}</p>
                    </div>
                  ))}
                </div>

                <Separator />

                {/* Totals */}
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Subtotal</span>
                    <span>£{subtotal.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Delivery</span>
                    <span>{delivery === 0 ? <span className="text-emerald-600 font-medium">FREE</span> : `£${delivery.toFixed(2)}`}</span>
                  </div>
                  {delivery > 0 && (
                    <p className="text-xs text-emerald-600">Free delivery on orders over £30</p>
                  )}
                </div>

                <Separator />

                <div className="flex justify-between text-lg font-bold">
                  <span>Total</span>
                  <span className="text-emerald-600">£{total.toFixed(2)}</span>
                </div>

                {/* Shipping Summary (Step 2) */}
                {step === 2 && (
                  <>
                    <Separator />
                    <div className="bg-gray-50 rounded-lg p-4">
                      <p className="font-semibold text-sm text-gray-900 mb-2">Shipping to:</p>
                      <p className="text-sm text-gray-600">
                        {shippingInfo.fullName}<br />
                        {shippingInfo.address}<br />
                        {shippingInfo.city}, {shippingInfo.postcode}<br />
                        {shippingInfo.phone}
                      </p>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
};

// Wrapper component with Stripe Elements provider
const Checkout = () => {
  return <CheckoutContent />;
};

export default Checkout;
