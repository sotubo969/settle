import Header from '../components/Header';
import Footer from '../components/Footer';
import { Card, CardContent } from '../components/ui/card';

const TermsOfService = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="bg-gradient-to-r from-emerald-600 to-emerald-500 text-white py-12 px-8 rounded-t-2xl">
          <h1 className="text-4xl font-bold mb-4">Terms of Service</h1>
          <p className="text-lg opacity-90">Last Updated: January 2025</p>
        </div>

        <Card className="rounded-t-none shadow-xl">
          <CardContent className="p-8 space-y-8">
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">1. Acceptance of Terms</h2>
              <p className="text-gray-700 leading-relaxed">
                By accessing and using AfroMarket UK ("the Platform"), you accept and agree to be bound by these Terms of Service. If you do not agree to these terms, please do not use our platform.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">2. Platform Description</h2>
              <p className="text-gray-700 leading-relaxed mb-3">
                AfroMarket UK is an online marketplace connecting verified vendors of African groceries with customers across the United Kingdom. We facilitate transactions between buyers and sellers but are not directly responsible for the products sold.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">3. User Accounts</h2>
              <div className="text-gray-700 leading-relaxed space-y-2">
                <p className="font-semibold">3.1 Account Creation</p>
                <p>You must create an account to make purchases. You agree to provide accurate information and keep your account secure.</p>
                
                <p className="font-semibold mt-4">3.2 Account Security</p>
                <p>You are responsible for maintaining the confidentiality of your password and account activities.</p>
                
                <p className="font-semibold mt-4">3.3 Account Termination</p>
                <p>We reserve the right to suspend or terminate accounts that violate these terms.</p>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">4. Vendor Terms</h2>
              <div className="text-gray-700 leading-relaxed space-y-2">
                <p className="font-semibold">4.1 Vendor Registration</p>
                <p>Vendors must apply and be approved before listing products. All information provided must be accurate and verifiable.</p>
                
                <p className="font-semibold mt-4">4.2 Commission Structure</p>
                <p>AfroMarket UK charges a flat commission of £1 per item sold. This commission is automatically deducted from each sale.</p>
                
                <p className="font-semibold mt-4">4.3 Product Listings</p>
                <p>Vendors must ensure product descriptions, prices, and images are accurate. Misleading information may result in account suspension.</p>
                
                <p className="font-semibold mt-4">4.4 Product Authenticity</p>
                <p>Vendors guarantee that all products are genuine, safe, and comply with UK regulations.</p>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">5. Orders and Payments</h2>
              <div className="text-gray-700 leading-relaxed space-y-2">
                <p className="font-semibold">5.1 Order Placement</p>
                <p>Orders are placed directly with vendors through our platform. Prices are as displayed at checkout.</p>
                
                <p className="font-semibold mt-4">5.2 Payment Methods</p>
                <p>We accept payments via Stripe (credit/debit cards, Apple Pay) and PayPal. All payments are processed securely.</p>
                
                <p className="font-semibold mt-4">5.3 Payment to Vendors</p>
                <p>Payments (minus platform commission) are transferred to vendors within 7 business days of order completion.</p>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">6. Delivery and Shipping</h2>
              <p className="text-gray-700 leading-relaxed">
                Delivery times and costs vary by vendor and location. Standard delivery is 2-5 business days. FREE delivery on orders over £30. See our <a href="/shipping" className="text-emerald-600 hover:underline">Shipping Information</a> page for details.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">7. Returns and Refunds</h2>
              <p className="text-gray-700 leading-relaxed">
                We offer a 14-day return policy for most items. Products must be unopened and in original packaging. See our <a href="/returns" className="text-emerald-600 hover:underline">Returns & Refunds</a> policy for complete details.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">8. Prohibited Activities</h2>
              <div className="text-gray-700 leading-relaxed">
                <p className="mb-2">Users must not:</p>
                <ul className="list-disc list-inside space-y-1 ml-4">
                  <li>Violate any laws or regulations</li>
                  <li>Sell counterfeit or unauthorized products</li>
                  <li>Engage in fraudulent activities</li>
                  <li>Harass other users or vendors</li>
                  <li>Manipulate reviews or ratings</li>
                  <li>Use the platform for unauthorized commercial purposes</li>
                </ul>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">9. Intellectual Property</h2>
              <p className="text-gray-700 leading-relaxed">
                All content on AfroMarket UK, including logos, text, images, and software, is owned by us or our licensors. Unauthorized use is prohibited.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">10. Limitation of Liability</h2>
              <p className="text-gray-700 leading-relaxed">
                AfroMarket UK acts as a marketplace platform. We are not responsible for the quality, safety, or legality of products sold by vendors. Our liability is limited to the maximum extent permitted by law.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">11. Privacy</h2>
              <p className="text-gray-700 leading-relaxed">
                Your privacy is important to us. Please review our <a href="/privacy" className="text-emerald-600 hover:underline">Privacy Policy</a> to understand how we collect and use your information.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">12. Changes to Terms</h2>
              <p className="text-gray-700 leading-relaxed">
                We reserve the right to modify these terms at any time. Continued use of the platform after changes constitutes acceptance of the modified terms.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">13. Contact Us</h2>
              <div className="text-gray-700 leading-relaxed">
                <p className="mb-2">For questions about these Terms of Service, contact us:</p>
                <p className="ml-4">
                  Email: <a href="mailto:legal@afromarket.uk" className="text-emerald-600 hover:underline">legal@afromarket.uk</a><br />
                  Phone: +44 20 1234 5678<br />
                  Address: London, United Kingdom
                </p>
              </div>
            </section>

            <div className="bg-emerald-50 border-l-4 border-emerald-600 p-6 rounded">
              <p className="text-gray-800 font-semibold mb-2">Agreement</p>
              <p className="text-gray-700">
                By using AfroMarket UK, you acknowledge that you have read, understood, and agree to be bound by these Terms of Service.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Footer />
    </div>
  );
};

export default TermsOfService;