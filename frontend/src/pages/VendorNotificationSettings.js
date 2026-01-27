import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Switch } from '../components/ui/switch';
import { Label } from '../components/ui/label';
import { Separator } from '../components/ui/separator';
import { Badge } from '../components/ui/badge';
import { 
  ArrowLeft, Bell, Mail, Smartphone, MessageSquare, 
  Package, Star, AlertCircle, Megaphone, Save, RefreshCw,
  CheckCircle, XCircle, Wifi, WifiOff
} from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';
import { usePushNotifications } from '../hooks/usePushNotifications';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const VendorNotificationSettings = () => {
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  
  const {
    isSupported: pushSupported,
    isSubscribed: pushSubscribed,
    permission: pushPermission,
    loading: pushLoading,
    error: pushError,
    subscribe: subscribePush,
    unsubscribe: unsubscribePush,
    testPush
  } = usePushNotifications();

  const [preferences, setPreferences] = useState({
    email: {
      orders: true,
      messages: true,
      reviews: true,
      adminAlerts: true,
      marketing: false
    },
    inapp: {
      orders: true,
      messages: true,
      reviews: true,
      adminAlerts: true,
      marketing: true
    },
    push: {
      enabled: true,
      orders: true,
      messages: true,
      reviews: false,
      adminAlerts: true
    }
  });

  const getToken = () => localStorage.getItem('afroToken');

  const fetchPreferences = useCallback(async () => {
    try {
      const token = getToken();
      if (!token) {
        navigate('/login');
        return;
      }

      const response = await axios.get(`${API_URL}/api/vendor/notifications/preferences`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.success) {
        setPreferences(response.data.preferences);
      }
    } catch (error) {
      console.error('Error fetching preferences:', error);
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
    
    fetchPreferences();
  }, [authLoading, isAuthenticated, navigate, fetchPreferences]);

  const savePreferences = async () => {
    setSaving(true);
    try {
      const token = getToken();
      
      // Convert nested structure to flat structure for API
      const flatPrefs = {
        email_orders: preferences.email.orders,
        email_messages: preferences.email.messages,
        email_reviews: preferences.email.reviews,
        email_admin_alerts: preferences.email.adminAlerts,
        email_marketing: preferences.email.marketing,
        inapp_orders: preferences.inapp.orders,
        inapp_messages: preferences.inapp.messages,
        inapp_reviews: preferences.inapp.reviews,
        inapp_admin_alerts: preferences.inapp.adminAlerts,
        inapp_marketing: preferences.inapp.marketing,
        push_enabled: preferences.push.enabled,
        push_orders: preferences.push.orders,
        push_messages: preferences.push.messages,
        push_reviews: preferences.push.reviews,
        push_admin_alerts: preferences.push.adminAlerts
      };

      await axios.put(
        `${API_URL}/api/vendor/notifications/preferences`,
        flatPrefs,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      toast.success('Notification preferences saved!');
    } catch (error) {
      toast.error('Failed to save preferences');
      console.error('Save error:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleToggle = (category, type) => {
    setPreferences(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [type]: !prev[category][type]
      }
    }));
  };

  const handlePushToggle = async () => {
    if (pushSubscribed) {
      const success = await unsubscribePush();
      if (success) {
        toast.success('Push notifications disabled');
      }
    } else {
      const success = await subscribePush();
      if (success) {
        toast.success('Push notifications enabled!');
      } else if (pushPermission === 'denied') {
        toast.error('Please enable notifications in your browser settings');
      }
    }
  };

  const handleTestPush = async () => {
    try {
      const result = await testPush();
      if (result.success) {
        toast.success(result.message);
      } else {
        toast.error(result.message);
      }
    } catch (error) {
      toast.error('Failed to send test notification');
    }
  };

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

  const notificationTypes = [
    { key: 'orders', label: 'New Orders', icon: Package, description: 'Get notified when you receive new orders' },
    { key: 'messages', label: 'Messages', icon: MessageSquare, description: 'Notifications for customer messages' },
    { key: 'reviews', label: 'Reviews', icon: Star, description: 'When customers leave reviews on your products' },
    { key: 'adminAlerts', label: 'Admin Alerts', icon: AlertCircle, description: 'Important updates from AfroMarket' },
    { key: 'marketing', label: 'Marketing & Tips', icon: Megaphone, description: 'Promotional tips and marketplace news' }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center gap-4 mb-6">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate('/vendor/notifications')}
            className="h-10 w-10"
          >
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <Bell className="h-6 w-6 text-emerald-600" />
              Notification Settings
            </h1>
            <p className="text-gray-500">Choose how you want to receive notifications</p>
          </div>
        </div>

        {/* Push Notification Status Card */}
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Smartphone className="h-6 w-6 text-purple-600" />
                <div>
                  <CardTitle>Browser Push Notifications</CardTitle>
                  <CardDescription>Receive instant notifications even when the browser is closed</CardDescription>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {pushSubscribed ? (
                  <Badge className="bg-emerald-100 text-emerald-700">
                    <CheckCircle className="h-3 w-3 mr-1" />
                    Enabled
                  </Badge>
                ) : (
                  <Badge variant="secondary">
                    <XCircle className="h-3 w-3 mr-1" />
                    Disabled
                  </Badge>
                )}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {!pushSupported ? (
              <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-yellow-800 text-sm">
                  Push notifications are not supported in your browser. Try using Chrome, Firefox, or Edge.
                </p>
              </div>
            ) : pushPermission === 'denied' ? (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-800 text-sm">
                  You've blocked notifications. Please enable them in your browser settings to receive push notifications.
                </p>
              </div>
            ) : (
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Switch
                    checked={pushSubscribed}
                    onCheckedChange={handlePushToggle}
                    disabled={pushLoading}
                  />
                  <span className="text-sm text-gray-600">
                    {pushSubscribed ? 'Push notifications are on' : 'Enable push notifications'}
                  </span>
                </div>
                {pushSubscribed && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleTestPush}
                    disabled={pushLoading}
                  >
                    Test Notification
                  </Button>
                )}
              </div>
            )}
            {pushError && (
              <p className="text-red-500 text-sm mt-2">{pushError}</p>
            )}
          </CardContent>
        </Card>

        {/* Email Notifications */}
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-center gap-3">
              <Mail className="h-6 w-6 text-blue-600" />
              <div>
                <CardTitle>Email Notifications</CardTitle>
                <CardDescription>Receive updates via email</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {notificationTypes.map(({ key, label, icon: Icon, description }) => (
              <div key={key} className="flex items-center justify-between py-2">
                <div className="flex items-center gap-3">
                  <Icon className="h-5 w-5 text-gray-400" />
                  <div>
                    <Label className="text-sm font-medium">{label}</Label>
                    <p className="text-xs text-gray-500">{description}</p>
                  </div>
                </div>
                <Switch
                  checked={preferences.email[key]}
                  onCheckedChange={() => handleToggle('email', key)}
                />
              </div>
            ))}
          </CardContent>
        </Card>

        {/* In-App Notifications */}
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-center gap-3">
              <Bell className="h-6 w-6 text-emerald-600" />
              <div>
                <CardTitle>In-App Notifications</CardTitle>
                <CardDescription>Notifications shown in the dashboard</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {notificationTypes.map(({ key, label, icon: Icon, description }) => (
              <div key={key} className="flex items-center justify-between py-2">
                <div className="flex items-center gap-3">
                  <Icon className="h-5 w-5 text-gray-400" />
                  <div>
                    <Label className="text-sm font-medium">{label}</Label>
                    <p className="text-xs text-gray-500">{description}</p>
                  </div>
                </div>
                <Switch
                  checked={preferences.inapp[key]}
                  onCheckedChange={() => handleToggle('inapp', key)}
                />
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Push Notification Types */}
        {pushSubscribed && (
          <Card className="mb-6">
            <CardHeader>
              <div className="flex items-center gap-3">
                <Smartphone className="h-6 w-6 text-purple-600" />
                <div>
                  <CardTitle>Push Notification Types</CardTitle>
                  <CardDescription>Choose which notifications to receive on your device</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {notificationTypes.filter(t => t.key !== 'marketing').map(({ key, label, icon: Icon, description }) => (
                <div key={key} className="flex items-center justify-between py-2">
                  <div className="flex items-center gap-3">
                    <Icon className="h-5 w-5 text-gray-400" />
                    <div>
                      <Label className="text-sm font-medium">{label}</Label>
                      <p className="text-xs text-gray-500">{description}</p>
                    </div>
                  </div>
                  <Switch
                    checked={preferences.push[key]}
                    onCheckedChange={() => handleToggle('push', key)}
                  />
                </div>
              ))}
            </CardContent>
          </Card>
        )}

        {/* Save Button */}
        <div className="flex justify-end gap-3">
          <Button
            variant="outline"
            onClick={fetchPreferences}
            disabled={saving}
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Reset
          </Button>
          <Button
            onClick={savePreferences}
            disabled={saving}
            className="bg-emerald-600 hover:bg-emerald-700"
          >
            {saving ? (
              <>
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="h-4 w-4 mr-2" />
                Save Preferences
              </>
            )}
          </Button>
        </div>
      </main>
      
      <Footer />
    </div>
  );
};

export default VendorNotificationSettings;
