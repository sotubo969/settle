import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
  Package, 
  AlertTriangle, 
  TrendingUp, 
  ShoppingBag,
  Edit,
  RefreshCw,
  Check,
  X
} from 'lucide-react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { toast } from 'sonner';
import { useAuth } from '../context/AuthContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const VendorDashboard = () => {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState(null);
  const [editingStock, setEditingStock] = useState(null);
  const [newStockValue, setNewStockValue] = useState('');
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    fetchDashboardData();
  }, [isAuthenticated, navigate]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('afroToken');
      const response = await axios.get(`${API}/vendor/dashboard`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDashboardData(response.data);
    } catch (error) {
      console.error('Error fetching vendor dashboard:', error);
      if (error.response?.status === 403) {
        toast.error('Vendor account not found or not approved');
        navigate('/');
      } else {
        toast.error('Failed to load vendor dashboard');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateStock = async (productId) => {
    if (!newStockValue || parseInt(newStockValue) < 0) {
      toast.error('Please enter a valid stock quantity');
      return;
    }

    setUpdating(true);
    try {
      const token = localStorage.getItem('afroToken');
      await axios.put(
        `${API}/vendor/products/${productId}/stock`,
        { stock_quantity: parseInt(newStockValue) },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success('Stock updated successfully');
      setEditingStock(null);
      setNewStockValue('');
      fetchDashboardData(); // Refresh data
    } catch (error) {
      console.error('Error updating stock:', error);
      toast.error(error.response?.data?.detail || 'Failed to update stock');
    } finally {
      setUpdating(false);
    }
  };

  const startEditing = (product) => {
    setEditingStock(product.id);
    setNewStockValue(product.stock_quantity?.toString() || '0');
  };

  const cancelEditing = () => {
    setEditingStock(null);
    setNewStockValue('');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="max-w-7xl mx-auto px-4 py-16 text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto text-emerald-600" />
          <p className="text-xl mt-4">Loading vendor dashboard...</p>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="max-w-7xl mx-auto px-4 py-16 text-center">
          <p className="text-xl text-gray-600">Unable to load vendor dashboard</p>
          <Button onClick={() => navigate('/')} className="mt-4">
            Go Home
          </Button>
        </div>
      </div>
    );
  }

  const { vendor, stats, products, alerts } = dashboardData;

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Vendor Dashboard</h1>
          <p className="text-gray-600 mt-1">Welcome, {vendor.business_name}</p>
          <Badge className={vendor.verified ? 'bg-emerald-100 text-emerald-700 mt-2' : 'bg-amber-100 text-amber-700 mt-2'}>
            {vendor.verified ? 'Verified Vendor' : 'Pending Verification'}
          </Badge>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Total Products</p>
                  <p className="text-2xl font-bold">{stats.total_products}</p>
                </div>
                <Package className="h-8 w-8 text-emerald-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Total Orders</p>
                  <p className="text-2xl font-bold">{stats.total_orders}</p>
                </div>
                <ShoppingBag className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Revenue</p>
                  <p className="text-2xl font-bold">£{stats.total_revenue.toFixed(2)}</p>
                </div>
                <TrendingUp className="h-8 w-8 text-purple-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card className={stats.low_stock_count > 0 ? 'border-amber-300' : ''}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Low Stock</p>
                  <p className="text-2xl font-bold">{stats.low_stock_count}</p>
                </div>
                <AlertTriangle className={`h-8 w-8 ${stats.low_stock_count > 0 ? 'text-amber-500' : 'text-gray-400'}`} />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Alerts Section */}
        {(alerts.low_stock.length > 0 || alerts.out_of_stock.length > 0) && (
          <Card className="mb-8 border-amber-300 bg-amber-50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-amber-700">
                <AlertTriangle className="h-5 w-5" />
                Stock Alerts
              </CardTitle>
            </CardHeader>
            <CardContent>
              {alerts.out_of_stock.length > 0 && (
                <div className="mb-4">
                  <h4 className="font-semibold text-red-600 mb-2">Out of Stock ({alerts.out_of_stock.length})</h4>
                  <div className="space-y-2">
                    {alerts.out_of_stock.map((product) => (
                      <div key={product.id} className="flex items-center justify-between bg-white p-3 rounded-lg">
                        <span className="font-medium">{product.name}</span>
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => startEditing(product)}
                        >
                          Restock
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {alerts.low_stock.length > 0 && (
                <div>
                  <h4 className="font-semibold text-amber-600 mb-2">Low Stock ({alerts.low_stock.length})</h4>
                  <div className="space-y-2">
                    {alerts.low_stock.map((product) => (
                      <div key={product.id} className="flex items-center justify-between bg-white p-3 rounded-lg">
                        <div>
                          <span className="font-medium">{product.name}</span>
                          <Badge variant="outline" className="ml-2 text-amber-600">
                            {product.stock_quantity} left
                          </Badge>
                        </div>
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => startEditing(product)}
                        >
                          Update
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Products Table */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Your Products</CardTitle>
            <Button onClick={fetchDashboardData} variant="outline" size="sm">
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4">Product</th>
                    <th className="text-left py-3 px-4">Price</th>
                    <th className="text-left py-3 px-4">Stock</th>
                    <th className="text-left py-3 px-4">Status</th>
                    <th className="text-left py-3 px-4">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {products.map((product) => (
                    <tr key={product.id} className="border-b hover:bg-gray-50">
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-3">
                          <img 
                            src={product.image} 
                            alt={product.name}
                            className="w-12 h-12 rounded object-cover"
                          />
                          <div>
                            <p className="font-medium">{product.name}</p>
                            <p className="text-sm text-gray-500">{product.category}</p>
                          </div>
                        </div>
                      </td>
                      <td className="py-3 px-4 font-semibold">£{product.price?.toFixed(2)}</td>
                      <td className="py-3 px-4">
                        {editingStock === product.id ? (
                          <div className="flex items-center gap-2">
                            <Input
                              type="number"
                              value={newStockValue}
                              onChange={(e) => setNewStockValue(e.target.value)}
                              className="w-20 h-8"
                              min="0"
                            />
                            <Button 
                              size="sm" 
                              variant="ghost"
                              onClick={() => handleUpdateStock(product.id)}
                              disabled={updating}
                            >
                              <Check className="h-4 w-4 text-emerald-600" />
                            </Button>
                            <Button 
                              size="sm" 
                              variant="ghost"
                              onClick={cancelEditing}
                            >
                              <X className="h-4 w-4 text-red-600" />
                            </Button>
                          </div>
                        ) : (
                          <span className={
                            product.stock_quantity <= 0 ? 'text-red-600 font-semibold' :
                            product.stock_quantity < 20 ? 'text-amber-600 font-semibold' :
                            'text-gray-900'
                          }>
                            {product.stock_quantity || 0}
                          </span>
                        )}
                      </td>
                      <td className="py-3 px-4">
                        {product.stock_quantity <= 0 ? (
                          <Badge variant="destructive">Out of Stock</Badge>
                        ) : product.stock_quantity < 20 ? (
                          <Badge className="bg-amber-100 text-amber-700">Low Stock</Badge>
                        ) : (
                          <Badge className="bg-emerald-100 text-emerald-700">In Stock</Badge>
                        )}
                      </td>
                      <td className="py-3 px-4">
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => startEditing(product)}
                        >
                          <Edit className="h-4 w-4 mr-1" />
                          Edit Stock
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              
              {products.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <Package className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                  <p>No products yet</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      <Footer />
    </div>
  );
};

export default VendorDashboard;
