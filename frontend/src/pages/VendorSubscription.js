import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Check, Crown, Star, Zap } from 'lucide-react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { toast } from 'sonner';
import { useAuth } from '../context/AuthContext';

const VendorSubscription = () => {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  const [loading, setLoading] = useState(false);

  const plans = [
    {
      name: 'FREE',
      price: 0,
      period: 'forever',
      commission: '£1.00',
      icon: Star,
      color: 'gray',
      features: [
        '£1 commission per sale',
        'Up to 10 products',
        'Basic listing',
        'Standard support',
        'Email notifications',
      ],
      limitations: [
        'No analytics',
        'No featured placement',
        'Limited support hours',
      ],
    },
    {
      name: 'BRONZE',
      price: 49,
      period: 'month',
      commission: '£0.75',
      icon: Star,
      color: 'orange',
      popular: false,
      features: [
        '£0.75 commission per sale (25% savings)',
        'Unlimited products',
        'Basic analytics dashboard',
        'Priority support',
        'Featured in category once/week',
        'Performance insights',
        'Inventory alerts',
      ],
    },
    {
      name: 'SILVER',
      price: 149,
      period: 'month',
      commission: '£0.50',
      icon: Crown,
      color: 'blue',
      popular: true,
      features: [
        '£0.50 commission per sale (50% savings)',
        'Everything in Bronze, plus:',
        'Advanced analytics & insights',
        '24/7 priority support',
        'Featured in homepage carousel',
        'Custom branding',
        'Marketing tools',
        '5 promoted listings/week',
        'Customer behavior analytics',
      ],
    },
    {
      name: 'GOLD',
      price: 299,
      period: 'month',
      commission: '£0.25',
      icon: Zap,
      color: 'emerald',
      popular: false,
      features: [
        '£0.25 commission per sale (75% savings)',
        'Everything in Silver, plus:',
        'Dedicated account manager',
        'API access',
        'Bulk upload tools',
        'Premium vendor badge',
        'Homepage hero feature (weekly)',
        'Advanced marketing automation',
        'Inventory management system',
        'Custom analytics reports',
        'White-label options',
      ],
    },
  ];

  const handleSubscribe = async (plan) => {
    if (!isAuthenticated) {
      toast.error('Please login to subscribe');
      navigate('/login');
      return;
    }

    if (user?.role !== 'vendor') {
      toast.error('Only vendors can subscribe to plans');
      navigate('/vendor/register');
      return;
    }

    if (plan.name === 'FREE') {
      toast.info('You are already on the FREE plan');
      return;
    }

    setLoading(true);
    
    // Simulate payment processing
    setTimeout(() => {
      toast.success(`Successfully subscribed to ${plan.name} plan!`);
      setLoading(false);
      navigate('/vendor/dashboard');
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      <Header />

      <div className="max-w-7xl mx-auto px-3 sm:px-4 py-8 sm:py-16">
        {/* Header */}
        <div className="text-center mb-12 sm:mb-16">
          <Badge className="mb-4 bg-emerald-100 text-emerald-700 hover:bg-emerald-100 text-sm sm:text-base px-3 py-1">
            Vendor Plans
          </Badge>
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold text-gray-900 mb-4 sm:mb-6">
            Grow Your Business with AfroMarket
          </h1>
          <p className="text-base sm:text-xl text-gray-600 max-w-3xl mx-auto">
            Choose the perfect plan to maximize your sales and reach thousands of customers across the UK
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-12">
          {plans.map((plan) => {
            const Icon = plan.icon;
            return (
              <Card
                key={plan.name}
                className={`relative ${
                  plan.popular
                    ? 'border-4 border-emerald-500 shadow-2xl scale-105'
                    : 'hover:shadow-xl'
                } transition-all duration-300`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                    <Badge className="bg-emerald-500 text-white px-4 py-1 text-sm">
                      MOST POPULAR
                    </Badge>
                  </div>
                )}

                <CardHeader className="text-center pb-4">
                  <div className={`mx-auto mb-4 p-3 rounded-full bg-${plan.color}-100 w-fit`}>
                    <Icon className={`h-6 w-6 sm:h-8 sm:w-8 text-${plan.color}-600`} />
                  </div>
                  <CardTitle className="text-2xl sm:text-3xl font-bold">{plan.name}</CardTitle>
                  <CardDescription className="text-sm">
                    {plan.price === 0 ? (
                      <span className="text-3xl sm:text-4xl font-bold text-gray-900">Free</span>
                    ) : (
                      <div>
                        <span className="text-3xl sm:text-4xl font-bold text-gray-900">£{plan.price}</span>
                        <span className="text-gray-600">/{plan.period}</span>
                      </div>
                    )}
                  </CardDescription>
                  <Badge variant="outline" className="mt-2">
                    {plan.commission} per sale
                  </Badge>
                </CardHeader>

                <CardContent className="space-y-4">
                  <ul className="space-y-2 sm:space-y-3 mb-6">
                    {plan.features.map((feature, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-xs sm:text-sm">
                        <Check className="h-4 w-4 sm:h-5 sm:w-5 text-emerald-600 flex-shrink-0 mt-0.5" />
                        <span>{feature}</span>
                      </li>
                    ))}
                  </ul>

                  <Button
                    className={`w-full ${
                      plan.popular
                        ? 'bg-emerald-600 hover:bg-emerald-700'
                        : 'bg-gray-900 hover:bg-gray-800'
                    } text-white py-5 sm:py-6 text-sm sm:text-base`}
                    onClick={() => handleSubscribe(plan)}
                    disabled={loading}
                  >
                    {plan.price === 0 ? 'Current Plan' : 'Subscribe Now'}
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Features Comparison */}
        <div className="bg-white rounded-2xl shadow-lg p-6 sm:p-8 mb-12">
          <h2 className="text-2xl sm:text-3xl font-bold text-center mb-8">Why Upgrade?</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="bg-emerald-100 p-4 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                <span className="text-2xl">📈</span>
              </div>
              <h3 className="font-semibold mb-2 text-base sm:text-lg">Lower Commissions</h3>
              <p className="text-xs sm:text-sm text-gray-600">
                Save up to 75% on transaction fees and keep more of your earnings
              </p>
            </div>
            <div className="text-center">
              <div className="bg-blue-100 p-4 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                <span className="text-2xl">🎯</span>
              </div>
              <h3 className="font-semibold mb-2 text-base sm:text-lg">More Visibility</h3>
              <p className="text-xs sm:text-sm text-gray-600">
                Get featured on homepage and category pages to reach more customers
              </p>
            </div>
            <div className="text-center">
              <div className="bg-orange-100 p-4 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                <span className="text-2xl">📊</span>
              </div>
              <h3 className="font-semibold mb-2 text-base sm:text-lg">Advanced Analytics</h3>
              <p className="text-xs sm:text-sm text-gray-600">
                Track sales, customer behavior, and optimize your store performance
              </p>
            </div>
          </div>
        </div>

        {/* CTA */}
        <div className="bg-gradient-to-r from-emerald-600 to-emerald-500 rounded-xl sm:rounded-2xl p-6 sm:p-12 text-white text-center">
          <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold mb-4">
            Ready to Grow Your Business?
          </h2>
          <p className="text-base sm:text-xl mb-6 sm:mb-8 max-w-2xl mx-auto">
            Join over 160 successful vendors on AfroMarket UK
          </p>
          <Button
            size="lg"
            className="bg-white text-emerald-600 hover:bg-gray-100 px-6 sm:px-8 py-4 sm:py-6 text-base sm:text-lg font-semibold"
            onClick={() => navigate('/vendor/register')}
          >
            Become a Vendor Today
          </Button>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default VendorSubscription;
