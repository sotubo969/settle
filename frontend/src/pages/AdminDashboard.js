import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Users, Package, ShoppingCart, TrendingUp, Eye, DollarSign, 
  Truck, BarChart3, PieChart, Activity, ArrowUpRight, ArrowDownRight,
  CheckCircle, Clock, XCircle, Search, Filter, Download
} from 'lucide-react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

const AdminDashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  
  // Admin-only email
  const ADMIN_EMAIL = 'sotubodammy@gmail.com';
  
  // Dashboard Data
  const [dashboardData, setDashboardData] = useState({
    totalVendors: 0,
    totalProducts: 0,
    totalOrders: 0,
    totalRevenue: 0,
    totalVisitors: 0,
    platformRevenue: 0,
    activeUsers: 0,
    pendingOrders: 0
  });
  
  const [vendors, setVendors] = useState([]);
  const [products, setProducts] = useState([]);
  const [orders, setOrders] = useState([]);
  const [analytics, setAnalytics] = useState({
    pageViews: [],
    productClicks: [],
    topProducts: [],
    topVendors: []
  });

  useEffect(() => {
    // Check if user is admin
    if (!user || user.email !== ADMIN_EMAIL) {
      navigate('/');
      return;
    }
    
    fetchDashboardData();
  }, [user, navigate]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch all data
      const [vendorsRes, productsRes, ordersRes] = await Promise.all([
        api.get('/vendors/all'),
        api.get('/products'),
        api.get('/admin/orders')
      ]);
      
      setVendors(vendorsRes.data || []);
      setProducts(productsRes.data || []);
      setOrders(ordersRes.data || []);
      
      // Calculate statistics
      calculateStatistics(vendorsRes.data, productsRes.data, ordersRes.data);
      
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateStatistics = (vendorList, productList, orderList) => {
    // Calculate vendor statistics
    const vendorStats = vendorList.map(vendor => {
      const vendorOrders = orderList.filter(order => 
        order.items?.some(item => item.vendor_id === vendor.id)
      );
      
      const vendorRevenue = vendorOrders.reduce((sum, order) => 
        sum + (order.total || 0), 0
      );
      
      const vendorProducts = productList.filter(p => p.vendor_id === vendor.id);
      
      return {
        ...vendor,
        totalOrders: vendorOrders.length,
        totalRevenue: vendorRevenue,
        totalProducts: vendorProducts.length,
        commission: vendorRevenue * 0.15 // 15% commission
      };
    });
    
    setVendors(vendorStats);
    
    // Calculate overall stats
    const totalRevenue = orderList.reduce((sum, order) => sum + (order.total || 0), 0);
    const platformCommission = totalRevenue * 0.15;
    
    setDashboardData({
      totalVendors: vendorList.length,
      totalProducts: productList.length,
      totalOrders: orderList.length,
      totalRevenue: totalRevenue,
      platformRevenue: platformCommission,
      activeUsers: 1250, // Mock data - would come from analytics
      totalVisitors: 15420, // Mock data
      pendingOrders: orderList.filter(o => o.status === 'pending').length
    });
    
    // Product analytics
    const productWithClicks = productList.map(p => ({
      ...p,
      clicks: Math.floor(Math.random() * 500) + 50, // Mock data
      views: Math.floor(Math.random() * 1000) + 100,
      conversions: Math.floor(Math.random() * 50) + 5
    })).sort((a, b) => b.clicks - a.clicks);
    
    setAnalytics({
      topProducts: productWithClicks.slice(0, 10),
      topVendors: vendorStats.sort((a, b) => b.totalRevenue - a.totalRevenue).slice(0, 10)
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="max-w-7xl mx-auto px-4 py-16">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <Header />
      
      <div className="max-w-[1600px] mx-auto px-4 py-8">
        {/* Admin Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2">
                Admin Dashboard
              </h1>
              <p className="text-gray-600">
                Welcome back, {user?.name}. Here's what's happening with your marketplace.
              </p>
            </div>
            <div className="flex gap-3">
              <Button variant="outline" className="gap-2">
                <Download className="h-4 w-4" />
                Export Report
              </Button>
              <Button className="bg-emerald-600 hover:bg-emerald-700 gap-2">
                <Activity className="h-4 w-4" />
                Real-time View
              </Button>
            </div>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="border-l-4 border-l-emerald-500 hover:shadow-lg transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Total Revenue</p>
                  <h3 className="text-3xl font-bold text-gray-900">
                    £{dashboardData.totalRevenue.toLocaleString()}
                  </h3>
                  <div className="flex items-center gap-1 mt-2">
                    <ArrowUpRight className="h-4 w-4 text-green-600" />
                    <span className="text-sm text-green-600 font-medium">+12.5%</span>
                  </div>
                </div>
                <div className="bg-emerald-100 p-4 rounded-full">
                  <DollarSign className="h-8 w-8 text-emerald-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-blue-500 hover:shadow-lg transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Platform Commission</p>
                  <h3 className="text-3xl font-bold text-gray-900">
                    £{dashboardData.platformRevenue.toLocaleString()}
                  </h3>
                  <div className="flex items-center gap-1 mt-2">
                    <ArrowUpRight className="h-4 w-4 text-green-600" />
                    <span className="text-sm text-green-600 font-medium">+8.2%</span>
                  </div>
                </div>
                <div className="bg-blue-100 p-4 rounded-full">
                  <TrendingUp className="h-8 w-8 text-blue-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-purple-500 hover:shadow-lg transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Total Visitors</p>
                  <h3 className="text-3xl font-bold text-gray-900">
                    {dashboardData.totalVisitors.toLocaleString()}
                  </h3>
                  <div className="flex items-center gap-1 mt-2">
                    <ArrowUpRight className="h-4 w-4 text-green-600" />
                    <span className="text-sm text-green-600 font-medium">+15.3%</span>
                  </div>
                </div>
                <div className="bg-purple-100 p-4 rounded-full">
                  <Eye className="h-8 w-8 text-purple-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-orange-500 hover:shadow-lg transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Total Orders</p>
                  <h3 className="text-3xl font-bold text-gray-900">
                    {dashboardData.totalOrders}
                  </h3>
                  <div className="flex items-center gap-1 mt-2">
                    <Clock className="h-4 w-4 text-orange-600" />
                    <span className="text-sm text-orange-600 font-medium">
                      {dashboardData.pendingOrders} pending
                    </span>
                  </div>
                </div>
                <div className="bg-orange-100 p-4 rounded-full">
                  <ShoppingCart className="h-8 w-8 text-orange-600" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Secondary Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Active Vendors</p>
                  <p className="text-2xl font-bold text-gray-900">{dashboardData.totalVendors}</p>
                </div>
                <Users className="h-8 w-8 text-gray-400" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Products</p>
                  <p className="text-2xl font-bold text-gray-900">{dashboardData.totalProducts}</p>
                </div>
                <Package className="h-8 w-8 text-gray-400" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Active Users</p>
                  <p className="text-2xl font-bold text-gray-900">{dashboardData.activeUsers}</p>
                </div>
                <Activity className="h-8 w-8 text-gray-400" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Avg Order Value</p>
                  <p className="text-2xl font-bold text-gray-900">
                    £{dashboardData.totalOrders > 0 ? (dashboardData.totalRevenue / dashboardData.totalOrders).toFixed(2) : '0.00'}
                  </p>
                </div>
                <BarChart3 className="h-8 w-8 text-gray-400" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Tabbed Content */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-5 lg:w-auto lg:inline-grid">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="vendors">Vendors</TabsTrigger>
            <TabsTrigger value="products">Products</TabsTrigger>
            <TabsTrigger value="orders">Orders</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </Tabs>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Top Vendors */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-emerald-600" />
                    Top Performing Vendors
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {analytics.topVendors.slice(0, 5).map((vendor, index) => (
                      <div key={vendor.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center gap-3">
                          <div className="bg-emerald-600 text-white w-8 h-8 rounded-full flex items-center justify-center font-bold">
                            {index + 1}
                          </div>
                          <div>
                            <p className="font-semibold text-gray-900">{vendor.name}</p>
                            <p className="text-sm text-gray-600">{vendor.totalProducts} products</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="font-bold text-emerald-600">£{vendor.totalRevenue?.toFixed(2) || '0.00'}</p>
                          <p className="text-xs text-gray-500">{vendor.totalOrders} orders</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Top Products */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Package className="h-5 w-5 text-blue-600" />
                    Most Clicked Products
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {analytics.topProducts.slice(0, 5).map((product, index) => (
                      <div key={product.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center gap-3">
                          <img 
                            src={product.image} 
                            alt={product.name}
                            className="w-12 h-12 object-cover rounded"
                          />
                          <div>
                            <p className="font-semibold text-gray-900 line-clamp-1">{product.name}</p>
                            <p className="text-sm text-gray-600">{product.clicks} clicks • {product.views} views</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="font-bold text-gray-900">£{product.price}</p>
                          <Badge variant="secondary" className="text-xs">
                            {((product.conversions / product.views) * 100).toFixed(1)}% CVR
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Recent Activity */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Orders</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-3 px-4">Order ID</th>
                        <th className="text-left py-3 px-4">Customer</th>
                        <th className="text-left py-3 px-4">Vendor</th>
                        <th className="text-left py-3 px-4">Amount</th>
                        <th className="text-left py-3 px-4">Status</th>
                        <th className="text-left py-3 px-4">Date</th>
                      </tr>
                    </thead>
                    <tbody>
                      {orders.slice(0, 10).map((order) => (
                        <tr key={order.id} className="border-b hover:bg-gray-50">
                          <td className="py-3 px-4 font-mono text-sm">#{order.id}</td>
                          <td className="py-3 px-4">{order.customer_name || 'N/A'}</td>
                          <td className="py-3 px-4">{order.vendor_name || 'Multiple'}</td>
                          <td className="py-3 px-4 font-semibold">£{order.total?.toFixed(2) || '0.00'}</td>
                          <td className="py-3 px-4">
                            <Badge className={
                              order.status === 'completed' ? 'bg-green-100 text-green-800' :
                              order.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-gray-100 text-gray-800'
                            }>
                              {order.status}
                            </Badge>
                          </td>
                          <td className="py-3 px-4 text-sm text-gray-600">
                            {new Date(order.created_at).toLocaleDateString()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Vendors Tab - Will continue in next part */}
          <TabsContent value="vendors" className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>All Vendors ({vendors.length})</CardTitle>
                  <div className="flex gap-2">
                    <Input placeholder="Search vendors..." className="w-64" />
                    <Button variant="outline" size="icon">
                      <Filter className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-3 px-4">Vendor Name</th>
                        <th className="text-left py-3 px-4">Products</th>
                        <th className="text-left py-3 px-4">Total Sales</th>
                        <th className="text-left py-3 px-4">Revenue</th>
                        <th className="text-left py-3 px-4">Commission (15%)</th>
                        <th className="text-left py-3 px-4">Status</th>
                        <th className="text-left py-3 px-4">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {vendors.map((vendor) => (
                        <tr key={vendor.id} className="border-b hover:bg-gray-50">
                          <td className="py-4 px-4">
                            <div>
                              <p className="font-semibold text-gray-900">{vendor.name}</p>
                              <p className="text-sm text-gray-600">{vendor.email}</p>
                            </div>
                          </td>
                          <td className="py-4 px-4">{vendor.totalProducts || 0}</td>
                          <td className="py-4 px-4">{vendor.totalOrders || 0}</td>
                          <td className="py-4 px-4 font-semibold text-emerald-600">
                            £{vendor.totalRevenue?.toFixed(2) || '0.00'}
                          </td>
                          <td className="py-4 px-4 font-semibold text-blue-600">
                            £{vendor.commission?.toFixed(2) || '0.00'}
                          </td>
                          <td className="py-4 px-4">
                            <Badge className="bg-green-100 text-green-800">Active</Badge>
                          </td>
                          <td className="py-4 px-4">
                            <Button variant="ghost" size="sm">View Details</Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Products Tab */}
          <TabsContent value="products" className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>All Products ({products.length})</CardTitle>
                  <Input placeholder="Search products..." className="w-64" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-3 px-4">Product</th>
                        <th className="text-left py-3 px-4">Vendor</th>
                        <th className="text-left py-3 px-4">Price</th>
                        <th className="text-left py-3 px-4">Stock</th>
                        <th className="text-left py-3 px-4">Clicks</th>
                        <th className="text-left py-3 px-4">Views</th>
                        <th className="text-left py-3 px-4">CVR</th>
                      </tr>
                    </thead>
                    <tbody>
                      {analytics.topProducts.map((product) => (
                        <tr key={product.id} className="border-b hover:bg-gray-50">
                          <td className="py-4 px-4">
                            <div className="flex items-center gap-3">
                              <img src={product.image} alt={product.name} className="w-12 h-12 object-cover rounded" />
                              <div>
                                <p className="font-semibold text-gray-900">{product.name}</p>
                                <p className="text-sm text-gray-600">{product.category}</p>
                              </div>
                            </div>
                          </td>
                          <td className="py-4 px-4">{product.vendor?.name || 'N/A'}</td>
                          <td className="py-4 px-4 font-semibold">£{product.price}</td>
                          <td className="py-4 px-4">{product.stock}</td>
                          <td className="py-4 px-4">{product.clicks}</td>
                          <td className="py-4 px-4">{product.views}</td>
                          <td className="py-4 px-4">
                            <Badge variant="secondary">
                              {((product.conversions / product.views) * 100).toFixed(1)}%
                            </Badge>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Orders Tab */}
          <TabsContent value="orders" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Order Management & Delivery Tracking</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-3 px-4">Order ID</th>
                        <th className="text-left py-3 px-4">Customer</th>
                        <th className="text-left py-3 px-4">Vendor</th>
                        <th className="text-left py-3 px-4">Products</th>
                        <th className="text-left py-3 px-4">Total</th>
                        <th className="text-left py-3 px-4">Commission</th>
                        <th className="text-left py-3 px-4">Status</th>
                        <th className="text-left py-3 px-4">Delivery</th>
                      </tr>
                    </thead>
                    <tbody>
                      {orders.map((order) => (
                        <tr key={order.id} className="border-b hover:bg-gray-50">
                          <td className="py-4 px-4 font-mono text-sm">#{order.id}</td>
                          <td className="py-4 px-4">{order.customer_name || 'N/A'}</td>
                          <td className="py-4 px-4">{order.vendor_name || 'Multiple'}</td>
                          <td className="py-4 px-4">{order.items?.length || 0} items</td>
                          <td className="py-4 px-4 font-semibold">£{order.total?.toFixed(2) || '0.00'}</td>
                          <td className="py-4 px-4 text-blue-600 font-semibold">
                            £{((order.total || 0) * 0.15).toFixed(2)}
                          </td>
                          <td className="py-4 px-4">
                            <Badge className={
                              order.status === 'completed' ? 'bg-green-100 text-green-800' :
                              order.status === 'processing' ? 'bg-blue-100 text-blue-800' :
                              order.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-gray-100 text-gray-800'
                            }>
                              {order.status}
                            </Badge>
                          </td>
                          <td className="py-4 px-4">
                            <div className="flex items-center gap-2">
                              <Truck className="h-4 w-4 text-emerald-600" />
                              <span className="text-sm">
                                {order.status === 'completed' ? 'Delivered' : 
                                 order.status === 'processing' ? 'In Transit' : 
                                 'Pending'}
                              </span>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Analytics Tab */}
          <TabsContent value="analytics" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Website Traffic Statistics</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                      <div>
                        <p className="text-sm text-gray-600">Total Page Views</p>
                        <p className="text-2xl font-bold">45,280</p>
                      </div>
                      <Eye className="h-8 w-8 text-purple-600" />
                    </div>
                    <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                      <div>
                        <p className="text-sm text-gray-600">Unique Visitors</p>
                        <p className="text-2xl font-bold">15,420</p>
                      </div>
                      <Users className="h-8 w-8 text-blue-600" />
                    </div>
                    <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                      <div>
                        <p className="text-sm text-gray-600">Avg. Session Duration</p>
                        <p className="text-2xl font-bold">4m 32s</p>
                      </div>
                      <Clock className="h-8 w-8 text-orange-600" />
                    </div>
                    <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                      <div>
                        <p className="text-sm text-gray-600">Bounce Rate</p>
                        <p className="text-2xl font-bold">32.5%</p>
                      </div>
                      <Activity className="h-8 w-8 text-red-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Conversion Metrics</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                      <div>
                        <p className="text-sm text-gray-600">Overall Conversion Rate</p>
                        <p className="text-2xl font-bold">3.8%</p>
                      </div>
                      <TrendingUp className="h-8 w-8 text-green-600" />
                    </div>
                    <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                      <div>
                        <p className="text-sm text-gray-600">Add to Cart Rate</p>
                        <p className="text-2xl font-bold">12.4%</p>
                      </div>
                      <ShoppingCart className="h-8 w-8 text-emerald-600" />
                    </div>
                    <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                      <div>
                        <p className="text-sm text-gray-600">Cart Abandonment</p>
                        <p className="text-2xl font-bold">68.2%</p>
                      </div>
                      <XCircle className="h-8 w-8 text-red-600" />
                    </div>
                    <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                      <div>
                        <p className="text-sm text-gray-600">Repeat Customer Rate</p>
                        <p className="text-2xl font-bold">45.3%</p>
                      </div>
                      <CheckCircle className="h-8 w-8 text-blue-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Top Pages */}
            <Card>
              <CardHeader>
                <CardTitle>Most Visited Pages</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {[
                    { page: '/products', views: 12420, percentage: 27.4 },
                    { page: '/', views: 8930, percentage: 19.7 },
                    { page: '/cart', views: 6540, percentage: 14.4 },
                    { page: '/product/[id]', views: 5890, percentage: 13.0 },
                    { page: '/vendor/dashboard', views: 3280, percentage: 7.2 }
                  ].map((item, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-mono text-sm">{item.page}</span>
                          <span className="text-sm text-gray-600">{item.views.toLocaleString()} views ({item.percentage}%)</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-emerald-600 h-2 rounded-full" 
                            style={{ width: `${item.percentage}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>

      <Footer />
    </div>
  );
};

export default AdminDashboard;
