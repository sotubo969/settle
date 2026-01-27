import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Package, Clock, Truck, CheckCircle, XCircle, ChevronRight, Search, Filter, Loader2, RefreshCw, MessageSquare, Star } from 'lucide-react';
import axios from 'axios';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../components/ui/dialog';
import { useAuth } from '../context/AuthContext';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const getStatusIcon = (status) => {
  switch (status) {
    case 'processing': return <Clock className="w-5 h-5 text-yellow-500" />;
    case 'shipped': return <Truck className="w-5 h-5 text-blue-500" />;
    case 'in_transit': return <Truck className="w-5 h-5 text-blue-600" />;
    case 'out_for_delivery': return <Truck className="w-5 h-5 text-green-500" />;
    case 'delivered': return <CheckCircle className="w-5 h-5 text-green-600" />;
    case 'cancelled': return <XCircle className="w-5 h-5 text-red-500" />;
    default: return <Package className="w-5 h-5 text-gray-500" />;
  }
};

const getStatusBadge = (status) => {
  const styles = {
    pending: 'bg-yellow-100 text-yellow-800',
    processing: 'bg-blue-100 text-blue-800',
    shipped: 'bg-indigo-100 text-indigo-800',
    in_transit: 'bg-purple-100 text-purple-800',
    out_for_delivery: 'bg-green-100 text-green-800',
    delivered: 'bg-green-200 text-green-900',
    cancelled: 'bg-red-100 text-red-800',
    refunded: 'bg-gray-100 text-gray-800'
  };
  return styles[status] || 'bg-gray-100 text-gray-800';
};

const OrderHistory = () => {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [statusFilter, setStatusFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [trackingData, setTrackingData] = useState(null);
  const [showTrackingModal, setShowTrackingModal] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    fetchOrders();
  }, [isAuthenticated, page, statusFilter]);

  const fetchOrders = async () => {
    try {
      const token = localStorage.getItem('afroToken');
      const params = new URLSearchParams({ page, limit: 10 });
      if (statusFilter !== 'all') params.append('status', statusFilter);
      
      const response = await axios.get(`${API}/orders/history?${params}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setOrders(response.data.orders);
      setTotalPages(response.data.pages);
    } catch (error) {
      console.error('Error fetching orders:', error);
      toast.error('Failed to load orders');
    } finally {
      setLoading(false);
    }
  };

  const fetchTracking = async (orderId) => {
    try {
      const response = await axios.get(`${API}/orders/tracking/${orderId}`);
      setTrackingData(response.data);
      setShowTrackingModal(true);
    } catch (error) {
      toast.error('Failed to load tracking info');
    }
  };

  const filteredOrders = orders.filter(order => 
    order.order_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    order.items?.some(item => item.name?.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-emerald-600" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900" data-testid="order-history-title">
              Order History
            </h1>
            <p className="text-gray-600 mt-1">Track and manage your orders</p>
          </div>
          
          <div className="flex gap-3 w-full md:w-auto">
            <div className="relative flex-1 md:w-64">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <Input 
                placeholder="Search orders..."
                className="pl-10"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                data-testid="order-search"
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-40" data-testid="status-filter">
                <Filter className="w-4 h-4 mr-2" />
                <SelectValue placeholder="Filter" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Orders</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="processing">Processing</SelectItem>
                <SelectItem value="shipped">Shipped</SelectItem>
                <SelectItem value="delivered">Delivered</SelectItem>
                <SelectItem value="cancelled">Cancelled</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {filteredOrders.length === 0 ? (
          <Card className="text-center py-12">
            <CardContent>
              <Package className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No orders found</h3>
              <p className="text-gray-500 mb-4">
                {searchTerm ? 'Try a different search term' : "You haven't placed any orders yet"}
              </p>
              <Link to="/products">
                <Button className="bg-emerald-600 hover:bg-emerald-700">
                  Start Shopping
                </Button>
              </Link>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {filteredOrders.map((order) => (
              <Card key={order.id} className="hover:shadow-md transition-shadow" data-testid={`order-${order.order_id}`}>
                <CardContent className="p-6">
                  <div className="flex flex-col md:flex-row justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-3">
                        {getStatusIcon(order.delivery_status)}
                        <div>
                          <p className="font-semibold text-gray-900">Order #{order.order_id}</p>
                          <p className="text-sm text-gray-500">
                            {new Date(order.created_at).toLocaleDateString('en-GB', {
                              day: 'numeric', month: 'short', year: 'numeric'
                            })}
                          </p>
                        </div>
                        <Badge className={getStatusBadge(order.delivery_status)}>
                          {order.delivery_status?.replace('_', ' ').toUpperCase()}
                        </Badge>
                      </div>
                      
                      <div className="flex flex-wrap gap-3 mb-4">
                        {order.items?.slice(0, 3).map((item, idx) => (
                          <div key={idx} className="flex items-center gap-2 bg-gray-50 rounded-lg p-2">
                            <img 
                              src={item.image} 
                              alt={item.name}
                              className="w-12 h-12 object-cover rounded"
                            />
                            <div className="text-sm">
                              <p className="font-medium line-clamp-1">{item.name}</p>
                              <p className="text-gray-500">Qty: {item.quantity}</p>
                            </div>
                          </div>
                        ))}
                        {order.items?.length > 3 && (
                          <div className="flex items-center justify-center w-12 h-12 bg-gray-100 rounded-lg text-sm text-gray-600">
                            +{order.items.length - 3}
                          </div>
                        )}
                      </div>
                      
                      {order.estimated_delivery && order.delivery_status !== 'delivered' && (
                        <p className="text-sm text-emerald-600">
                          <Clock className="w-4 h-4 inline mr-1" />
                          Estimated delivery: {new Date(order.estimated_delivery).toLocaleDateString('en-GB', {
                            weekday: 'short', day: 'numeric', month: 'short'
                          })}
                        </p>
                      )}
                    </div>
                    
                    <div className="flex flex-col items-end gap-2">
                      <p className="text-2xl font-bold text-gray-900">£{order.total?.toFixed(2)}</p>
                      
                      <div className="flex gap-2">
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => fetchTracking(order.order_id)}
                          data-testid={`track-${order.order_id}`}
                        >
                          <Truck className="w-4 h-4 mr-1" />
                          Track
                        </Button>
                        
                        {order.delivery_status === 'delivered' && (
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => navigate(`/product/${order.items?.[0]?.id}?review=true`)}
                          >
                            <Star className="w-4 h-4 mr-1" />
                            Review
                          </Button>
                        )}
                        
                        <Button 
                          variant="ghost" 
                          size="sm"
                          onClick={() => setSelectedOrder(order)}
                        >
                          <ChevronRight className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex justify-center gap-2 mt-8">
            <Button 
              variant="outline" 
              disabled={page === 1}
              onClick={() => setPage(p => p - 1)}
            >
              Previous
            </Button>
            <span className="flex items-center px-4 text-sm text-gray-600">
              Page {page} of {totalPages}
            </span>
            <Button 
              variant="outline" 
              disabled={page === totalPages}
              onClick={() => setPage(p => p + 1)}
            >
              Next
            </Button>
          </div>
        )}
      </div>

      {/* Tracking Modal */}
      <Dialog open={showTrackingModal} onOpenChange={setShowTrackingModal}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Order Tracking</DialogTitle>
          </DialogHeader>
          
          {trackingData && (
            <div className="py-4">
              <div className="flex justify-between items-center mb-6">
                <span className="text-sm text-gray-500">Order #{trackingData.order_id}</span>
                {trackingData.tracking_number && (
                  <Badge variant="outline">{trackingData.tracking_number}</Badge>
                )}
              </div>
              
              <div className="space-y-4">
                {trackingData.timeline?.map((step, idx) => (
                  <div key={idx} className="flex gap-4">
                    <div className="flex flex-col items-center">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                        step.completed 
                          ? 'bg-emerald-100 text-emerald-600' 
                          : 'bg-gray-100 text-gray-400'
                      }`}>
                        {step.completed ? <CheckCircle className="w-5 h-5" /> : <Clock className="w-5 h-5" />}
                      </div>
                      {idx < trackingData.timeline.length - 1 && (
                        <div className={`w-0.5 h-12 ${step.completed ? 'bg-emerald-200' : 'bg-gray-200'}`} />
                      )}
                    </div>
                    <div className="flex-1 pb-4">
                      <p className={`font-medium ${step.completed ? 'text-gray-900' : 'text-gray-400'}`}>
                        {step.title}
                      </p>
                      <p className="text-sm text-gray-500">{step.description}</p>
                      {step.date && (
                        <p className="text-xs text-gray-400 mt-1">
                          {new Date(step.date).toLocaleString('en-GB')}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      <Footer />
    </div>
  );
};

export default OrderHistory;
