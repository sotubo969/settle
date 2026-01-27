import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Store, Mail, Phone, MapPin, FileText, ArrowLeft, Chrome } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Separator } from '../components/ui/separator';
import { toast } from 'sonner';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import Header from '../components/Header';
import Footer from '../components/Footer';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const VendorRegister = () => {
  const navigate = useNavigate();
  const { user, isAuthenticated, loginWithGoogle, firebaseEnabled } = useAuth();
  const [loading, setLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);
  const [formData, setFormData] = useState({
    businessName: '',
    ownerName: '',
    email: '',
    phone: '',
    address: '',
    city: '',
    postcode: '',
    description: '',
  });

  // Pre-fill email if user is logged in
  useState(() => {
    if (user?.email) {
      setFormData(prev => ({ ...prev, email: user.email, ownerName: user.name || '' }));
    }
  }, [user]);

  const handleGoogleSignIn = async () => {
    setGoogleLoading(true);
    try {
      const result = await loginWithGoogle();
      if (result.success) {
        toast.success('Signed in with Google! Please complete the form below.');
        setFormData(prev => ({
          ...prev,
          email: result.user?.email || '',
          ownerName: result.user?.name || result.user?.displayName || ''
        }));
      } else {
        toast.error(result.error || 'Google sign-in failed');
      }
    } catch (error) {
      toast.error('Google sign-in failed');
    } finally {
      setGoogleLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Get token if user is logged in
      const token = localStorage.getItem('afroToken');
      
      // Use authenticated endpoint if logged in, public endpoint otherwise
      const endpoint = token ? `${API}/vendors/register` : `${API}/vendors/register/public`;
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      
      const response = await axios.post(endpoint, {
        businessName: formData.businessName,
        description: formData.description,
        email: formData.email,
        phone: formData.phone,
        address: formData.address,
        city: formData.city,
        postcode: formData.postcode,
        ownerName: formData.ownerName
      }, { headers });
      
      if (response.data.success) {
        const emailNote = response.data.emailSent 
          ? 'An email has been sent to the admin for review.' 
          : '';
        toast.success(`Vendor application submitted! We will review and email you within 2-3 business days. ${emailNote}`);
        navigate('/');
      } else {
        toast.error(response.data.message || 'Registration failed');
      }
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Registration failed. Please try again.';
      toast.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <div className="max-w-4xl mx-auto px-4 py-12">
        <Link to="/">
          <Button variant="ghost" className="mb-6">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Home
          </Button>
        </Link>

        <div className="text-center mb-12">
          <div className="inline-block p-4 bg-emerald-100 rounded-full mb-4">
            <Store className="h-12 w-12 text-emerald-600" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Become a Vendor</h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Join the UK's premier African grocery marketplace and reach thousands of customers
          </p>
        </div>

        {/* Benefits */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <Card>
            <CardContent className="pt-6 text-center">
              <div className="bg-emerald-100 h-12 w-12 rounded-full flex items-center justify-center mx-auto mb-4">
                <Store className="h-6 w-6 text-emerald-600" />
              </div>
              <h3 className="font-semibold mb-2">Your Own Storefront</h3>
              <p className="text-sm text-gray-600">Get a dedicated vendor page to showcase your products</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6 text-center">
              <div className="bg-orange-100 h-12 w-12 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-orange-600">£1</span>
              </div>
              <h3 className="font-semibold mb-2">Low Commission</h3>
              <p className="text-sm text-gray-600">Only £1 per sale - keep more of your earnings</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6 text-center">
              <div className="bg-blue-100 h-12 w-12 rounded-full flex items-center justify-center mx-auto mb-4">
                <MapPin className="h-6 w-6 text-blue-600" />
              </div>
              <h3 className="font-semibold mb-2">Local Reach</h3>
              <p className="text-sm text-gray-600">Connect with customers across the UK</p>
            </CardContent>
          </Card>
        </div>

        <Card className="shadow-xl">
          <CardHeader>
            <CardTitle className="text-2xl">Vendor Application</CardTitle>
            <CardDescription>Fill in your business details to get started</CardDescription>
          </CardHeader>
          <CardContent>
            {/* Google Sign-In Option */}
            {firebaseEnabled && !isAuthenticated && (
              <>
                <div className="mb-6">
                  <Button
                    type="button"
                    variant="outline"
                    className="w-full h-12 text-base"
                    onClick={handleGoogleSignIn}
                    disabled={googleLoading}
                    data-testid="vendor-google-signin"
                  >
                    {googleLoading ? (
                      <span className="flex items-center gap-2">
                        <div className="animate-spin h-5 w-5 border-2 border-gray-300 border-t-emerald-600 rounded-full" />
                        Signing in...
                      </span>
                    ) : (
                      <span className="flex items-center gap-2">
                        <Chrome className="h-5 w-5" />
                        Continue with Google
                      </span>
                    )}
                  </Button>
                  <p className="text-xs text-gray-500 text-center mt-2">
                    Sign in with Google to pre-fill your details
                  </p>
                </div>
                <div className="relative mb-6">
                  <Separator />
                  <span className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-white px-4 text-sm text-gray-500">
                    or fill manually
                  </span>
                </div>
              </>
            )}
            
            {isAuthenticated && (
              <div className="mb-6 p-4 bg-emerald-50 border border-emerald-200 rounded-lg">
                <p className="text-emerald-800 text-sm">
                  ✓ Signed in as <strong>{user?.email}</strong>
                </p>
              </div>
            )}
            
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="businessName">Business Name *</Label>
                  <div className="relative">
                    <Store className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                    <Input
                      id="businessName"
                      name="businessName"
                      placeholder="Your African Store"
                      className="pl-10"
                      value={formData.businessName}
                      onChange={handleChange}
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="ownerName">Owner Name *</Label>
                  <Input
                    id="ownerName"
                    name="ownerName"
                    placeholder="John Doe"
                    value={formData.ownerName}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email">Email Address *</Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                    <Input
                      id="email"
                      name="email"
                      type="email"
                      placeholder="business@email.com"
                      className="pl-10"
                      value={formData.email}
                      onChange={handleChange}
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="phone">Phone Number *</Label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                    <Input
                      id="phone"
                      name="phone"
                      type="tel"
                      placeholder="+44 20 1234 5678"
                      className="pl-10"
                      value={formData.phone}
                      onChange={handleChange}
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2 md:col-span-2">
                  <Label htmlFor="address">Business Address *</Label>
                  <div className="relative">
                    <MapPin className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                    <Input
                      id="address"
                      name="address"
                      placeholder="Street address"
                      className="pl-10"
                      value={formData.address}
                      onChange={handleChange}
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="city">City *</Label>
                  <Input
                    id="city"
                    name="city"
                    placeholder="Manchester"
                    value={formData.city}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="postcode">Postcode *</Label>
                  <Input
                    id="postcode"
                    name="postcode"
                    placeholder="SW1A 1AA"
                    value={formData.postcode}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className="space-y-2 md:col-span-2">
                  <Label htmlFor="description">Business Description *</Label>
                  <div className="relative">
                    <FileText className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                    <Textarea
                      id="description"
                      name="description"
                      placeholder="Tell us about your business, products you sell, and what makes you unique..."
                      className="pl-10 min-h-32"
                      value={formData.description}
                      onChange={handleChange}
                      required
                    />
                  </div>
                </div>
              </div>

              <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-6">
                <h3 className="font-semibold text-emerald-900 mb-2">What happens next?</h3>
                <ul className="space-y-2 text-sm text-emerald-800">
                  <li className="flex items-start gap-2">
                    <span className="text-emerald-600 font-bold">1.</span>
                    <span>Submit your application</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-emerald-600 font-bold">2.</span>
                    <span>Our team reviews your details (usually within 2-3 business days)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-emerald-600 font-bold">3.</span>
                    <span>Once approved, you'll get access to your vendor dashboard</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-emerald-600 font-bold">4.</span>
                    <span>Start listing products and reaching customers!</span>
                  </li>
                </ul>
              </div>

              <Button
                type="submit"
                size="lg"
                className="w-full bg-emerald-600 hover:bg-emerald-700"
                disabled={loading}
              >
                {loading ? 'Submitting...' : 'Submit Application'}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>

      <Footer />
    </div>
  );
};

export default VendorRegister;