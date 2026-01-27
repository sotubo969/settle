// Firebase configuration and initialization
import { initializeApp, getApps } from 'firebase/app';
import { 
  getAuth, 
  GoogleAuthProvider, 
  signInWithPopup,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  sendEmailVerification,
  signOut,
  onAuthStateChanged,
  setPersistence,
  browserLocalPersistence
} from 'firebase/auth';

// Firebase configuration from environment variables
const firebaseConfig = {
  apiKey: process.env.REACT_APP_FIREBASE_API_KEY,
  authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID,
  storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.REACT_APP_FIREBASE_APP_ID
};

// Check if Firebase is configured
const isFirebaseConfigured = () => {
  return !!(firebaseConfig.apiKey && firebaseConfig.projectId);
};

// Initialize Firebase only if configured
let app = null;
let auth = null;

if (isFirebaseConfigured()) {
  try {
    app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0];
    auth = getAuth(app);
    // Set persistence to local storage (survives browser close)
    setPersistence(auth, browserLocalPersistence).catch(console.error);
    console.log('Firebase initialized successfully');
  } catch (error) {
    console.warn('Firebase initialization failed:', error.message);
  }
} else {
  console.warn('Firebase not configured - authentication features will be limited');
}

// Google Auth Provider
const googleProvider = new GoogleAuthProvider();
googleProvider.setCustomParameters({
  prompt: 'select_account'
});

// Auth helper functions
export const signInWithGoogle = async () => {
  if (!auth) {
    return {
      success: false,
      error: 'Firebase not configured. Please configure Firebase credentials.'
    };
  }
  
  try {
    const result = await signInWithPopup(auth, googleProvider);
    const user = result.user;
    const idToken = await user.getIdToken();
    
    return {
      success: true,
      user: {
        uid: user.uid,
        email: user.email,
        displayName: user.displayName,
        photoURL: user.photoURL,
        emailVerified: true, // Google users are always verified
        authProvider: 'google'
      },
      idToken
    };
  } catch (error) {
    console.error('Google sign-in error:', error);
    let errorMessage = 'Google sign-in failed';
    
    if (error.code === 'auth/popup-closed-by-user') {
      errorMessage = 'Sign-in cancelled';
    } else if (error.code === 'auth/popup-blocked') {
      errorMessage = 'Popup blocked. Please allow popups for this site.';
    } else if (error.code === 'auth/unauthorized-domain') {
      errorMessage = 'This domain is not authorized for Google sign-in. Please add this domain to Firebase Console → Authentication → Settings → Authorized domains.';
    } else if (error.code === 'auth/network-request-failed') {
      errorMessage = 'Network error. Please check: 1) Your internet connection, 2) Domain is authorized in Firebase Console → Authentication → Settings → Authorized domains, 3) Google Sign-In is enabled in Firebase Console.';
    } else if (error.code === 'auth/operation-not-allowed') {
      errorMessage = 'Google sign-in is not enabled. Please enable it in Firebase Console → Authentication → Sign-in method.';
    } else if (error.code === 'auth/internal-error') {
      errorMessage = 'Authentication service error. Please ensure Google Sign-In provider is enabled in Firebase Console.';
    } else {
      errorMessage = error.message;
    }
    
    return {
      success: false,
      error: errorMessage
    };
  }
};

export const registerWithEmail = async (email, password, displayName) => {
  if (!auth) {
    return {
      success: false,
      error: 'Firebase not configured. Please configure Firebase credentials.'
    };
  }
  
  try {
    const result = await createUserWithEmailAndPassword(auth, email, password);
    const user = result.user;
    
    // Send email verification
    await sendEmailVerification(user, {
      url: `${window.location.origin}/login?verified=true`,
      handleCodeInApp: false
    });
    
    const idToken = await user.getIdToken();
    
    return {
      success: true,
      user: {
        uid: user.uid,
        email: user.email,
        displayName: displayName,
        photoURL: null,
        emailVerified: false,
        authProvider: 'email'
      },
      idToken,
      verificationSent: true
    };
  } catch (error) {
    console.error('Email registration error:', error);
    let errorMessage = 'Registration failed';
    
    switch (error.code) {
      case 'auth/email-already-in-use':
        errorMessage = 'This email is already registered';
        break;
      case 'auth/weak-password':
        errorMessage = 'Password should be at least 6 characters';
        break;
      case 'auth/invalid-email':
        errorMessage = 'Invalid email address';
        break;
      default:
        errorMessage = error.message;
    }
    
    return {
      success: false,
      error: errorMessage
    };
  }
};

export const loginWithEmail = async (email, password) => {
  if (!auth) {
    return {
      success: false,
      error: 'Firebase not configured. Please configure Firebase credentials.'
    };
  }
  
  try {
    const result = await signInWithEmailAndPassword(auth, email, password);
    const user = result.user;
    
    // Check if email is verified for email/password users
    if (!user.emailVerified) {
      return {
        success: false,
        error: 'Please verify your email before logging in. Check your inbox for the verification link.',
        needsVerification: true,
        user: {
          uid: user.uid,
          email: user.email,
          emailVerified: false
        }
      };
    }
    
    const idToken = await user.getIdToken();
    
    return {
      success: true,
      user: {
        uid: user.uid,
        email: user.email,
        displayName: user.displayName,
        photoURL: user.photoURL,
        emailVerified: user.emailVerified,
        authProvider: 'email'
      },
      idToken
    };
  } catch (error) {
    console.error('Email login error:', error);
    let errorMessage = 'Login failed';
    
    switch (error.code) {
      case 'auth/user-not-found':
        errorMessage = 'No account found with this email';
        break;
      case 'auth/wrong-password':
        errorMessage = 'Incorrect password';
        break;
      case 'auth/invalid-email':
        errorMessage = 'Invalid email address';
        break;
      case 'auth/user-disabled':
        errorMessage = 'This account has been disabled';
        break;
      case 'auth/invalid-credential':
        errorMessage = 'Invalid email or password';
        break;
      default:
        errorMessage = error.message;
    }
    
    return {
      success: false,
      error: errorMessage
    };
  }
};

export const resendVerificationEmail = async () => {
  if (!auth) {
    return { success: false, error: 'Firebase not configured' };
  }
  
  try {
    const user = auth.currentUser;
    if (user && !user.emailVerified) {
      await sendEmailVerification(user, {
        url: `${window.location.origin}/login?verified=true`,
        handleCodeInApp: false
      });
      return { success: true, message: 'Verification email sent!' };
    }
    return { success: false, error: 'No user to verify or already verified' };
  } catch (error) {
    console.error('Resend verification error:', error);
    return { success: false, error: error.message };
  }
};

export const logoutFirebase = async () => {
  if (!auth) {
    return { success: true };
  }
  
  try {
    await signOut(auth);
    return { success: true };
  } catch (error) {
    console.error('Logout error:', error);
    return { success: false, error: error.message };
  }
};

export const getCurrentUser = () => {
  return auth?.currentUser || null;
};

export const getIdToken = async () => {
  const user = auth?.currentUser;
  if (user) {
    return await user.getIdToken(true);
  }
  return null;
};

export const onAuthStateChange = (callback) => {
  if (!auth) {
    // If Firebase is not configured, immediately call callback with null
    callback(null);
    return () => {}; // Return empty unsubscribe function
  }
  return onAuthStateChanged(auth, callback);
};

// Check if user is verified (Google = always true, Email = check emailVerified)
export const isUserVerified = (user) => {
  if (!user) return false;
  
  // Google users are always considered verified
  const providers = user.providerData || [];
  const isGoogleUser = providers.some(p => p.providerId === 'google.com');
  
  if (isGoogleUser) return true;
  
  // Email users must have verified email
  return user.emailVerified === true;
};

export { auth, app, isFirebaseConfigured };
