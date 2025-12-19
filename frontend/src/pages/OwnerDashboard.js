import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { 
  LayoutDashboard, Users, Package, BarChart3, CreditCard, Truck, 
  TrendingUp, DollarSign, ShoppingCart, Eye, MousePointer, 
  CheckCircle, Clock, XCircle, Search, Filter, RefreshCw,
  ChevronDown, ChevronUp, ArrowUpRight, ArrowDownRight,
  Store, AlertCircle, Calendar, MapPin, Phone, Mail
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const OwnerDashboard = () => {
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Data states
  const [dashboardData, setDashboardData] = useState(null);
  const [vendors, setVendors] = useState([]);
  const [products, setProducts] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [transactions, setTransactions] = useState(null);
  const [sales, setSales] = useState(null);
  const [deliveries, setDeliveries] = useState(null);
  
  // Filter states
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [deliveryStatusFilter, setDeliveryStatusFilter] = useState('all');
  
  // Check if user is owner
  const OWNER_EMAIL = 'sotubodammy@gmail.com';
  const isOwner = user?.email === OWNER_EMAIL;
  
  // Get token from localStorage
  const getToken = () => localStorage.getItem('afroToken');

  useEffect(() => {
    // Wait for auth to load
    if (authLoading) return;
    
    const token = getToken();
    if (!isAuthenticated || !token) {
      navigate('/login');
      return;
    }
    
    if (!isOwner) {
      navigate('/');
      return;
    }
    
    fetchDashboardData();
  }, [isAuthenticated, authLoading, isOwner, navigate]);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const token = getToken();
      const headers = { 'Authorization': `Bearer ${token}` };
      
      // Fetch all data in parallel
      const [dashRes, vendorsRes, productsRes, analyticsRes, transRes, salesRes, deliveriesRes] = await Promise.all([
        fetch(`${API_URL}/api/owner/dashboard`, { headers }),
        fetch(`${API_URL}/api/owner/vendors`, { headers }),
        fetch(`${API_URL}/api/owner/products`, { headers }),
        fetch(`${API_URL}/api/owner/analytics?days=30`, { headers }),
        fetch(`${API_URL}/api/owner/transactions`, { headers }),
        fetch(`${API_URL}/api/owner/sales`, { headers }),
        fetch(`${API_URL}/api/owner/deliveries`, { headers })
      ]);
      
      if (!dashRes.ok) throw new Error('Failed to fetch dashboard data');
      
      const [dashData, vendorsData, productsData, analyticsData, transData, salesData, deliveriesData] = await Promise.all([
        dashRes.json(),
        vendorsRes.json(),
        productsRes.json(),
        analyticsRes.json(),
        transRes.json(),
        salesRes.json(),
        deliveriesRes.json()
      ]);
      
      setDashboardData(dashData);
      setVendors(vendorsData.vendors || []);
      setProducts(productsData.products || []);
      setAnalytics(analyticsData);
      setTransactions(transData);
      setSales(salesData);
      setDeliveries(deliveriesData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const updateDeliveryStatus = async (orderId, status, trackingNumber = '', carrier = '') => {
    try {
      const token = getToken();
      const response = await fetch(`${API_URL}/api/owner/deliveries/${orderId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          deliveryStatus: status,
          trackingNumber,
          carrier
        })
      });
      
      if (response.ok) {
        fetchDashboardData();
      }
    } catch (err) {
      console.error('Failed to update delivery:', err);
    }
  };

  const approveVendor = async (vendorId, status) => {
    try {
      const token = getToken();
      const response = await fetch(`${API_URL}/api/owner/vendors/${vendorId}/approve?status=${status}`, {
        method: 'PUT',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        fetchDashboardData();
      }
    } catch (err) {
      console.error('Failed to update vendor:', err);
    }
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'vendors', label: 'Vendors', icon: Store },
    { id: 'products', label: 'Products', icon: Package },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'transactions', label: 'Transactions', icon: CreditCard },
    { id: 'sales', label: 'Sales', icon: TrendingUp },
    { id: 'deliveries', label: 'Deliveries', icon: Truck }
  ];

  const StatCard = ({ title, value, icon: Icon, trend, trendValue, color = 'emerald' }) => (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-500">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
          {trend && (
            <div className={`flex items-center mt-2 text-sm ${trend === 'up' ? 'text-emerald-600' : 'text-red-600'}`}>
              {trend === 'up' ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
              <span>{trendValue}</span>
            </div>
          )}
        </div>
        <div className={`p-3 bg-${color}-100 rounded-lg`}>
          <Icon className={`w-6 h-6 text-${color}-600`} />
        </div>
      </div>
    </div>
  );

  const StatusBadge = ({ status }) => {
    const statusColors = {
      approved: 'bg-emerald-100 text-emerald-800',
      pending: 'bg-yellow-100 text-yellow-800',
      rejected: 'bg-red-100 text-red-800',
      processing: 'bg-blue-100 text-blue-800',
      shipped: 'bg-purple-100 text-purple-800',
      in_transit: 'bg-indigo-100 text-indigo-800',
      out_for_delivery: 'bg-orange-100 text-orange-800',
      delivered: 'bg-emerald-100 text-emerald-800',
      completed: 'bg-emerald-100 text-emerald-800'
    };
    
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[status] || 'bg-gray-100 text-gray-800'}`}>
        {status?.replace('_', ' ').toUpperCase()}
      </span>
    );
  };

  // Filter functions
  const filteredVendors = vendors.filter(v => {
    const matchesSearch = v.businessName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         v.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || v.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const filteredProducts = products.filter(p => {
    const matchesSearch = p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         p.vendorName?.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  });

  const filteredDeliveries = deliveries?.deliveries?.filter(d => {
    const matchesSearch = d.orderId.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         d.customerName.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = deliveryStatusFilter === 'all' || d.deliveryStatus === deliveryStatusFilter;
    return matchesSearch && matchesStatus;
  }) || [];

  if (!isOwner) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900">Access Denied</h2>
            <p className="text-gray-600 mt-2">This page is only accessible to the owner.</p>
          </div>
        </div>
        <Footer />
      </div>
    );
  }

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="flex items-center justify-center h-96">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600"></div>
        </div>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Owner Dashboard</h1>
            <p className="text-gray-600 mt-1">Welcome back, {user?.name}</p>
          </div>
          <button 
            onClick={fetchDashboardData}
            className="mt-4 md:mt-0 flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh Data
          </button>
        </div>

        {/* Tabs */}
        <div className="flex flex-wrap gap-2 mb-8 bg-white p-2 rounded-xl shadow-sm">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                activeTab === tab.id 
                  ? 'bg-emerald-600 text-white' 
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              <span className="hidden sm:inline">{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && dashboardData && (
          <div className="space-y-8">
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <StatCard 
                title="Total Revenue" 
                value={`£${dashboardData.overview.totalRevenue.toLocaleString()}`}
                icon={DollarSign}
                color="emerald"
              />
              <StatCard 
                title="Total Orders" 
                value={dashboardData.overview.totalOrders}
                icon={ShoppingCart}
                color="blue"
              />
              <StatCard 
                title="Total Vendors" 
                value={dashboardData.overview.totalVendors}
                icon={Store}
                color="purple"
              />
              <StatCard 
                title="Total Products" 
                value={dashboardData.overview.totalProducts}
                icon={Package}
                color="orange"
              />
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <StatCard 
                title="Total Users" 
                value={dashboardData.overview.totalUsers}
                icon={Users}
                color="indigo"
              />
              <StatCard 
                title="Commission Earned" 
                value={`£${dashboardData.overview.totalCommission.toLocaleString()}`}
                icon={TrendingUp}
                color="emerald"
              />
              <StatCard 
                title="Pending Orders" 
                value={dashboardData.overview.pendingOrders}
                icon={Clock}
                color="yellow"
              />
              <StatCard 
                title="Page Visits (30d)" 
                value={dashboardData.overview.totalPageVisits}
                icon={Eye}
                color="pink"
              />
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Vendor Status</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Approved Vendors</span>
                    <span className="font-semibold text-emerald-600">{dashboardData.overview.approvedVendors}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Pending Approval</span>
                    <span className="font-semibold text-yellow-600">{dashboardData.overview.pendingVendors}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-emerald-600 h-2 rounded-full" 
                      style={{ width: `${(dashboardData.overview.approvedVendors / dashboardData.overview.totalVendors) * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Order Status</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Completed Orders</span>
                    <span className="font-semibold text-emerald-600">{dashboardData.overview.completedOrders}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Recent Orders (7d)</span>
                    <span className="font-semibold text-blue-600">{dashboardData.overview.recentOrders}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Product Clicks</span>
                    <span className="font-semibold text-purple-600">{dashboardData.overview.productClicks}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Vendors Tab */}
        {activeTab === 'vendors' && (
          <div className="space-y-6">
            {/* Filters */}
            <div className="flex flex-col md:flex-row gap-4 bg-white p-4 rounded-xl shadow-sm">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Search vendors..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                />
              </div>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-emerald-500"
              >
                <option value="all">All Status</option>
                <option value="approved">Approved</option>
                <option value="pending">Pending</option>
                <option value="rejected">Rejected</option>
              </select>
            </div>

            {/* Vendors Table */}
            <div className="bg-white rounded-xl shadow-sm overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Vendor</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Contact</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Location</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Products</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Revenue</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {filteredVendors.map(vendor => (
                      <tr key={vendor.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4">
                          <div>
                            <p className="font-medium text-gray-900">{vendor.businessName}</p>
                            <p className="text-sm text-gray-500">{vendor.description?.substring(0, 50)}...</p>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex flex-col text-sm">
                            <span className="flex items-center gap-1 text-gray-600">
                              <Mail className="w-3 h-3" /> {vendor.email}
                            </span>
                            <span className="flex items-center gap-1 text-gray-600">
                              <Phone className="w-3 h-3" /> {vendor.phone}
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-1 text-sm text-gray-600">
                            <MapPin className="w-3 h-3" />
                            {vendor.city}, {vendor.postcode}
                          </div>
                        </td>
                        <td className="px-6 py-4 text-center">
                          <span className="font-medium">{vendor.productCount}</span>
                        </td>
                        <td className="px-6 py-4">
                          <span className="font-medium text-emerald-600">£{vendor.revenue?.toLocaleString()}</span>
                        </td>
                        <td className="px-6 py-4">
                          <StatusBadge status={vendor.status} />
                        </td>
                        <td className="px-6 py-4">
                          {vendor.status === 'pending' && (
                            <div className="flex gap-2">
                              <button
                                onClick={() => approveVendor(vendor.id, 'approved')}
                                className="px-3 py-1 bg-emerald-100 text-emerald-700 rounded-lg text-sm hover:bg-emerald-200"
                              >
                                Approve
                              </button>
                              <button
                                onClick={() => approveVendor(vendor.id, 'rejected')}
                                className="px-3 py-1 bg-red-100 text-red-700 rounded-lg text-sm hover:bg-red-200"
                              >
                                Reject
                              </button>
                            </div>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Products Tab */}
        {activeTab === 'products' && (
          <div className="space-y-6">
            {/* Search */}
            <div className="bg-white p-4 rounded-xl shadow-sm">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Search products..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Products Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredProducts.map(product => (
                <div key={product.id} className="bg-white rounded-xl shadow-sm overflow-hidden hover:shadow-md transition-shadow">
                  <img src={product.image} alt={product.name} className="w-full h-48 object-cover" />
                  <div className="p-4">
                    <h3 className="font-semibold text-gray-900">{product.name}</h3>
                    <p className="text-sm text-gray-500">{product.brand}</p>
                    <div className="flex items-center justify-between mt-2">
                      <span className="text-lg font-bold text-emerald-600">£{product.price}</span>
                      <span className={`text-sm ${product.inStock ? 'text-emerald-600' : 'text-red-600'}`}>
                        {product.inStock ? `${product.stock} in stock` : 'Out of stock'}
                      </span>
                    </div>
                    <div className="mt-3 pt-3 border-t border-gray-100">
                      <p className="text-sm text-gray-600">Vendor: <span className="font-medium">{product.vendorName}</span></p>
                      <div className="flex items-center gap-4 mt-2 text-sm text-gray-500">
                        <span className="flex items-center gap-1">
                          <Eye className="w-4 h-4" /> {product.analytics?.views || 0} views
                        </span>
                        <span className="flex items-center gap-1">
                          <MousePointer className="w-4 h-4" /> {product.analytics?.clicks || 0} clicks
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && analytics && (
          <div className="space-y-6">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <StatCard 
                title="Total Visits (30d)" 
                value={analytics.totalVisits}
                icon={Eye}
                color="blue"
              />
              <StatCard 
                title="Total Orders (30d)" 
                value={analytics.totalOrders}
                icon={ShoppingCart}
                color="emerald"
              />
              <StatCard 
                title="Total Revenue (30d)" 
                value={`£${analytics.totalRevenue?.toLocaleString()}`}
                icon={DollarSign}
                color="purple"
              />
            </div>

            {/* Top Products */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Products by Clicks</h3>
              <div className="space-y-4">
                {analytics.topProducts?.map((product, index) => (
                  <div key={product.id} className="flex items-center gap-4">
                    <span className="w-8 h-8 flex items-center justify-center bg-emerald-100 text-emerald-600 rounded-full font-bold">
                      {index + 1}
                    </span>
                    <img src={product.image} alt={product.name} className="w-12 h-12 rounded-lg object-cover" />
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">{product.name}</p>
                    </div>
                    <span className="text-emerald-600 font-semibold">{product.clicks} clicks</span>
                  </div>
                ))}
                {(!analytics.topProducts || analytics.topProducts.length === 0) && (
                  <p className="text-gray-500 text-center py-4">No product analytics data yet</p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Transactions Tab */}
        {activeTab === 'transactions' && transactions && (
          <div className="space-y-6">
            {/* Summary */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <StatCard 
                title="Total Transactions" 
                value={transactions.summary?.totalTransactions}
                icon={CreditCard}
                color="blue"
              />
              <StatCard 
                title="Total Revenue" 
                value={`£${transactions.summary?.totalRevenue?.toLocaleString()}`}
                icon={DollarSign}
                color="emerald"
              />
              <StatCard 
                title="Total Commission" 
                value={`£${transactions.summary?.totalCommission?.toLocaleString()}`}
                icon={TrendingUp}
                color="purple"
              />
            </div>

            {/* Vendor Transactions */}
            <div className="bg-white rounded-xl shadow-sm overflow-hidden">
              <div className="p-6 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Transactions by Vendor</h3>
              </div>
              <div className="divide-y divide-gray-200">
                {transactions.vendorTransactions?.map(vendor => (
                  <div key={vendor.vendorId} className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h4 className="font-semibold text-gray-900">{vendor.vendorName}</h4>
                        <p className="text-sm text-gray-500">{vendor.totalOrders} orders</p>
                      </div>
                      <div className="text-right">
                        <p className="text-lg font-bold text-emerald-600">£{vendor.totalRevenue?.toLocaleString()}</p>
                        <p className="text-sm text-gray-500">Commission: £{vendor.totalCommission?.toLocaleString()}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* All Transactions Table */}
            <div className="bg-white rounded-xl shadow-sm overflow-hidden">
              <div className="p-6 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">All Transactions</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order ID</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Customer</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Items</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Commission</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {transactions.allTransactions?.slice(0, 20).map(trans => (
                      <tr key={trans.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 font-medium text-gray-900">{trans.orderId}</td>
                        <td className="px-6 py-4">
                          <div>
                            <p className="text-gray-900">{trans.customerName}</p>
                            <p className="text-sm text-gray-500">{trans.customerEmail}</p>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-center">{trans.items}</td>
                        <td className="px-6 py-4 font-medium text-emerald-600">£{trans.total?.toFixed(2)}</td>
                        <td className="px-6 py-4 text-gray-600">£{trans.commission?.toFixed(2)}</td>
                        <td className="px-6 py-4"><StatusBadge status={trans.status} /></td>
                        <td className="px-6 py-4 text-sm text-gray-500">
                          {new Date(trans.createdAt).toLocaleDateString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Sales Tab */}
        {activeTab === 'sales' && sales && (
          <div className="space-y-6">
            {/* Summary */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <StatCard 
                title="Total Vendors" 
                value={sales.summary?.totalVendors}
                icon={Store}
                color="blue"
              />
              <StatCard 
                title="Total Sales" 
                value={`£${sales.summary?.totalSales?.toLocaleString()}`}
                icon={DollarSign}
                color="emerald"
              />
              <StatCard 
                title="Your Commission" 
                value={`£${sales.summary?.totalCommission?.toLocaleString()}`}
                icon={TrendingUp}
                color="purple"
              />
              <StatCard 
                title="Vendor Earnings" 
                value={`£${sales.summary?.totalVendorEarnings?.toLocaleString()}`}
                icon={Users}
                color="orange"
              />
            </div>

            {/* Sales Table */}
            <div className="bg-white rounded-xl shadow-sm overflow-hidden">
              <div className="p-6 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Sales by Vendor</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Vendor</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Products</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Items Sold</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Orders</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total Sales</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Commission</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Vendor Earning</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {sales.vendorSales?.map(vendor => (
                      <tr key={vendor.vendorId} className="hover:bg-gray-50">
                        <td className="px-6 py-4">
                          <div>
                            <p className="font-medium text-gray-900">{vendor.vendorName}</p>
                            <p className="text-sm text-gray-500">{vendor.email}</p>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-center">{vendor.productCount}</td>
                        <td className="px-6 py-4 text-center">{vendor.totalItemsSold}</td>
                        <td className="px-6 py-4 text-center">{vendor.orderCount}</td>
                        <td className="px-6 py-4 font-medium text-emerald-600">£{vendor.totalSales?.toLocaleString()}</td>
                        <td className="px-6 py-4 text-purple-600">£{vendor.commissionEarned?.toLocaleString()}</td>
                        <td className="px-6 py-4 font-medium text-blue-600">£{vendor.vendorEarning?.toLocaleString()}</td>
                        <td className="px-6 py-4"><StatusBadge status={vendor.status} /></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Deliveries Tab */}
        {activeTab === 'deliveries' && deliveries && (
          <div className="space-y-6">
            {/* Status Summary */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {Object.entries(deliveries.statusCounts || {}).map(([status, count]) => (
                <div key={status} className="bg-white rounded-xl shadow-sm p-4 text-center">
                  <p className="text-2xl font-bold text-gray-900">{count}</p>
                  <p className="text-sm text-gray-500 capitalize">{status.replace('_', ' ')}</p>
                </div>
              ))}
            </div>

            {/* Filters */}
            <div className="flex flex-col md:flex-row gap-4 bg-white p-4 rounded-xl shadow-sm">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Search by order ID or customer..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                />
              </div>
              <select
                value={deliveryStatusFilter}
                onChange={(e) => setDeliveryStatusFilter(e.target.value)}
                className="px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-emerald-500"
              >
                <option value="all">All Status</option>
                <option value="processing">Processing</option>
                <option value="shipped">Shipped</option>
                <option value="in_transit">In Transit</option>
                <option value="out_for_delivery">Out for Delivery</option>
                <option value="delivered">Delivered</option>
              </select>
            </div>

            {/* Deliveries List */}
            <div className="space-y-4">
              {filteredDeliveries.map(delivery => (
                <div key={delivery.id} className="bg-white rounded-xl shadow-sm p-6">
                  <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                    <div>
                      <div className="flex items-center gap-3">
                        <h4 className="font-semibold text-gray-900">{delivery.orderId}</h4>
                        <StatusBadge status={delivery.deliveryStatus} />
                      </div>
                      <p className="text-sm text-gray-600 mt-1">
                        Customer: {delivery.customerName} ({delivery.customerEmail})
                      </p>
                      <p className="text-sm text-gray-500 mt-1">
                        {delivery.itemCount} items | £{delivery.total?.toFixed(2)}
                      </p>
                      {delivery.trackingNumber && (
                        <p className="text-sm text-blue-600 mt-1">
                          Tracking: {delivery.trackingNumber} ({delivery.carrier})
                        </p>
                      )}
                    </div>
                    <div className="flex flex-col gap-2">
                      <select
                        value={delivery.deliveryStatus}
                        onChange={(e) => updateDeliveryStatus(delivery.orderId, e.target.value)}
                        className="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-emerald-500"
                      >
                        <option value="processing">Processing</option>
                        <option value="shipped">Shipped</option>
                        <option value="in_transit">In Transit</option>
                        <option value="out_for_delivery">Out for Delivery</option>
                        <option value="delivered">Delivered</option>
                      </select>
                      <p className="text-xs text-gray-500">
                        Created: {new Date(delivery.createdAt).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  
                  {/* Shipping Address */}
                  <div className="mt-4 pt-4 border-t border-gray-100">
                    <p className="text-sm font-medium text-gray-700">Shipping Address:</p>
                    <p className="text-sm text-gray-600">
                      {delivery.shippingAddress?.fullName}, {delivery.shippingAddress?.address}, 
                      {delivery.shippingAddress?.city}, {delivery.shippingAddress?.postcode}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <Footer />
    </div>
  );
};

export default OwnerDashboard;
