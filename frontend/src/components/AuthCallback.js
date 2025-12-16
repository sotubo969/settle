import React, { useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import api from '../services/api';

/**
 * AuthCallback Component
 * Handles session_id from Emergent Auth and exchanges it for user data
 * Uses useRef to prevent race conditions under React StrictMode
 */
function AuthCallback() {
  const navigate = useNavigate();
  const location = useLocation();
  const hasProcessed = useRef(false);

  useEffect(() => {
    // Prevent double processing in StrictMode
    if (hasProcessed.current) return;
    hasProcessed.current = true;

    const processSession = async () => {
      try {
        // Extract session_id from URL fragment
        const hash = location.hash;
        const params = new URLSearchParams(hash.replace('#', ''));
        const sessionId = params.get('session_id');

        if (!sessionId) {
          console.error('No session_id found in URL');
          navigate('/login');
          return;
        }

        // Exchange session_id for user data and session_token
        const response = await api.post('/auth/session', {
          session_id: sessionId
        });

        if (response.data.success) {
          const { session_token, user } = response.data;

          // Store session_token in cookie (7 days expiry)
          const expiryDays = 7;
          const expiryDate = new Date();
          expiryDate.setTime(expiryDate.getTime() + (expiryDays * 24 * 60 * 60 * 1000));
          
          document.cookie = `session_token=${session_token}; expires=${expiryDate.toUTCString()}; path=/; SameSite=Lax`;

          // Navigate to homepage with user data
          navigate('/', { 
            replace: true,
            state: { user }
          });
        } else {
          throw new Error('Session exchange failed');
        }
      } catch (error) {
        console.error('Auth callback error:', error);
        navigate('/login', { replace: true });
      }
    };

    processSession();
  }, [location, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Completing authentication...</p>
      </div>
    </div>
  );
}

export default AuthCallback;
