import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { 
  Bell, CheckCheck, AlertCircle, CheckCircle, Info, 
  Package, MessageSquare, ArrowLeft, RefreshCw, Trash2,
  ExternalLink
} from 'lucide-react';
import axios from 'axios';
import { formatDistanceToNow, format } from 'date-fns';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const VendorNotificationsPage = () => {
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // all, unread, approval, rejection, order

  const getToken = () => localStorage.getItem('afroToken');

  const fetchNotifications = useCallback(async () => {
    try {
      const token = getToken();
      if (!token) {
        navigate('/login');
        return;
      }

      const response = await axios.get(`${API_URL}/api/vendor/notifications`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.success) {
        setNotifications(response.data.notifications || []);
        setUnreadCount(response.data.unreadCount || 0);
      }
    } catch (error) {
      console.error('Error fetching notifications:', error);
      if (error.response?.status === 401 || error.response?.status === 403) {
        navigate('/login');
      }
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  useEffect(() => {
    if (authLoading) return;
    
    const token = getToken();
    if (!token && !isAuthenticated) {
      navigate('/login');
      return;
    }
    
    fetchNotifications();
  }, [authLoading, isAuthenticated, navigate, fetchNotifications]);

  const markAsRead = async (notificationId) => {
    try {
      const token = getToken();
      await axios.put(
        `${API_URL}/api/vendor/notifications/${notificationId}/read`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      setNotifications(prev =>
        prev.map(n => n.id === notificationId ? { ...n, isRead: true } : n)
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
      toast.success('Marked as read');
    } catch (error) {
      toast.error('Failed to mark as read');
    }
  };

  const markAllAsRead = async () => {
    try {
      const token = getToken();
      await axios.put(
        `${API_URL}/api/vendor/notifications/mark-all-read`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      setNotifications(prev => prev.map(n => ({ ...n, isRead: true })));
      setUnreadCount(0);
      toast.success('All notifications marked as read');
    } catch (error) {
      toast.error('Failed to mark all as read');
    }
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'approval':
        return <CheckCircle className="h-6 w-6 text-emerald-500" />;
      case 'rejection':
        return <AlertCircle className="h-6 w-6 text-red-500" />;
      case 'order':
        return <Package className="h-6 w-6 text-blue-500" />;
      case 'message':
        return <MessageSquare className="h-6 w-6 text-purple-500" />;
      default:
        return <Info className="h-6 w-6 text-gray-500" />;
    }
  };

  const getTypeLabel = (type) => {
    switch (type) {
      case 'approval':
        return { label: 'Approved', color: 'bg-emerald-100 text-emerald-700' };
      case 'rejection':
        return { label: 'Update', color: 'bg-red-100 text-red-700' };
      case 'order':
        return { label: 'Order', color: 'bg-blue-100 text-blue-700' };
      case 'message':
        return { label: 'Message', color: 'bg-purple-100 text-purple-700' };
      default:
        return { label: 'System', color: 'bg-gray-100 text-gray-700' };
    }
  };

  const filteredNotifications = notifications.filter(n => {
    if (filter === 'all') return true;
    if (filter === 'unread') return !n.isRead;
    return n.type === filter;
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="max-w-4xl mx-auto px-4 py-8">
          <div className="flex justify-center items-center py-20">
            <div className="animate-spin h-10 w-10 border-3 border-emerald-500 border-t-transparent rounded-full" />
          </div>
        </div>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => navigate('/vendor/dashboard')}
              className="h-10 w-10"
            >
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                <Bell className="h-6 w-6 text-emerald-600" />
                Notifications
              </h1>
              <p className="text-gray-500">
                {unreadCount > 0 ? `${unreadCount} unread notifications` : 'All caught up!'}
              </p>
            </div>
          </div>
          
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={fetchNotifications}
              className="flex items-center gap-2"
            >
              <RefreshCw className="h-4 w-4" />
              Refresh
            </Button>
            {unreadCount > 0 && (
              <Button
                variant="default"
                size="sm"
                onClick={markAllAsRead}
                className="bg-emerald-600 hover:bg-emerald-700 flex items-center gap-2"
              >
                <CheckCheck className="h-4 w-4" />
                Mark all read
              </Button>
            )}
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
          {[
            { key: 'all', label: 'All' },
            { key: 'unread', label: 'Unread' },
            { key: 'approval', label: 'Approvals' },
            { key: 'rejection', label: 'Updates' },
            { key: 'order', label: 'Orders' },
          ].map(({ key, label }) => (
            <Button
              key={key}
              variant={filter === key ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilter(key)}
              className={filter === key ? 'bg-emerald-600 hover:bg-emerald-700' : ''}
            >
              {label}
              {key === 'unread' && unreadCount > 0 && (
                <Badge className="ml-2 bg-red-500 text-white">{unreadCount}</Badge>
              )}
            </Button>
          ))}
        </div>

        {/* Notifications List */}
        {filteredNotifications.length === 0 ? (
          <Card>
            <CardContent className="py-16 text-center">
              <Bell className="h-16 w-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                {filter === 'unread' ? 'No unread notifications' : 'No notifications'}
              </h3>
              <p className="text-gray-500">
                {filter === 'unread' 
                  ? "You're all caught up!" 
                  : "You'll receive notifications about your vendor account here"
                }
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-3">
            {filteredNotifications.map((notification) => {
              const typeInfo = getTypeLabel(notification.type);
              return (
                <Card 
                  key={notification.id}
                  className={`transition-all hover:shadow-md cursor-pointer ${
                    !notification.isRead ? 'border-l-4 border-l-emerald-500 bg-emerald-50/30' : ''
                  }`}
                  onClick={() => {
                    if (!notification.isRead) {
                      markAsRead(notification.id);
                    }
                    if (notification.link) {
                      navigate(notification.link);
                    }
                  }}
                  data-testid={`notification-card-${notification.id}`}
                >
                  <CardContent className="p-4">
                    <div className="flex gap-4">
                      <div className="flex-shrink-0">
                        {getNotificationIcon(notification.type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-2 mb-1">
                          <div className="flex items-center gap-2">
                            <h3 className={`font-semibold ${notification.isRead ? 'text-gray-700' : 'text-gray-900'}`}>
                              {notification.title}
                            </h3>
                            <Badge className={typeInfo.color} variant="secondary">
                              {typeInfo.label}
                            </Badge>
                          </div>
                          {!notification.isRead && (
                            <span className="flex-shrink-0 w-3 h-3 bg-emerald-500 rounded-full" />
                          )}
                        </div>
                        <p className={`text-sm mb-2 ${notification.isRead ? 'text-gray-500' : 'text-gray-600'}`}>
                          {notification.message}
                        </p>
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-gray-400">
                            {format(new Date(notification.createdAt), 'MMM d, yyyy h:mm a')} · {formatDistanceToNow(new Date(notification.createdAt), { addSuffix: true })}
                          </span>
                          {notification.link && (
                            <span className="text-xs text-emerald-600 flex items-center gap-1 hover:underline">
                              <ExternalLink className="h-3 w-3" />
                              View details
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </main>
      
      <Footer />
    </div>
  );
};

export default VendorNotificationsPage;
