import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;
const VAPID_PUBLIC_KEY = process.env.REACT_APP_VAPID_PUBLIC_KEY;

// Convert URL-safe base64 to Uint8Array
function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding)
    .replace(/-/g, '+')
    .replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

export function usePushNotifications() {
  const [isSupported, setIsSupported] = useState(false);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [subscription, setSubscription] = useState(null);
  const [permission, setPermission] = useState('default');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const getToken = () => localStorage.getItem('afroToken');

  // Check if push notifications are supported
  useEffect(() => {
    const checkSupport = async () => {
      const supported = 'serviceWorker' in navigator && 'PushManager' in window;
      setIsSupported(supported);
      
      if (supported) {
        setPermission(Notification.permission);
        
        // Register service worker
        try {
          const registration = await navigator.serviceWorker.register('/sw-push.js');
          console.log('Push SW registered:', registration.scope);
          
          // Check existing subscription
          const existingSubscription = await registration.pushManager.getSubscription();
          if (existingSubscription) {
            setSubscription(existingSubscription);
            setIsSubscribed(true);
          }
        } catch (err) {
          console.error('SW registration failed:', err);
          setError(err.message);
        }
      }
      
      setLoading(false);
    };

    checkSupport();
  }, []);

  // Subscribe to push notifications
  const subscribe = useCallback(async () => {
    if (!isSupported || !VAPID_PUBLIC_KEY) {
      setError('Push notifications not supported or not configured');
      return false;
    }

    try {
      setLoading(true);
      setError(null);

      // Request notification permission
      const permissionResult = await Notification.requestPermission();
      setPermission(permissionResult);

      if (permissionResult !== 'granted') {
        setError('Notification permission denied');
        setLoading(false);
        return false;
      }

      // Get service worker registration
      const registration = await navigator.serviceWorker.ready;

      // Subscribe to push manager
      const newSubscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY)
      });

      setSubscription(newSubscription);
      setIsSubscribed(true);

      // Send subscription to backend
      const token = getToken();
      if (token) {
        const subscriptionJSON = newSubscription.toJSON();
        await axios.post(
          `${API_URL}/api/vendor/push/subscribe`,
          {
            endpoint: subscriptionJSON.endpoint,
            p256dh_key: subscriptionJSON.keys.p256dh,
            auth_key: subscriptionJSON.keys.auth,
            device_name: navigator.userAgent.includes('Mobile') ? 'Mobile Device' : 'Desktop Browser'
          },
          { headers: { Authorization: `Bearer ${token}` } }
        );
        console.log('Push subscription saved to server');
      }

      setLoading(false);
      return true;
    } catch (err) {
      console.error('Push subscription error:', err);
      setError(err.message);
      setLoading(false);
      return false;
    }
  }, [isSupported]);

  // Unsubscribe from push notifications
  const unsubscribe = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      if (subscription) {
        await subscription.unsubscribe();

        // Remove from backend
        const token = getToken();
        if (token) {
          await axios.delete(
            `${API_URL}/api/vendor/push/unsubscribe`,
            {
              params: { endpoint: subscription.endpoint },
              headers: { Authorization: `Bearer ${token}` }
            }
          );
        }

        setSubscription(null);
        setIsSubscribed(false);
      }

      setLoading(false);
      return true;
    } catch (err) {
      console.error('Push unsubscribe error:', err);
      setError(err.message);
      setLoading(false);
      return false;
    }
  }, [subscription]);

  // Test push notification
  const testPush = useCallback(async () => {
    try {
      const token = getToken();
      if (!token) {
        throw new Error('Not authenticated');
      }

      const response = await axios.post(
        `${API_URL}/api/vendor/push/test`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );

      return response.data;
    } catch (err) {
      console.error('Push test error:', err);
      throw err;
    }
  }, []);

  return {
    isSupported,
    isSubscribed,
    permission,
    loading,
    error,
    subscribe,
    unsubscribe,
    testPush
  };
}

export default usePushNotifications;
