import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Check, Truck, Tag, Sparkles, Crown, Gift } from 'lucide-react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { toast } from 'sonner';
import { useAuth } from '../context/AuthContext';

const PremiumMembership = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [loading, setLoading] = useState(false);

  const benefits = [
    {
      icon: Truck,
      title: 'FREE Unlimited Delivery',
      description: 'No delivery fees on any order, any time',
      savings: '£4.99 per order',
    },
    {
      icon: Tag,
      title: 'Exclusive 10% Discount',
      description: 'On all products, every single time you shop',
      savings: 'Average £15/month',
    },
    {
      icon: Sparkles,
      title: 'Early Access',
      description: 'Be first to shop new products and special offers',
      savings: 'Priceless',
    },
    {
      icon: Crown,
      title: 'Priority Support',
      description: '24/7 dedicated customer service',
      savings: 'VIP treatment',
    },
    {
      icon: Gift,
      title: 'Member-Only Deals',
      description: 'Special promotions and flash sales',
      savings: 'Up to 50% off',
    },
  ];

  const handleSubscribe = async () => {
    if (!isAuthenticated) {
      toast.error('Please login to subscribe');
      navigate('/login');
      return;
    }

    setLoading(true);
    
    // Simulate payment processing
    setTimeout(() => {
      toast.success('Welcome to AfroMarket Plus! Your membership is now active.');
      setLoading(false);
      navigate('/profile');
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      <Header />

      <div className="max-w-7xl mx-auto px-3 sm:px-4 py-8 sm:py-16">
        {/* Hero Section */}
        <div className="text-center mb-12 sm:mb-16">
          <Badge className="mb-4 bg-gradient-to-r from-orange-500 to-pink-500 text-white hover:from-orange-600 hover:to-pink-600 text-sm sm:text-base px-4 py-1">
            ✨ Premium Membership
          </Badge>
          <h1 className="text-3xl sm:text-4xl md:text-6xl font-bold mb-4 sm:mb-6">
            <span className="bg-gradient-to-r from-orange-600 via-pink-600 to-purple-600 bg-clip-text text-transparent">
              AfroMarket Plus
            </span>
          </h1>
          <p className="text-lg sm:text-xl text-gray-600 max-w-3xl mx-auto mb-6 sm:mb-8">
            Shop smarter, save more. Get FREE delivery and exclusive perks for just £9.99/month
          </p>
          
          {/* Savings Calculator */}
          <div className="bg-white rounded-2xl shadow-lg p-6 sm:p-8 max-w-2xl mx-auto mb-8">
            <p className="text-sm sm:text-base text-gray-600 mb-2">Average Monthly Savings</p>
            <p className="text-4xl sm:text-6xl font-bold text-emerald-600 mb-2">£25-£40</p>
            <p className="text-xs sm:text-sm text-gray-500">Pay only £9.99/month</p>
          </div>
        </div>

        {/* Benefits Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 mb-12">
          {benefits.map((benefit, idx) => {
            const Icon = benefit.icon;
            return (
              <Card key={idx} className="hover:shadow-xl transition-all duration-300 border-2 hover:border-orange-500">
                <CardContent className="p-4 sm:p-6">
                  <div className="bg-gradient-to-br from-orange-100 to-pink-100 p-3 rounded-full w-fit mb-4">
                    <Icon className="h-6 w-6 sm:h-8 sm:w-8 text-orange-600" />
                  </div>
                  <h3 className="font-bold text-base sm:text-lg mb-2">{benefit.title}</h3>
                  <p className="text-xs sm:text-sm text-gray-600 mb-3">{benefit.description}</p>
                  <Badge variant="outline" className="text-emerald-600 border-emerald-300">
                    Save: {benefit.savings}
                  </Badge>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Pricing Card */}
        <div className="max-w-4xl mx-auto mb-12">
          <Card className="border-4 border-gradient-to-r from-orange-500 to-pink-500 shadow-2xl">
            <CardContent className="p-6 sm:p-12">
              <div className="grid md:grid-cols-2 gap-8 items-center">
                <div>
                  <h2 className="text-2xl sm:text-3xl font-bold mb-4">
                    Start Saving Today
                  </h2>
                  <div className="mb-6">
                    <span className="text-5xl sm:text-6xl font-bold text-gray-900">£9.99</span>
                    <span className="text-xl text-gray-600">/month</span>
                  </div>
                  <ul className="space-y-3 mb-6">
                    <li className="flex items-center gap-2">
                      <Check className="h-5 w-5 text-emerald-600" />
                      <span className="text-sm sm:text-base">Cancel anytime</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <Check className="h-5 w-5 text-emerald-600" />
                      <span className="text-sm sm:text-base">No hidden fees</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <Check className="h-5 w-5 text-emerald-600" />
                      <span className="text-sm sm:text-base">Instant activation</span>
                    </li>
                  </ul>
                </div>
                <div className="text-center">
                  <div className="bg-gradient-to-br from-orange-50 to-pink-50 rounded-2xl p-6 sm:p-8 mb-6">
                    <p className="text-sm sm:text-base text-gray-600 mb-2">Break-even at just</p>
                    <p className="text-3xl sm:text-4xl font-bold text-orange-600 mb-2">2 orders</p>
                    <p className="text-xs sm:text-sm text-gray-500">per month!</p>
                  </div>
                  <Button
                    size="lg"
                    className="w-full bg-gradient-to-r from-orange-500 to-pink-500 hover:from-orange-600 hover:to-pink-600 text-white py-5 sm:py-6 text-base sm:text-lg font-bold shadow-xl"
                    onClick={handleSubscribe}
                    disabled={loading}
                  >
                    {loading ? 'Processing...' : 'Join AfroMarket Plus →'}
                  </Button>
                  <p className="text-xs sm:text-sm text-gray-500 mt-4">
                    30-day money-back guarantee
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Testimonials */}
        <div className="bg-white rounded-2xl shadow-lg p-6 sm:p-12 mb-12">
          <h2 className="text-2xl sm:text-3xl font-bold text-center mb-8 sm:mb-12">What Members Say</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                name: 'Sarah O.',
                quote: "I save over £30 every month! The free delivery alone is worth it.",
                orders: 15,
              },
              {
                name: 'James K.',
                quote: "Early access to new products is amazing. I get the best items first!",
                orders: 22,
              },
              {
                name: 'Amara N.',
                quote: "The 10% discount adds up fast. Best decision for my monthly shopping.",
                orders: 18,
              },
            ].map((testimonial, idx) => (
              <div key={idx} className="bg-gray-50 rounded-xl p-4 sm:p-6">
                <div className="flex items-center gap-2 mb-3">
                  <div className="bg-gradient-to-br from-orange-400 to-pink-400 rounded-full w-10 h-10 sm:w-12 sm:h-12 flex items-center justify-center text-white font-bold text-sm sm:text-base">
                    {testimonial.name[0]}
                  </div>
                  <div>
                    <p className="font-semibold text-sm sm:text-base">{testimonial.name}</p>
                    <p className="text-xs text-gray-500">{testimonial.orders} orders</p>
                  </div>
                </div>
                <p className="text-xs sm:text-sm text-gray-700 italic">"{testimonial.quote}"</p>
              </div>
            ))}
          </div>
        </div>

        {/* FAQ */}
        <div className="max-w-3xl mx-auto">
          <h2 className="text-2xl sm:text-3xl font-bold text-center mb-8">Frequently Asked Questions</h2>
          <div className="space-y-4">
            {[
              {
                q: 'Can I cancel anytime?',
                a: 'Yes! Cancel your membership anytime with no penalty. Your benefits continue until the end of your billing period.',
              },
              {
                q: 'When does FREE delivery apply?',
                a: 'All orders qualify for FREE delivery when you have an active Plus membership. No minimum order required!',
              },
              {
                q: 'How do I get my 10% discount?',
                a: 'The discount is automatically applied at checkout for all Plus members. No codes needed!',
              },
            ].map((faq, idx) => (
              <Card key={idx}>
                <CardContent className="p-4 sm:p-6">
                  <h3 className="font-semibold text-sm sm:text-base mb-2">{faq.q}</h3>
                  <p className="text-xs sm:text-sm text-gray-600">{faq.a}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default PremiumMembership;
