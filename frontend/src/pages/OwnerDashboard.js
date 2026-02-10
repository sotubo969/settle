import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { toast } from 'sonner';
import { 
  LayoutDashboard, Users, Package, BarChart3, CreditCard, Truck, 
  TrendingUp, TrendingDown, DollarSign, ShoppingCart, Eye, MousePointer, 
  CheckCircle, Clock, XCircle, Search, RefreshCw, Settings,
  ArrowUpRight, ArrowDownRight, Store, AlertCircle, MapPin, Phone, Mail,
  Calendar, Filter, Download, MoreVertical, Edit, Trash2, Check, X,
  ChevronLeft, ChevronRight, Bell, Shield, Zap, Award, Target,
  PieChart, Activity, Box, UserCheck, UserX, Banknote, Receipt,
  Star, ThumbsUp, MessageSquare, FileText, Globe, Percent, Megaphone
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const OwnerDashboard = () => {
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(false); // Start as false, set to true when fetching
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const [dataLoaded, setDataLoaded] = useState(false);
  
  // Data states
  const [dashboardData, setDashboardData] = useState({});
  const [vendors, setVendors] = useState([]);
  const [products, setProducts] = useState([]);
  const [analytics, setAnalytics] = useState({});
  const [transactions, setTransactions] = useState([]);
  const [sales, setSales] = useState([]);
  const [deliveries, setDeliveries] = useState([]);
  const [ads, setAds] = useState([]);
  const [pendingAds, setPendingAds] = useState([]);
  
  // Filter states
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [deliveryStatusFilter, setDeliveryStatusFilter] = useState('all');
  const [adStatusFilter, setAdStatusFilter] = useState('all');
  const [dateRange, setDateRange] = useState('30');
  const [currentPage, setCurrentPage] = useState(1);
  const [sortBy, setSortBy] = useState('newest');
  
  // Modal states
  const [selectedVendor, setSelectedVendor] = useState(null);
  const [showVendorModal, setShowVendorModal] = useState(false);
  const [vendorApprovalNotes, setVendorApprovalNotes] = useState('');
  const [selectedDelivery, setSelectedDelivery] = useState(null);
  const [showTrackingModal, setShowTrackingModal] = useState(false);
  const [trackingForm, setTrackingForm] = useState({ trackingNumber: '', carrier: '', estimatedDelivery: '' });
  const [selectedAd, setSelectedAd] = useState(null);
  const [showAdModal, setShowAdModal] = useState(false);
  const [adApprovalNotes, setAdApprovalNotes] = useState('');
  
  const OWNER_EMAIL = 'sotubodammy@gmail.com';
  const getToken = () => localStorage.getItem('afroToken');
  const getStoredUser = () => {
    try {
      const savedUser = localStorage.getItem('afroUser');
      return savedUser ? JSON.parse(savedUser) : null;
    } catch {
      return null;
    }
  };
  const ITEMS_PER_PAGE = 10;
  
  // Check owner status from both context and localStorage
  const storedUser = getStoredUser();
  const currentUser = user || storedUser;
  const isOwner = currentUser?.email === OWNER_EMAIL;

  // Fetch function defined as useCallback
  const fetchDashboardData = useCallback(async () => {
    setLoading(true);
    setRefreshing(true);
    try {
      const token = getToken();
      if (!token) {
        console.error('No auth token found');
        setLoading(false);
        setRefreshing(false);
        return;
      }
      
      const headers = { 'Authorization': `Bearer ${token}` };
      
      // Helper function to fetch with fallback on error
      const fetchSafe = async (url, fallback) => {
        try {
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 15000);
          const res = await fetch(url, { headers, signal: controller.signal });
          clearTimeout(timeoutId);
          if (res.ok) {
            return await res.json();
          }
          console.warn(`API ${url} returned ${res.status}`);
          return fallback;
        } catch (err) {
          console.warn(`Failed to fetch ${url}:`, err.message);
          return fallback;
        }
      };
      
      // Fetch all data in parallel with individual error handling
      const [dashData, vendorsData, productsData, analyticsData, transData, salesData, deliveriesData, pendingAdsData, allAdsData] = await Promise.all([
        fetchSafe(`${API_URL}/api/owner/dashboard`, {}),
        fetchSafe(`${API_URL}/api/owner/vendors`, { vendors: [] }),
        fetchSafe(`${API_URL}/api/owner/products`, { products: [] }),
        fetchSafe(`${API_URL}/api/owner/analytics?days=${dateRange}`, {}),
        fetchSafe(`${API_URL}/api/owner/transactions`, []),
        fetchSafe(`${API_URL}/api/owner/sales`, []),
        fetchSafe(`${API_URL}/api/owner/deliveries`, []),
        fetchSafe(`${API_URL}/api/ads/pending`, { ads: [] }),
        fetchSafe(`${API_URL}/api/ads/all`, { ads: [] })
      ]);
      
      // Update state with fetched data
      setDashboardData(dashData || {});
      setVendors(vendorsData?.vendors || vendorsData || []);
      setProducts(productsData?.products || productsData || []);
      setAnalytics(analyticsData || {});
      setTransactions(transData || []);
      setSales(salesData || []);
      setDeliveries(deliveriesData || []);
      setPendingAds(pendingAdsData?.ads || []);
      setAds(allAdsData?.ads || []);
      
      console.log('Dashboard data loaded successfully');
      setDataLoaded(true);
    } catch (err) {
      console.error('Dashboard fetch error:', err.message);
      setError(err.message);
      toast.error('Failed to fetch some dashboard data');
      setDataLoaded(true); // Still mark as loaded to show error state
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [dateRange]);

  // Auth and data fetch effect
  useEffect(() => {
    // Wait for auth to finish loading
    if (authLoading) return;
    
    // Get auth info from localStorage as backup
    const token = getToken();
    const localUser = getStoredUser();
    
    // Check authentication - allow if either context user or localStorage user exists
    const hasAuth = isAuthenticated || (token && localUser);
    if (!hasAuth) {
      console.log('OwnerDashboard: No auth found, redirecting to login');
      navigate('/login');
      return;
    }
    
    // Check owner status - use context user or localStorage user
    const userToCheck = user || localUser;
    const isOwner = userToCheck?.email === OWNER_EMAIL || userToCheck?.is_admin === true;
    
    if (!isOwner) {
      console.log('OwnerDashboard: Not owner, redirecting to home');
      navigate('/');
      return;
    }
    
    console.log('OwnerDashboard: Owner verified, fetching data');
    fetchDashboardData();
  }, [isAuthenticated, authLoading, user, navigate, fetchDashboardData]);

  const updateDeliveryStatus = async (orderId, status, trackingNumber = '', carrier = '', estimatedDelivery = '') => {
    try {
      const token = getToken();
      const response = await fetch(`${API_URL}/api/owner/deliveries/${orderId}`, {
        method: 'PUT',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ deliveryStatus: status, trackingNumber, carrier, estimatedDelivery })
      });
      if (response.ok) {
        toast.success(`Delivery status updated to ${status.replace('_', ' ')}`);
        fetchDashboardData();
        setShowTrackingModal(false);
        setSelectedDelivery(null);
      }
    } catch (err) {
      toast.error('Failed to update delivery');
    }
  };

  const approveVendor = async (vendorId, status) => {
    try {
      const token = getToken();
      const response = await fetch(`${API_URL}/api/owner/vendors/${vendorId}/approve?status=${status}`, {
        method: 'PUT',
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ notes: vendorApprovalNotes })
      });
      if (response.ok) {
        toast.success(`Vendor ${status === 'approved' ? 'approved' : 'rejected'} successfully`);
        setShowVendorModal(false);
        setSelectedVendor(null);
        setVendorApprovalNotes('');
        fetchDashboardData();
      }
    } catch (err) {
      toast.error('Failed to update vendor');
    }
  };

  const openVendorModal = (vendor) => {
    setSelectedVendor(vendor);
    setVendorApprovalNotes('');
    setShowVendorModal(true);
  };

  const handleAdApproval = async (adId, action) => {
    try {
      const token = getToken();
      const response = await fetch(`${API_URL}/api/ads/${adId}/approve`, {
        method: 'POST',
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ad_id: adId,
          action: action,
          admin_notes: adApprovalNotes
        })
      });
      
      if (response.ok) {
        toast.success(`Ad ${action === 'approve' ? 'approved' : 'rejected'} successfully`);
        setShowAdModal(false);
        setSelectedAd(null);
        setAdApprovalNotes('');
        fetchDashboardData();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to update ad');
      }
    } catch (err) {
      toast.error('Failed to update ad');
    }
  };

  // Filter ads
  const filteredAds = ads.filter(ad => {
    const matchesSearch = ad.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         ad.vendor?.business_name?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = adStatusFilter === 'all' || ad.status === adStatusFilter;
    return matchesSearch && matchesStatus;
  });

  // Navigation tabs with icons and badges
  const tabs = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard, badge: null },
    { id: 'vendors', label: 'Vendors', icon: Store, badge: dashboardData?.pendingVendors || dashboardData?.overview?.pendingVendors },
    { id: 'products', label: 'Products', icon: Package, badge: null },
    { id: 'orders', label: 'Orders', icon: ShoppingCart, badge: dashboardData?.pendingOrders || dashboardData?.overview?.pendingOrders },
    { id: 'ads', label: 'Advertisements', icon: Megaphone, badge: pendingAds?.length },
    { id: 'analytics', label: 'Analytics', icon: BarChart3, badge: null },
    { id: 'transactions', label: 'Finance', icon: CreditCard, badge: null },
    { id: 'deliveries', label: 'Deliveries', icon: Truck, badge: deliveries?.statusCounts?.processing },
    { id: 'customers', label: 'Customers', icon: Users, badge: null },
  ];

  // Stat Card Component
  const StatCard = ({ title, value, subtitle, icon: Icon, trend, trendValue, color = 'emerald', size = 'normal' }) => {
    const colorClasses = {
      emerald: 'from-emerald-500 to-emerald-600',
      blue: 'from-blue-500 to-blue-600',
      purple: 'from-purple-500 to-purple-600',
      orange: 'from-orange-500 to-orange-600',
      pink: 'from-pink-500 to-pink-600',
      indigo: 'from-indigo-500 to-indigo-600',
      yellow: 'from-yellow-500 to-yellow-600',
      red: 'from-red-500 to-red-600',
    };
    
    return (
      <div className={`relative overflow-hidden bg-white rounded-2xl shadow-lg border border-gray-100 ${size === 'large' ? 'p-8' : 'p-6'} hover:shadow-xl transition-all duration-300 group`}>
        <div className="absolute top-0 right-0 w-32 h-32 transform translate-x-8 -translate-y-8">
          <div className={`w-full h-full rounded-full bg-gradient-to-br ${colorClasses[color]} opacity-10 group-hover:opacity-20 transition-opacity`}></div>
        </div>
        <div className="relative flex items-start justify-between">
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-500 uppercase tracking-wider">{title}</p>
            <p className={`${size === 'large' ? 'text-4xl' : 'text-3xl'} font-bold text-gray-900 mt-2`}>{value}</p>
            {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
            {trend && (
              <div className={`flex items-center mt-3 ${trend === 'up' ? 'text-emerald-600' : 'text-red-500'}`}>
                {trend === 'up' ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                <span className="text-sm font-semibold ml-1">{trendValue}</span>
                <span className="text-xs text-gray-500 ml-2">vs last period</span>
              </div>
            )}
          </div>
          <div className={`p-4 rounded-2xl bg-gradient-to-br ${colorClasses[color]} shadow-lg`}>
            <Icon className="w-7 h-7 text-white" />
          </div>
        </div>
      </div>
    );
  };

  // Status Badge Component
  const StatusBadge = ({ status, size = 'normal' }) => {
    const statusConfig = {
      approved: { bg: 'bg-emerald-100', text: 'text-emerald-700', dot: 'bg-emerald-500' },
      pending: { bg: 'bg-amber-100', text: 'text-amber-700', dot: 'bg-amber-500' },
      rejected: { bg: 'bg-red-100', text: 'text-red-700', dot: 'bg-red-500' },
      processing: { bg: 'bg-blue-100', text: 'text-blue-700', dot: 'bg-blue-500' },
      shipped: { bg: 'bg-purple-100', text: 'text-purple-700', dot: 'bg-purple-500' },
      in_transit: { bg: 'bg-indigo-100', text: 'text-indigo-700', dot: 'bg-indigo-500' },
      out_for_delivery: { bg: 'bg-orange-100', text: 'text-orange-700', dot: 'bg-orange-500' },
      delivered: { bg: 'bg-emerald-100', text: 'text-emerald-700', dot: 'bg-emerald-500' },
      completed: { bg: 'bg-emerald-100', text: 'text-emerald-700', dot: 'bg-emerald-500' },
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

  // Progress Bar Component
  const ProgressBar = ({ value, max, color = 'emerald', showLabel = true }) => {
    const percentage = max > 0 ? (value / max) * 100 : 0;
    const colorClasses = {
      emerald: 'bg-emerald-500',
      blue: 'bg-blue-500',
      purple: 'bg-purple-500',
      orange: 'bg-orange-500',
    };
    
    return (
      <div className="w-full">
        <div className="flex justify-between mb-1">
          {showLabel && <span className="text-sm text-gray-600">{value}</span>}
          {showLabel && <span className="text-sm text-gray-400">{percentage.toFixed(0)}%</span>}
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div className={`${colorClasses[color]} h-2 rounded-full transition-all duration-500`} style={{ width: `${Math.min(percentage, 100)}%` }}></div>
        </div>
      </div>
    );
  };

  // Filter functions
  const filteredVendors = vendors.filter(v => {
    const matchesSearch = v.businessName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         v.email?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || v.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const filteredProducts = products.filter(p => {
    const matchesSearch = p.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         p.vendorName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         p.category?.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  });

  const filteredDeliveries = deliveries?.deliveries?.filter(d => {
    const matchesSearch = d.orderId?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         d.customerName?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = deliveryStatusFilter === 'all' || d.deliveryStatus === deliveryStatusFilter;
    return matchesSearch && matchesStatus;
  }) || [];

  // Pagination
  const paginate = (items) => {
    const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
    return items.slice(startIndex, startIndex + ITEMS_PER_PAGE);
  };

  const totalPages = (items) => Math.ceil(items.length / ITEMS_PER_PAGE);

  // Loading state - only show during auth loading or initial data fetch
  if (authLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
        <Header />
        <div className="flex items-center justify-center h-[calc(100vh-200px)]">
          <div className="text-center">
            <div className="relative">
              <div className="w-20 h-20 border-4 border-emerald-200 rounded-full animate-pulse"></div>
              <div className="absolute top-0 left-0 w-20 h-20 border-4 border-emerald-600 rounded-full animate-spin border-t-transparent"></div>
            </div>
            <p className="mt-4 text-gray-600 font-medium">Checking permissions...</p>
          </div>
        </div>
        <Footer />
      </div>
    );
  }

  // Show loading while fetching data
  if (loading && !dataLoaded) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
        <Header />
        <div className="flex items-center justify-center h-[calc(100vh-200px)]">
          <div className="text-center">
            <div className="relative">
              <div className="w-20 h-20 border-4 border-emerald-200 rounded-full animate-pulse"></div>
              <div className="absolute top-0 left-0 w-20 h-20 border-4 border-emerald-600 rounded-full animate-spin border-t-transparent"></div>
            </div>
            <p className="mt-4 text-gray-600 font-medium">Loading dashboard...</p>
          </div>
        </div>
        <Footer />
      </div>
    );
  }

  // Access denied
  if (!isOwner) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
        <Header />
        <div className="flex items-center justify-center h-[calc(100vh-200px)]">
          <div className="text-center bg-white p-12 rounded-3xl shadow-xl">
            <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <Shield className="w-10 h-10 text-red-500" />
            </div>
            <h2 className="text-3xl font-bold text-gray-900">Access Denied</h2>
            <p className="text-gray-600 mt-3 max-w-md">This dashboard is exclusively for the platform owner. Please contact support if you believe this is an error.</p>
          </div>
        </div>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50">
      <Header />
      
      {/* Dashboard Container */}
      <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Header Section */}
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-8 gap-4">
          <div>
            <div className="flex items-center gap-3">
              <div className="p-3 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-2xl shadow-lg">
                <Shield className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Owner Dashboard</h1>
                <p className="text-gray-500 mt-1">Welcome back, <span className="font-semibold text-emerald-600">{user?.name}</span></p>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className="px-4 py-2.5 bg-white border border-gray-200 rounded-xl text-sm font-medium focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
            >
              <option value="7">Last 7 days</option>
              <option value="30">Last 30 days</option>
              <option value="90">Last 90 days</option>
              <option value="365">Last year</option>
            </select>
            
            <button 
              onClick={fetchDashboardData}
              disabled={refreshing}
              className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-emerald-500 to-emerald-600 text-white rounded-xl hover:from-emerald-600 hover:to-emerald-700 transition-all shadow-lg shadow-emerald-500/30 font-medium disabled:opacity-50"
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
                onClick={() => { setActiveTab(tab.id); setCurrentPage(1); setSearchTerm(''); }}
                className={`relative flex items-center gap-2 px-5 py-3 rounded-xl font-medium transition-all ${
                  activeTab === tab.id 
                    ? 'bg-gradient-to-r from-emerald-500 to-emerald-600 text-white shadow-lg shadow-emerald-500/30' 
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <tab.icon className="w-5 h-5" />
                <span>{tab.label}</span>
                {tab.badge > 0 && (
                  <span className={`absolute -top-1 -right-1 w-5 h-5 flex items-center justify-center text-xs font-bold rounded-full ${
                    activeTab === tab.id ? 'bg-white text-emerald-600' : 'bg-red-500 text-white'
                  }`}>
                    {tab.badge}
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>

        {/* ==================== OVERVIEW TAB ==================== */}
        {activeTab === 'overview' && dashboardData && (
          <div className="space-y-8">
            {/* Main Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <StatCard 
                title="Total Revenue" 
                value={`£${(dashboardData.totalRevenue || dashboardData.overview?.totalRevenue || 0).toLocaleString()}`}
                subtitle="All time earnings"
                icon={DollarSign}
                trend="up"
                trendValue="+12.5%"
                color="emerald"
              />
              <StatCard 
                title="Total Orders" 
                value={(dashboardData.totalOrders || dashboardData.overview?.totalOrders || 0).toLocaleString()}
                subtitle={`${dashboardData.pendingOrders || dashboardData.overview?.pendingOrders || 0} pending`}
                icon={ShoppingCart}
                trend="up"
                trendValue="+8.2%"
                color="blue"
              />
              <StatCard 
                title="Commission Earned" 
                value={`£${(dashboardData.platformCommission || dashboardData.overview?.totalCommission || (dashboardData.totalRevenue || 0) * 0.1).toLocaleString()}`}
                subtitle="10% platform fee"
                icon={Percent}
                trend="up"
                trendValue="+15.3%"
                color="purple"
              />
              <StatCard 
                title="Active Vendors" 
                value={dashboardData.totalVendors || dashboardData.overview?.approvedVendors || 0}
                subtitle={`${dashboardData.pendingVendors || dashboardData.overview?.pendingVendors || 0} pending approval`}
                icon={Store}
                color="orange"
              />
            </div>

            {/* Secondary Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <StatCard title="Total Products" value={dashboardData.totalProducts || dashboardData.overview?.totalProducts || 0} icon={Package} color="indigo" />
              <StatCard title="Total Customers" value={dashboardData.totalUsers || dashboardData.overview?.totalUsers || 0} icon={Users} color="pink" />
              <StatCard title="Page Views" value={(dashboardData.totalPageVisits || dashboardData.overview?.totalPageVisits || 0).toLocaleString()} icon={Eye} color="blue" />
              <StatCard title="Product Clicks" value={(dashboardData.productClicks || dashboardData.overview?.productClicks || 0).toLocaleString()} icon={MousePointer} color="emerald" />
            </div>

            {/* Charts and Insights Row */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Revenue Breakdown */}
              <div className="lg:col-span-2 bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-xl font-bold text-gray-900">Revenue Breakdown</h3>
                  <div className="flex items-center gap-4 text-sm">
                    <span className="flex items-center gap-2"><span className="w-3 h-3 bg-emerald-500 rounded-full"></span> Revenue</span>
                    <span className="flex items-center gap-2"><span className="w-3 h-3 bg-purple-500 rounded-full"></span> Commission</span>
                  </div>
                </div>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-gradient-to-r from-emerald-50 to-emerald-100 rounded-xl">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-emerald-500 rounded-lg"><Banknote className="w-5 h-5 text-white" /></div>
                      <div>
                        <p className="font-semibold text-gray-900">Gross Revenue</p>
                        <p className="text-sm text-gray-500">Total sales value</p>
                      </div>
                    </div>
                    <p className="text-2xl font-bold text-emerald-600">£{(dashboardData.totalRevenue || dashboardData.overview?.totalRevenue || 0).toLocaleString()}</p>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-gradient-to-r from-purple-50 to-purple-100 rounded-xl">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-purple-500 rounded-lg"><Percent className="w-5 h-5 text-white" /></div>
                      <div>
                        <p className="font-semibold text-gray-900">Platform Commission</p>
                        <p className="text-sm text-gray-500">10% of all sales</p>
                      </div>
                    </div>
                    <p className="text-2xl font-bold text-purple-600">£{(dashboardData.platformCommission || dashboardData.overview?.totalCommission || (dashboardData.totalRevenue || 0) * 0.1).toLocaleString()}</p>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-gradient-to-r from-blue-50 to-blue-100 rounded-xl">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-blue-500 rounded-lg"><Store className="w-5 h-5 text-white" /></div>
                      <div>
                        <p className="font-semibold text-gray-900">Vendor Payouts</p>
                        <p className="text-sm text-gray-500">90% to vendors</p>
                      </div>
                    </div>
                    <p className="text-2xl font-bold text-blue-600">£{((dashboardData.totalRevenue || 0) * 0.9).toLocaleString()}</p>
                  </div>
                </div>
              </div>

              {/* Quick Actions & Alerts */}
              <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
                <h3 className="text-xl font-bold text-gray-900 mb-6">Quick Actions</h3>
                <div className="space-y-3">
                  {(dashboardData.pendingVendors || dashboardData.overview?.pendingVendors || 0) > 0 && (
                    <button onClick={() => { setActiveTab('vendors'); setStatusFilter('pending'); }} 
                      className="w-full flex items-center justify-between p-4 bg-amber-50 border border-amber-200 rounded-xl hover:bg-amber-100 transition-colors group">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-amber-500 rounded-lg"><UserCheck className="w-5 h-5 text-white" /></div>
                        <div className="text-left">
                          <p className="font-semibold text-amber-800">Pending Vendors</p>
                          <p className="text-sm text-amber-600">{dashboardData.pendingVendors || dashboardData.overview?.pendingVendors || 0} awaiting approval</p>
                        </div>
                      </div>
                      <ChevronRight className="w-5 h-5 text-amber-500 group-hover:translate-x-1 transition-transform" />
                    </button>
                  )}
                  
                  {(dashboardData.pendingOrders || dashboardData.overview?.pendingOrders || 0) > 0 && (
                    <button onClick={() => setActiveTab('orders')} 
                      className="w-full flex items-center justify-between p-4 bg-blue-50 border border-blue-200 rounded-xl hover:bg-blue-100 transition-colors group">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-blue-500 rounded-lg"><Clock className="w-5 h-5 text-white" /></div>
                        <div className="text-left">
                          <p className="font-semibold text-blue-800">Pending Orders</p>
                          <p className="text-sm text-blue-600">{dashboardData.pendingOrders || dashboardData.overview?.pendingOrders || 0} need processing</p>
                        </div>
                      </div>
                      <ChevronRight className="w-5 h-5 text-blue-500 group-hover:translate-x-1 transition-transform" />
                    </button>
                  )}
                  
                  <button onClick={() => setActiveTab('deliveries')} 
                    className="w-full flex items-center justify-between p-4 bg-purple-50 border border-purple-200 rounded-xl hover:bg-purple-100 transition-colors group">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-purple-500 rounded-lg"><Truck className="w-5 h-5 text-white" /></div>
                      <div className="text-left">
                        <p className="font-semibold text-purple-800">Track Deliveries</p>
                        <p className="text-sm text-purple-600">{deliveries?.totalDeliveries || 0} total shipments</p>
                      </div>
                    </div>
                    <ChevronRight className="w-5 h-5 text-purple-500 group-hover:translate-x-1 transition-transform" />
                  </button>
                  
                  <button onClick={() => setActiveTab('analytics')} 
                    className="w-full flex items-center justify-between p-4 bg-emerald-50 border border-emerald-200 rounded-xl hover:bg-emerald-100 transition-colors group">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-emerald-500 rounded-lg"><BarChart3 className="w-5 h-5 text-white" /></div>
                      <div className="text-left">
                        <p className="font-semibold text-emerald-800">View Analytics</p>
                        <p className="text-sm text-emerald-600">Performance insights</p>
                      </div>
                    </div>
                    <ChevronRight className="w-5 h-5 text-emerald-500 group-hover:translate-x-1 transition-transform" />
                  </button>
                </div>
              </div>
            </div>

            {/* Top Performers */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Top Vendors */}
              <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-xl font-bold text-gray-900">Top Vendors</h3>
                  <button onClick={() => setActiveTab('vendors')} className="text-emerald-600 text-sm font-medium hover:underline">View all</button>
                </div>
                <div className="space-y-4">
                  {Array.isArray(sales?.vendorSales) && sales.vendorSales.length > 0 ? sales.vendorSales.slice(0, 5).map((vendor, index) => (
                    <div key={vendor?.vendorId || index} className="flex items-center gap-4 p-3 rounded-xl hover:bg-gray-50 transition-colors">
                      <div className={`w-10 h-10 rounded-xl flex items-center justify-center font-bold text-white ${
                        index === 0 ? 'bg-gradient-to-br from-yellow-400 to-yellow-500' :
                        index === 1 ? 'bg-gradient-to-br from-gray-400 to-gray-500' :
                        index === 2 ? 'bg-gradient-to-br from-amber-600 to-amber-700' :
                        'bg-gradient-to-br from-gray-300 to-gray-400'
                      }`}>
                        {index + 1}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-semibold text-gray-900 truncate">{vendor?.vendorName || 'Vendor'}</p>
                        <p className="text-sm text-gray-500">{vendor?.orderCount || 0} orders</p>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-emerald-600">£{(vendor?.totalSales || 0).toLocaleString()}</p>
                        <p className="text-xs text-gray-500">{vendor?.productCount || 0} products</p>
                      </div>
                    </div>
                  )) : (
                    <p className="text-gray-500 text-center py-8">No vendor data yet</p>
                  )}
                </div>
              </div>

              {/* Top Products */}
              <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-xl font-bold text-gray-900">Top Products</h3>
                  <button onClick={() => setActiveTab('products')} className="text-emerald-600 text-sm font-medium hover:underline">View all</button>
                </div>
                <div className="space-y-4">
                  {Array.isArray(analytics?.topProducts) && analytics.topProducts.length > 0 ? analytics.topProducts.slice(0, 5).map((product, index) => (
                    <div key={product?.id || index} className="flex items-center gap-4 p-3 rounded-xl hover:bg-gray-50 transition-colors">
                      <img src={product?.image || '/placeholder.png'} alt={product?.name || 'Product'} className="w-12 h-12 rounded-xl object-cover" />
                      <div className="flex-1 min-w-0">
                        <p className="font-semibold text-gray-900 truncate">{product?.name || 'Product'}</p>
                        <p className="text-sm text-gray-500">{product?.clicks || 0} clicks</p>
                      </div>
                      <div className="flex items-center gap-1 text-emerald-600">
                        <TrendingUp className="w-4 h-4" />
                        <span className="font-semibold">#{index + 1}</span>
                      </div>
                    </div>
                  )) : (
                    <p className="text-gray-500 text-center py-8">No product data yet</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ==================== VENDORS TAB ==================== */}
        {activeTab === 'vendors' && (
          <div className="space-y-6">
            {/* Vendor Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <StatCard title="Total Vendors" value={vendors.length} icon={Store} color="blue" />
              <StatCard title="Approved" value={vendors.filter(v => v.status === 'approved').length} icon={CheckCircle} color="emerald" />
              <StatCard title="Pending" value={vendors.filter(v => v.status === 'pending').length} icon={Clock} color="orange" />
              <StatCard title="Rejected" value={vendors.filter(v => v.status === 'rejected').length} icon={XCircle} color="red" />
            </div>

            {/* Filters */}
            <div className="flex flex-col md:flex-row gap-4 bg-white p-4 rounded-2xl shadow-sm border border-gray-100">
              <div className="flex-1 relative">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Search vendors by name or email..."
                  value={searchTerm}
                  onChange={(e) => { setSearchTerm(e.target.value); setCurrentPage(1); }}
                  className="w-full pl-12 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                />
              </div>
              <select
                value={statusFilter}
                onChange={(e) => { setStatusFilter(e.target.value); setCurrentPage(1); }}
                className="px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-emerald-500 min-w-[150px]"
              >
                <option value="all">All Status</option>
                <option value="approved">Approved</option>
                <option value="pending">Pending</option>
                <option value="rejected">Rejected</option>
              </select>
            </div>

            {/* Vendors Table */}
            <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="bg-gradient-to-r from-gray-50 to-gray-100">
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Vendor</th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Contact</th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Location</th>
                      <th className="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider">Products</th>
                      <th className="px-6 py-4 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider">Revenue</th>
                      <th className="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider">Status</th>
                      <th className="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {paginate(filteredVendors).map(vendor => (
                      <tr key={vendor.id} className="hover:bg-gray-50 transition-colors">
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-gradient-to-br from-emerald-400 to-emerald-600 rounded-xl flex items-center justify-center text-white font-bold">
                              {vendor.businessName?.charAt(0)}
                            </div>
                            <div>
                              <p className="font-semibold text-gray-900">{vendor.businessName}</p>
                              <p className="text-sm text-gray-500 max-w-xs truncate">{vendor.description?.substring(0, 40)}...</p>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="space-y-1">
                            <p className="flex items-center gap-2 text-sm text-gray-600">
                              <Mail className="w-4 h-4 text-gray-400" /> {vendor.email}
                            </p>
                            <p className="flex items-center gap-2 text-sm text-gray-600">
                              <Phone className="w-4 h-4 text-gray-400" /> {vendor.phone}
                            </p>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <p className="flex items-center gap-2 text-sm text-gray-600">
                            <MapPin className="w-4 h-4 text-gray-400" /> {vendor.city}, {vendor.postcode}
                          </p>
                        </td>
                        <td className="px-6 py-4 text-center">
                          <span className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">
                            <Package className="w-4 h-4" /> {vendor.productCount}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-right">
                          <p className="font-bold text-emerald-600">£{vendor.revenue?.toLocaleString()}</p>
                          <p className="text-xs text-gray-500">{vendor.orderCount} orders</p>
                        </td>
                        <td className="px-6 py-4 text-center">
                          <StatusBadge status={vendor.status} />
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center justify-center gap-2">
                            {vendor.status === 'pending' && (
                              <>
                                <button onClick={() => openVendorModal(vendor)}
                                  className="px-3 py-1.5 bg-emerald-100 text-emerald-600 rounded-lg hover:bg-emerald-200 transition-colors text-sm font-medium" title="Review">
                                  Review
                                </button>
                              </>
                            )}
                            {vendor.status === 'approved' && (
                              <span className="text-sm text-emerald-600 font-medium">✓ Approved</span>
                            )}
                            {vendor.status === 'rejected' && (
                              <span className="text-sm text-red-600 font-medium">✗ Rejected</span>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              
              {/* Pagination */}
              {totalPages(filteredVendors) > 1 && (
                <div className="flex items-center justify-between px-6 py-4 border-t border-gray-100">
                  <p className="text-sm text-gray-600">
                    Showing {((currentPage - 1) * ITEMS_PER_PAGE) + 1} to {Math.min(currentPage * ITEMS_PER_PAGE, filteredVendors.length)} of {filteredVendors.length} vendors
                  </p>
                  <div className="flex items-center gap-2">
                    <button onClick={() => setCurrentPage(p => Math.max(1, p - 1))} disabled={currentPage === 1}
                      className="p-2 border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">
                      <ChevronLeft className="w-5 h-5" />
                    </button>
                    <span className="px-4 py-2 bg-emerald-100 text-emerald-700 rounded-lg font-medium">{currentPage}</span>
                    <button onClick={() => setCurrentPage(p => Math.min(totalPages(filteredVendors), p + 1))} disabled={currentPage === totalPages(filteredVendors)}
                      className="p-2 border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">
                      <ChevronRight className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ==================== PRODUCTS TAB ==================== */}
        {activeTab === 'products' && (
          <div className="space-y-6">
            {/* Product Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <StatCard title="Total Products" value={products.length} icon={Package} color="blue" />
              <StatCard title="In Stock" value={products.filter(p => p.inStock).length} icon={CheckCircle} color="emerald" />
              <StatCard title="Out of Stock" value={products.filter(p => !p.inStock).length} icon={AlertCircle} color="red" />
              <StatCard title="Featured" value={products.filter(p => p.featured).length} icon={Star} color="yellow" />
            </div>

            {/* Search */}
            <div className="bg-white p-4 rounded-2xl shadow-sm border border-gray-100">
              <div className="relative">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Search products by name, vendor, or category..."
                  value={searchTerm}
                  onChange={(e) => { setSearchTerm(e.target.value); setCurrentPage(1); }}
                  className="w-full pl-12 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Products Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {paginate(filteredProducts).map(product => (
                <div key={product.id} className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden hover:shadow-xl transition-all group">
                  <div className="relative">
                    <img src={product.image} alt={product.name} className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300" />
                    {product.featured && (
                      <span className="absolute top-3 left-3 px-2 py-1 bg-yellow-500 text-white text-xs font-bold rounded-lg flex items-center gap-1">
                        <Star className="w-3 h-3" /> Featured
                      </span>
                    )}
                    {!product.inStock && (
                      <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                        <span className="px-4 py-2 bg-red-500 text-white font-bold rounded-lg">Out of Stock</span>
                      </div>
                    )}
                  </div>
                  <div className="p-4">
                    <h3 className="font-bold text-gray-900 truncate">{product.name}</h3>
                    <p className="text-sm text-gray-500">{product.brand}</p>
                    <div className="flex items-center justify-between mt-3">
                      <span className="text-xl font-bold text-emerald-600">£{product.price}</span>
                      <span className="text-sm text-gray-500">{product.stock} in stock</span>
                    </div>
                    <div className="mt-3 pt-3 border-t border-gray-100">
                      <p className="text-sm text-gray-600 flex items-center gap-1">
                        <Store className="w-4 h-4" /> {product.vendorName}
                      </p>
                      <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                        <span className="flex items-center gap-1"><Eye className="w-3 h-3" /> {product.analytics?.views || 0}</span>
                        <span className="flex items-center gap-1"><MousePointer className="w-3 h-3" /> {product.analytics?.clicks || 0}</span>
                        <span className="flex items-center gap-1"><ShoppingCart className="w-3 h-3" /> {product.analytics?.cartAdds || 0}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            {totalPages(filteredProducts) > 1 && (
              <div className="flex items-center justify-center gap-2">
                <button onClick={() => setCurrentPage(p => Math.max(1, p - 1))} disabled={currentPage === 1}
                  className="p-2 border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-50">
                  <ChevronLeft className="w-5 h-5" />
                </button>
                <span className="px-4 py-2 bg-emerald-100 text-emerald-700 rounded-lg font-medium">
                  Page {currentPage} of {totalPages(filteredProducts)}
                </span>
                <button onClick={() => setCurrentPage(p => Math.min(totalPages(filteredProducts), p + 1))} disabled={currentPage === totalPages(filteredProducts)}
                  className="p-2 border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-50">
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            )}
          </div>
        )}

        {/* ==================== ORDERS TAB ==================== */}
        {activeTab === 'orders' && (
          <div className="space-y-6">
            {/* Order Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <StatCard title="Total Orders" value={Array.isArray(transactions) ? transactions.length : 0} icon={ShoppingCart} color="blue" />
              <StatCard title="Total Revenue" value={`£${Array.isArray(transactions) ? transactions.reduce((sum, o) => sum + (o?.total || o?.amount || 0), 0).toLocaleString() : '0'}`} icon={DollarSign} color="emerald" />
              <StatCard title="Pending" value={dashboardData?.pendingOrders || 0} icon={Clock} color="orange" />
              <StatCard title="Completed" value={Array.isArray(transactions) ? transactions.filter(o => o?.status === 'completed' || o?.status === 'confirmed').length : 0} icon={CheckCircle} color="emerald" />
            </div>

            {/* Orders Table */}
            <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
              <div className="p-6 border-b border-gray-100">
                <h3 className="text-xl font-bold text-gray-900">All Orders</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="bg-gradient-to-r from-gray-50 to-gray-100">
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase">Order ID</th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase">Customer</th>
                      <th className="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase">Items</th>
                      <th className="px-6 py-4 text-right text-xs font-semibold text-gray-600 uppercase">Total</th>
                      <th className="px-6 py-4 text-right text-xs font-semibold text-gray-600 uppercase">Commission</th>
                      <th className="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase">Status</th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase">Date</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {Array.isArray(transactions) && transactions.length > 0 ? transactions.slice(0, 20).map((order, idx) => (
                      <tr key={order?.id || idx} className="hover:bg-gray-50 transition-colors">
                        <td className="px-6 py-4">
                          <span className="font-mono font-semibold text-emerald-600">{order?.orderId || order?.id || 'N/A'}</span>
                        </td>
                        <td className="px-6 py-4">
                          <p className="font-medium text-gray-900">{order?.user || order?.customerName || 'Customer'}</p>
                          <p className="text-sm text-gray-500">{order?.customerEmail || ''}</p>
                        </td>
                        <td className="px-6 py-4 text-center">
                          <span className="inline-flex items-center justify-center w-8 h-8 bg-blue-100 text-blue-700 rounded-full font-semibold">
                            {Array.isArray(order?.items) ? order.items.length : (order?.items || 1)}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-right">
                          <span className="font-bold text-gray-900">£{(order?.total || order?.amount || 0).toFixed(2)}</span>
                        </td>
                        <td className="px-6 py-4 text-right">
                          <span className="font-medium text-purple-600">£{((order?.total || order?.amount || 0) * 0.1).toFixed(2)}</span>
                        </td>
                        <td className="px-6 py-4 text-center">
                          <StatusBadge status={order?.status || 'pending'} size="small" />
                        </td>
                        <td className="px-6 py-4">
                          <span className="text-sm text-gray-500">{order?.date || order?.created_at ? new Date(order?.date || order?.created_at).toLocaleDateString() : 'N/A'}</span>
                        </td>
                      </tr>
                    )) : (
                      <tr>
                        <td colSpan="7" className="px-6 py-8 text-center text-gray-500">No orders yet</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* ==================== ANALYTICS TAB ==================== */}
        {activeTab === 'analytics' && analytics && (
          <div className="space-y-6">
            {/* Analytics Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <StatCard title={`Visits (${dateRange}d)`} value={analytics.totalVisits?.toLocaleString() || '0'} icon={Eye} color="blue" size="large" />
              <StatCard title={`Orders (${dateRange}d)`} value={analytics.totalOrders?.toLocaleString() || '0'} icon={ShoppingCart} color="emerald" size="large" />
              <StatCard title={`Revenue (${dateRange}d)`} value={`£${analytics.totalRevenue?.toLocaleString() || '0'}`} icon={DollarSign} color="purple" size="large" />
            </div>

            {/* Top Products */}
            <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-6">Top Products by Engagement</h3>
              {Array.isArray(analytics?.topProducts) && analytics.topProducts.length > 0 ? (
                <div className="space-y-4">
                  {analytics.topProducts.map((product, index) => (
                    <div key={product?.id || index} className="flex items-center gap-4 p-4 bg-gray-50 rounded-xl">
                      <span className={`w-10 h-10 rounded-xl flex items-center justify-center font-bold text-white ${
                        index === 0 ? 'bg-gradient-to-br from-yellow-400 to-yellow-500' :
                        index === 1 ? 'bg-gradient-to-br from-gray-400 to-gray-500' :
                        index === 2 ? 'bg-gradient-to-br from-amber-600 to-amber-700' :
                        'bg-gradient-to-br from-gray-300 to-gray-400'
                      }`}>{index + 1}</span>
                      <img src={product?.image || '/placeholder.png'} alt={product?.name || 'Product'} className="w-16 h-16 rounded-xl object-cover" />
                      <div className="flex-1">
                        <p className="font-semibold text-gray-900">{product?.name || 'Product'}</p>
                        <div className="flex items-center gap-4 mt-1">
                          <ProgressBar value={product?.clicks || 0} max={analytics.topProducts[0]?.clicks || 1} color="emerald" showLabel={false} />
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-2xl font-bold text-emerald-600">{product?.clicks || 0}</p>
                        <p className="text-sm text-gray-500">clicks</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <BarChart3 className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">No analytics data available yet</p>
                  <p className="text-sm text-gray-400 mt-1">Data will appear as users interact with products</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ==================== FINANCE/TRANSACTIONS TAB ==================== */}
        {activeTab === 'transactions' && (
          <div className="space-y-6">
            {/* Finance Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <StatCard title="Gross Revenue" value={`£${(dashboardData?.totalRevenue || 0).toLocaleString()}`} icon={DollarSign} color="emerald" />
              <StatCard title="Your Commission" value={`£${(dashboardData?.platformCommission || (dashboardData?.totalRevenue || 0) * 0.1).toLocaleString()}`} icon={Percent} color="purple" />
              <StatCard title="Vendor Payouts" value={`£${((dashboardData?.totalRevenue || 0) * 0.9).toLocaleString()}`} icon={Banknote} color="blue" />
              <StatCard title="Avg Order Value" value={`£${dashboardData?.totalOrders > 0 ? ((dashboardData?.totalRevenue || 0) / dashboardData.totalOrders).toFixed(2) : '0.00'}`} icon={Receipt} color="orange" />
            </div>

            {/* Vendor Revenue Breakdown */}
            <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
              <div className="p-6 border-b border-gray-100">
                <h3 className="text-xl font-bold text-gray-900">Vendor Revenue Breakdown</h3>
                <p className="text-sm text-gray-500 mt-1">Revenue, commission, and payouts by vendor</p>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="bg-gradient-to-r from-gray-50 to-gray-100">
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase">Vendor</th>
                      <th className="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase">Products</th>
                      <th className="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase">Orders</th>
                      <th className="px-6 py-4 text-right text-xs font-semibold text-gray-600 uppercase">Total Sales</th>
                      <th className="px-6 py-4 text-right text-xs font-semibold text-gray-600 uppercase">Your Commission (10%)</th>
                      <th className="px-6 py-4 text-right text-xs font-semibold text-gray-600 uppercase">Vendor Payout (90%)</th>
                      <th className="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {Array.isArray(vendors) && vendors.length > 0 ? vendors.filter(v => v?.status === 'approved').map((vendor, idx) => (
                      <tr key={vendor?.id || idx} className="hover:bg-gray-50 transition-colors">
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-gradient-to-br from-emerald-400 to-emerald-600 rounded-xl flex items-center justify-center text-white font-bold">
                              {(vendor?.business_name || vendor?.businessName || 'V').charAt(0)}
                            </div>
                            <div>
                              <p className="font-semibold text-gray-900">{vendor?.business_name || vendor?.businessName || 'Vendor'}</p>
                              <p className="text-sm text-gray-500">{vendor?.email || ''}</p>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-center font-medium">{vendor?.productCount || 0}</td>
                        <td className="px-6 py-4 text-center font-medium">{vendor?.orderCount || 0}</td>
                        <td className="px-6 py-4 text-right font-bold text-gray-900">£{(vendor?.revenue || 0).toLocaleString()}</td>
                        <td className="px-6 py-4 text-right font-bold text-purple-600">£{((vendor?.revenue || 0) * 0.1).toLocaleString()}</td>
                        <td className="px-6 py-4 text-right font-bold text-emerald-600">£{((vendor?.revenue || 0) * 0.9).toLocaleString()}</td>
                        <td className="px-6 py-4 text-center">
                          <StatusBadge status={vendor?.status || 'active'} size="small" />
                        </td>
                      </tr>
                    )) : (
                      <tr>
                        <td colSpan="7" className="px-6 py-8 text-center text-gray-500">No vendor data yet</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* ==================== DELIVERIES TAB ==================== */}
        {activeTab === 'deliveries' && deliveries && (
          <div className="space-y-6">
            {/* Delivery Stats */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl p-6 text-white">
                <p className="text-3xl font-bold">{deliveries.statusCounts?.processing || 0}</p>
                <p className="text-blue-100 mt-1">Processing</p>
              </div>
              <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl p-6 text-white">
                <p className="text-3xl font-bold">{deliveries.statusCounts?.shipped || 0}</p>
                <p className="text-purple-100 mt-1">Shipped</p>
              </div>
              <div className="bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-2xl p-6 text-white">
                <p className="text-3xl font-bold">{deliveries.statusCounts?.in_transit || 0}</p>
                <p className="text-indigo-100 mt-1">In Transit</p>
              </div>
              <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-2xl p-6 text-white">
                <p className="text-3xl font-bold">{deliveries.statusCounts?.out_for_delivery || 0}</p>
                <p className="text-orange-100 mt-1">Out for Delivery</p>
              </div>
              <div className="bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-2xl p-6 text-white">
                <p className="text-3xl font-bold">{deliveries.statusCounts?.delivered || 0}</p>
                <p className="text-emerald-100 mt-1">Delivered</p>
              </div>
            </div>

            {/* Filters */}
            <div className="flex flex-col md:flex-row gap-4 bg-white p-4 rounded-2xl shadow-sm border border-gray-100">
              <div className="flex-1 relative">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Search by order ID or customer..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-12 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                />
              </div>
              <select
                value={deliveryStatusFilter}
                onChange={(e) => setDeliveryStatusFilter(e.target.value)}
                className="px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-emerald-500 min-w-[180px]"
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
                <div key={delivery.id} className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 hover:shadow-xl transition-shadow">
                  <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="font-mono font-bold text-lg text-emerald-600">{delivery.orderId}</span>
                        <StatusBadge status={delivery.deliveryStatus} />
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-gray-600">
                        <p><span className="text-gray-400">Customer:</span> {delivery.customerName}</p>
                        <p><span className="text-gray-400">Email:</span> {delivery.customerEmail}</p>
                        <p><span className="text-gray-400">Items:</span> {delivery.itemCount} items</p>
                        <p><span className="text-gray-400">Total:</span> <span className="font-bold text-gray-900">£{delivery.total?.toFixed(2)}</span></p>
                      </div>
                      {delivery.trackingNumber && (
                        <p className="mt-2 text-sm"><span className="text-gray-400">Tracking:</span> <span className="font-mono text-blue-600">{delivery.trackingNumber}</span> ({delivery.carrier})</p>
                      )}
                      <p className="mt-2 text-sm text-gray-500">
                        <span className="text-gray-400">Address:</span> {delivery.shippingAddress?.fullName}, {delivery.shippingAddress?.address}, {delivery.shippingAddress?.city}, {delivery.shippingAddress?.postcode}
                      </p>
                    </div>
                    
                    <div className="flex flex-col gap-3 lg:w-64">
                      <select
                        value={delivery.deliveryStatus}
                        onChange={(e) => updateDeliveryStatus(delivery.orderId, e.target.value, delivery.trackingNumber, delivery.carrier)}
                        className="px-4 py-3 border border-gray-200 rounded-xl text-sm font-medium focus:ring-2 focus:ring-emerald-500"
                      >
                        <option value="processing">Processing</option>
                        <option value="shipped">Shipped</option>
                        <option value="in_transit">In Transit</option>
                        <option value="out_for_delivery">Out for Delivery</option>
                        <option value="delivered">Delivered</option>
                      </select>
                      
                      <button
                        onClick={() => { setSelectedDelivery(delivery); setShowTrackingModal(true); setTrackingForm({ trackingNumber: delivery.trackingNumber || '', carrier: delivery.carrier || '', estimatedDelivery: '' }); }}
                        className="px-4 py-2 border border-emerald-500 text-emerald-600 rounded-xl text-sm font-medium hover:bg-emerald-50 transition-colors"
                      >
                        {delivery.trackingNumber ? 'Update Tracking' : 'Add Tracking'}
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ==================== CUSTOMERS TAB ==================== */}
        {activeTab === 'ads' && (
          <div className="space-y-6">
            {/* Ad Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <StatCard 
                title="Pending Approval" 
                value={pendingAds?.length || 0} 
                icon={Clock} 
                color="yellow" 
              />
              <StatCard 
                title="Active Ads" 
                value={ads?.filter(a => a.status === 'active').length || 0} 
                icon={CheckCircle} 
                color="emerald" 
              />
              <StatCard 
                title="Total Revenue" 
                value={`£${ads?.filter(a => a.payment_status === 'paid').reduce((sum, a) => sum + a.price, 0).toFixed(2) || '0.00'}`} 
                icon={DollarSign} 
                color="blue" 
              />
              <StatCard 
                title="Total Impressions" 
                value={ads?.reduce((sum, a) => sum + (a.impressions || 0), 0).toLocaleString() || '0'} 
                icon={Eye} 
                color="purple" 
              />
            </div>

            {/* Pending Ads Section */}
            {pendingAds?.length > 0 && (
              <div className="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-2xl p-6 border border-yellow-200">
                <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2 mb-4">
                  <AlertCircle className="w-5 h-5 text-yellow-600" />
                  Pending Approval ({pendingAds.length})
                </h3>
                <div className="grid gap-4">
                  {pendingAds.map(ad => (
                    <div key={ad.id} className="bg-white rounded-xl p-4 shadow-sm flex flex-col md:flex-row gap-4">
                      <img src={ad.image} alt={ad.title} className="w-full md:w-40 h-32 object-cover rounded-lg" />
                      <div className="flex-1">
                        <div className="flex items-start justify-between">
                          <div>
                            <h4 className="font-semibold text-gray-900">{ad.title}</h4>
                            <p className="text-sm text-gray-500">{ad.vendor?.business_name}</p>
                          </div>
                          <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-xs font-medium">
                            {ad.ad_type_name}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mt-2">{ad.description}</p>
                        <div className="flex items-center gap-4 mt-3 text-sm text-gray-500">
                          <span>Duration: {ad.duration_days} days</span>
                          <span>Price: £{ad.price?.toFixed(2)}</span>
                        </div>
                        <div className="flex gap-2 mt-4">
                          <button
                            onClick={() => handleAdApproval(ad.id, 'approve')}
                            className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 flex items-center gap-1"
                          >
                            <Check className="w-4 h-4" /> Approve
                          </button>
                          <button
                            onClick={() => { setSelectedAd(ad); setShowAdModal(true); }}
                            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center gap-1"
                          >
                            <X className="w-4 h-4" /> Reject
                          </button>
                          <a 
                            href={ad.image} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 flex items-center gap-1"
                          >
                            <Eye className="w-4 h-4" /> View Image
                          </a>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* All Ads Table */}
            <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
              <div className="p-6 border-b border-gray-100">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                  <h3 className="text-lg font-bold text-gray-900">All Advertisements</h3>
                  <div className="flex gap-3">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                      <input
                        type="text"
                        placeholder="Search ads..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-10 pr-4 py-2 border border-gray-200 rounded-lg"
                      />
                    </div>
                    <select
                      value={adStatusFilter}
                      onChange={(e) => setAdStatusFilter(e.target.value)}
                      className="px-4 py-2 border border-gray-200 rounded-lg"
                    >
                      <option value="all">All Status</option>
                      <option value="pending">Pending</option>
                      <option value="active">Active</option>
                      <option value="paused">Paused</option>
                      <option value="rejected">Rejected</option>
                      <option value="expired">Expired</option>
                    </select>
                  </div>
                </div>
              </div>
              
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase">Ad</th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase">Vendor</th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase">Type</th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase">Status</th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase">Price</th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase">Performance</th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase">Dates</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {paginate(filteredAds).map(ad => (
                      <tr key={ad.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-3">
                            <img src={ad.image} alt={ad.title} className="w-16 h-12 object-cover rounded-lg" />
                            <div>
                              <p className="font-medium text-gray-900">{ad.title}</p>
                              <p className="text-xs text-gray-500 truncate max-w-[200px]">{ad.description}</p>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">{ad.vendor?.business_name}</td>
                        <td className="px-6 py-4">
                          <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
                            {ad.ad_type_name || ad.ad_type}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            ad.status === 'active' ? 'bg-green-100 text-green-800' :
                            ad.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                            ad.status === 'rejected' ? 'bg-red-100 text-red-800' :
                            ad.status === 'paused' ? 'bg-gray-100 text-gray-800' :
                            'bg-orange-100 text-orange-800'
                          }`}>
                            {ad.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm font-medium text-gray-900">£{ad.price?.toFixed(2)}</td>
                        <td className="px-6 py-4">
                          <div className="text-sm">
                            <div className="flex items-center gap-1 text-gray-600">
                              <Eye className="w-3 h-3" /> {ad.impressions?.toLocaleString() || 0}
                            </div>
                            <div className="flex items-center gap-1 text-gray-600">
                              <MousePointer className="w-3 h-3" /> {ad.clicks || 0} clicks
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-xs text-gray-500">
                          {ad.start_date && (
                            <div>Start: {new Date(ad.start_date).toLocaleDateString()}</div>
                          )}
                          {ad.end_date && (
                            <div>End: {new Date(ad.end_date).toLocaleDateString()}</div>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              
              {filteredAds.length === 0 && (
                <div className="text-center py-12">
                  <Megaphone className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                  <p className="text-gray-500">No advertisements found</p>
                </div>
              )}
              
              {/* Pagination */}
              {filteredAds.length > ITEMS_PER_PAGE && (
                <div className="px-6 py-4 border-t border-gray-100 flex items-center justify-between">
                  <p className="text-sm text-gray-500">
                    Showing {((currentPage - 1) * ITEMS_PER_PAGE) + 1} to {Math.min(currentPage * ITEMS_PER_PAGE, filteredAds.length)} of {filteredAds.length}
                  </p>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                      disabled={currentPage === 1}
                      className="px-3 py-1 border rounded-lg disabled:opacity-50"
                    >
                      <ChevronLeft className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => setCurrentPage(p => Math.min(totalPages(filteredAds), p + 1))}
                      disabled={currentPage === totalPages(filteredAds)}
                      className="px-3 py-1 border rounded-lg disabled:opacity-50"
                    >
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Vendor Approval Modal */}
        {showVendorModal && selectedVendor && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6 border-b border-gray-100">
                <div className="flex items-center justify-between">
                  <h3 className="text-xl font-bold text-gray-900">Vendor Application Review</h3>
                  <button onClick={() => { setShowVendorModal(false); setSelectedVendor(null); }}
                    className="p-2 hover:bg-gray-100 rounded-lg">
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>
              
              <div className="p-6 space-y-6">
                {/* Vendor Details */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-500 mb-1">Business Name</label>
                    <p className="text-lg font-semibold text-gray-900">{selectedVendor.businessName || selectedVendor.business_name}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-500 mb-1">Status</label>
                    <StatusBadge status={selectedVendor.status} />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-500 mb-1">Email</label>
                    <p className="text-gray-900 flex items-center gap-2">
                      <Mail className="w-4 h-4 text-gray-400" />
                      {selectedVendor.email}
                    </p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-500 mb-1">Phone</label>
                    <p className="text-gray-900 flex items-center gap-2">
                      <Phone className="w-4 h-4 text-gray-400" />
                      {selectedVendor.phone}
                    </p>
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-500 mb-1">Address</label>
                    <p className="text-gray-900 flex items-center gap-2">
                      <MapPin className="w-4 h-4 text-gray-400" />
                      {selectedVendor.address}, {selectedVendor.city}, {selectedVendor.postcode}
                    </p>
                  </div>
                  {selectedVendor.description && (
                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-gray-500 mb-1">Description</label>
                      <p className="text-gray-700">{selectedVendor.description}</p>
                    </div>
                  )}
                </div>

                {/* Stats */}
                <div className="grid grid-cols-3 gap-4 p-4 bg-gray-50 rounded-xl">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-emerald-600">£{selectedVendor.revenue?.toLocaleString() || 0}</p>
                    <p className="text-xs text-gray-500">Revenue</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-blue-600">{selectedVendor.productCount || 0}</p>
                    <p className="text-xs text-gray-500">Products</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-purple-600">{selectedVendor.orderCount || 0}</p>
                    <p className="text-xs text-gray-500">Orders</p>
                  </div>
                </div>

                {/* Notes */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Admin Notes (optional)</label>
                  <textarea
                    value={vendorApprovalNotes}
                    onChange={(e) => setVendorApprovalNotes(e.target.value)}
                    placeholder="Add any notes about this vendor..."
                    rows={3}
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-emerald-500"
                  />
                </div>

                {/* Action Buttons */}
                {selectedVendor.status === 'pending' && (
                  <div className="flex gap-3">
                    <button 
                      onClick={() => approveVendor(selectedVendor.id, 'approved')}
                      className="flex-1 py-3 bg-emerald-600 text-white rounded-xl hover:bg-emerald-700 font-semibold flex items-center justify-center gap-2 transition-colors"
                    >
                      <Check className="w-5 h-5" />
                      Approve Vendor
                    </button>
                    <button 
                      onClick={() => approveVendor(selectedVendor.id, 'rejected')}
                      className="flex-1 py-3 bg-red-600 text-white rounded-xl hover:bg-red-700 font-semibold flex items-center justify-center gap-2 transition-colors"
                    >
                      <X className="w-5 h-5" />
                      Reject Vendor
                    </button>
                  </div>
                )}
                
                {selectedVendor.status !== 'pending' && (
                  <div className="text-center py-4 bg-gray-50 rounded-xl">
                    <p className="text-gray-600">
                      This vendor has already been {selectedVendor.status === 'approved' ? 'approved ✓' : 'rejected ✗'}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Ad Rejection Modal */}
        {showAdModal && selectedAd && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-2">Reject Advertisement</h3>
              <p className="text-sm text-gray-500 mb-4">Ad: {selectedAd.title}</p>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Reason for rejection (optional)</label>
                  <textarea
                    value={adApprovalNotes}
                    onChange={(e) => setAdApprovalNotes(e.target.value)}
                    placeholder="Enter reason for rejection..."
                    rows={3}
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-red-500"
                  />
                </div>
                
                <div className="flex gap-3">
                  <button
                    onClick={() => { setShowAdModal(false); setSelectedAd(null); setAdApprovalNotes(''); }}
                    className="flex-1 px-4 py-3 border border-gray-200 rounded-xl hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={() => handleAdApproval(selectedAd.id, 'reject')}
                    className="flex-1 px-4 py-3 bg-red-600 text-white rounded-xl hover:bg-red-700"
                  >
                    Reject Ad
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'customers' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <StatCard title="Total Customers" value={dashboardData?.totalUsers || dashboardData?.overview?.totalUsers || 0} icon={Users} color="blue" />
              <StatCard title="Active Vendors" value={dashboardData?.totalVendors || dashboardData?.overview?.approvedVendors || 0} icon={Store} color="emerald" />
              <StatCard title="Total Orders" value={dashboardData?.totalOrders || dashboardData?.overview?.totalOrders || 0} icon={ShoppingCart} color="purple" />
            </div>

            <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-12 text-center">
              <Users className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-xl font-bold text-gray-900">Customer Management</h3>
              <p className="text-gray-500 mt-2 max-w-md mx-auto">
                View detailed customer information, order history, and engagement metrics. 
                Customer data is securely managed and GDPR compliant.
              </p>
              <div className="flex items-center justify-center gap-4 mt-6">
                <div className="text-center px-6 py-4 bg-gray-50 rounded-xl">
                  <p className="text-3xl font-bold text-gray-900">{dashboardData?.totalUsers || dashboardData?.overview?.totalUsers || 0}</p>
                  <p className="text-sm text-gray-500">Registered Users</p>
                </div>
                <div className="text-center px-6 py-4 bg-gray-50 rounded-xl">
                  <p className="text-3xl font-bold text-emerald-600">{dashboardData?.totalOrders || dashboardData?.overview?.totalOrders || 0}</p>
                  <p className="text-sm text-gray-500">Total Orders</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tracking Modal */}
        {showTrackingModal && selectedDelivery && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-4">Update Tracking Information</h3>
              <p className="text-sm text-gray-500 mb-6">Order: {selectedDelivery.orderId}</p>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Tracking Number</label>
                  <input
                    type="text"
                    value={trackingForm.trackingNumber}
                    onChange={(e) => setTrackingForm(f => ({ ...f, trackingNumber: e.target.value }))}
                    placeholder="e.g., 1Z999AA10123456784"
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-emerald-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Carrier</label>
                  <select
                    value={trackingForm.carrier}
                    onChange={(e) => setTrackingForm(f => ({ ...f, carrier: e.target.value }))}
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-emerald-500"
                  >
                    <option value="">Select carrier</option>
                    <option value="Royal Mail">Royal Mail</option>
                    <option value="DPD">DPD</option>
                    <option value="Hermes">Hermes/Evri</option>
                    <option value="DHL">DHL</option>
                    <option value="UPS">UPS</option>
                    <option value="FedEx">FedEx</option>
                    <option value="Amazon Logistics">Amazon Logistics</option>
                    <option value="Yodel">Yodel</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Estimated Delivery Date</label>
                  <input
                    type="date"
                    value={trackingForm.estimatedDelivery}
                    onChange={(e) => setTrackingForm(f => ({ ...f, estimatedDelivery: e.target.value }))}
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-emerald-500"
                  />
                </div>
              </div>
              
              <div className="flex gap-3 mt-6">
                <button
                  onClick={() => { setShowTrackingModal(false); setSelectedDelivery(null); }}
                  className="flex-1 px-4 py-3 border border-gray-200 text-gray-700 rounded-xl font-medium hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={() => updateDeliveryStatus(selectedDelivery.orderId, selectedDelivery.deliveryStatus, trackingForm.trackingNumber, trackingForm.carrier, trackingForm.estimatedDelivery)}
                  className="flex-1 px-4 py-3 bg-gradient-to-r from-emerald-500 to-emerald-600 text-white rounded-xl font-medium hover:from-emerald-600 hover:to-emerald-700"
                >
                  Save Tracking
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      <Footer />
    </div>
  );
};

export default OwnerDashboard;
