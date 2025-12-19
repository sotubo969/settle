import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Mail, ArrowLeft, CheckCircle, AlertCircle, Shield, Clock } from 'lucide-react';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState('');

  const validateEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validate email format
    if (!email.trim()) {
      setError('Please enter your email address');
      return;
    }

    if (!validateEmail(email)) {
      setError('Please enter a valid email address');
      return;
    }

    setLoading(true);

    try {
      const response = await axios.post(`${API}/auth/forgot-password`, { email });
      setSent(true);
      toast.success('Password reset instructions sent!');
    } catch (error) {
      // Even if there's an error, we show the success page for security
      // This prevents email enumeration attacks
      setSent(true);
    } finally {
      setLoading(false);
    }
  };

  if (sent) {
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
                <CheckCircle className="h-10 w-10 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-white">Check Your Email</h2>
            </div>
            
            <CardContent className="pt-8 pb-8 px-8">
              <div className="text-center space-y-4">
                <p className="text-gray-700">
                  If an account exists for <strong className="text-emerald-600">{email}</strong>, 
                  you will receive a password reset link shortly.
                </p>
                
                <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-left">
                  <div className="flex items-start gap-3">
                    <Clock className="h-5 w-5 text-amber-600 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="font-semibold text-amber-800 text-sm">Link expires in 30 minutes</p>
                      <p className="text-amber-700 text-sm mt-1">
                        For security, the reset link will expire. If it expires, request a new one.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="bg-gray-50 rounded-xl p-4 text-left">
                  <p className="font-semibold text-gray-800 text-sm mb-2">Didn't receive the email?</p>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>• Check your spam or junk folder</li>
                    <li>• Verify the email address is correct</li>
                    <li>• Wait a few minutes and try again</li>
                  </ul>
                </div>

                <div className="pt-4 space-y-3">
                  <Button 
                    onClick={() => setSent(false)} 
                    variant="outline" 
                    className="w-full border-emerald-500 text-emerald-600 hover:bg-emerald-50"
                  >
                    Try Another Email
                  </Button>
                  <Link to="/login" className="block">
                    <Button className="w-full bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700">
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
              <Shield className="h-10 w-10 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-white">Forgot Password?</h1>
            <p className="text-emerald-100 mt-2">No worries, we'll help you reset it</p>
          </div>
          
          <CardContent className="pt-8 pb-8 px-8">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="email" className="text-gray-700 font-medium">
                  Email Address
                </Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="Enter your registered email"
                    className={`pl-10 h-12 border-2 ${error ? 'border-red-300 focus:border-red-500' : 'border-gray-200 focus:border-emerald-500'} rounded-xl`}
                    value={email}
                    onChange={(e) => { setEmail(e.target.value); setError(''); }}
                    required
                  />
                </div>
                {error && (
                  <div className="flex items-center gap-2 text-red-600 text-sm mt-2">
                    <AlertCircle className="h-4 w-4" />
                    <span>{error}</span>
                  </div>
                )}
                <p className="text-sm text-gray-500 mt-2">
                  Enter the email address associated with your account and we'll send you a link to reset your password.
                </p>
              </div>

              <Button 
                type="submit" 
                className="w-full h-12 text-base font-semibold bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 rounded-xl shadow-lg shadow-emerald-500/30" 
                disabled={loading}
              >
                {loading ? (
                  <span className="flex items-center gap-2">
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Sending...
                  </span>
                ) : 'Send Reset Link'}
              </Button>

              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-200" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-4 bg-white text-gray-500">or</span>
                </div>
              </div>

              <div className="text-center space-y-3">
                <p className="text-gray-600">
                  Remember your password?{' '}
                  <Link to="/login" className="text-emerald-600 font-semibold hover:underline">
                    Sign in
                  </Link>
                </p>
                <p className="text-gray-600">
                  Don't have an account?{' '}
                  <Link to="/register" className="text-emerald-600 font-semibold hover:underline">
                    Sign up
                  </Link>
                </p>
              </div>
            </form>
          </CardContent>
        </Card>

        <p className="text-center text-sm text-gray-500 mt-6">
          For security reasons, we don't confirm if an email exists in our system.
        </p>
      </div>
    </div>
  );
};

export default ForgotPassword;
