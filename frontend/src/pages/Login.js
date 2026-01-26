import { useState, useEffect } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { Mail, Lock, ArrowLeft, Loader2, AlertCircle, CheckCircle, RefreshCw } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Alert, AlertDescription } from '../components/ui/alert';
import { toast } from 'sonner';
import { useAuth } from '../context/AuthContext';

const Login = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { 
    loginWithGoogle, 
    loginWithEmail, 
    isAuthenticated, 
    isVerified, 
    resendVerification, 
    refreshVerificationStatus,
    firebaseEnabled 
  } = useAuth();
  const [loading, setLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);
  const [showVerificationAlert, setShowVerificationAlert] = useState(false);
  const [resendingEmail, setResendingEmail] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  // Check if user just verified their email
  useEffect(() => {
    if (searchParams.get('verified') === 'true') {
      toast.success('Email verified! You can now log in.');
    }
  }, [searchParams]);

  // Redirect if already authenticated and verified
  useEffect(() => {
    if (isAuthenticated && isVerified) {
      navigate('/');
    }
  }, [isAuthenticated, isVerified, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setShowVerificationAlert(false);

    try {
      const result = await loginWithEmail(formData.email, formData.password);
      
      if (result.success) {
        toast.success('Welcome back!');
        navigate('/');
      } else if (result.needsVerification) {
        setShowVerificationAlert(true);
        toast.error('Please verify your email before logging in');
      } else {
        toast.error(result.error || 'Login failed');
      }
    } catch (error) {
      toast.error(error.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    if (!firebaseEnabled) {
      toast.error('Google sign-in is not available. Please configure Firebase.');
      return;
    }
    
    setGoogleLoading(true);
    
    try {
      const result = await loginWithGoogle();
      
      if (result.success) {
        toast.success('Welcome back!');
        navigate('/');
      } else {
        toast.error(result.error || 'Google sign-in failed');
      }
    } catch (error) {
      toast.error(error.message || 'Google sign-in failed');
    } finally {
      setGoogleLoading(false);
    }
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

  const handleCheckVerification = async () => {
    const verified = await refreshVerificationStatus();
    if (verified) {
      toast.success('Email verified! Logging you in...');
      navigate('/');
    } else {
      toast.info('Email not yet verified. Please check your inbox.');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-orange-50 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <Link to="/">
          <Button variant="ghost" className="mb-6">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Home
          </Button>
        </Link>

        <Card className="shadow-2xl">
          <CardHeader className="space-y-2 text-center">
            <CardTitle className="text-3xl font-bold">Welcome Back</CardTitle>
            <CardDescription className="text-base">Sign in to your AfroMarket account</CardDescription>
          </CardHeader>
          <CardContent>
            {showVerificationAlert && firebaseEnabled && (
              <Alert className="mb-4 border-yellow-200 bg-yellow-50">
                <AlertCircle className="h-4 w-4 text-yellow-600" />
                <AlertDescription className="text-yellow-800">
                  <p className="font-medium mb-2">Email verification required</p>
                  <p className="text-sm mb-3">Please verify your email before logging in. Check your inbox for the verification link.</p>
                  <div className="flex gap-2">
                    <Button 
                      size="sm" 
                      variant="outline" 
                      onClick={handleResendVerification}
                      disabled={resendingEmail}
                      className="text-yellow-700 border-yellow-300 hover:bg-yellow-100"
                    >
                      {resendingEmail ? (
                        <><Loader2 className="h-3 w-3 mr-1 animate-spin" /> Sending...</>
                      ) : (
                        <><Mail className="h-3 w-3 mr-1" /> Resend Email</>
                      )}
                    </Button>
                    <Button 
                      size="sm" 
                      variant="outline" 
                      onClick={handleCheckVerification}
                      className="text-yellow-700 border-yellow-300 hover:bg-yellow-100"
                    >
                      <RefreshCw className="h-3 w-3 mr-1" /> I've Verified
                    </Button>
                  </div>
                </AlertDescription>
              </Alert>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
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
                    data-testid="login-email-input"
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
                    placeholder="Enter your password"
                    className="pl-10"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    required
                    data-testid="login-password-input"
                  />
                </div>
              </div>

              <div className="flex justify-end">
                <Link to="/forgot-password">
                  <Button variant="link" className="px-0 text-emerald-600">
                    Forgot password?
                  </Button>
                </Link>
              </div>

              <Button 
                type="submit" 
                className="w-full bg-emerald-600 hover:bg-emerald-700" 
                size="lg" 
                disabled={loading}
                data-testid="login-submit-btn"
              >
                {loading ? (
                  <><Loader2 className="h-4 w-4 mr-2 animate-spin" /> Signing in...</>
                ) : (
                  'Sign In'
                )}
              </Button>

              {firebaseEnabled && (
                <>
                  <div className="relative my-6">
                    <div className="absolute inset-0 flex items-center">
                      <span className="w-full border-t" />
                    </div>
                    <div className="relative flex justify-center text-xs uppercase">
                      <span className="bg-white px-2 text-gray-500">Or continue with</span>
                    </div>
                  </div>

                  <Button
                    type="button"
                    variant="outline"
                    className="w-full"
                    size="lg"
                    onClick={handleGoogleLogin}
                    disabled={googleLoading}
                    data-testid="google-login-btn"
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
                    Continue with Google
                    <CheckCircle className="h-4 w-4 ml-2 text-green-500" />
                  </Button>

                  <p className="text-xs text-center text-gray-500 mt-2">
                    Google sign-in is instant - no email verification required
                  </p>
                </>
              )}

              <div className="text-center text-sm mt-6">
                Don't have an account?{' '}
                <Link to="/register" className="text-emerald-600 font-semibold hover:underline">
                  Sign up
                </Link>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Login;
