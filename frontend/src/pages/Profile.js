import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, Package, MapPin, CreditCard, LogOut, Edit2, Plus, Trash2, Heart } from 'lucide-react';
import axios from 'axios';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Separator } from '../components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { toast } from 'sonner';
import { useAuth } from '../context/AuthContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Profile = () => {
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useAuth();
  const [orders, setOrders] = useState([]);
  const [wishlist, setWishlist] = useState([]);
  const [addresses, setAddresses] = useState([]);
  const [paymentMethods, setPaymentMethods] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Profile edit state
  const [editProfile, setEditProfile] = useState(false);
  const [profileData, setProfileData] = useState({
    name: user?.name || '',
    phone: user?.phone || ''
  });
  
  // Address dialog state
  const [addressDialog, setAddressDialog] = useState(false);
  const [newAddress, setNewAddress] = useState({
    fullName: '',
    address: '',
    city: '',
    postcode: '',
    phone: '',
    isDefault: false
  });
  
  // Payment method dialog state
  const [paymentDialog, setPaymentDialog] = useState(false);
  const [newPayment, setNewPayment] = useState({
    type: 'card',
    cardNumber: '',
    cardHolder: '',
    expiryDate: '',
    isDefault: false
  });

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    console.log('Fetching user data for profile...');
    fetchUserData();
  }, [isAuthenticated]);

  const fetchUserData = async () => {
    const token = localStorage.getItem('afroToken');
    console.log('Token found:', !!token);
    
    if (!token) {
      console.log('No token, redirecting to login');
      setLoading(false);
      navigate('/login');
      return;
    }

    try {
      console.log('Fetching data from API...');
      const [ordersRes, wishlistRes, meRes] = await Promise.all([
        axios.get(`${API}/orders`, { headers: { Authorization: `Bearer ${token}` }}).catch(err => {
          console.error('Orders fetch error:', err.response?.status);
          return { data: [] };
        }),
        axios.get(`${API}/wishlist`, { headers: { Authorization: `Bearer ${token}` }}).catch(err => {
          console.error('Wishlist fetch error:', err.response?.status);
          return { data: { items: [] } };
        }),
        axios.get(`${API}/auth/me`, { headers: { Authorization: `Bearer ${token}` }}).catch(err => {
          console.error('Me fetch error:', err.response?.status);
          return { data: {} };
        })
      ]);

      console.log('Data fetched successfully');
      setOrders(ordersRes.data || []);
      setWishlist(wishlistRes.data?.items || []);
      setAddresses(meRes.data?.addresses || []);
      setPaymentMethods(meRes.data?.payment_methods || []);
      setProfileData({
        name: meRes.data?.name || '',
        phone: meRes.data?.phone || ''
      });
    } catch (error) {
      console.error('Error fetching user data:', error);
      toast.error('Failed to load profile data');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateProfile = async () => {
    const token = localStorage.getItem('afroToken');
    try {
      await axios.put(`${API}/profile/update`, profileData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Profile updated successfully');
      setEditProfile(false);
    } catch (error) {
      toast.error('Failed to update profile');
    }
  };

  const handleAddAddress = async () => {
    const token = localStorage.getItem('afroToken');
    try {
      const res = await axios.post(`${API}/profile/addresses`, newAddress, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAddresses(res.data.addresses);
      setAddressDialog(false);
      setNewAddress({ fullName: '', address: '', city: '', postcode: '', phone: '', isDefault: false });
      toast.success('Address added successfully');
    } catch (error) {
      toast.error('Failed to add address');
    }
  };

  const handleDeleteAddress = async (index) => {
    const token = localStorage.getItem('afroToken');
    try {
      const res = await axios.delete(`${API}/profile/addresses/${index}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAddresses(res.data.addresses);
      toast.success('Address deleted');
    } catch (error) {
      toast.error('Failed to delete address');
    }
  };

  const handleAddPaymentMethod = async () => {
    const token = localStorage.getItem('afroToken');
    try {
      const res = await axios.post(`${API}/profile/payment-methods`, newPayment, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPaymentMethods(res.data.paymentMethods);
      setPaymentDialog(false);
      setNewPayment({ type: 'card', cardNumber: '', cardHolder: '', expiryDate: '', isDefault: false });
      toast.success('Payment method added');
    } catch (error) {
      toast.error('Failed to add payment method');
    }
  };

  const handleDeletePaymentMethod = async (index) => {
    const token = localStorage.getItem('afroToken');
    try {
      const res = await axios.delete(`${API}/profile/payment-methods/${index}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPaymentMethods(res.data.paymentMethods);
      toast.success('Payment method deleted');
    } catch (error) {
      toast.error('Failed to delete payment method');
    }
  };

  const handleRemoveFromWishlist = async (productId) => {
    const token = localStorage.getItem('afroToken');
    try {
      await axios.delete(`${API}/wishlist/remove/${productId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setWishlist(wishlist.filter(item => item.id !== productId));
      toast.success('Removed from wishlist');
    } catch (error) {
      toast.error('Failed to remove from wishlist');
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="max-w-7xl mx-auto px-4 py-16 text-center">
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <div className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">My Account</h1>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <Card className="shadow-xl">
              <CardContent className="pt-6">
                <div className="flex flex-col items-center text-center">
                  <div className="w-24 h-24 bg-emerald-100 rounded-full flex items-center justify-center mb-4">
                    <User className="h-12 w-12 text-emerald-600" />
                  </div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-1">{user?.name}</h2>
                  <p className="text-gray-600 mb-4">{user?.email}</p>
                  <Badge className="bg-emerald-100 text-emerald-700 hover:bg-emerald-100">
                    {user?.role === 'vendor' ? 'Vendor' : 'Customer'}
                  </Badge>
                </div>

                <Separator className="my-6" />

                <div className="space-y-2">
                  <Button variant="outline" className="w-full justify-start text-red-600 hover:text-red-700 hover:bg-red-50" onClick={handleLogout}>
                    <LogOut className="h-4 w-4 mr-2" />
                    Logout
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-2">
            <Tabs defaultValue="orders" className="w-full">
              <TabsList className="grid w-full grid-cols-5 mb-6">
                <TabsTrigger value="orders">Orders</TabsTrigger>
                <TabsTrigger value="wishlist">Wishlist</TabsTrigger>
                <TabsTrigger value="profile">Profile</TabsTrigger>
                <TabsTrigger value="addresses">Addresses</TabsTrigger>
                <TabsTrigger value="payments">Payments</TabsTrigger>
              </TabsList>

              {/* Orders Tab */}
              <TabsContent value="orders">
                <Card>
                  <CardHeader>
                    <CardTitle>Order History</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {orders.length === 0 ? (
                      <div className="text-center py-12">
                        <Package className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                        <p className="text-gray-600 mb-4">No orders yet</p>
                        <Button onClick={() => navigate('/products')}>Start Shopping</Button>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        {orders.map((order) => (
                          <Card key={order.id} className="hover:shadow-lg transition-shadow">
                            <CardContent className="pt-6">
                              <div className="flex justify-between items-start mb-4">
                                <div>
                                  <p className="font-semibold text-lg">{order.orderId}</p>
                                  <p className="text-sm text-gray-600">{order.date}</p>
                                </div>
                                <Badge className={order.status === 'delivered' ? 'bg-green-100 text-green-700' : 'bg-orange-100 text-orange-700'}>
                                  {order.status}
                                </Badge>
                              </div>
                              <div className="flex justify-between items-center pt-4 border-t">
                                <div>
                                  <p className="text-sm text-gray-600">{order.items} items</p>
                                  <p className="text-xl font-bold text-emerald-600">£{order.total.toFixed(2)}</p>
                                </div>
                                <Button variant="outline">Track Order</Button>
                              </div>
                            </CardContent>
                          </Card>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Wishlist Tab */}
              <TabsContent value="wishlist">
                <Card>
                  <CardHeader>
                    <CardTitle>My Wishlist</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {wishlist.length === 0 ? (
                      <div className="text-center py-12">
                        <Heart className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                        <p className="text-gray-600 mb-4">Your wishlist is empty</p>
                        <Button onClick={() => navigate('/products')}>Browse Products</Button>
                      </div>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {wishlist.map((item) => (
                          <Card key={item.id} className="relative">
                            <CardContent className="pt-6">
                              <img src={item.image} alt={item.name} className="w-full h-40 object-cover rounded mb-3" />
                              <h3 className="font-semibold line-clamp-2 mb-2">{item.name}</h3>
                              <p className="text-emerald-600 font-bold text-xl mb-3">£{item.price.toFixed(2)}</p>
                              <div className="flex gap-2">
                                <Button size="sm" className="flex-1" onClick={() => navigate(`/product/${item.id}`)}>
                                  View
                                </Button>
                                <Button size="sm" variant="outline" onClick={() => handleRemoveFromWishlist(item.id)}>
                                  <Trash2 className="h-4 w-4" />
                                </Button>
                              </div>
                            </CardContent>
                          </Card>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Profile Settings Tab */}
              <TabsContent value="profile">
                <Card>
                  <CardHeader>
                    <CardTitle>Profile Settings</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div>
                        <Label>Name</Label>
                        {editProfile ? (
                          <Input
                            value={profileData.name}
                            onChange={(e) => setProfileData({ ...profileData, name: e.target.value })}
                          />
                        ) : (
                          <p className="text-lg font-medium">{profileData.name}</p>
                        )}
                      </div>
                      <div>
                        <Label>Email</Label>
                        <p className="text-lg font-medium">{user?.email}</p>
                      </div>
                      <div>
                        <Label>Phone</Label>
                        {editProfile ? (
                          <Input
                            value={profileData.phone}
                            onChange={(e) => setProfileData({ ...profileData, phone: e.target.value })}
                          />
                        ) : (
                          <p className="text-lg font-medium">{profileData.phone || 'Not set'}</p>
                        )}
                      </div>
                      <div className="flex gap-2 pt-4">
                        {editProfile ? (
                          <>
                            <Button onClick={handleUpdateProfile}>Save Changes</Button>
                            <Button variant="outline" onClick={() => setEditProfile(false)}>Cancel</Button>
                          </>
                        ) : (
                          <Button onClick={() => setEditProfile(true)}>
                            <Edit2 className="h-4 w-4 mr-2" />
                            Edit Profile
                          </Button>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Addresses Tab */}
              <TabsContent value="addresses">
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between">
                    <CardTitle>My Addresses</CardTitle>
                    <Dialog open={addressDialog} onOpenChange={setAddressDialog}>
                      <DialogTrigger asChild>
                        <Button size="sm">
                          <Plus className="h-4 w-4 mr-2" />
                          Add Address
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle>Add New Address</DialogTitle>
                        </DialogHeader>
                        <div className="space-y-4">
                          <div>
                            <Label>Full Name</Label>
                            <Input value={newAddress.fullName} onChange={(e) => setNewAddress({ ...newAddress, fullName: e.target.value })} />
                          </div>
                          <div>
                            <Label>Address</Label>
                            <Input value={newAddress.address} onChange={(e) => setNewAddress({ ...newAddress, address: e.target.value })} />
                          </div>
                          <div className="grid grid-cols-2 gap-4">
                            <div>
                              <Label>City</Label>
                              <Input value={newAddress.city} onChange={(e) => setNewAddress({ ...newAddress, city: e.target.value })} />
                            </div>
                            <div>
                              <Label>Postcode</Label>
                              <Input value={newAddress.postcode} onChange={(e) => setNewAddress({ ...newAddress, postcode: e.target.value })} />
                            </div>
                          </div>
                          <div>
                            <Label>Phone</Label>
                            <Input value={newAddress.phone} onChange={(e) => setNewAddress({ ...newAddress, phone: e.target.value })} />
                          </div>
                          <Button onClick={handleAddAddress} className="w-full">Add Address</Button>
                        </div>
                      </DialogContent>
                    </Dialog>
                  </CardHeader>
                  <CardContent>
                    {addresses.length === 0 ? (
                      <div className="text-center py-8">
                        <MapPin className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                        <p className="text-gray-600">No addresses saved</p>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {addresses.map((addr, index) => (
                          <Card key={index}>
                            <CardContent className="pt-4 flex justify-between items-start">
                              <div>
                                <p className="font-semibold">{addr.fullName}</p>
                                <p className="text-sm text-gray-600">{addr.address}</p>
                                <p className="text-sm text-gray-600">{addr.city}, {addr.postcode}</p>
                                <p className="text-sm text-gray-600">{addr.phone}</p>
                              </div>
                              <Button size="sm" variant="ghost" onClick={() => handleDeleteAddress(index)}>
                                <Trash2 className="h-4 w-4 text-red-500" />
                              </Button>
                            </CardContent>
                          </Card>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Payment Methods Tab */}
              <TabsContent value="payments">
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between">
                    <CardTitle>Payment Methods</CardTitle>
                    <Dialog open={paymentDialog} onOpenChange={setPaymentDialog}>
                      <DialogTrigger asChild>
                        <Button size="sm">
                          <Plus className="h-4 w-4 mr-2" />
                          Add Payment
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle>Add Payment Method</DialogTitle>
                        </DialogHeader>
                        <div className="space-y-4">
                          <div>
                            <Label>Card Number</Label>
                            <Input value={newPayment.cardNumber} onChange={(e) => setNewPayment({ ...newPayment, cardNumber: e.target.value })} placeholder="1234 5678 9012 3456" />
                          </div>
                          <div>
                            <Label>Card Holder Name</Label>
                            <Input value={newPayment.cardHolder} onChange={(e) => setNewPayment({ ...newPayment, cardHolder: e.target.value })} />
                          </div>
                          <div>
                            <Label>Expiry Date</Label>
                            <Input value={newPayment.expiryDate} onChange={(e) => setNewPayment({ ...newPayment, expiryDate: e.target.value })} placeholder="MM/YY" />
                          </div>
                          <Button onClick={handleAddPaymentMethod} className="w-full">Add Card</Button>
                        </div>
                      </DialogContent>
                    </Dialog>
                  </CardHeader>
                  <CardContent>
                    {paymentMethods.length === 0 ? (
                      <div className="text-center py-8">
                        <CreditCard className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                        <p className="text-gray-600">No payment methods saved</p>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {paymentMethods.map((pm, index) => (
                          <Card key={index}>
                            <CardContent className="pt-4 flex justify-between items-center">
                              <div className="flex items-center gap-3">
                                <CreditCard className="h-8 w-8 text-gray-600" />
                                <div>
                                  <p className="font-semibold">{pm.cardNumberMasked || 'Card'}</p>
                                  <p className="text-sm text-gray-600">{pm.cardHolder}</p>
                                </div>
                              </div>
                              <Button size="sm" variant="ghost" onClick={() => handleDeletePaymentMethod(index)}>
                                <Trash2 className="h-4 w-4 text-red-500" />
                              </Button>
                            </CardContent>
                          </Card>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default Profile;
