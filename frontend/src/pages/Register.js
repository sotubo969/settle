/**
 * Register Page - Unified Firebase Authentication
 * Single clean signup form with email/password and Google sign-in
 * Google sign-in users skip email verification
 * Email/password users need to verify their email
 */
import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, User as UserIcon, ArrowLeft, Loader2, Eye, EyeOff, CheckCircle, MailCheck } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent } from '../components/ui/card';
import { toast } from 'sonner';
import { useAuth } from '../context/AuthContext';

// Google icon SVG component
const GoogleIcon = () => (
  <svg className="w-5 h-5" viewBox="0 0 24 24">
    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
  </svg>
);

// Password strength indicator
const PasswordStrength = ({ password }) => {
  const getStrength = () => {
    if (!password) return { level: 0, label: '', color: 'bg-gray-200' };
    if (password.length < 6) return { level: 1, label: 'Too short', color: 'bg-red-500' };
    if (password.length < 8) return { level: 2, label: 'Weak', color: 'bg-orange-500' };
    if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(password)) return { level: 2, label: 'Fair', color: 'bg-yellow-500' };
    if (password.length >= 10 && /(?=.*[!@#$%^&*])/.test(password)) return { level: 4, label: 'Strong', color: 'bg-emerald-500' };
    return { level: 3, label: 'Good', color: 'bg-emerald-400' };
  };
  
  const strength = getStrength();
  
  if (!password) return null;
  
  return (
    <div className="mt-2">
      <div className="flex gap-1 mb-1">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className={`h-1 flex-1 rounded-full transition-all ${
              i <= strength.level ? strength.color : 'bg-gray-200'
            }`}
          />
        ))}
      </div>
      <p className={`text-xs ${strength.level >= 3 ? 'text-emerald-600' : 'text-gray-500'}`}>
        {strength.label}
      </p>
    </div>
  );
};

const Register = () => {
  const navigate = useNavigate();
  const { 
    loginWithGoogle, 
    registerWithEmail,
    isAuthenticated, 
    isVerified,
    resendVerification,
    firebaseEnabled
  } = useAuth();
  
  // Form state
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);
  const [error, setError] = useState('');
  const [showVerificationScreen, setShowVerificationScreen] = useState(false);
  const [resendingEmail, setResendingEmail] = useState(false);

  // Redirect if already authenticated and verified
  useEffect(() => {
    if (isAuthenticated && isVerified) {
      navigate('/');
    }
  }, [isAuthenticated, isVerified, navigate]);

  // Handle email/password registration
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    // Validation
    if (!name.trim()) {
      setError('Please enter your name');
      return;
    }
    
    if (!email) {
      setError('Please enter your email address');
      return;
    }
    
    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }
    
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    
    setLoading(true);
    
    try {
      const result = await registerWithEmail(email, password, name);
      
      if (result.success) {
        if (result.verificationSent) {
          // Show verification screen for email/password signups
          setShowVerificationScreen(true);
          toast.success('Account created! Please verify your email.');
        } else {
          // Direct login (legacy mode)
          toast.success('Welcome to AfroMarket!');
          navigate('/');
        }
      } else {
        setError(result.error || 'Registration failed. Please try again.');
      }
    } catch (err) {
      setError(err.message || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Handle Google sign-up (no email verification needed)
  const handleGoogleSignup = async () => {
    setError('');
    setGoogleLoading(true);
    
    try {
      const result = await loginWithGoogle();
      
      if (result.success) {
        toast.success('Welcome to AfroMarket!');
        navigate('/');
      } else {
        setError(result.error || 'Google sign-up failed. Please try again.');
      }
    } catch (err) {
      setError('Google sign-up unavailable. Please use email/password.');
    } finally {
      setGoogleLoading(false);
    }
  };

  // Handle resend verification email
  const handleResendVerification = async () => {
    setResendingEmail(true);
    try {
      const result = await resendVerification();
      if (result.success) {
        toast.success('Verification email sent! Check your inbox.');
      } else {
        toast.error(result.error || 'Failed to send verification email');
      }
    } catch (err) {
      toast.error('Failed to send verification email');
    } finally {
      setResendingEmail(false);
    }
  };

  // Verification Screen after successful email/password registration
  if (showVerificationScreen) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-white to-orange-50 flex items-center justify-center px-4 py-12">
        <Card className="w-full max-w-md shadow-2xl border-0 overflow-hidden">
          <div className="bg-gradient-to-r from-emerald-600 to-emerald-500 px-6 py-12 text-center">
            <div className="mx-auto w-20 h-20 bg-white/20 rounded-full flex items-center justify-center mb-4">
              <MailCheck className="h-10 w-10 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-white mb-2">Check Your Email</h1>
            <p className="text-emerald-100">We've sent a verification link to</p>
            <p className="text-white font-semibold mt-1">{email}</p>
          </div>
          
          <CardContent className="p-6 space-y-6">
            <div className="bg-emerald-50 rounded-lg p-4 border border-emerald-200">
              <div className="flex items-start gap-3">
                <CheckCircle className="h-5 w-5 text-emerald-600 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="text-emerald-800 font-medium">Account created successfully!</p>
                  <p className="text-emerald-700 text-sm mt-1">
                    Click the link in your email to activate your account and start shopping.
                  </p>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <p className="text-center text-gray-600 text-sm">
                Didn't receive the email? Check your spam folder or
              </p>
              
              <Button
                variant="outline"
                className="w-full h-11 border-emerald-600 text-emerald-600 hover:bg-emerald-50"
                onClick={handleResendVerification}
                disabled={resendingEmail}
              >
                {resendingEmail ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    Sending...
                  </>
                ) : (
                  'Resend Verification Email'
                )}
              </Button>

              <Link to="/login" className="block">
                <Button variant="ghost" className="w-full text-gray-600">
                  Return to Login
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-white to-orange-50 flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        {/* Back to Home */}
        <Link to="/">
          <Button variant="ghost" className="mb-6 text-gray-600 hover:text-gray-900">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Home
          </Button>
        </Link>

        {/* Main Card */}
        <Card className="shadow-2xl border-0 overflow-hidden">
          {/* Header with gradient */}
          <div className="bg-gradient-to-r from-emerald-600 to-emerald-500 px-6 py-8 text-center">
            <h1 className="text-2xl font-bold text-white mb-1">Create Account</h1>
            <p className="text-emerald-100">Join AfroMarket today</p>
          </div>
          
          <CardContent className="p-6 space-y-6">
            {/* Error Alert */}
            {error && (
              <div className="bg-red-50 text-red-700 px-4 py-3 rounded-lg text-sm border border-red-200">
                {error}
              </div>
            )}

            {/* Google Sign-Up Button */}
            <Button
              type="button"
              variant="outline"
              className="w-full h-12 text-gray-700 border-2 hover:bg-gray-50 font-medium"
              onClick={handleGoogleSignup}
              disabled={googleLoading || !firebaseEnabled}
            >
              {googleLoading ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <>
                  <GoogleIcon />
                  <span className="ml-3">Continue with Google</span>
                </>
              )}
            </Button>

            {/* Divider */}
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-200"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4 bg-white text-gray-500">or create with email</span>
              </div>
            </div>

            {/* Registration Form */}
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Name Field */}
              <div className="space-y-2">
                <Label htmlFor="name" className="text-gray-700 font-medium">
                  Full Name
                </Label>
                <div className="relative">
                  <UserIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <Input
                    id="name"
                    type="text"
                    placeholder="John Doe"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="pl-10 h-12 border-gray-200 focus:border-emerald-500 focus:ring-emerald-500"
                    disabled={loading}
                  />
                </div>
              </div>

              {/* Email Field */}
              <div className="space-y-2">
                <Label htmlFor="email" className="text-gray-700 font-medium">
                  Email Address
                </Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="you@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="pl-10 h-12 border-gray-200 focus:border-emerald-500 focus:ring-emerald-500"
                    disabled={loading}
                  />
                </div>
              </div>

              {/* Password Field */}
              <div className="space-y-2">
                <Label htmlFor="password" className="text-gray-700 font-medium">
                  Password
                </Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="pl-10 pr-10 h-12 border-gray-200 focus:border-emerald-500 focus:ring-emerald-500"
                    disabled={loading}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                  </button>
                </div>
                <PasswordStrength password={password} />
              </div>

              {/* Confirm Password Field */}
              <div className="space-y-2">
                <Label htmlFor="confirmPassword" className="text-gray-700 font-medium">
                  Confirm Password
                </Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <Input
                    id="confirmPassword"
                    type={showConfirmPassword ? 'text' : 'password'}
                    placeholder="••••••••"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="pl-10 pr-10 h-12 border-gray-200 focus:border-emerald-500 focus:ring-emerald-500"
                    disabled={loading}
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showConfirmPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                  </button>
                </div>
                {confirmPassword && password !== confirmPassword && (
                  <p className="text-xs text-red-500">Passwords do not match</p>
                )}
              </div>

              {/* Submit Button */}
              <Button
                type="submit"
                className="w-full h-12 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-base"
                disabled={loading || (password !== confirmPassword)}
              >
                {loading ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin mr-2" />
                    Creating account...
                  </>
                ) : (
                  'Create Account'
                )}
              </Button>
            </form>

            {/* Sign In Link */}
            <p className="text-center text-gray-600">
              Already have an account?{' '}
              <Link to="/login" className="text-emerald-600 hover:text-emerald-700 font-semibold">
                Sign In
              </Link>
            </p>
          </CardContent>
        </Card>

        {/* Footer */}
        <p className="text-center text-gray-500 text-sm mt-6">
          By creating an account, you agree to our{' '}
          <Link to="/terms" className="text-emerald-600 hover:underline">Terms</Link>
          {' '}and{' '}
          <Link to="/privacy" className="text-emerald-600 hover:underline">Privacy Policy</Link>
        </p>
      </div>
    </div>
  );
};

export default Register;
