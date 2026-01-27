import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, User as UserIcon, ArrowLeft, Loader2, CheckCircle, AlertCircle, MailCheck, AlertTriangle } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Alert, AlertDescription } from '../components/ui/alert';
import { toast } from 'sonner';
import { useAuth } from '../context/AuthContext';

const Register = () => {
  const navigate = useNavigate();
  const { 
    loginWithGoogle, 
    registerWithEmail,
    legacyRegister,
    isAuthenticated, 
    isVerified, 
    resendVerification,
    firebaseEnabled,
    disableFirebaseAuth
  } = useAuth();
  const [loading, setLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);
  const [showVerificationSent, setShowVerificationSent] = useState(false);
  const [showNetworkError, setShowNetworkError] = useState(false);
  const [useLegacyMode, setUseLegacyMode] = useState(false);
  const [registeredEmail, setRegisteredEmail] = useState('');
  const [resendingEmail, setResendingEmail] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });

  // Redirect if already authenticated and verified
  useEffect(() => {
    if (isAuthenticated && isVerified) {
      navigate('/');
    }
  }, [isAuthenticated, isVerified, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (formData.password !== formData.confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    if (formData.password.length < 6) {
      toast.error('Password must be at least 6 characters');
      return;
    }

    setLoading(true);
    setShowNetworkError(false);

    try {
      let result;
      
      // Use legacy registration if in legacy mode
      if (useLegacyMode) {
        result = await legacyRegister(formData.email, formData.password, formData.name);
      } else {
        result = await registerWithEmail(formData.email, formData.password, formData.name);
      }
      
      if (result.success) {
        if (result.verificationSent && !useLegacyMode) {
          setShowVerificationSent(true);
          setRegisteredEmail(formData.email);
          toast.success('Account created! Please check your email to verify.');
        } else {
          // Legacy auth - direct login
          toast.success('Account created! Welcome to AfroMarket!');
          navigate('/');
        }
      } else if (result.error?.includes('network') || result.error?.includes('Network')) {
        setShowNetworkError(true);
        toast.error('Network error - try using standard registration');
      } else {
        toast.error(result.error || 'Registration failed');
      }
    } catch (error) {
      toast.error(error.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSignup = async () => {
    if (!firebaseEnabled) {
      toast.error('Google sign-up requires Firebase configuration');
      return;
    }
    
    setGoogleLoading(true);
    setShowNetworkError(false);
    
    try {
      const result = await loginWithGoogle();
      
      if (result.success) {
        toast.success('Welcome to AfroMarket!');
        navigate('/');
      } else if (result.error?.includes('network') || result.error?.includes('Network') || result.fallbackAvailable) {
        setShowNetworkError(true);
        toast.error('Network error - please use email registration');
      } else {
        toast.error(result.error || 'Google sign-up failed');
      }
    } catch (error) {
      setShowNetworkError(true);
      toast.error('Google sign-up unavailable - please use email registration');
    } finally {
      setGoogleLoading(false);
    }
  };

  const handleUseLegacyMode = () => {
    setUseLegacyMode(true);
    setShowNetworkError(false);
    disableFirebaseAuth();
    toast.success('Switched to standard registration mode');
  };

  const handleResendVerification = async () => {
    setResendingEmail(true);
    try {
      const result = await resendVerification();
      if (result.success) {
        toast.success('Verification email sent! Check your inbox.');
      } else {
        toast.error(result.error || 'Failed to send verification email');
      }
    } catch (error) {
      toast.error('Failed to send verification email');
    } finally {
      setResendingEmail(false);
    }
  };

  // Show verification sent screen (Firebase only)
  if (showVerificationSent && !useLegacyMode) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-orange-50 flex items-center justify-center px-4">
        <div className="w-full max-w-md">
          <Card className="shadow-2xl">
            <CardHeader className="space-y-2 text-center">
              <div className="mx-auto w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mb-4">
                <MailCheck className="h-8 w-8 text-emerald-600" />
              </div>
              <CardTitle className="text-2xl font-bold">Verify Your Email</CardTitle>
              <CardDescription className="text-base">
                We've sent a verification link to
              </CardDescription>
              <p className="font-semibold text-emerald-600">{registeredEmail}</p>
            </CardHeader>
            <CardContent className="space-y-4">
              <Alert className="border-emerald-200 bg-emerald-50">
                <CheckCircle className="h-4 w-4 text-emerald-600" />
                <AlertDescription className="text-emerald-800">
                  <p className="font-medium">Account created successfully!</p>
                  <p className="text-sm mt-1">
                    Please check your email and click the verification link to activate your account.
                  </p>
                </AlertDescription>
              </Alert>

              <div className="space-y-3">
                <p className="text-sm text-gray-600 text-center">
                  Didn't receive the email? Check your spam folder or
                </p>
                <Button 
                  variant="outline" 
                  className="w-full"
                  onClick={handleResendVerification}
                  disabled={resendingEmail}
                >
                  {resendingEmail ? (
                    <><Loader2 className="h-4 w-4 mr-2 animate-spin" /> Sending...</>
                  ) : (
                    <><Mail className="h-4 w-4 mr-2" /> Resend Verification Email</>
                  )}
                </Button>
              </div>

              <div className="relative my-4">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-white px-2 text-gray-500">or</span>
                </div>
              </div>

              <Link to="/login">
                <Button variant="default" className="w-full bg-emerald-600 hover:bg-emerald-700">
                  Go to Login
                </Button>
              </Link>

              <p className="text-xs text-center text-gray-500">
                After verifying your email, you can log in to your account
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-orange-50 flex items-center justify-center px-4 py-8">
      <div className="w-full max-w-md">
        <Link to="/">
          <Button variant="ghost" className="mb-6">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Home
          </Button>
        </Link>

        <Card className="shadow-2xl">
          <CardHeader className="space-y-2 text-center">
            <CardTitle className="text-3xl font-bold">Create Account</CardTitle>
            <CardDescription className="text-base">
              Join AfroMarket UK today
              {useLegacyMode && (
                <span className="block text-xs text-emerald-600 mt-1">
                  (Using standard registration)
                </span>
              )}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {showNetworkError && (
              <Alert className="mb-4 border-orange-200 bg-orange-50">
                <AlertTriangle className="h-4 w-4 text-orange-600" />
                <AlertDescription className="text-orange-800">
                  <p className="font-medium mb-2">Connection issue detected</p>
                  <p className="text-sm mb-3">
                    Having trouble connecting. You can use standard registration instead.
                  </p>
                  <Button 
                    size="sm" 
                    onClick={handleUseLegacyMode}
                    className="bg-orange-600 hover:bg-orange-700 text-white"
                  >
                    Use Standard Registration
                  </Button>
                </AlertDescription>
              </Alert>
            )}

            {/* Google Sign-up - Recommended (Firebase only) */}
            {firebaseEnabled && !useLegacyMode && (
              <div className="mb-6">
                <Button
                  type="button"
                  variant="outline"
                  className="w-full border-2 border-emerald-200 hover:border-emerald-400 hover:bg-emerald-50"
                  size="lg"
                  onClick={handleGoogleSignup}
                  disabled={googleLoading}
                  data-testid="google-signup-btn"
                >
                  {googleLoading ? (
                    <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                  ) : (
                    <svg className="h-5 w-5 mr-2" viewBox="0 0 24 24">
                      <path
                        fill="#4285F4"
                        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                      />
                      <path
                        fill="#34A853"
                        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                      />
                      <path
                        fill="#FBBC05"
                        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                      />
                      <path
                        fill="#EA4335"
                        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                      />
                    </svg>
                  )}
                  Sign up with Google
                </Button>
                <p className="text-xs text-center text-gray-500 mt-2">
                  <CheckCircle className="h-3 w-3 inline mr-1 text-green-500" />
                  Instant sign-up - no email verification required
                </p>
              </div>
            )}

            {firebaseEnabled && !useLegacyMode && (
              <div className="relative my-6">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-white px-2 text-gray-500">Or sign up with email</span>
                </div>
              </div>
            )}

            {firebaseEnabled && !useLegacyMode && (
              <Alert className="mb-4 border-blue-200 bg-blue-50">
                <AlertCircle className="h-4 w-4 text-blue-600" />
                <AlertDescription className="text-blue-800 text-sm">
                  Email sign-up requires email verification before you can log in
                </AlertDescription>
              </Alert>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Full Name</Label>
                <div className="relative">
                  <UserIcon className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                  <Input
                    id="name"
                    type="text"
                    placeholder="John Doe"
                    className="pl-10"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                    data-testid="register-name-input"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="your@email.com"
                    className="pl-10"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    required
                    data-testid="register-email-input"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                  <Input
                    id="password"
                    type="password"
                    placeholder="Create a password (min 6 characters)"
                    className="pl-10"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    required
                    data-testid="register-password-input"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="confirmPassword">Confirm Password</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                  <Input
                    id="confirmPassword"
                    type="password"
                    placeholder="Confirm your password"
                    className="pl-10"
                    value={formData.confirmPassword}
                    onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                    required
                    data-testid="register-confirm-password-input"
                  />
                </div>
              </div>

              <Button 
                type="submit" 
                className="w-full bg-emerald-600 hover:bg-emerald-700" 
                size="lg" 
                disabled={loading}
                data-testid="register-submit-btn"
              >
                {loading ? (
                  <><Loader2 className="h-4 w-4 mr-2 animate-spin" /> Creating account...</>
                ) : (
                  'Create Account'
                )}
              </Button>

              <div className="text-center text-sm mt-6">
                Already have an account?{' '}
                <Link to="/login" className="text-emerald-600 font-semibold hover:underline">
                  Sign in
                </Link>
              </div>

              {!useLegacyMode && (
                <div className="text-center mt-4">
                  <button
                    type="button"
                    onClick={handleUseLegacyMode}
                    className="text-xs text-gray-500 hover:text-gray-700 underline"
                  >
                    Having trouble? Use standard registration
                  </button>
                </div>
              )}
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Register;
