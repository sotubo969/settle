import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import { 
  onAuthStateChange, 
  getIdToken, 
  logoutFirebase, 
  isUserVerified,
  signInWithGoogle,
  loginWithEmail as firebaseLoginWithEmail,
  registerWithEmail as firebaseRegisterWithEmail,
  resendVerificationEmail,
  isFirebaseConfigured
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
  const [firebaseEnabled] = useState(isFirebaseConfigured());

  // Listen to Firebase auth state changes (if configured)
  useEffect(() => {
    if (firebaseEnabled) {
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
          // No Firebase user, check for legacy token
          checkLegacyAuth();
        }
        
        setLoading(false);
      });

      return () => unsubscribe();
    } else {
      // Firebase not configured, use legacy auth only
      checkLegacyAuth();
      setLoading(false);
    }
  }, [firebaseEnabled]);

  // Check for legacy authentication
  const checkLegacyAuth = () => {
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
  };

  // Google Sign-In (Firebase)
  const loginWithGoogleProvider = async () => {
    if (!firebaseEnabled) {
      return {
        success: false,
        error: 'Firebase not configured. Please use email/password login.'
      };
    }
    
    try {
      const result = await signInWithGoogle();
      
      if (result.success) {
        // Sync with backend
        try {
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
        } catch (error) {
          console.error('Backend sync error:', error);
          // Still consider success if Firebase auth worked
          setUser(result.user);
          setIsVerified(true);
          return { success: true, user: result.user };
        }
      }
      
      return result;
    } catch (error) {
      console.error('Google login error:', error);
      return { success: false, error: error.message };
    }
  };

  // Email/Password Login (Firebase or Legacy)
  const loginWithEmailPassword = async (email, password) => {
    if (firebaseEnabled) {
      try {
        const result = await firebaseLoginWithEmail(email, password);
        
        if (result.success) {
          // Sync with backend
          try {
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
          } catch (error) {
            console.error('Backend sync error:', error);
          }
        }
        
        return result;
      } catch (error) {
        console.error('Firebase email login error:', error);
        return { success: false, error: error.message };
      }
    } else {
      // Fallback to legacy auth
      try {
        const response = await axios.post(`${API}/auth/login`, { email, password });
        if (response.data.success) {
          const userData = response.data.user;
          setUser(userData);
          setIsVerified(true);
          localStorage.setItem('afroToken', response.data.token);
          localStorage.setItem('afroUser', JSON.stringify(userData));
          return { success: true, user: userData };
        }
        return { success: false, error: 'Login failed' };
      } catch (error) {
        return { success: false, error: error.response?.data?.detail || 'Login failed' };
      }
    }
  };

  // Email/Password Registration (Firebase or Legacy)
  const registerWithEmailPassword = async (email, password, displayName) => {
    if (firebaseEnabled) {
      try {
        const result = await firebaseRegisterWithEmail(email, password, displayName);
        
        if (result.success) {
          // Don't sync with backend until verified
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
        console.error('Firebase registration error:', error);
        return { success: false, error: error.message };
      }
    } else {
      // Fallback to legacy auth
      try {
        const response = await axios.post(`${API}/auth/register`, { 
          name: displayName, 
          email, 
          password 
        });
        if (response.data.success) {
          const userData = response.data.user;
          setUser(userData);
          setIsVerified(true);
          localStorage.setItem('afroToken', response.data.token);
          localStorage.setItem('afroUser', JSON.stringify(userData));
          return { success: true, user: userData };
        }
        return { success: false, error: 'Registration failed' };
      } catch (error) {
        return { success: false, error: error.response?.data?.detail || 'Registration failed' };
      }
    }
  };

  // Resend verification email
  const resendVerification = async () => {
    if (!firebaseEnabled) {
      return { success: false, error: 'Firebase not configured' };
    }
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
      if (firebaseEnabled) {
        await logoutFirebase();
      }
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
    if (firebaseUser && firebaseEnabled) {
      await firebaseUser.reload();
      const verified = isUserVerified(firebaseUser);
      setIsVerified(verified);
      
      if (verified && !user?.emailVerified) {
        // User just got verified, sync with backend
        try {
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
        } catch (error) {
          console.error('Backend sync error:', error);
        }
      }
      
      return verified;
    }
    return isVerified;
  };

  const value = {
    user,
    firebaseUser,
    login,
    logout,
    loading,
    isAuthenticated: !!user,
    isVerified,
    firebaseEnabled,
    loginWithGoogle: loginWithGoogleProvider,
    loginWithEmail: loginWithEmailPassword,
    registerWithEmail: registerWithEmailPassword,
    resendVerification,
    refreshVerificationStatus
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
