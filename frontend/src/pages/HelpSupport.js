import { useState } from 'react';
import { Mail, Phone, MessageCircle, Search, ChevronDown, ChevronUp } from 'lucide-react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { toast } from 'sonner';

const HelpSupport = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedFaq, setExpandedFaq] = useState(null);
  const [contactForm, setContactForm] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  });

  const faqs = [
    {
      id: 1,
      question: 'How do I create an account?',
      answer: 'Click on the "Sign in" button in the top right corner, then select "Create Account". You can register with your email or use Google/Apple Sign In for quick access.'
    },
    {
      id: 2,
      question: 'How do I place an order?',
      answer: 'Browse our products, add items to your cart, then click the cart icon and proceed to checkout. You\'ll need to provide shipping information and payment details.'
    },
    {
      id: 3,
      question: 'What payment methods do you accept?',
      answer: 'We accept credit/debit cards through Stripe, PayPal, and Apple Pay. All payments are secure and encrypted.'
    },
    {
      id: 4,
      question: 'How long does delivery take?',
      answer: 'Standard delivery takes 2-5 business days. Same-day delivery is available for orders over £30 in selected areas. You\'ll receive tracking information once your order is dispatched.'
    },
    {
      id: 5,
      question: 'What is the delivery fee?',
      answer: 'Delivery is FREE for orders over £30. For orders under £30, there is a £4.99 delivery charge.'
    },
    {
      id: 6,
      question: 'Can I track my order?',
      answer: 'Yes! Once your order is dispatched, you\'ll receive a tracking link via email. You can also view your order status in the "My Orders" section of your profile.'
    },
    {
      id: 7,
      question: 'How do I become a vendor?',
      answer: 'Click on "Become a Vendor" in the top navigation. Fill in your business details and submit the application. Our team will review and contact you within 2-3 business days.'
    },
    {
      id: 8,
      question: 'What commission does AfroMarket UK charge?',
      answer: 'We charge a flat commission of £1 per item sold. This helps us maintain the platform and provide excellent service to both vendors and customers.'
    },
    {
      id: 9,
      question: 'How do I contact a vendor?',
      answer: 'Visit the vendor\'s storefront from any product page. You\'ll find their contact information and can message them directly through the platform.'
    },
    {
      id: 10,
      question: 'What is your return policy?',
      answer: 'We offer a 14-day return policy for most items. Products must be unopened and in original packaging. Contact the vendor directly or our support team to initiate a return.'
    },
    {
      id: 11,
      question: 'Are the products authentic?',
      answer: 'Yes! We verify all vendors before they can sell on our platform. All products are sourced from trusted suppliers and verified African grocery stores across the UK.'
    },
    {
      id: 12,
      question: 'How do I change my password?',
      answer: 'Go to your Profile settings, click on "Account & Lists", then select "Change Password". You\'ll need to enter your current password and new password.'
    }
  ];

  const filteredFaqs = faqs.filter(faq =>
    faq.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
    faq.answer.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const toggleFaq = (id) => {
    setExpandedFaq(expandedFaq === id ? null : id);
  };

  const handleContactSubmit = (e) => {
    e.preventDefault();
    // In production, this would send to backend
    toast.success('Message sent! We\'ll get back to you within 24 hours.');
    setContactForm({ name: '', email: '', subject: '', message: '' });
  };

  const handleInputChange = (e) => {
    setContactForm({ ...contactForm, [e.target.name]: e.target.value });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      {/* Hero Section */}
      <div className="bg-gradient-to-r from-emerald-600 to-emerald-500 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <h1 className="text-5xl font-bold mb-4">How Can We Help You?</h1>
          <p className="text-xl mb-8 opacity-90">Find answers to your questions or get in touch with our support team</p>
          
          {/* Search Bar */}
          <div className="max-w-2xl mx-auto">
            <div className="relative">
              <Search className="absolute left-4 top-4 h-5 w-5 text-gray-400" />
              <Input
                type="text"
                placeholder="Search for answers..."
                className="pl-12 pr-4 py-6 text-lg text-gray-900"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content - FAQs */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle className="text-2xl">Frequently Asked Questions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {filteredFaqs.length === 0 ? (
                    <p className="text-center text-gray-500 py-8">No FAQs found matching your search.</p>
                  ) : (
                    filteredFaqs.map((faq) => (
                      <div
                        key={faq.id}
                        className="border rounded-lg overflow-hidden transition-all hover:shadow-md"
                      >
                        <button
                          onClick={() => toggleFaq(faq.id)}
                          className="w-full px-6 py-4 text-left flex justify-between items-center bg-white hover:bg-gray-50 transition-colors"
                        >
                          <span className="font-semibold text-gray-900">{faq.question}</span>
                          {expandedFaq === faq.id ? (
                            <ChevronUp className="h-5 w-5 text-emerald-600" />
                          ) : (
                            <ChevronDown className="h-5 w-5 text-gray-400" />
                          )}
                        </button>
                        {expandedFaq === faq.id && (
                          <div className="px-6 py-4 bg-gray-50 border-t">
                            <p className="text-gray-700 leading-relaxed">{faq.answer}</p>
                          </div>
                        )}
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Contact Form */}
            <Card className="mt-8">
              <CardHeader>
                <CardTitle className="text-2xl">Still Need Help? Contact Us</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleContactSubmit} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">Your Name</label>
                      <Input
                        name="name"
                        value={contactForm.name}
                        onChange={handleInputChange}
                        placeholder="John Doe"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2">Email Address</label>
                      <Input
                        name="email"
                        type="email"
                        value={contactForm.email}
                        onChange={handleInputChange}
                        placeholder="john@example.com"
                        required
                      />
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-2">Subject</label>
                    <Input
                      name="subject"
                      value={contactForm.subject}
                      onChange={handleInputChange}
                      placeholder="How can we help?"
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-2">Message</label>
                    <Textarea
                      name="message"
                      value={contactForm.message}
                      onChange={handleInputChange}
                      placeholder="Tell us more about your issue..."
                      rows={6}
                      required
                    />
                  </div>
                  
                  <Button type="submit" size="lg" className="w-full bg-emerald-600 hover:bg-emerald-700">
                    <Mail className="h-5 w-5 mr-2" />
                    Send Message
                  </Button>
                </form>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar - Contact Info */}
          <div className="lg:col-span-1">
            <Card className="mb-6">
              <CardHeader>
                <CardTitle>Contact Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-start gap-3 p-4 bg-emerald-50 rounded-lg">
                  <Mail className="h-5 w-5 text-emerald-600 mt-1" />
                  <div>
                    <p className="font-semibold text-gray-900">Email Support</p>
                    <a href="mailto:support@afromarket.uk" className="text-emerald-600 hover:underline">
                      support@afromarket.uk
                    </a>
                    <p className="text-sm text-gray-600 mt-1">Response within 24 hours</p>
                  </div>
                </div>

                <div className="flex items-start gap-3 p-4 bg-orange-50 rounded-lg">
                  <Phone className="h-5 w-5 text-orange-600 mt-1" />
                  <div>
                    <p className="font-semibold text-gray-900">Phone Support</p>
                    <a href="tel:+442012345678" className="text-orange-600 hover:underline">
                      +44 20 1234 5678
                    </a>
                    <p className="text-sm text-gray-600 mt-1">Mon-Fri: 9am - 6pm GMT</p>
                  </div>
                </div>

                <div className="flex items-start gap-3 p-4 bg-blue-50 rounded-lg">
                  <MessageCircle className="h-5 w-5 text-blue-600 mt-1" />
                  <div>
                    <p className="font-semibold text-gray-900">Live Chat</p>
                    <p className="text-blue-600">Coming Soon</p>
                    <p className="text-sm text-gray-600 mt-1">Instant support</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Quick Links</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  <li>
                    <a href="#" className="text-emerald-600 hover:underline flex items-center gap-2">
                      → Terms of Service
                    </a>
                  </li>
                  <li>
                    <a href="#" className="text-emerald-600 hover:underline flex items-center gap-2">
                      → Privacy Policy
                    </a>
                  </li>
                  <li>
                    <a href="#" className="text-emerald-600 hover:underline flex items-center gap-2">
                      → Shipping Information
                    </a>
                  </li>
                  <li>
                    <a href="#" className="text-emerald-600 hover:underline flex items-center gap-2">
                      → Returns & Refunds
                    </a>
                  </li>
                  <li>
                    <a href="/vendor/register" className="text-emerald-600 hover:underline flex items-center gap-2">
                      → Become a Vendor
                    </a>
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default HelpSupport;
