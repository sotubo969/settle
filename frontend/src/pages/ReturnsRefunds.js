import Header from '../components/Header';
import Footer from '../components/Footer';
import { Card, CardContent } from '../components/ui/card';
import { RotateCcw, AlertCircle } from 'lucide-react';

const ReturnsRefunds = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="bg-gradient-to-r from-purple-600 to-purple-500 text-white py-12 px-8 rounded-t-2xl">
          <div className="flex items-center gap-3 mb-4">
            <RotateCcw className="h-10 w-10" />
            <h1 className="text-4xl font-bold">Returns & Refunds Policy</h1>
          </div>
          <p className="text-lg opacity-90">Your satisfaction is our priority</p>
        </div>

        <Card className="rounded-t-none shadow-xl">
          <CardContent className="p-8 space-y-8">
            <section>
              <div className="bg-purple-50 border-l-4 border-purple-600 p-6 rounded mb-6">
                <p className="text-purple-900 font-bold text-xl">14-Day Return Policy</p>
                <p className="text-purple-800 mt-2">Changed your mind? Return most items within 14 days for a full refund.</p>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">1. Return Eligibility</h2>
              <div className="space-y-4 text-gray-700">
                <div>
                  <h3 className="font-semibold text-lg mb-2">✅ Items You Can Return</h3>
                  <ul className="list-disc list-inside space-y-1 ml-4">
                    <li>Unopened packaged foods within 14 days</li>
                    <li>Beauty and household products (unopened)</li>
                    <li>Dried and preserved foods (unopened)</li>
                    <li>Products in original packaging with seals intact</li>
                    <li>Items that are faulty or damaged on arrival</li>
                  </ul>
                </div>

                <div>
                  <h3 className="font-semibold text-lg mb-2">❌ Items You Cannot Return</h3>
                  <ul className="list-disc list-inside space-y-1 ml-4">
                    <li>Fresh produce (fruits, vegetables, meat, fish)</li>
                    <li>Frozen foods (once delivered)</li>
                    <li>Opened or used products</li>
                    <li>Products without original packaging</li>
                    <li>Items past their return window (14 days)</li>
                    <li>Perishable goods</li>
                  </ul>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">2. How to Return an Item</h2>
              <div className="space-y-3 text-gray-700">
                <div className="flex items-start gap-3">
                  <span className="bg-purple-100 text-purple-700 font-bold h-8 w-8 rounded-full flex items-center justify-center flex-shrink-0">1</span>
                  <div>
                    <p className="font-semibold">Contact the Vendor</p>
                    <p className="text-sm">Log in to your account, go to "My Orders", and click "Return Item" on the order. This notifies the vendor.</p>
                  </div>
                </div>
                
                <div className="flex items-start gap-3">
                  <span className="bg-purple-100 text-purple-700 font-bold h-8 w-8 rounded-full flex items-center justify-center flex-shrink-0">2</span>
                  <div>
                    <p className="font-semibold">Vendor Approval</p>
                    <p className="text-sm">The vendor will review your request and approve it (usually within 24 hours).</p>
                  </div>
                </div>
                
                <div className="flex items-start gap-3">
                  <span className="bg-purple-100 text-purple-700 font-bold h-8 w-8 rounded-full flex items-center justify-center flex-shrink-0">3</span>
                  <div>
                    <p className="font-semibold">Return Shipping</p>
                    <p className="text-sm">You'll receive a prepaid return label via email. Print it and attach to the package.</p>
                  </div>
                </div>
                
                <div className="flex items-start gap-3">
                  <span className="bg-purple-100 text-purple-700 font-bold h-8 w-8 rounded-full flex items-center justify-center flex-shrink-0">4</span>
                  <div>
                    <p className="font-semibold">Ship the Item</p>
                    <p className="text-sm">Drop off at your nearest post office or courier depot. Keep your receipt.</p>
                  </div>
                </div>
                
                <div className="flex items-start gap-3">
                  <span className="bg-purple-100 text-purple-700 font-bold h-8 w-8 rounded-full flex items-center justify-center flex-shrink-0">5</span>
                  <div>
                    <p className="font-semibold">Refund Processing</p>
                    <p className="text-sm">Once the vendor receives and inspects the item, your refund will be processed within 5-7 business days.</p>
                  </div>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">3. Refund Methods</h2>
              <div className="text-gray-700 space-y-3">
                <p>Refunds are issued to your original payment method:</p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li><strong>Credit/Debit Card:</strong> 5-7 business days after approval</li>
                  <li><strong>PayPal:</strong> 3-5 business days after approval</li>
                  <li><strong>Apple Pay:</strong> 5-7 business days after approval</li>
                </ul>
                <p className="text-sm italic mt-3">
                  Note: Bank processing times may vary. Contact your bank if you don't see the refund after 10 business days.
                </p>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">4. Return Shipping Costs</h2>
              <div className="text-gray-700 space-y-3">
                <div className="bg-green-50 border-l-4 border-green-600 p-4 rounded">
                  <p className="font-semibold text-green-900">FREE Returns on Faulty Items</p>
                  <p className="text-sm text-green-800 mt-1">If an item is faulty, damaged, or not as described, we cover return shipping costs.</p>
                </div>
                
                <div className="bg-orange-50 border-l-4 border-orange-600 p-4 rounded">
                  <p className="font-semibold text-orange-900">Customer-Paid Returns</p>
                  <p className="text-sm text-orange-800 mt-1">If you're returning for other reasons (change of mind), you cover return shipping (£3.99).</p>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">5. Damaged or Faulty Items</h2>
              <div className="text-gray-700 leading-relaxed space-y-3">
                <p className="font-semibold">If you receive a damaged or faulty item:</p>
                <ol className="list-decimal list-inside space-y-2 ml-4">
                  <li>Take photos of the item and packaging</li>
                  <li>Contact us within 48 hours of delivery</li>
                  <li>We'll arrange collection at no cost to you</li>
                  <li>Choose a replacement or full refund</li>
                </ol>
                <p className="text-sm italic mt-3">
                  You don't need to return damaged items - we trust our customers. Just send us photos for verification.
                </p>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">6. Exchanges</h2>
              <p className="text-gray-700 leading-relaxed">
                We don't offer direct exchanges. If you need a different product:
              </p>
              <ol className="list-decimal list-inside space-y-1 ml-4 mt-2 text-gray-700">
                <li>Return the original item for a refund</li>
                <li>Place a new order for the item you want</li>
              </ol>
              <p className="text-sm italic text-gray-600 mt-3">
                This ensures you get the item you want as quickly as possible.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">7. Partial Refunds</h2>
              <p className="text-gray-700 leading-relaxed mb-2">
                In some cases, partial refunds may be issued:
              </p>
              <ul className="list-disc list-inside space-y-1 ml-4 text-gray-700">
                <li>Items returned after 14 days (at vendor's discretion)</li>
                <li>Items not in original condition or missing packaging</li>
                <li>Items with visible signs of use</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">8. Refund Timeline</h2>
              <div className="bg-gray-50 p-4 rounded-lg text-gray-700">
                <div className="space-y-2">
                  <p><strong>Return initiated:</strong> Day 0</p>
                  <p><strong>Item shipped back:</strong> Day 1-2</p>
                  <p><strong>Vendor receives item:</strong> Day 3-5</p>
                  <p><strong>Inspection & approval:</strong> Day 5-7</p>
                  <p><strong>Refund processed:</strong> Day 7-10</p>
                  <p><strong>Refund appears in account:</strong> Day 10-14</p>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">9. Cancellations</h2>
              <div className="text-gray-700 leading-relaxed space-y-3">
                <div>
                  <p className="font-semibold">Before Dispatch</p>
                  <p>You can cancel your order before it's dispatched. Go to "My Orders" and click "Cancel Order". Full refund issued within 3-5 business days.</p>
                </div>
                
                <div>
                  <p className="font-semibold">After Dispatch</p>
                  <p>Once dispatched, you'll need to receive the item and follow the standard return process.</p>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">10. Platform Commission</h2>
              <div className="bg-blue-50 border-l-4 border-blue-600 p-4 rounded">
                <p className="text-blue-900 font-semibold">Important Note</p>
                <p className="text-blue-800 text-sm mt-1">
                  The £1 platform commission per item is non-refundable as it covers payment processing and platform fees. Only the product cost is refunded.
                </p>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">11. Contact Returns Support</h2>
              <div className="text-gray-700 leading-relaxed">
                <p className="mb-2">Need help with a return or refund?</p>
                <p className="ml-4">
                  Email: <a href="mailto:returns@afromarket.uk" className="text-purple-600 hover:underline">returns@afromarket.uk</a><br />
                  Phone: +44 20 1234 5678<br />
                  Hours: Monday-Friday, 9am-6pm GMT<br />
                  Average response time: 24 hours
                </p>
              </div>
            </section>

            <div className="bg-purple-50 border-l-4 border-purple-600 p-6 rounded">
              <p className="text-gray-800 font-semibold mb-2 flex items-center gap-2">
                <AlertCircle className="h-5 w-5 text-purple-600" />
                Important Reminders
              </p>
              <ul className="text-gray-700 space-y-1 text-sm">
                <li>• Returns must be requested within 14 days of delivery</li>
                <li>• Items must be unopened and in original packaging</li>
                <li>• Fresh and frozen items cannot be returned</li>
                <li>• Take photos of damaged items before contacting us</li>
                <li>• Keep your return shipping receipt until refund is received</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>

      <Footer />
    </div>
  );
};

export default ReturnsRefunds;