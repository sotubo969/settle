import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Megaphone, Plus, Eye, MousePointer, Clock, CheckCircle, 
  XCircle, Pause, Play, AlertCircle, TrendingUp, Loader2,
  Image as ImageIcon, Link as LinkIcon, DollarSign
} from 'lucide-react';
import axios from 'axios';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from '../components/ui/dialog';
import { useAuth } from '../context/AuthContext';
import { toast } from 'sonner';
import { loadStripe } from '@stripe/stripe-js';
import { Elements, CardElement, useStripe, useElements } from '@stripe/react-stripe-js';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;
const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY);

// Helper to get auth token
const getAuthToken = () => {
  return localStorage.getItem('afroToken') || localStorage.getItem('token');
};

// Ad Payment Form Component
const AdPaymentForm = ({ ad, onSuccess, onCancel }) => {
  const stripe = useStripe();
  const elements = useElements();
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const handlePayment = async (e) => {
    e.preventDefault();
    if (!stripe || !elements) return;

    setLoading(true);
    setErrorMessage('');
    
    try {
      const token = getAuthToken();
      
      if (!token) {
        toast.error('Please log in to continue');
        return;
      }
      
      // Create payment intent
      const { data: paymentData } = await axios.post(
        `${API}/ads/${ad.id}/pay`,
        {},
        { headers: { Authorization: `Bearer ${token}` }}
      );

      if (!paymentData.client_secret) {
        throw new Error('Failed to create payment session');
      }

      // Confirm payment with Stripe
      const { error, paymentIntent } = await stripe.confirmCardPayment(
        paymentData.client_secret,
        {
          payment_method: {
            card: elements.getElement(CardElement),
          }
        }
      );

      if (error) {
        setErrorMessage(error.message);
        toast.error(error.message);
      } else if (paymentIntent.status === 'succeeded') {
        // Confirm payment on backend
        await axios.post(
          `${API}/ads/${ad.id}/confirm-payment`,
          null,
          { 
            headers: { Authorization: `Bearer ${token}` },
            params: { payment_intent_id: paymentIntent.id }
          }
        );
        toast.success('Payment successful! Your ad is pending approval.');
        onSuccess();
      }
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message || 'Payment failed';
      setErrorMessage(errorMsg);
      toast.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handlePayment} className="space-y-4">
      <div className="p-4 bg-gray-50 rounded-lg">
        <p className="text-sm text-gray-600 mb-2">Amount to pay:</p>
        <p className="text-2xl font-bold text-green-600">£{ad.price?.toFixed(2)}</p>
      </div>
      
      <div className="p-4 border rounded-lg">
        <Label className="mb-2 block">Card Details</Label>
        <CardElement 
          options={{
            style: {
              base: {
                fontSize: '16px',
                color: '#424770',
                '::placeholder': { color: '#aab7c4' }
              }
            }
          }}
        />
      </div>

      {errorMessage && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {errorMessage}
        </div>
      )}

      <div className="flex gap-2">
        <Button type="button" variant="outline" onClick={onCancel} className="flex-1">
          Cancel
        </Button>
        <Button type="submit" disabled={!stripe || loading} className="flex-1 bg-green-600 hover:bg-green-700">
          {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
          Pay £{ad.price?.toFixed(2)}
        </Button>
      </div>
    </form>
  );
};

const VendorAds = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [ads, setAds] = useState([]);
  const [pricing, setPricing] = useState({});
  const [loading, setLoading] = useState(true);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showPaymentDialog, setShowPaymentDialog] = useState(false);
  const [selectedAd, setSelectedAd] = useState(null);
  const [products, setProducts] = useState([]);
  const [creating, setCreating] = useState(false);
  
  const [newAd, setNewAd] = useState({
    title: '',
    description: '',
    image: '',
    link_url: '',
    product_id: null,
    ad_type: 'basic',
    duration_days: 7
  });

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    fetchData();
  }, [user]);

  const fetchData = async () => {
    try {
      const token = getAuthToken();
      
      if (!token) {
        toast.error('Please log in to view your ads');
        navigate('/login');
        return;
      }
      
      const headers = { Authorization: `Bearer ${token}` };

      const [adsRes, pricingRes, productsRes] = await Promise.all([
        axios.get(`${API}/ads/vendor`, { headers }),
        axios.get(`${API}/ads/pricing`),
        axios.get(`${API}/vendor/products`, { headers }).catch(() => ({ data: { products: [] }}))
      ]);

      setAds(adsRes.data.ads || []);
      setPricing(pricingRes.data.pricing || {});
      setProducts(productsRes.data.products || []);
    } catch (error) {
      console.error('Error fetching data:', error);
      if (error.response?.status === 401) {
        toast.error('Session expired. Please log in again.');
        navigate('/login');
      } else if (error.response?.status === 403) {
        toast.error('Only approved vendors can create ads');
      } else {
        toast.error('Failed to load ads data');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAd = async () => {
    if (!newAd.title || !newAd.image) {
      toast.error('Please fill in title and image URL');
      return;
    }

    setCreating(true);
    try {
      const token = getAuthToken();
      
      if (!token) {
        toast.error('Please log in to create ads');
        navigate('/login');
        return;
      }
      
      const { data } = await axios.post(
        `${API}/ads/create`,
        newAd,
        { headers: { Authorization: `Bearer ${token}` }}
      );

      toast.success('Ad created! Now complete payment.');
      setShowCreateDialog(false);
      
      // Set selected ad for payment
      setSelectedAd({
        id: data.ad_id,
        price: data.price,
        ad_type: data.ad_type,
        duration_days: data.duration_days
      });
      setShowPaymentDialog(true);
      
      // Reset form
      setNewAd({
        title: '',
        description: '',
        image: '',
        link_url: '',
        product_id: null,
        ad_type: 'basic',
        duration_days: 7
      });
      
      // Refresh ads list
      fetchData();
    } catch (error) {
      if (error.response?.status === 401) {
        toast.error('Session expired. Please log in again.');
        navigate('/login');
      } else {
        toast.error(error.response?.data?.detail || 'Failed to create ad');
      }
    } finally {
      setCreating(false);
    }
  };

  const handlePauseResume = async (adId, currentStatus) => {
    try {
      const token = getAuthToken();
      await axios.post(
        `${API}/ads/${adId}/pause`,
        {},
        { headers: { Authorization: `Bearer ${token}` }}
      );
      toast.success(currentStatus === 'active' ? 'Ad paused' : 'Ad resumed');
      fetchData();
    } catch (error) {
      if (error.response?.status === 401) {
        toast.error('Session expired. Please log in again.');
        navigate('/login');
      } else {
        toast.error('Failed to update ad status');
      }
    }
  };

  const getPrice = () => {
    const { ad_type, duration_days } = newAd;
    
    // Fallback pricing if API hasn't loaded yet
    const fallbackPricing = {
      basic: { '7_days': 9.99, '14_days': 16.99, '30_days': 29.99 },
      featured: { '7_days': 19.99, '14_days': 34.99, '30_days': 59.99 },
      premium_banner: { '7_days': 34.99, '14_days': 59.99, '30_days': 99.99 }
    };
    
    const pricingData = pricing && Object.keys(pricing).length > 0 ? pricing : fallbackPricing;
    
    if (pricingData[ad_type]) {
      return pricingData[ad_type][`${duration_days}_days`] || 0;
    }
    return 0;
  };

  // Calculate current price for display
  const currentPrice = getPrice();

  const getStatusBadge = (status, paymentStatus) => {
    if (paymentStatus === 'pending') {
      return <Badge className="bg-yellow-100 text-yellow-800">Payment Required</Badge>;
    }
    switch (status) {
      case 'pending':
        return <Badge className="bg-blue-100 text-blue-800">Pending Approval</Badge>;
      case 'approved':
      case 'active':
        return <Badge className="bg-green-100 text-green-800">Active</Badge>;
      case 'rejected':
        return <Badge className="bg-red-100 text-red-800">Rejected</Badge>;
      case 'paused':
        return <Badge className="bg-gray-100 text-gray-800">Paused</Badge>;
      case 'expired':
        return <Badge className="bg-orange-100 text-orange-800">Expired</Badge>;
      default:
        return <Badge>{status}</Badge>;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-green-600" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <Megaphone className="w-8 h-8 text-green-600" />
              My Advertisements
            </h1>
            <p className="text-gray-600 mt-1">Promote your products to reach more customers</p>
          </div>
          
          <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
            <DialogTrigger asChild>
              <Button className="bg-green-600 hover:bg-green-700">
                <Plus className="w-4 h-4 mr-2" />
                Create New Ad
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Create Advertisement</DialogTitle>
              </DialogHeader>
              
              <div className="space-y-4 py-4">
                {/* Ad Type Selection */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {Object.entries(pricing).map(([type, info]) => (
                    <div
                      key={type}
                      onClick={() => setNewAd(prev => ({ ...prev, ad_type: type }))}
                      className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                        newAd.ad_type === type 
                          ? 'border-green-600 bg-green-50' 
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <h4 className="font-semibold text-gray-900">{info.name}</h4>
                      <p className="text-xs text-gray-500 mt-1">{info.description}</p>
                      <p className="text-lg font-bold text-green-600 mt-2">
                        From £{info['7_days']}
                      </p>
                    </div>
                  ))}
                </div>

                {/* Duration */}
                <div>
                  <Label>Duration</Label>
                  <Select 
                    value={String(newAd.duration_days)} 
                    onValueChange={(v) => setNewAd(prev => ({ ...prev, duration_days: parseInt(v) }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select duration" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="7">
                        7 Days - £{newAd.ad_type === 'basic' ? '9.99' : newAd.ad_type === 'featured' ? '19.99' : '34.99'}
                      </SelectItem>
                      <SelectItem value="14">
                        14 Days - £{newAd.ad_type === 'basic' ? '16.99' : newAd.ad_type === 'featured' ? '34.99' : '59.99'}
                      </SelectItem>
                      <SelectItem value="30">
                        30 Days - £{newAd.ad_type === 'basic' ? '29.99' : newAd.ad_type === 'featured' ? '59.99' : '99.99'}
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Title */}
                <div>
                  <Label>Ad Title *</Label>
                  <Input
                    value={newAd.title}
                    onChange={(e) => setNewAd(prev => ({ ...prev, title: e.target.value }))}
                    placeholder="e.g., Fresh African Groceries - 20% Off!"
                    maxLength={100}
                  />
                </div>

                {/* Description */}
                <div>
                  <Label>Description</Label>
                  <Textarea
                    value={newAd.description}
                    onChange={(e) => setNewAd(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="Brief description of your ad..."
                    rows={3}
                  />
                </div>

                {/* Image URL */}
                <div>
                  <Label>Image URL *</Label>
                  <Input
                    value={newAd.image}
                    onChange={(e) => setNewAd(prev => ({ ...prev, image: e.target.value }))}
                    placeholder="https://example.com/your-ad-image.jpg"
                  />
                  {newAd.image && (
                    <img src={newAd.image} alt="Preview" className="mt-2 h-32 object-cover rounded-lg" />
                  )}
                </div>

                {/* Link URL */}
                <div>
                  <Label>Link URL (optional)</Label>
                  <Input
                    value={newAd.link_url}
                    onChange={(e) => setNewAd(prev => ({ ...prev, link_url: e.target.value }))}
                    placeholder="https://your-product-page.com"
                  />
                </div>

                {/* Product Selection */}
                {products.length > 0 && (
                  <div>
                    <Label>Promote Specific Product (optional)</Label>
                    <Select 
                      value={String(newAd.product_id || '')} 
                      onValueChange={(v) => setNewAd(prev => ({ ...prev, product_id: v ? parseInt(v) : null }))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select a product" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="">No specific product</SelectItem>
                        {products.map(p => (
                          <SelectItem key={p.id} value={String(p.id)}>{p.name}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                )}

                {/* Price Summary */}
                <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                  <div className="flex justify-between items-center">
                    <span className="font-medium">Total Price:</span>
                    <span className="text-2xl font-bold text-green-600">£{currentPrice.toFixed(2)}</span>
                  </div>
                  <p className="text-sm text-gray-500 mt-1">
                    {newAd.ad_type === 'basic' ? 'Basic Ad' : newAd.ad_type === 'featured' ? 'Featured Ad' : 'Premium Banner'} for {newAd.duration_days} days
                  </p>
                </div>
              </div>

              <DialogFooter>
                <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                  Cancel
                </Button>
                <Button 
                  onClick={handleCreateAd} 
                  disabled={creating || !newAd.title || !newAd.image}
                  className="bg-green-600 hover:bg-green-700"
                >
                  {creating ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                  Create Ad & Pay £{currentPrice.toFixed(2)}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>

        {/* Pricing Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          {Object.entries(pricing).map(([type, info]) => (
            <Card key={type} className="border-2 hover:border-green-300 transition-colors">
              <CardHeader className="pb-2">
                <CardTitle className="text-lg">{info.name}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-500 mb-3">{info.description}</p>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span>7 days:</span>
                    <span className="font-semibold">£{info['7_days']}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>14 days:</span>
                    <span className="font-semibold">£{info['14_days']}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>30 days:</span>
                    <span className="font-semibold">£{info['30_days']}</span>
                  </div>
                </div>
                <div className="mt-3 pt-3 border-t">
                  <span className="text-xs text-green-600 font-medium">
                    {info.boost_multiplier}x visibility boost
                  </span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Ads List */}
        <Card>
          <CardHeader>
            <CardTitle>Your Ads</CardTitle>
          </CardHeader>
          <CardContent>
            {ads.length === 0 ? (
              <div className="text-center py-12">
                <Megaphone className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No advertisements yet</h3>
                <p className="text-gray-500 mb-4">Create your first ad to boost your product visibility</p>
                <Button onClick={() => setShowCreateDialog(true)} className="bg-green-600 hover:bg-green-700">
                  <Plus className="w-4 h-4 mr-2" />
                  Create Your First Ad
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                {ads.map(ad => (
                  <div key={ad.id} className="flex flex-col md:flex-row gap-4 p-4 border rounded-lg hover:bg-gray-50">
                    <img 
                      src={ad.image} 
                      alt={ad.title}
                      className="w-full md:w-40 h-32 object-cover rounded-lg"
                    />
                    <div className="flex-1">
                      <div className="flex items-start justify-between">
                        <div>
                          <h4 className="font-semibold text-gray-900">{ad.title}</h4>
                          <p className="text-sm text-gray-500">{ad.description}</p>
                        </div>
                        {getStatusBadge(ad.status, ad.payment_status)}
                      </div>
                      
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                        <div>
                          <p className="text-xs text-gray-500">Type</p>
                          <p className="font-medium">{pricing[ad.ad_type]?.name || ad.ad_type}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Duration</p>
                          <p className="font-medium">{ad.duration_days} days</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Impressions</p>
                          <p className="font-medium flex items-center gap-1">
                            <Eye className="w-4 h-4" /> {ad.impressions.toLocaleString()}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Clicks (CTR)</p>
                          <p className="font-medium flex items-center gap-1">
                            <MousePointer className="w-4 h-4" /> {ad.clicks} ({ad.ctr}%)
                          </p>
                        </div>
                      </div>

                      {ad.admin_notes && ad.status === 'rejected' && (
                        <div className="mt-3 p-2 bg-red-50 rounded text-sm text-red-700">
                          <strong>Rejection reason:</strong> {ad.admin_notes}
                        </div>
                      )}

                      <div className="flex gap-2 mt-4">
                        {ad.payment_status === 'pending' && (
                          <Button 
                            size="sm" 
                            className="bg-green-600 hover:bg-green-700"
                            onClick={() => {
                              setSelectedAd(ad);
                              setShowPaymentDialog(true);
                            }}
                          >
                            <DollarSign className="w-4 h-4 mr-1" />
                            Pay Now
                          </Button>
                        )}
                        {(ad.status === 'active' || ad.status === 'paused') && (
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => handlePauseResume(ad.id, ad.status)}
                          >
                            {ad.status === 'active' ? (
                              <><Pause className="w-4 h-4 mr-1" /> Pause</>
                            ) : (
                              <><Play className="w-4 h-4 mr-1" /> Resume</>
                            )}
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Payment Dialog */}
      <Dialog open={showPaymentDialog} onOpenChange={setShowPaymentDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Complete Payment</DialogTitle>
          </DialogHeader>
          {selectedAd && (
            <Elements stripe={stripePromise}>
              <AdPaymentForm 
                ad={selectedAd}
                onSuccess={() => {
                  setShowPaymentDialog(false);
                  setSelectedAd(null);
                  fetchData();
                }}
                onCancel={() => {
                  setShowPaymentDialog(false);
                  setSelectedAd(null);
                }}
              />
            </Elements>
          )}
        </DialogContent>
      </Dialog>

      <Footer />
    </div>
  );
};

export default VendorAds;
