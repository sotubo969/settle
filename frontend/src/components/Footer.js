import { Link } from 'react-router-dom';
import { Facebook, Twitter, Instagram, Mail, Phone, MapPin } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-gray-900 text-gray-300 mt-20">
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* About */}
          <div>
            <h3 className="text-white font-bold text-lg mb-4">About AfroMarket UK</h3>
            <p className="text-sm leading-relaxed mb-4">
              The UK's premier marketplace for authentic African groceries. Supporting local vendors and bringing communities together.
            </p>
            <div className="flex gap-3">
              <a href="#" className="hover:text-emerald-400 transition-colors">
                <Facebook className="h-5 w-5" />
              </a>
              <a href="#" className="hover:text-emerald-400 transition-colors">
                <Twitter className="h-5 w-5" />
              </a>
              <a href="#" className="hover:text-emerald-400 transition-colors">
                <Instagram className="h-5 w-5" />
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-white font-bold text-lg mb-4">Quick Links</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link to="/products" className="hover:text-emerald-400 transition-colors">
                  All Products
                </Link>
              </li>
              <li>
                <Link to="/vendor/register" className="hover:text-emerald-400 transition-colors">
                  Become a Vendor
                </Link>
              </li>
              <li>
                <Link to="/profile" className="hover:text-emerald-400 transition-colors">
                  My Orders
                </Link>
              </li>
              <li>
                <a href="#" className="hover:text-emerald-400 transition-colors">
                  Help & Support
                </a>
              </li>
            </ul>
          </div>

          {/* Categories */}
          <div>
            <h3 className="text-white font-bold text-lg mb-4">Popular Categories</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link to="/products?category=fresh-produce" className="hover:text-emerald-400 transition-colors">
                  Fresh Produce
                </Link>
              </li>
              <li>
                <Link to="/products?category=grains-flours" className="hover:text-emerald-400 transition-colors">
                  Grains & Flours
                </Link>
              </li>
              <li>
                <Link to="/products?category=condiments" className="hover:text-emerald-400 transition-colors">
                  Condiments
                </Link>
              </li>
              <li>
                <Link to="/products?category=snacks" className="hover:text-emerald-400 transition-colors">
                  Snacks
                </Link>
              </li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h3 className="text-white font-bold text-lg mb-4">Contact Us</h3>
            <ul className="space-y-3 text-sm">
              <li className="flex items-center gap-2">
                <Mail className="h-4 w-4 text-emerald-400" />
                support@afromarket.uk
              </li>
              <li className="flex items-center gap-2">
                <Phone className="h-4 w-4 text-emerald-400" />
                +44 20 1234 5678
              </li>
              <li className="flex items-start gap-2">
                <MapPin className="h-4 w-4 text-emerald-400 mt-1" />
                <span>London, United Kingdom</span>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-gray-800 mt-8 pt-8 text-sm text-center">
          <p>&copy; 2025 AfroMarket UK. All rights reserved. Built with care for the African diaspora community.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;