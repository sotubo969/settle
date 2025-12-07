import Header from '../components/Header';
import Footer from '../components/Footer';
import { Card, CardContent } from '../components/ui/card';
import { Truck, Package, MapPin, Clock } from 'lucide-react';

const ShippingInformation = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="bg-gradient-to-r from-orange-600 to-orange-500 text-white py-12 px-8 rounded-t-2xl">
          <div className="flex items-center gap-3 mb-4">
            <Truck className="h-10 w-10" />
            <h1 className="text-4xl font-bold">Shipping Information</h1>
          </div>
          <p className="text-lg opacity-90">Fast, reliable delivery across the UK</p>
        </div>

        <Card className="rounded-t-none shadow-xl">
          <CardContent className="p-8 space-y-8">
            <section>
              <div className="bg-green-50 border-l-4 border-green-600 p-6 rounded mb-6">
                <p className="text-green-900 font-bold text-xl">🎉 FREE Delivery on Orders Over £30!</p>
                <p className="text-green-800 mt-2">Save on shipping costs with qualifying orders</p>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <Clock className="h-6 w-6 text-orange-600" />
                Delivery Times
              </h2>
              <div className="space-y-4">
                <div className="border-l-4 border-orange-500 pl-4 py-2">
                  <h3 className="font-semibold text-lg text-gray-900">Standard Delivery (2-5 Business Days)</h3>
                  <p className="text-gray-700 mt-1">
                    Our most popular option. Most orders are delivered within 3 business days.
                  </p>
                  <p className="text-sm text-gray-600 mt-2">
                    Cost: £4.99 (FREE over £30)
                  </p>
                </div>

                <div className="border-l-4 border-emerald-500 pl-4 py-2">
                  <h3 className="font-semibold text-lg text-gray-900">Same-Day Delivery (Selected Areas)</h3>
                  <p className="text-gray-700 mt-1">
                    Order before 2 PM for same-day delivery in London, Birmingham, and Manchester.
                  </p>
                  <p className="text-sm text-gray-600 mt-2">
                    Cost: £8.99 (minimum order £30)
                  </p>
                </div>

                <div className="border-l-4 border-blue-500 pl-4 py-2">
                  <h3 className="font-semibold text-lg text-gray-900">Express Delivery (Next Day)</h3>
                  <p className="text-gray-700 mt-1">
                    Order before 6 PM for next-day delivery (Monday-Friday).
                  </p>
                  <p className="text-sm text-gray-600 mt-2">
                    Cost: £6.99
                  </p>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <MapPin className="h-6 w-6 text-orange-600" />
                Delivery Coverage
              </h2>
              <p className="text-gray-700 leading-relaxed mb-4">
                We deliver to all UK addresses, including:
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-semibold text-gray-900 mb-2">✅ Mainland UK</h3>
                  <p className="text-sm text-gray-700">England, Scotland, Wales - all addresses covered</p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-semibold text-gray-900 mb-2">✅ Northern Ireland</h3>
                  <p className="text-sm text-gray-700">Standard delivery: 3-6 business days</p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-semibold text-gray-900 mb-2">✅ Scottish Highlands</h3>
                  <p className="text-sm text-gray-700">Extended delivery: 4-7 business days</p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-semibold text-gray-900 mb-2">✅ Offshore Islands</h3>
                  <p className="text-sm text-gray-700">Subject to additional charges</p>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <Package className="h-6 w-6 text-orange-600" />
                Order Processing
              </h2>
              <div className="space-y-3 text-gray-700">
                <div className="flex items-start gap-3">
                  <span className="bg-orange-100 text-orange-700 font-bold h-8 w-8 rounded-full flex items-center justify-center flex-shrink-0">1</span>
                  <div>
                    <p className="font-semibold">Order Confirmation</p>
                    <p className="text-sm">You'll receive an email confirmation immediately after placing your order.</p>
                  </div>
                </div>
                
                <div className="flex items-start gap-3">
                  <span className="bg-orange-100 text-orange-700 font-bold h-8 w-8 rounded-full flex items-center justify-center flex-shrink-0">2</span>
                  <div>
                    <p className="font-semibold">Processing (Same Day)</p>
                    <p className="text-sm">Our vendors prepare your order for shipment within 24 hours.</p>
                  </div>
                </div>
                
                <div className="flex items-start gap-3">
                  <span className="bg-orange-100 text-orange-700 font-bold h-8 w-8 rounded-full flex items-center justify-center flex-shrink-0">3</span>
                  <div>
                    <p className="font-semibold">Dispatch Notification</p>
                    <p className="text-sm">You'll receive tracking information once your order is shipped.</p>
                  </div>
                </div>
                
                <div className="flex items-start gap-3">
                  <span className="bg-orange-100 text-orange-700 font-bold h-8 w-8 rounded-full flex items-center justify-center flex-shrink-0">4</span>
                  <div>
                    <p className="font-semibold">Delivery</p>
                    <p className="text-sm">Your order arrives at your doorstep!</p>
                  </div>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Order Tracking</h2>
              <p className="text-gray-700 leading-relaxed mb-3">
                Track your order in real-time:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4 text-gray-700">
                <li>Log in to your account and go to "My Orders"</li>
                <li>Click on the order you want to track</li>
                <li>View real-time delivery status and estimated arrival</li>
                <li>You'll also receive email updates at each stage</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Packaging</h2>
              <p className="text-gray-700 leading-relaxed">
                We take care to ensure your products arrive in perfect condition:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4 mt-3 text-gray-700">
                <li>Fresh produce packed with ice packs (where appropriate)</li>
                <li>Frozen items delivered in insulated packaging</li>
                <li>Fragile items wrapped with extra protection</li>
                <li>Eco-friendly packaging materials used whenever possible</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Delivery Issues</h2>
              <div className="space-y-4 text-gray-700">
                <div>
                  <h3 className="font-semibold mb-2">Nobody Home?</h3>
                  <p>Our couriers will leave a card with instructions. Most items can be redelivered or collected from a local depot.</p>
                </div>
                
                <div>
                  <h3 className="font-semibold mb-2">Damaged Items</h3>
                  <p>If items arrive damaged, please contact us within 48 hours with photos. We'll arrange a replacement or refund.</p>
                </div>
                
                <div>
                  <h3 className="font-semibold mb-2">Missing Items</h3>
                  <p>Check your order confirmation. If items are missing, contact us immediately and we'll investigate.</p>
                </div>
                
                <div>
                  <h3 className="font-semibold mb-2">Delayed Delivery</h3>
                  <p>While rare, delays can occur. Check your tracking information or contact support for updates.</p>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Special Delivery Instructions</h2>
              <p className="text-gray-700 leading-relaxed mb-3">
                You can add special delivery instructions during checkout:
              </p>
              <ul className="list-disc list-inside space-y-1 ml-4 text-gray-700">
                <li>Safe place to leave packages</li>
                <li>Specific delivery time windows</li>
                <li>Delivery to neighbors</li>
                <li>Access codes for buildings</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Contact Delivery Support</h2>
              <div className="text-gray-700 leading-relaxed">
                <p className="mb-2">For delivery-related questions:</p>
                <p className="ml-4">
                  Email: <a href="mailto:delivery@afromarket.uk" className="text-orange-600 hover:underline">delivery@afromarket.uk</a><br />
                  Phone: +44 20 1234 5678<br />
                  Hours: Monday-Friday, 9am-6pm GMT
                </p>
              </div>
            </section>

            <div className="bg-orange-50 border-l-4 border-orange-600 p-6 rounded">
              <p className="text-gray-800 font-semibold mb-2">🚚 Quick Delivery Tips</p>
              <ul className="text-gray-700 space-y-1">
                <li>• Order before 2 PM for same-day delivery (selected areas)</li>
                <li>• Orders over £30 qualify for FREE standard delivery</li>
                <li>• Track your order in real-time from "My Orders"</li>
                <li>• Add delivery instructions at checkout for smooth delivery</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>

      <Footer />
    </div>
  );
};

export default ShippingInformation;