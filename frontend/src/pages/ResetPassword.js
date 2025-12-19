import { useState, useEffect } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { Lock, ArrowLeft, CheckCircle, AlertCircle, Eye, EyeOff, Shield, XCircle, Check } from 'lucide-react';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent } from '../components/ui/card';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ResetPassword = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get('token');
  
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [verifying, setVerifying] = useState(true);
  const [tokenValid, setTokenValid] = useState(false);
  const [tokenError, setTokenError] = useState('');
  const [email, setEmail] = useState('');
  const [success, setSuccess] = useState(false);
  const [errors, setErrors] = useState({});

  // Password validation rules
  const passwordRules = [
    { id: 'length', label: 'At least 8 characters', test: (p) => p.length >= 8 },
    { id: 'uppercase', label: 'One uppercase letter', test: (p) => /[A-Z]/.test(p) },
    { id: 'lowercase', label: 'One lowercase letter', test: (p) => /[a-z]/.test(p) },
    { id: 'number', label: 'One number', test: (p) => /\d/.test(p) },
  ];

  const getPasswordStrength = () => {
    const passedRules = passwordRules.filter(rule => rule.test(password)).length;
    if (passedRules === 0) return { label: '', color: '', width: '0%' };
    if (passedRules === 1) return { label: 'Weak', color: 'bg-red-500', width: '25%' };
    if (passedRules === 2) return { label: 'Fair', color: 'bg-orange-500', width: '50%' };
    if (passedRules === 3) return { label: 'Good', color: 'bg-yellow-500', width: '75%' };
    return { label: 'Strong', color: 'bg-emerald-500', width: '100%' };
  };

  // Verify token on mount
  useEffect(() => {
    const verifyToken = async () => {
      if (!token) {
        setTokenError('No reset token provided. Please request a new password reset link.');
        setVerifying(false);
        return;
      }

      try {
        const response = await axios.get(`${API}/auth/reset-password/verify/${token}`);
        if (response.data.valid) {
          setTokenValid(true);
          setEmail(response.data.email || '');
        }
      } catch (error) {
        setTokenError(error.response?.data?.detail || 'Invalid or expired reset link. Please request a new password reset.');
      } finally {
        setVerifying(false);
      }
    };

    verifyToken();
  }, [token]);

  const validateForm = () => {
    const newErrors = {};

    // Check all password rules
    const failedRules = passwordRules.filter(rule => !rule.test(password));
    if (failedRules.length > 0) {
      newErrors.password = `Password must have: ${failedRules.map(r => r.label.toLowerCase()).join(', ')}`;
    }

    if (password !== confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      const response = await axios.post(`${API}/auth/reset-password`, {
        token,
        password,
        confirmPassword
      });

      setSuccess(true);
      toast.success('Password reset successful!');
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Failed to reset password. Please try again.';
      toast.error(errorMessage);
      
      if (errorMessage.includes('expired') || errorMessage.includes('Invalid')) {
        setTokenValid(false);
        setTokenError(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  // Loading state while verifying token
  if (verifying) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-white to-orange-50 flex items-center justify-center px-4">
        <Card className="shadow-2xl border-0 w-full max-w-md overflow-hidden">
          <div className="bg-gradient-to-r from-emerald-500 to-emerald-600 p-6 text-center">
            <div className="bg-white/20 rounded-full h-16 w-16 flex items-center justify-center mx-auto mb-4">
              <Shield className="h-10 w-10 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-white">Verifying Link</h2>
          </div>
          <CardContent className="py-12">
            <div className="flex flex-col items-center gap-4">
              <div className="relative">
                <div className="w-16 h-16 border-4 border-emerald-200 rounded-full animate-pulse"></div>
                <div className="absolute top-0 left-0 w-16 h-16 border-4 border-emerald-600 rounded-full animate-spin border-t-transparent"></div>
              </div>
              <p className="text-gray-600">Verifying your reset link...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Invalid token state
  if (!tokenValid) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-white to-orange-50 flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-md">
          <Link to="/login">
            <Button variant="ghost" className="mb-6 text-gray-600 hover:text-gray-900">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Login
            </Button>
          </Link>

          <Card className="shadow-2xl border-0 overflow-hidden">
            <div className="bg-gradient-to-r from-red-500 to-red-600 p-6 text-center">
              <div className="bg-white/20 rounded-full h-16 w-16 flex items-center justify-center mx-auto mb-4">
                <XCircle className="h-10 w-10 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-white">Link Expired or Invalid</h2>
            </div>
            
            <CardContent className="pt-8 pb-8 px-8">
              <div className="text-center space-y-4">
                <p className="text-gray-700">{tokenError}</p>
                
                <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-left">
                  <p className="font-semibold text-amber-800 text-sm mb-2">Why did this happen?</p>
                  <ul className="text-sm text-amber-700 space-y-1">
                    <li>• The link has expired (valid for 30 minutes)</li>
                    <li>• The link has already been used</li>
                    <li>• The link was copied incorrectly</li>
                  </ul>
                </div>

                <div className="pt-4 space-y-3">
                  <Link to="/forgot-password" className="block">
                    <Button className="w-full bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700">
                      Request New Reset Link
                    </Button>
                  </Link>
                  <Link to="/login" className="block">
                    <Button variant="outline" className="w-full">
                      Return to Login
                    </Button>
                  </Link>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  // Success state
  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-white to-orange-50 flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-md">
          <Card className="shadow-2xl border-0 overflow-hidden">
            <div className="bg-gradient-to-r from-emerald-500 to-emerald-600 p-6 text-center">
              <div className="bg-white/20 rounded-full h-16 w-16 flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="h-10 w-10 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-white">Password Reset Successful!</h2>
            </div>
            
            <CardContent className="pt-8 pb-8 px-8">
              <div className="text-center space-y-4">
                <div className="w-20 h-20 bg-emerald-100 rounded-full flex items-center justify-center mx-auto">
                  <Check className="h-12 w-12 text-emerald-600" />
                </div>
                
                <p className="text-gray-700">
                  Your password has been successfully reset. You can now log in with your new password.
                </p>

                <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4">
                  <p className="text-emerald-700 text-sm">
                    A confirmation email has been sent to <strong>{email}</strong>
                  </p>
                </div>

                <div className="pt-4">
                  <Link to="/login" className="block">
                    <Button className="w-full h-12 text-base font-semibold bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 rounded-xl shadow-lg shadow-emerald-500/30">
                      Sign In Now
                    </Button>
                  </Link>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  // Password reset form
  const passwordStrength = getPasswordStrength();

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-white to-orange-50 flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        <Link to="/login">
          <Button variant="ghost" className="mb-6 text-gray-600 hover:text-gray-900">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Login
          </Button>
        </Link>

        <Card className="shadow-2xl border-0 overflow-hidden">
          <div className="bg-gradient-to-r from-emerald-500 to-emerald-600 p-6 text-center">
            <div className="bg-white/20 rounded-full h-16 w-16 flex items-center justify-center mx-auto mb-4">
              <Lock className="h-10 w-10 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-white">Create New Password</h1>
            {email && <p className="text-emerald-100 mt-2">For {email}</p>}
          </div>
          
          <CardContent className="pt-8 pb-8 px-8">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* New Password */}
              <div className="space-y-2">
                <Label htmlFor="password" className="text-gray-700 font-medium">
                  New Password
                </Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Enter new password"
                    className={`pl-10 pr-10 h-12 border-2 ${errors.password ? 'border-red-300 focus:border-red-500' : 'border-gray-200 focus:border-emerald-500'} rounded-xl`}
                    value={password}
                    onChange={(e) => { setPassword(e.target.value); setErrors({}); }}
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                  </button>
                </div>

                {/* Password Strength Indicator */}
                {password && (
                  <div className="space-y-2 mt-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-500">Password Strength</span>
                      <span className={`text-sm font-medium ${
                        passwordStrength.label === 'Strong' ? 'text-emerald-600' :
                        passwordStrength.label === 'Good' ? 'text-yellow-600' :
                        passwordStrength.label === 'Fair' ? 'text-orange-600' : 'text-red-600'
                      }`}>{passwordStrength.label}</span>
                    </div>
                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div 
                        className={`h-full ${passwordStrength.color} transition-all duration-300`}
                        style={{ width: passwordStrength.width }}
                      />
                    </div>
                  </div>
                )}

                {/* Password Rules */}
                <div className="grid grid-cols-2 gap-2 mt-3">
                  {passwordRules.map(rule => (
                    <div 
                      key={rule.id}
                      className={`flex items-center gap-2 text-sm ${
                        rule.test(password) ? 'text-emerald-600' : 'text-gray-400'
                      }`}
                    >
                      {rule.test(password) ? (
                        <CheckCircle className="h-4 w-4" />
                      ) : (
                        <div className="h-4 w-4 border-2 border-current rounded-full" />
                      )}
                      <span>{rule.label}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Confirm Password */}
              <div className="space-y-2">
                <Label htmlFor="confirmPassword" className="text-gray-700 font-medium">
                  Confirm New Password
                </Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <Input
                    id="confirmPassword"
                    type={showConfirmPassword ? 'text' : 'password'}
                    placeholder="Confirm new password"
                    className={`pl-10 pr-10 h-12 border-2 ${errors.confirmPassword ? 'border-red-300 focus:border-red-500' : 'border-gray-200 focus:border-emerald-500'} rounded-xl`}
                    value={confirmPassword}
                    onChange={(e) => { setConfirmPassword(e.target.value); setErrors({}); }}
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showConfirmPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                  </button>
                </div>
                
                {/* Password Match Indicator */}
                {confirmPassword && (
                  <div className={`flex items-center gap-2 text-sm mt-2 ${
                    password === confirmPassword ? 'text-emerald-600' : 'text-red-500'
                  }`}>
                    {password === confirmPassword ? (
                      <>
                        <CheckCircle className="h-4 w-4" />
                        <span>Passwords match</span>
                      </>
                    ) : (
                      <>
                        <AlertCircle className="h-4 w-4" />
                        <span>Passwords do not match</span>
                      </>
                    )}
                  </div>
                )}
              </div>

              {/* Error Messages */}
              {(errors.password || errors.confirmPassword) && (
                <div className="bg-red-50 border border-red-200 rounded-xl p-4">
                  <div className="flex items-start gap-2 text-red-600">
                    <AlertCircle className="h-5 w-5 mt-0.5 flex-shrink-0" />
                    <div className="text-sm">
                      {errors.password && <p>{errors.password}</p>}
                      {errors.confirmPassword && <p>{errors.confirmPassword}</p>}
                    </div>
                  </div>
                </div>
              )}

              <Button 
                type="submit" 
                className="w-full h-12 text-base font-semibold bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 rounded-xl shadow-lg shadow-emerald-500/30" 
                disabled={loading || !password || !confirmPassword}
              >
                {loading ? (
                  <span className="flex items-center gap-2">
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Resetting Password...
                  </span>
                ) : 'Reset Password'}
              </Button>
            </form>
          </CardContent>
        </Card>

        <p className="text-center text-sm text-gray-500 mt-6">
          Having trouble? <Link to="/help" className="text-emerald-600 hover:underline">Contact Support</Link>
        </p>
      </div>
    </div>
  );
};

export default ResetPassword;
