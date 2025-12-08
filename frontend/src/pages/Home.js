import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ChevronLeft, ChevronRight, Star, TrendingUp, ShoppingBag, Truck } from 'lucide-react';
import axios from 'axios';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { banners, categories } from '../mock';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Home = () => {
  const [currentBanner, setCurrentBanner] = useState(0);
  const [featuredProducts, setFeaturedProducts] = useState([]);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await axios.get(`${API}/products?featured=true`);
        setFeaturedProducts(response.data);
      } catch (error) {
        console.error('Error fetching products:', error);
      }
    };
    fetchProducts();
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentBanner((prev) => (prev + 1) % banners.length);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const nextBanner = () => setCurrentBanner((prev) => (prev + 1) % banners.length);
  const prevBanner = () => setCurrentBanner((prev) => (prev - 1 + banners.length) % banners.length);

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      {/* Hero Carousel */}
      <div className="relative h-[300px] sm:h-[400px] md:h-[500px] overflow-hidden bg-gradient-to-br from-emerald-50 to-orange-50">
        {banners.map((banner, index) => (
          <div
            key={banner.id}
            className={`absolute inset-0 transition-all duration-700 ease-in-out ${
              index === currentBanner ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-full'
            }`}
            style={{
              backgroundImage: `linear-gradient(rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.4)), url(${banner.image})`,
              backgroundSize: 'cover',
              backgroundPosition: 'center',
            }}
          >
            <div className="max-w-7xl mx-auto h-full flex items-center px-4">
              <div className="text-white max-w-2xl animate-fade-in">
                <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold mb-2 sm:mb-4 drop-shadow-lg">
                  {banner.title}
                </h1>
                <p className="text-base sm:text-xl md:text-2xl mb-4 sm:mb-8 drop-shadow-md">{banner.subtitle}</p>
                <Link to={banner.link}>
                  <Button size="lg" className="bg-orange-500 hover:bg-orange-600 text-white px-6 sm:px-8 py-4 sm:py-6 text-base sm:text-lg font-semibold shadow-xl hover:shadow-2xl transform hover:scale-105 transition-all">
                    {banner.cta}
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        ))}

        {/* Navigation Buttons */}
        <Button
          variant="ghost"
          size="icon"
          className="absolute left-4 top-1/2 -translate-y-1/2 bg-white/80 hover:bg-white text-gray-800 rounded-full h-12 w-12 shadow-lg"
          onClick={prevBanner}
        >
          <ChevronLeft className="h-6 w-6" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="absolute right-4 top-1/2 -translate-y-1/2 bg-white/80 hover:bg-white text-gray-800 rounded-full h-12 w-12 shadow-lg"
          onClick={nextBanner}
        >
          <ChevronRight className="h-6 w-6" />
        </Button>

        {/* Dots Indicator */}
        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex gap-2">
          {banners.map((_, index) => (
            <button
              key={index}
              className={`h-3 rounded-full transition-all duration-300 ${
                index === currentBanner ? 'w-8 bg-white' : 'w-3 bg-white/50'
              }`}
              onClick={() => setCurrentBanner(index)}
            />
          ))}
        </div>
      </div>

      {/* Features Bar */}
      <div className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-2 sm:px-4 py-4 sm:py-6">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-6">
            <div className="flex items-center gap-3 sm:gap-4 p-3 sm:p-4 rounded-lg hover:bg-gray-50 transition-colors">
              <div className="bg-emerald-100 p-2 sm:p-3 rounded-full">
                <Truck className="h-5 w-5 sm:h-6 sm:w-6 text-emerald-600" />
              </div>
              <div>
                <h3 className="font-semibold text-sm sm:text-base">Fast Delivery</h3>
                <p className="text-xs sm:text-sm text-gray-600">Same-day delivery available</p>
              </div>
            </div>
            <div className="flex items-center gap-3 sm:gap-4 p-3 sm:p-4 rounded-lg hover:bg-gray-50 transition-colors">
              <div className="bg-orange-100 p-2 sm:p-3 rounded-full">
                <ShoppingBag className="h-5 w-5 sm:h-6 sm:w-6 text-orange-600" />
              </div>
              <div>
                <h3 className="font-semibold text-sm sm:text-base">Authentic Products</h3>
                <p className="text-xs sm:text-sm text-gray-600">From verified vendors</p>
              </div>
            </div>
            <div className="flex items-center gap-3 sm:gap-4 p-3 sm:p-4 rounded-lg hover:bg-gray-50 transition-colors">
              <div className="bg-blue-100 p-2 sm:p-3 rounded-full">
                <TrendingUp className="h-5 w-5 sm:h-6 sm:w-6 text-blue-600" />
              </div>
              <div>
                <h3 className="font-semibold text-sm sm:text-base">Best Prices</h3>
                <p className="text-xs sm:text-sm text-gray-600">Competitive marketplace rates</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-12">
        {/* Categories Section */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold mb-8 text-gray-900">Shop by Category</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {categories.map((category) => (
              <Link key={category.id} to={`/products?category=${category.slug}`}>
                <Card className="group hover:shadow-xl transition-all duration-300 hover:-translate-y-2 overflow-hidden border-2 hover:border-emerald-500">
                  <CardContent className="p-0">
                    <div className="relative h-40 overflow-hidden">
                      <img
                        src={category.image}
                        alt={category.name}
                        className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
                      <div className="absolute bottom-3 left-3 right-3">
                        <h3 className="text-white font-semibold text-lg">{category.name}</h3>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        </section>

        {/* Featured Products */}
        <section className="mb-16">
          <div className="flex justify-between items-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900">Featured Products</h2>
            <Link to="/products">
              <Button variant="outline" className="border-emerald-600 text-emerald-600 hover:bg-emerald-50">
                View All Products
              </Button>
            </Link>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {featuredProducts.map((product) => (
              <Link key={product.id} to={`/product/${product.id}`}>
                <Card className="group hover:shadow-xl transition-all duration-300 hover:-translate-y-2 h-full">
                  <CardContent className="p-4">
                    <div className="relative mb-4 overflow-hidden rounded-lg">
                      {product.originalPrice && (
                        <Badge className="absolute top-2 left-2 bg-red-500 text-white z-10">
                          Sale
                        </Badge>
                      )}
                      <img
                        src={product.image}
                        alt={product.name}
                        className="w-full h-48 object-cover group-hover:scale-110 transition-transform duration-500"
                      />
                    </div>
                    <div className="space-y-2">
                      <p className="text-sm text-gray-600">{product.brand}</p>
                      <h3 className="font-semibold text-gray-900 line-clamp-2 group-hover:text-emerald-600 transition-colors">
                        {product.name}
                      </h3>
                      <div className="flex items-center gap-2">
                        <div className="flex items-center gap-1">
                          <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                          <span className="text-sm font-medium">{product.rating}</span>
                        </div>
                        <span className="text-sm text-gray-500">({product.reviews})</span>
                      </div>
                      <div className="flex items-baseline gap-2">
                        <span className="text-2xl font-bold text-emerald-600">£{product.price}</span>
                        {product.originalPrice && (
                          <span className="text-sm text-gray-500 line-through">£{product.originalPrice}</span>
                        )}
                      </div>
                      <p className="text-xs text-gray-600">by {product.vendor.name}</p>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        </section>

        {/* Call to Action */}
        <section className="bg-gradient-to-r from-emerald-600 to-emerald-500 rounded-2xl p-12 text-white text-center shadow-xl">
          <h2 className="text-4xl font-bold mb-4">Join Our Vendor Community</h2>
          <p className="text-xl mb-8 max-w-2xl mx-auto">
            Are you an African grocery shop owner? Start selling on AfroMarket UK and reach thousands of customers across the UK.
          </p>
          <Link to="/vendor/register">
            <Button size="lg" className="bg-white text-emerald-600 hover:bg-gray-100 px-8 py-6 text-lg font-semibold shadow-xl hover:shadow-2xl transform hover:scale-105 transition-all">
              Become a Vendor Today
            </Button>
          </Link>
        </section>
      </div>

      <Footer />
    </div>
  );
};

export default Home;