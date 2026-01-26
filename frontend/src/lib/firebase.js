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

// Initialize Firebase (singleton pattern)
const app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0];
const auth = getAuth(app);

// Set persistence to local storage (survives browser close)
setPersistence(auth, browserLocalPersistence);

// Google Auth Provider
const googleProvider = new GoogleAuthProvider();
googleProvider.setCustomParameters({
  prompt: 'select_account'
});

// Auth helper functions
export const signInWithGoogle = async () => {
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
    return {
      success: false,
      error: error.message
    };
  }
};

export const registerWithEmail = async (email, password, displayName) => {
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
  try {
    await signOut(auth);
    return { success: true };
  } catch (error) {
    console.error('Logout error:', error);
    return { success: false, error: error.message };
  }
};

export const getCurrentUser = () => {
  return auth.currentUser;
};

export const getIdToken = async () => {
  const user = auth.currentUser;
  if (user) {
    return await user.getIdToken(true);
  }
  return null;
};

export const onAuthStateChange = (callback) => {
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

export { auth, app };
