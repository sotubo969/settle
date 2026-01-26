import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import { 
  onAuthStateChange, 
  getIdToken, 
  logoutFirebase, 
  isUserVerified,
  signInWithGoogle,
  loginWithEmail,
  registerWithEmail,
  resendVerificationEmail
} from '../lib/firebase';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [firebaseUser, setFirebaseUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isVerified, setIsVerified] = useState(false);

  // Listen to Firebase auth state changes
  useEffect(() => {
    const unsubscribe = onAuthStateChange(async (fbUser) => {
      setFirebaseUser(fbUser);
      
      if (fbUser) {
        const verified = isUserVerified(fbUser);
        setIsVerified(verified);
        
        if (verified) {
          try {
            // Get fresh ID token
            const idToken = await getIdToken();
            
            // Sync with backend
            const response = await axios.post(`${API}/auth/firebase`, {
              idToken,
              displayName: fbUser.displayName,
              photoURL: fbUser.photoURL
            });
            
            if (response.data.success) {
              const userData = response.data.user;
              setUser(userData);
              localStorage.setItem('afroToken', response.data.token);
              localStorage.setItem('afroUser', JSON.stringify(userData));
            }
          } catch (error) {
            console.error('Backend sync error:', error);
            // Still set basic user info from Firebase
            setUser({
              id: fbUser.uid,
              email: fbUser.email,
              name: fbUser.displayName || fbUser.email?.split('@')[0],
              avatar: fbUser.photoURL,
              role: 'customer',
              emailVerified: verified,
              authProvider: fbUser.providerData?.[0]?.providerId || 'email'
            });
          }
        } else {
          // User exists but not verified
          setUser({
            id: fbUser.uid,
            email: fbUser.email,
            name: fbUser.displayName || fbUser.email?.split('@')[0],
            avatar: fbUser.photoURL,
            role: 'customer',
            emailVerified: false,
            authProvider: 'email'
          });
        }
      } else {
        // Check for legacy token
        const legacyToken = localStorage.getItem('afroToken');
        const savedUser = localStorage.getItem('afroUser');
        
        if (legacyToken && savedUser) {
          try {
            const userData = JSON.parse(savedUser);
            setUser(userData);
            setIsVerified(true); // Legacy users are considered verified
          } catch (error) {
            console.error('Error parsing saved user:', error);
            localStorage.removeItem('afroToken');
            localStorage.removeItem('afroUser');
            setUser(null);
            setIsVerified(false);
          }
        } else {
          setUser(null);
          setIsVerified(false);
        }
      }
      
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  // Google Sign-In
  const loginWithGoogleProvider = async () => {
    try {
      const result = await signInWithGoogle();
      
      if (result.success) {
        // Sync with backend
        const response = await axios.post(`${API}/auth/firebase`, {
          idToken: result.idToken,
          displayName: result.user.displayName,
          photoURL: result.user.photoURL
        });
        
        if (response.data.success) {
          const userData = response.data.user;
          setUser(userData);
          setIsVerified(true);
          localStorage.setItem('afroToken', response.data.token);
          localStorage.setItem('afroUser', JSON.stringify(userData));
          return { success: true, user: userData };
        }
      }
      
      return result;
    } catch (error) {
      console.error('Google login error:', error);
      return { success: false, error: error.message };
    }
  };

  // Email/Password Login
  const loginWithEmailPassword = async (email, password) => {
    try {
      const result = await loginWithEmail(email, password);
      
      if (result.success) {
        // Sync with backend
        const response = await axios.post(`${API}/auth/firebase`, {
          idToken: result.idToken,
          displayName: result.user.displayName,
          photoURL: result.user.photoURL
        });
        
        if (response.data.success) {
          const userData = response.data.user;
          setUser(userData);
          setIsVerified(true);
          localStorage.setItem('afroToken', response.data.token);
          localStorage.setItem('afroUser', JSON.stringify(userData));
          return { success: true, user: userData };
        }
      }
      
      return result;
    } catch (error) {
      console.error('Email login error:', error);
      return { success: false, error: error.message };
    }
  };

  // Email/Password Registration
  const registerWithEmailPassword = async (email, password, displayName) => {
    try {
      const result = await registerWithEmail(email, password, displayName);
      
      if (result.success) {
        // Don't sync with backend until verified
        // Just set minimal user info
        setUser({
          id: result.user.uid,
          email: result.user.email,
          name: displayName,
          role: 'customer',
          emailVerified: false,
          authProvider: 'email'
        });
        setIsVerified(false);
        
        return { 
          success: true, 
          verificationSent: true,
          message: 'Account created! Please check your email to verify your account before logging in.'
        };
      }
      
      return result;
    } catch (error) {
      console.error('Registration error:', error);
      return { success: false, error: error.message };
    }
  };

  // Resend verification email
  const resendVerification = async () => {
    return await resendVerificationEmail();
  };

  // Legacy login (for backward compatibility)
  const login = (userData, token) => {
    setUser(userData);
    setIsVerified(true);
    localStorage.setItem('afroToken', token);
    localStorage.setItem('afroUser', JSON.stringify(userData));
  };

  // Logout
  const logout = async () => {
    try {
      await logoutFirebase();
    } catch (error) {
      console.error('Firebase logout error:', error);
    }
    setUser(null);
    setFirebaseUser(null);
    setIsVerified(false);
    localStorage.removeItem('afroToken');
    localStorage.removeItem('afroUser');
  };

  // Refresh user verification status
  const refreshVerificationStatus = async () => {
    if (firebaseUser) {
      await firebaseUser.reload();
      const verified = isUserVerified(firebaseUser);
      setIsVerified(verified);
      
      if (verified && !user?.emailVerified) {
        // User just got verified, sync with backend
        const idToken = await getIdToken();
        const response = await axios.post(`${API}/auth/firebase`, {
          idToken,
          displayName: firebaseUser.displayName,
          photoURL: firebaseUser.photoURL
        });
        
        if (response.data.success) {
          const userData = response.data.user;
          setUser(userData);
          localStorage.setItem('afroToken', response.data.token);
          localStorage.setItem('afroUser', JSON.stringify(userData));
        }
      }
      
      return verified;
    }
    return false;
  };

  const value = {
    user,
    firebaseUser,
    login,
    logout,
    loading,
    isAuthenticated: !!user,
    isVerified,
    loginWithGoogle: loginWithGoogleProvider,
    loginWithEmail: loginWithEmailPassword,
    registerWithEmail: registerWithEmailPassword,
    resendVerification,
    refreshVerificationStatus
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
