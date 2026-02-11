import React from 'react';
import { Link } from 'react-router-dom';
import { Home, Search, ArrowLeft } from 'lucide-react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { Button } from '../components/ui/button';

const NotFound = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-orange-50">
      <Header />
      
      <div className="max-w-4xl mx-auto px-4 py-16 sm:py-24 text-center">
        {/* 404 Illustration */}
        <div className="mb-8">
          <div className="text-9xl font-bold text-emerald-600 opacity-20">404</div>
          <div className="relative -mt-20">
            <div className="text-6xl mb-4">🛒</div>
            <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Oops! Page Not Found
            </h1>
            <p className="text-lg text-gray-600 max-w-md mx-auto mb-8">
              The page you're looking for seems to have wandered off. 
              Don't worry, let's get you back on track!
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
          <Link to="/">
            <Button size="lg" className="bg-emerald-600 hover:bg-emerald-700 text-white gap-2">
              <Home className="h-5 w-5" />
              Go to Homepage
            </Button>
          </Link>
          <Link to="/products">
            <Button size="lg" variant="outline" className="border-emerald-600 text-emerald-600 hover:bg-emerald-50 gap-2">
              <Search className="h-5 w-5" />
              Browse Products
            </Button>
          </Link>
        </div>

        {/* Quick Links */}
        <div className="bg-white rounded-2xl shadow-lg p-8 max-w-2xl mx-auto">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">
            Popular Destinations
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <Link 
              to="/products?category=fresh-produce" 
              className="p-4 rounded-xl bg-emerald-50 hover:bg-emerald-100 transition-colors text-center"
            >
              <span className="text-2xl mb-2 block">🥬</span>
              <span className="text-sm font-medium text-gray-700">Fresh Produce</span>
            </Link>
            <Link 
              to="/products?category=grains-flours" 
              className="p-4 rounded-xl bg-orange-50 hover:bg-orange-100 transition-colors text-center"
            >
              <span className="text-2xl mb-2 block">🌾</span>
              <span className="text-sm font-medium text-gray-700">Grains & Flours</span>
            </Link>
            <Link 
              to="/products?category=snacks" 
              className="p-4 rounded-xl bg-amber-50 hover:bg-amber-100 transition-colors text-center"
            >
              <span className="text-2xl mb-2 block">🍪</span>
              <span className="text-sm font-medium text-gray-700">Snacks</span>
            </Link>
            <Link 
              to="/products?category=drinks" 
              className="p-4 rounded-xl bg-blue-50 hover:bg-blue-100 transition-colors text-center"
            >
              <span className="text-2xl mb-2 block">🥤</span>
              <span className="text-sm font-medium text-gray-700">Drinks</span>
            </Link>
          </div>
        </div>

        {/* Back Button */}
        <button 
          onClick={() => window.history.back()}
          className="mt-8 inline-flex items-center gap-2 text-gray-600 hover:text-emerald-600 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Go back to previous page
        </button>
      </div>

      <Footer />
    </div>
  );
};

export default NotFound;
