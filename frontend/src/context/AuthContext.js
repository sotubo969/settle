import React, { createContext, useContext, useState, useEffect, useRef, useCallback } from 'react';
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
  const [useFirebaseAuth, setUseFirebaseAuth] = useState(true);
  
  // Track if we're using legacy auth to prevent Firebase from interfering
  const isLegacySession = useRef(false);
  const authInitialized = useRef(false);

  // Check for legacy auth FIRST before Firebase
  const checkLegacyAuth = useCallback(() => {
    const legacyToken = localStorage.getItem('afroToken');
    const savedUser = localStorage.getItem('afroUser');
    
    if (legacyToken && savedUser) {
      try {
        const userData = JSON.parse(savedUser);
        setUser(userData);
        setIsVerified(true);
        isLegacySession.current = true;
        console.log('Legacy auth session restored for:', userData.email);
        return true;
      } catch (error) {
        console.error('Error parsing saved user:', error);
        localStorage.removeItem('afroToken');
        localStorage.removeItem('afroUser');
      }
    }
    return false;
  }, []);

  // Initialize auth - check legacy first, then Firebase
  useEffect(() => {
    if (authInitialized.current) return;
    authInitialized.current = true;
    
    // PRIORITY 1: Check for existing legacy session
    const hasLegacySession = checkLegacyAuth();
    
    if (hasLegacySession) {
      // Legacy session found - don't let Firebase override it
      setLoading(false);
      return;
    }
    
    // PRIORITY 2: No legacy session - set up Firebase listener
    if (firebaseEnabled && useFirebaseAuth) {
      const unsubscribe = onAuthStateChange(async (fbUser) => {
        // Don't override legacy sessions
        if (isLegacySession.current) {
          console.log('Skipping Firebase auth change - legacy session active');
          return;
        }
        
        setFirebaseUser(fbUser);
        
        if (fbUser) {
          const verified = isUserVerified(fbUser);
          setIsVerified(verified);
          
          if (verified) {
            try {
              const idToken = await getIdToken();
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
          // No Firebase user and no legacy session
          setUser(null);
          setIsVerified(false);
        }
        
        setLoading(false);
      });

      return () => unsubscribe();
    } else {
      setLoading(false);
    }
  }, [firebaseEnabled, useFirebaseAuth, checkLegacyAuth]);

  // Legacy login function (direct API call) - OPTIMIZED
  const legacyLogin = async (email, password) => {
    try {
      const response = await axios.post(`${API}/auth/login`, { email, password }, {
        timeout: 10000 // 10 second timeout for login
      });
      if (response.data.success) {
        const userData = response.data.user;
        setUser(userData);
        setIsVerified(true);
        isLegacySession.current = true; // Mark as legacy session
        localStorage.setItem('afroToken', response.data.token);
        localStorage.setItem('afroUser', JSON.stringify(userData));
        console.log('Legacy login successful for:', userData.email);
        return { success: true, user: userData };
      }
      return { success: false, error: 'Login failed' };
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message || 'Invalid email or password';
      console.error('Legacy login error:', errorMsg);
      return { success: false, error: errorMsg };
    }
  };

  // Legacy registration function (direct API call) - OPTIMIZED
  const legacyRegister = async (email, password, name) => {
    try {
      const response = await axios.post(`${API}/auth/register`, { 
        name, 
        email, 
        password 
      }, {
        timeout: 10000 // 10 second timeout
      });
      if (response.data.success) {
        const userData = response.data.user;
        setUser(userData);
        setIsVerified(true);
        isLegacySession.current = true; // Mark as legacy session
        localStorage.setItem('afroToken', response.data.token);
        localStorage.setItem('afroUser', JSON.stringify(userData));
        return { success: true, user: userData };
      }
      return { success: false, error: 'Registration failed' };
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Registration failed';
      return { success: false, error: errorMsg };
    }
  };

  // Google Sign-In (Firebase)
  const loginWithGoogleProvider = async () => {
    if (!firebaseEnabled || !useFirebaseAuth) {
      return {
        success: false,
        error: 'Google sign-in is not available. Please use email/password login.'
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
      
      // Check if it's a network error - offer fallback
      if (result.error?.includes('network') || result.error?.includes('Network')) {
        return {
          ...result,
          fallbackAvailable: true,
          fallbackMessage: 'Try using email/password login instead'
        };
      }
      
      return result;
    } catch (error) {
      console.error('Google login error:', error);
      return { 
        success: false, 
        error: error.message,
        fallbackAvailable: true,
        fallbackMessage: 'Try using email/password login instead'
      };
    }
  };

  // Email/Password Login (Firebase with Legacy fallback)
  const loginWithEmailPassword = async (email, password) => {
    // Try Firebase first if enabled
    if (firebaseEnabled && useFirebaseAuth) {
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
        
        // If Firebase returns any error (user not found, invalid credentials, etc.), 
        // fall back to legacy auth to check local database
        if (!result.success) {
          console.log('Firebase login failed, trying legacy auth...');
          const legacyResult = await legacyLogin(email, password);
          if (legacyResult.success) {
            return legacyResult;
          }
          // If both failed, return the more informative error
          return result.error?.includes('No account') || result.error?.includes('Invalid') 
            ? legacyResult 
            : result;
        }
        
        return result;
      } catch (error) {
        console.error('Firebase email login error:', error);
        // Fall back to legacy auth on any Firebase error
        console.log('Firebase error, falling back to legacy auth');
        return await legacyLogin(email, password);
      }
    }
    
    // Use legacy auth directly
    return await legacyLogin(email, password);
  };

  // Email/Password Registration (Firebase with Legacy fallback)
  const registerWithEmailPassword = async (email, password, displayName) => {
    // Try Firebase first if enabled
    if (firebaseEnabled && useFirebaseAuth) {
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
        
        // If Firebase returns network error, fall back to legacy auth
        if (result.error?.includes('network') || result.error?.includes('Network')) {
          console.log('Firebase network error, falling back to legacy registration');
          return await legacyRegister(email, password, displayName);
        }
        
        return result;
      } catch (error) {
        console.error('Firebase registration error:', error);
        // Fall back to legacy auth on Firebase errors
        if (error.message?.includes('network') || error.message?.includes('Network')) {
          console.log('Firebase error, falling back to legacy registration');
          return await legacyRegister(email, password, displayName);
        }
        return { success: false, error: error.message };
      }
    }
    
    // Use legacy auth directly
    return await legacyRegister(email, password, displayName);
  };

  // Resend verification email
  const resendVerification = async () => {
    if (!firebaseEnabled || !useFirebaseAuth) {
      return { success: false, error: 'Email verification not available' };
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
      if (firebaseEnabled && useFirebaseAuth && !isLegacySession.current) {
        await logoutFirebase();
      }
    } catch (error) {
      console.error('Firebase logout error:', error);
    }
    setUser(null);
    setFirebaseUser(null);
    setIsVerified(false);
    isLegacySession.current = false; // Clear legacy session flag
    localStorage.removeItem('afroToken');
    localStorage.removeItem('afroUser');
    console.log('User logged out');
  };

  // Refresh user verification status
  const refreshVerificationStatus = async () => {
    if (firebaseUser && firebaseEnabled && useFirebaseAuth) {
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

  // Disable Firebase auth (use legacy only)
  const disableFirebaseAuth = () => {
    setUseFirebaseAuth(false);
  };

  const value = {
    user,
    firebaseUser,
    login,
    logout,
    loading,
    isAuthenticated: !!user,
    isVerified,
    firebaseEnabled: firebaseEnabled && useFirebaseAuth,
    loginWithGoogle: loginWithGoogleProvider,
    loginWithEmail: loginWithEmailPassword,
    registerWithEmail: registerWithEmailPassword,
    resendVerification,
    refreshVerificationStatus,
    disableFirebaseAuth,
    legacyLogin,
    legacyRegister
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
