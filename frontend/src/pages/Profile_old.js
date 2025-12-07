import { useNavigate } from 'react-router-dom';
import { User, Package, MapPin, CreditCard, LogOut } from 'lucide-react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Separator } from '../components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { useAuth } from '../context/AuthContext';
import { mockOrders } from '../mock';

const Profile = () => {
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useAuth();

  if (!isAuthenticated) {
    navigate('/login');
    return null;
  }

  const handleLogout = () => {
    logout();
    navigate('/');
  };

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
                  <Button variant="outline" className="w-full justify-start" onClick={() => {}}>
                    <User className="h-4 w-4 mr-2" />
                    Profile Settings
                  </Button>
                  <Button variant="outline" className="w-full justify-start" onClick={() => {}}>
                    <MapPin className="h-4 w-4 mr-2" />
                    Addresses
                  </Button>
                  <Button variant="outline" className="w-full justify-start" onClick={() => {}}>
                    <CreditCard className="h-4 w-4 mr-2" />
                    Payment Methods
                  </Button>
                  <Button
                    variant="outline"
                    className="w-full justify-start text-red-600 hover:text-red-700 hover:bg-red-50"
                    onClick={handleLogout}
                  >
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
              <TabsList className="grid w-full grid-cols-2 mb-6">
                <TabsTrigger value="orders">My Orders</TabsTrigger>
                <TabsTrigger value="wishlist">Wishlist</TabsTrigger>
              </TabsList>

              <TabsContent value="orders">
                <Card>
                  <CardHeader>
                    <CardTitle>Order History</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {mockOrders.map((order) => (
                        <Card key={order.id} className="hover:shadow-lg transition-shadow">
                          <CardContent className="pt-6">
                            <div className="flex justify-between items-start mb-4">
                              <div>
                                <p className="font-semibold text-lg">{order.id}</p>
                                <p className="text-sm text-gray-600">{order.date}</p>
                              </div>
                              <Badge
                                className={
                                  order.status === 'Delivered'
                                    ? 'bg-green-100 text-green-700 hover:bg-green-100'
                                    : 'bg-orange-100 text-orange-700 hover:bg-orange-100'
                                }
                              >
                                {order.status}
                              </Badge>
                            </div>
                            <div className="flex justify-between items-center pt-4 border-t">
                              <div>
                                <p className="text-sm text-gray-600">{order.items} items</p>
                                <p className="text-xl font-bold text-emerald-600">£{order.total.toFixed(2)}</p>
                              </div>
                              <Button variant="outline">View Details</Button>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="wishlist">
                <Card>
                  <CardHeader>
                    <CardTitle>My Wishlist</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-center py-12">
                      <Package className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                      <p className="text-gray-600 mb-4">Your wishlist is empty</p>
                      <Button onClick={() => navigate('/products')}>Browse Products</Button>
                    </div>
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