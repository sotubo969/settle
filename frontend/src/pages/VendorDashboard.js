import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { toast } from 'sonner';
import { 
  LayoutDashboard, Package, ShoppingCart, DollarSign, TrendingUp,
  Users, Eye, MousePointer, Clock, CheckCircle, AlertCircle,
  ChevronLeft, ChevronRight, RefreshCw, Store, Truck, CreditCard,
  ArrowUpRight, ArrowDownRight, Mail, Phone, MapPin, Calendar,
  BarChart3, PieChart, Search, Filter, Download, Plus, XCircle,
  Banknote, Receipt, Percent, Box, Target, Award, Megaphone
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const VendorDashboard = () => {
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  
  // Data states
  const [dashboardData, setDashboardData] = useState(null);
  const [orders, setOrders] = useState([]);
  const [sales, setSales] = useState(null);
  const [transactions, setTransactions] = useState(null);
  const [productAnalytics, setProductAnalytics] = useState([]);
  
  // Filter states
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [dateRange, setDateRange] = useState('30');
  const [currentPage, setCurrentPage] = useState(1);
  
  const ITEMS_PER_PAGE = 10;
  const getToken = () => localStorage.getItem('afroToken');
  const getStoredUser = () => {
    try {
      const savedUser = localStorage.getItem('afroUser');
      return savedUser ? JSON.parse(savedUser) : null;
    } catch {
      return null;
    }
  };

  useEffect(() => {
    if (authLoading) return;
    
    const token = getToken();
    const localUser = getStoredUser();
    
    if (!token || (!isAuthenticated && !localUser)) {
      navigate('/login');
      return;
    }
    
    fetchDashboardData();
  }, [isAuthenticated, authLoading, navigate]);

  const fetchDashboardData = useCallback(async () => {
    setLoading(true);
    setRefreshing(true);
    try {
      const token = getToken();
      const headers = { 'Authorization': `Bearer ${token}` };
      
      const [dashRes, ordersRes, salesRes, transRes, analyticsRes] = await Promise.all([
        fetch(`${API_URL}/api/vendor/dashboard`, { headers }),
        fetch(`${API_URL}/api/vendor/orders`, { headers }),
        fetch(`${API_URL}/api/vendor/sales?days=${dateRange}`, { headers }),
        fetch(`${API_URL}/api/vendor/transactions`, { headers }),
        fetch(`${API_URL}/api/vendor/products/analytics`, { headers })
      ]);
      
      if (!dashRes.ok) {
        if (dashRes.status === 403) {
          toast.error('You are not registered as a vendor');
          navigate('/become-vendor');
          return;
        }
        throw new Error('Failed to fetch dashboard data');
      }
      
      const [dashData, ordersData, salesData, transData, analyticsData] = await Promise.all([
        dashRes.json(),
        ordersRes.json(),
        salesRes.json(),
        transRes.json(),
        analyticsRes.json()
      ]);
      
      setDashboardData(dashData);
      setOrders(ordersData.orders || []);
      setSales(salesData);
      setTransactions(transData);
      setProductAnalytics(analyticsData.products || []);
      toast.success('Dashboard data refreshed');
    } catch (err) {
      toast.error(err.message);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [dateRange, navigate]);

  // Navigation tabs
  const tabs = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'orders', label: 'Orders', icon: ShoppingCart, badge: dashboardData?.stats?.pendingOrders },
    { id: 'products', label: 'Products', icon: Package },
    { id: 'sales', label: 'Sales Analytics', icon: BarChart3 },
    { id: 'transactions', label: 'Transactions', icon: CreditCard },
    { id: 'advertise', label: 'Advertise', icon: Megaphone, highlight: true },
  ];

  // Stat Card Component - Professional single color theme
  const StatCard = ({ title, value, subtitle, icon: Icon, trend, trendValue }) => {
    return (
      <div className="relative overflow-hidden bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:shadow-md transition-all duration-300">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-500">{title}</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
            {subtitle && <p className="text-sm text-gray-400 mt-1">{subtitle}</p>}
            {trend && (
              <div className={`flex items-center mt-2 ${trend === 'up' ? 'text-emerald-600' : 'text-red-500'}`}>
                {trend === 'up' ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                <span className="text-sm font-medium ml-1">{trendValue}</span>
              </div>
            )}
          </div>
          <div className="p-3 rounded-xl bg-emerald-50 text-emerald-600">
            <Icon className="w-6 h-6" />
          </div>
        </div>
      </div>
    );
  };

  // Status Badge Component
  const StatusBadge = ({ status, size = 'normal' }) => {
    const statusConfig = {
      pending: { bg: 'bg-amber-100', text: 'text-amber-700', dot: 'bg-amber-500' },
      confirmed: { bg: 'bg-blue-100', text: 'text-blue-700', dot: 'bg-blue-500' },
      processing: { bg: 'bg-indigo-100', text: 'text-indigo-700', dot: 'bg-indigo-500' },
      shipped: { bg: 'bg-purple-100', text: 'text-purple-700', dot: 'bg-purple-500' },
      delivered: { bg: 'bg-emerald-100', text: 'text-emerald-700', dot: 'bg-emerald-500' },
      completed: { bg: 'bg-emerald-100', text: 'text-emerald-700', dot: 'bg-emerald-500' },
      paid: { bg: 'bg-emerald-100', text: 'text-emerald-700', dot: 'bg-emerald-500' },
      cancelled: { bg: 'bg-gray-100', text: 'text-gray-700', dot: 'bg-gray-500' },
    };
    const config = statusConfig[status] || statusConfig.pending;
    
    return (
      <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full ${size === 'small' ? 'text-xs' : 'text-sm'} font-medium ${config.bg} ${config.text}`}>
        <span className={`w-2 h-2 rounded-full ${config.dot}`}></span>
        {status?.replace('_', ' ').toUpperCase()}
      </span>
    );
  };

  // Filter orders
  const filteredOrders = orders.filter(o => {
    const matchesSearch = o.orderId?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         o.customer?.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         o.customer?.email?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || o.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  // Pagination
  const paginate = (items) => {
    const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
    return items.slice(startIndex, startIndex + ITEMS_PER_PAGE);
  };
  const totalPages = (items) => Math.ceil(items.length / ITEMS_PER_PAGE);

  // Loading state
  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-50">
        <Header />
        <div className="flex items-center justify-center h-[calc(100vh-200px)]">
          <div className="text-center">
            <div className="relative">
              <div className="w-20 h-20 border-4 border-purple-200 rounded-full animate-pulse"></div>
              <div className="absolute top-0 left-0 w-20 h-20 border-4 border-purple-600 rounded-full animate-spin border-t-transparent"></div>
            </div>
            <p className="mt-4 text-gray-600 font-medium">Loading your dashboard...</p>
          </div>
        </div>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-indigo-50">
      <Header />
      
      <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header Section */}
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-8 gap-4">
          <div>
            <div className="flex items-center gap-3">
              <div className="p-3 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl shadow-lg">
                <Store className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Vendor Dashboard</h1>
                <p className="text-gray-500 mt-1">
                  Welcome, <span className="font-semibold text-purple-600">{dashboardData?.vendor?.businessName || user?.name}</span>
                </p>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className="px-4 py-2.5 bg-white border border-gray-200 rounded-xl text-sm font-medium focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="7">Last 7 days</option>
              <option value="30">Last 30 days</option>
              <option value="90">Last 90 days</option>
              <option value="365">Last year</option>
            </select>
            
            <button 
              onClick={fetchDashboardData}
              disabled={refreshing}
              className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-xl hover:from-purple-600 hover:to-purple-700 transition-all shadow-lg shadow-purple-500/30 font-medium disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
              {refreshing ? 'Refreshing...' : 'Refresh'}
            </button>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-2 mb-8 overflow-x-auto">
          <div className="flex gap-1 min-w-max">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => { 
                  if (tab.id === 'advertise') {
                    navigate('/vendor/ads');
                  } else {
                    setActiveTab(tab.id); 
                    setCurrentPage(1); 
                    setSearchTerm(''); 
                  }
                }}
                className={`relative flex items-center gap-2 px-4 py-2.5 rounded-lg font-medium transition-all ${
                  tab.highlight
                    ? 'bg-emerald-600 text-white hover:bg-emerald-700'
                    : activeTab === tab.id 
                      ? 'bg-gray-900 text-white' 
                      : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                <span className="text-sm">{tab.label}</span>
                {tab.badge > 0 && (
                  <span className={`ml-1 px-1.5 py-0.5 text-xs font-medium rounded ${
                    activeTab === tab.id ? 'bg-white text-gray-900' : 'bg-red-500 text-white'
                  }`}>
                    {tab.badge}
                  </span>
                )}
                {tab.highlight && (
                  <span className="ml-1 px-1.5 py-0.5 bg-white/20 rounded text-xs">NEW</span>
                )}
              </button>
            ))}
          </div>
        </div>

        {/* ==================== OVERVIEW TAB ==================== */}
        {activeTab === 'overview' && dashboardData && (
          <div className="space-y-6">
            {/* Main Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <StatCard 
                title="Total Revenue" 
                value={`£${dashboardData.stats.totalRevenue?.toLocaleString()}`}
                subtitle="Gross earnings"
                icon={DollarSign}
                trend="up"
                trendValue="+12.5%"
              />
              <StatCard 
                title="Net Earnings" 
                value={`£${dashboardData.stats.netEarnings?.toLocaleString()}`}
                subtitle="After platform fees"
                icon={Banknote}
              />
              <StatCard 
                title="Total Orders" 
                value={dashboardData.stats.totalOrders}
                subtitle={`${dashboardData.stats.pendingOrders} pending`}
                icon={ShoppingCart}
              />
              <StatCard 
                title="Products" 
                value={dashboardData.stats.totalProducts}
                subtitle="Active listings"
                icon={Package}
              />
            </div>

            {/* Secondary Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <StatCard title="Items Sold" value={dashboardData.stats.totalItemsSold} icon={Box} />
              <StatCard title="Platform Fees" value={`£${dashboardData.stats.commission?.toLocaleString()}`} icon={Percent} />
              <StatCard title="Product Views" value={dashboardData.stats.totalViews?.toLocaleString()} icon={Eye} />
              <StatCard title="Product Clicks" value={dashboardData.stats.totalClicks?.toLocaleString()} icon={MousePointer} />
            </div>

            {/* Advertise Banner - Professional Design */}
            <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
              <div className="flex flex-col md:flex-row items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-emerald-50 rounded-xl">
                    <Megaphone className="w-8 h-8 text-emerald-600" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">Boost Your Sales with Advertising</h3>
                    <p className="text-gray-500 text-sm mt-1">Get up to 5x more visibility • From £9.99 per week</p>
                  </div>
                </div>
                <button
                  onClick={() => navigate('/vendor/ads')}
                  className="px-6 py-3 bg-emerald-600 text-white font-medium rounded-lg hover:bg-emerald-700 transition-colors whitespace-nowrap"
                >
                  Create Ad →
                </button>
              </div>
            </div>

            {/* Quick Actions & Recent Orders */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Earnings Breakdown */}
              <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Earnings Breakdown</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-gray-200 rounded-lg"><DollarSign className="w-4 h-4 text-gray-600" /></div>
                      <div>
                        <p className="font-medium text-gray-900 text-sm">Gross Revenue</p>
                        <p className="text-xs text-gray-500">Total sales value</p>
                      </div>
                    </div>
                    <p className="text-lg font-bold text-gray-900">£{dashboardData.stats.totalRevenue?.toLocaleString()}</p>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-gray-200 rounded-lg"><Percent className="w-4 h-4 text-gray-600" /></div>
                      <div>
                        <p className="font-medium text-gray-900 text-sm">Platform Fee (10%)</p>
                        <p className="text-xs text-gray-500">AfroMarket commission</p>
                      </div>
                    </div>
                    <p className="text-lg font-bold text-red-600">-£{dashboardData.stats.commission?.toLocaleString()}</p>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-emerald-50 rounded-lg border border-emerald-200">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-emerald-100 rounded-lg"><Banknote className="w-4 h-4 text-emerald-600" /></div>
                      <div>
                        <p className="font-medium text-gray-900 text-sm">Your Net Earnings</p>
                        <p className="text-xs text-gray-500">Amount you receive</p>
                      </div>
                    </div>
                    <p className="text-lg font-bold text-emerald-600">£{dashboardData.stats.netEarnings?.toLocaleString()}</p>
                  </div>
                </div>
              </div>

              {/* Order Status */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Order Status</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-amber-50 rounded-lg"><Clock className="w-4 h-4 text-amber-600" /></div>
                      <span className="text-sm text-gray-700">Pending Orders</span>
                    </div>
                    <span className="text-lg font-bold text-gray-900">{dashboardData.stats.pendingOrders}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-blue-50 rounded-lg"><Truck className="w-4 h-4 text-blue-600" /></div>
                      <span className="text-sm text-gray-700">Processing</span>
                    </div>
                    <span className="text-lg font-bold text-gray-900">{dashboardData.stats.processingOrders}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-emerald-50 rounded-lg"><CheckCircle className="w-4 h-4 text-emerald-600" /></div>
                      <span className="text-sm text-gray-700">Completed</span>
                    </div>
                    <span className="text-lg font-bold text-gray-900">{dashboardData.stats.completedOrders}</span>
                  </div>
                </div>
                
                <button 
                  onClick={() => setActiveTab('orders')}
                  className="w-full mt-4 py-2.5 bg-gray-900 text-white rounded-lg text-sm font-medium hover:bg-gray-800 transition-colors"
                >
                  View All Orders
                </button>
              </div>
            </div>

            {/* Top Products */}
            <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-gray-900">🏆 Top Performing Products</h3>
                <button onClick={() => setActiveTab('products')} className="text-purple-600 text-sm font-medium hover:underline">View all</button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {productAnalytics.slice(0, 4).map((product, index) => (
                  <div key={product.id} className="p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors">
                    <div className="flex items-center gap-3 mb-3">
                      <span className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold text-white ${
                        index === 0 ? 'bg-gradient-to-br from-yellow-400 to-yellow-500' :
                        index === 1 ? 'bg-gradient-to-br from-gray-400 to-gray-500' :
                        index === 2 ? 'bg-gradient-to-br from-amber-600 to-amber-700' :
                        'bg-gradient-to-br from-purple-400 to-purple-500'
                      }`}>{index + 1}</span>
                      <img src={product.image} alt={product.name} className="w-12 h-12 rounded-lg object-cover" />
                    </div>
                    <p className="font-semibold text-gray-900 truncate">{product.name}</p>
                    <div className="flex items-center justify-between mt-2 text-sm">
                      <span className="text-gray-500">{product.views} views</span>
                      <span className="text-purple-600 font-medium">£{product.price}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ==================== ORDERS TAB ==================== */}
        {activeTab === 'orders' && (
          <div className="space-y-6">
            {/* Filters */}
            <div className="flex flex-col md:flex-row gap-4 bg-white p-4 rounded-2xl shadow-sm border border-gray-100">
              <div className="flex-1 relative">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Search by order ID, customer name or email..."
                  value={searchTerm}
                  onChange={(e) => { setSearchTerm(e.target.value); setCurrentPage(1); }}
                  className="w-full pl-12 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
              </div>
              <select
                value={statusFilter}
                onChange={(e) => { setStatusFilter(e.target.value); setCurrentPage(1); }}
                className="px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 min-w-[150px]"
              >
                <option value="all">All Status</option>
                <option value="pending">Pending</option>
                <option value="confirmed">Confirmed</option>
                <option value="completed">Completed</option>
              </select>
            </div>

            {/* Orders List */}
            <div className="space-y-4">
              {paginate(filteredOrders).map(order => (
                <div key={order.id} className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden hover:shadow-xl transition-shadow">
                  {/* Order Header */}
                  <div className="p-6 border-b border-gray-100">
                    <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                      <div>
                        <div className="flex items-center gap-3 mb-2">
                          <span className="font-mono font-bold text-lg text-purple-600">#{order.orderId}</span>
                          <StatusBadge status={order.status} />
                        </div>
                        <p className="text-sm text-gray-500">
                          <Calendar className="w-4 h-4 inline mr-1" />
                          {new Date(order.createdAt).toLocaleDateString('en-GB', { 
                            day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' 
                          })}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-2xl font-bold text-gray-900">£{order.total?.toFixed(2)}</p>
                        <p className="text-sm text-emerald-600 font-medium">Your earning: £{order.netEarning?.toFixed(2)}</p>
                      </div>
                    </div>
                  </div>
                  
                  {/* Customer Info & Items */}
                  <div className="p-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Customer Information */}
                    <div className="bg-blue-50 rounded-xl p-4">
                      <h4 className="font-semibold text-blue-800 mb-3 flex items-center gap-2">
                        <Users className="w-5 h-5" /> Customer Details for Delivery
                      </h4>
                      <div className="space-y-2 text-sm">
                        <p className="flex items-center gap-2 text-gray-700">
                          <span className="font-medium w-20">Name:</span> {order.customer?.name}
                        </p>
                        <p className="flex items-center gap-2 text-gray-700">
                          <Mail className="w-4 h-4 text-gray-400" /> {order.customer?.email}
                        </p>
                        <p className="flex items-center gap-2 text-gray-700">
                          <Phone className="w-4 h-4 text-gray-400" /> {order.customer?.phone || 'N/A'}
                        </p>
                        <p className="flex items-start gap-2 text-gray-700">
                          <MapPin className="w-4 h-4 text-gray-400 mt-0.5" />
                          <span>
                            {order.customer?.address}<br />
                            {order.customer?.city}, {order.customer?.postcode}
                          </span>
                        </p>
                      </div>
                    </div>
                    
                    {/* Order Items */}
                    <div>
                      <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                        <Package className="w-5 h-5" /> Order Items ({order.itemCount})
                      </h4>
                      <div className="space-y-2">
                        {order.items?.map((item, idx) => (
                          <div key={idx} className="flex items-center gap-3 p-2 bg-gray-50 rounded-lg">
                            <img src={item.image} alt={item.name} className="w-10 h-10 rounded-lg object-cover" />
                            <div className="flex-1 min-w-0">
                              <p className="font-medium text-gray-900 truncate">{item.name}</p>
                              <p className="text-sm text-gray-500">Qty: {item.quantity}</p>
                            </div>
                            <span className="font-semibold text-gray-900">£{item.price?.toFixed(2)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                  
                  {/* Order Footer */}
                  <div className="px-6 py-4 bg-gray-50 border-t border-gray-100">
                    <div className="flex flex-wrap items-center justify-between gap-4">
                      <div className="flex items-center gap-4 text-sm">
                        <span className="text-gray-500">Delivery: <StatusBadge status={order.deliveryStatus} size="small" /></span>
                        {order.trackingNumber && (
                          <span className="text-blue-600">Tracking: {order.trackingNumber}</span>
                        )}
                      </div>
                      <div className="flex items-center gap-2 text-sm">
                        <span className="text-gray-500">Platform fee:</span>
                        <span className="text-red-600 font-medium">-£{order.commission?.toFixed(2)}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            {totalPages(filteredOrders) > 1 && (
              <div className="flex items-center justify-center gap-2">
                <button onClick={() => setCurrentPage(p => Math.max(1, p - 1))} disabled={currentPage === 1}
                  className="p-2 border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-50">
                  <ChevronLeft className="w-5 h-5" />
                </button>
                <span className="px-4 py-2 bg-purple-100 text-purple-700 rounded-lg font-medium">
                  Page {currentPage} of {totalPages(filteredOrders)}
                </span>
                <button onClick={() => setCurrentPage(p => Math.min(totalPages(filteredOrders), p + 1))} disabled={currentPage === totalPages(filteredOrders)}
                  className="p-2 border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-50">
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            )}

            {filteredOrders.length === 0 && (
              <div className="text-center py-12 bg-white rounded-2xl">
                <ShoppingCart className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500">No orders found</p>
              </div>
            )}
          </div>
        )}

        {/* ==================== PRODUCTS TAB ==================== */}
        {activeTab === 'products' && (
          <div className="space-y-6">
            <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
              <div className="p-6 border-b border-gray-100">
                <h3 className="text-xl font-bold text-gray-900">Product Performance Analytics</h3>
                <p className="text-gray-500 mt-1">Track views, clicks, and conversions for your products</p>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="bg-gradient-to-r from-gray-50 to-gray-100">
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase">Product</th>
                      <th className="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase">Price</th>
                      <th className="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase">Stock</th>
                      <th className="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase">Views</th>
                      <th className="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase">Clicks</th>
                      <th className="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase">Add to Cart</th>
                      <th className="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase">Conversion</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {productAnalytics.map(product => (
                      <tr key={product.id} className="hover:bg-gray-50 transition-colors">
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-3">
                            <img src={product.image} alt={product.name} className="w-12 h-12 rounded-xl object-cover" />
                            <span className="font-medium text-gray-900">{product.name}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-center font-semibold text-gray-900">£{product.price}</td>
                        <td className="px-6 py-4 text-center">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            product.stock > 10 ? 'bg-emerald-100 text-emerald-700' :
                            product.stock > 0 ? 'bg-amber-100 text-amber-700' : 'bg-red-100 text-red-700'
                          }`}>
                            {product.stock}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-center">
                          <span className="flex items-center justify-center gap-1 text-blue-600">
                            <Eye className="w-4 h-4" /> {product.views}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-center">
                          <span className="flex items-center justify-center gap-1 text-purple-600">
                            <MousePointer className="w-4 h-4" /> {product.clicks}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-center">
                          <span className="flex items-center justify-center gap-1 text-emerald-600">
                            <ShoppingCart className="w-4 h-4" /> {product.cartAdds}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-center">
                          <span className={`font-semibold ${product.conversionRate > 5 ? 'text-emerald-600' : 'text-gray-600'}`}>
                            {product.conversionRate}%
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* ==================== SALES TAB ==================== */}
        {activeTab === 'sales' && sales && (
          <div className="space-y-6">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <StatCard title={`Revenue (${dateRange}d)`} value={`£${sales.summary?.totalRevenue?.toLocaleString()}`} icon={DollarSign} color="emerald" />
              <StatCard title={`Orders (${dateRange}d)`} value={sales.summary?.totalOrders} icon={ShoppingCart} color="blue" />
              <StatCard title={`Items Sold (${dateRange}d)`} value={sales.summary?.totalItemsSold} icon={Package} color="purple" />
            </div>

            {/* Product Sales Chart */}
            <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-6">📊 Product Sales Breakdown</h3>
              {sales.productSales?.length > 0 ? (
                <div className="space-y-4">
                  {sales.productSales.map((product, index) => (
                    <div key={product.productId} className="flex items-center gap-4">
                      <span className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold text-white ${
                        index === 0 ? 'bg-gradient-to-br from-yellow-400 to-yellow-500' :
                        index === 1 ? 'bg-gradient-to-br from-gray-400 to-gray-500' :
                        index === 2 ? 'bg-gradient-to-br from-amber-600 to-amber-700' :
                        'bg-gradient-to-br from-purple-400 to-purple-500'
                      }`}>{index + 1}</span>
                      <img src={product.image} alt={product.productName} className="w-12 h-12 rounded-xl object-cover" />
                      <div className="flex-1">
                        <p className="font-semibold text-gray-900">{product.productName}</p>
                        <p className="text-sm text-gray-500">{product.quantity} units sold</p>
                      </div>
                      <div className="text-right">
                        <p className="text-xl font-bold text-emerald-600">£{product.revenue?.toLocaleString()}</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <BarChart3 className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">No sales data for this period</p>
                </div>
              )}
            </div>

            {/* Daily Sales */}
            {sales.dailySales?.length > 0 && (
              <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
                <h3 className="text-xl font-bold text-gray-900 mb-6">📈 Daily Sales Trend</h3>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="bg-gray-50">
                        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Date</th>
                        <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 uppercase">Revenue</th>
                        <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase">Orders</th>
                        <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase">Items</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {sales.dailySales.slice(-10).reverse().map(day => (
                        <tr key={day.date} className="hover:bg-gray-50">
                          <td className="px-4 py-3 font-medium text-gray-900">{day.date}</td>
                          <td className="px-4 py-3 text-right font-semibold text-emerald-600">£{day.revenue?.toFixed(2)}</td>
                          <td className="px-4 py-3 text-center">{day.orders}</td>
                          <td className="px-4 py-3 text-center">{day.items}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ==================== TRANSACTIONS TAB ==================== */}
        {activeTab === 'transactions' && transactions && (
          <div className="space-y-6">
            {/* Summary */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <StatCard title="Gross Earnings" value={`£${transactions.summary?.totalGrossEarnings?.toLocaleString()}`} icon={DollarSign} color="blue" />
              <StatCard title="Platform Fees" value={`£${transactions.summary?.totalPlatformFees?.toLocaleString()}`} icon={Percent} color="red" />
              <StatCard title="Net Earnings" value={`£${transactions.summary?.totalNetEarnings?.toLocaleString()}`} icon={Banknote} color="emerald" />
              <StatCard title="Pending Payout" value={`£${transactions.summary?.pendingPayout?.toLocaleString()}`} icon={Clock} color="orange" />
            </div>

            {/* Transactions Table */}
            <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
              <div className="p-6 border-b border-gray-100">
                <h3 className="text-xl font-bold text-gray-900">Transaction History</h3>
                <p className="text-gray-500 mt-1">All your earnings and platform fee deductions</p>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="bg-gradient-to-r from-gray-50 to-gray-100">
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase">Order ID</th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase">Date</th>
                      <th className="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase">Items</th>
                      <th className="px-6 py-4 text-right text-xs font-semibold text-gray-600 uppercase">Gross</th>
                      <th className="px-6 py-4 text-right text-xs font-semibold text-gray-600 uppercase">Fee (10%)</th>
                      <th className="px-6 py-4 text-right text-xs font-semibold text-gray-600 uppercase">Net</th>
                      <th className="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase">Payout Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {transactions.transactions?.map(trans => (
                      <tr key={trans.id} className="hover:bg-gray-50 transition-colors">
                        <td className="px-6 py-4 font-mono font-semibold text-purple-600">{trans.orderId}</td>
                        <td className="px-6 py-4 text-gray-600">{new Date(trans.date).toLocaleDateString()}</td>
                        <td className="px-6 py-4 text-center">{trans.items}</td>
                        <td className="px-6 py-4 text-right font-medium">£{trans.grossAmount?.toFixed(2)}</td>
                        <td className="px-6 py-4 text-right text-red-600">-£{trans.platformFee?.toFixed(2)}</td>
                        <td className="px-6 py-4 text-right font-bold text-emerald-600">£{trans.netAmount?.toFixed(2)}</td>
                        <td className="px-6 py-4 text-center">
                          <StatusBadge status={trans.payoutStatus} size="small" />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>

      <Footer />
    </div>
  );
};

export default VendorDashboard;
