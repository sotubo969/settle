import Header from '../components/Header';
import Footer from '../components/Footer';
import { Card, CardContent } from '../components/ui/card';
import { Shield } from 'lucide-react';

const PrivacyPolicy = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="bg-gradient-to-r from-blue-600 to-blue-500 text-white py-12 px-8 rounded-t-2xl">
          <div className="flex items-center gap-3 mb-4">
            <Shield className="h-10 w-10" />
            <h1 className="text-4xl font-bold">Privacy Policy</h1>
          </div>
          <p className="text-lg opacity-90">Last Updated: January 2025</p>
        </div>

        <Card className="rounded-t-none shadow-xl">
          <CardContent className="p-8 space-y-8">
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">1. Introduction</h2>
              <p className="text-gray-700 leading-relaxed">
                AfroMarket UK ("we", "our", or "us") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our platform.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">2. Information We Collect</h2>
              <div className="text-gray-700 leading-relaxed space-y-4">
                <div>
                  <p className="font-semibold mb-2">2.1 Personal Information</p>
                  <ul className="list-disc list-inside space-y-1 ml-4">
                    <li>Name and contact information (email, phone number)</li>
                    <li>Delivery address</li>
                    <li>Payment information (processed securely by Stripe/PayPal)</li>
                    <li>Account credentials</li>
                  </ul>
                </div>
                
                <div>
                  <p className="font-semibold mb-2">2.2 Business Information (for Vendors)</p>
                  <ul className="list-disc list-inside space-y-1 ml-4">
                    <li>Business name and registration details</li>
                    <li>Tax information</li>
                    <li>Bank account details for payments</li>
                  </ul>
                </div>
                
                <div>
                  <p className="font-semibold mb-2">2.3 Automatic Information</p>
                  <ul className="list-disc list-inside space-y-1 ml-4">
                    <li>IP address and device information</li>
                    <li>Browser type and version</li>
                    <li>Pages visited and time spent</li>
                    <li>Referring website</li>
                    <li>Cookies and similar tracking technologies</li>
                  </ul>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">3. How We Use Your Information</h2>
              <div className="text-gray-700 leading-relaxed">
                <p className="mb-2">We use your information to:</p>
                <ul className="list-disc list-inside space-y-1 ml-4">
                  <li>Process and fulfill orders</li>
                  <li>Communicate with you about orders and account</li>
                  <li>Provide customer support</li>
                  <li>Process payments securely</li>
                  <li>Improve our platform and services</li>
                  <li>Prevent fraud and ensure security</li>
                  <li>Send marketing communications (with your consent)</li>
                  <li>Comply with legal obligations</li>
                </ul>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">4. Information Sharing</h2>
              <div className="text-gray-700 leading-relaxed space-y-4">
                <div>
                  <p className="font-semibold mb-2">4.1 With Vendors</p>
                  <p>We share necessary order information with vendors to fulfill your purchases (name, delivery address, contact details).</p>
                </div>
                
                <div>
                  <p className="font-semibold mb-2">4.2 With Service Providers</p>
                  <p>We work with trusted third parties who help us operate our platform:</p>
                  <ul className="list-disc list-inside space-y-1 ml-4 mt-2">
                    <li>Payment processors (Stripe, PayPal)</li>
                    <li>Delivery services</li>
                    <li>Cloud hosting providers</li>
                    <li>Analytics services</li>
                  </ul>
                </div>
                
                <div>
                  <p className="font-semibold mb-2">4.3 Legal Requirements</p>
                  <p>We may disclose information when required by law or to protect our rights and safety.</p>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">5. Data Security</h2>
              <p className="text-gray-700 leading-relaxed">
                We implement industry-standard security measures to protect your information:
              </p>
              <ul className="list-disc list-inside space-y-1 ml-4 mt-2 text-gray-700">
                <li>SSL/TLS encryption for data transmission</li>
                <li>Secure password hashing</li>
                <li>Regular security audits</li>
                <li>Access controls and authentication</li>
                <li>Payment data handled by PCI-DSS compliant processors</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">6. Your Rights</h2>
              <div className="text-gray-700 leading-relaxed">
                <p className="mb-2">Under UK GDPR, you have the right to:</p>
                <ul className="list-disc list-inside space-y-1 ml-4">
                  <li><strong>Access:</strong> Request a copy of your personal data</li>
                  <li><strong>Rectification:</strong> Correct inaccurate information</li>
                  <li><strong>Erasure:</strong> Request deletion of your data</li>
                  <li><strong>Restriction:</strong> Limit how we use your data</li>
                  <li><strong>Portability:</strong> Receive your data in a portable format</li>
                  <li><strong>Objection:</strong> Object to processing of your data</li>
                  <li><strong>Withdraw consent:</strong> For marketing communications</li>
                </ul>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">7. Cookies</h2>
              <p className="text-gray-700 leading-relaxed mb-3">
                We use cookies and similar technologies to enhance your experience. Cookies help us:
              </p>
              <ul className="list-disc list-inside space-y-1 ml-4 text-gray-700">
                <li>Remember your preferences and settings</li>
                <li>Keep you signed in</li>
                <li>Understand how you use our platform</li>
                <li>Show relevant advertisements</li>
              </ul>
              <p className="text-gray-700 leading-relaxed mt-3">
                You can control cookies through your browser settings.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">8. Third-Party OAuth</h2>
              <p className="text-gray-700 leading-relaxed">
                When you sign in with Google or Apple, we receive basic profile information (name, email, profile picture). We do not receive your Google/Apple password. Review their privacy policies for more information.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">9. Data Retention</h2>
              <p className="text-gray-700 leading-relaxed">
                We retain your information for as long as necessary to provide services and comply with legal obligations. You can request deletion of your account and data at any time.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">10. Children's Privacy</h2>
              <p className="text-gray-700 leading-relaxed">
                Our platform is not intended for children under 13. We do not knowingly collect information from children. If you believe we have collected information from a child, please contact us immediately.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">11. International Transfers</h2>
              <p className="text-gray-700 leading-relaxed">
                Your data may be transferred to and processed in countries outside the UK. We ensure appropriate safeguards are in place to protect your data.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">12. Changes to This Policy</h2>
              <p className="text-gray-700 leading-relaxed">
                We may update this Privacy Policy from time to time. We will notify you of significant changes via email or platform notification.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">13. Contact Us</h2>
              <div className="text-gray-700 leading-relaxed">
                <p className="mb-2">For privacy-related questions or to exercise your rights:</p>
                <p className="ml-4">
                  Email: <a href="mailto:privacy@afromarket.uk" className="text-blue-600 hover:underline">privacy@afromarket.uk</a><br />
                  Data Protection Officer: <a href="mailto:dpo@afromarket.uk" className="text-blue-600 hover:underline">dpo@afromarket.uk</a><br />
                  Phone: +44 20 1234 5678<br />
                  Address: London, United Kingdom
                </p>
              </div>
            </section>

            <div className="bg-blue-50 border-l-4 border-blue-600 p-6 rounded">
              <p className="text-gray-800 font-semibold mb-2">Your Trust Matters</p>
              <p className="text-gray-700">
                We are committed to protecting your privacy and handling your data responsibly. Your trust is essential to our mission of connecting the African diaspora community with authentic groceries.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Footer />
    </div>
  );
};

export default PrivacyPolicy;