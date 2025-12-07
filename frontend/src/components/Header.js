import { Link, useNavigate } from 'react-router-dom';
import { Search, ShoppingCart, User, Menu, MapPin, Package, Store } from 'lucide-react';
import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useCart } from '../context/CartContext';
import { Button } from './ui/button';
import { Input } from './ui/input';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from './ui/dropdown-menu';
import { Sheet, SheetContent, SheetTrigger } from './ui/sheet';
import { categories } from '../mock';

const Header = () => {
  const navigate = useNavigate();
  const { user, logout, isAuthenticated } = useAuth();
  const { getCartCount } = useCart();
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/products?search=${searchQuery}`);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <header className="sticky top-0 z-50 bg-gradient-to-r from-emerald-700 to-emerald-600 shadow-lg">
      {/* Top Bar */}
      <div className="bg-emerald-800 text-white py-2 px-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center text-sm">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1">
              <MapPin className="h-4 w-4" />
              Deliver to United Kingdom
            </span>
          </div>
          <div className="flex items-center gap-4">
            <Link to="/vendor/register" className="hover:text-emerald-200 transition-colors">
              Become a Vendor
            </Link>
            <Link to="/profile" className="hover:text-emerald-200 transition-colors">
              Track Orders
            </Link>
          </div>
        </div>
      </div>

      {/* Main Header */}
      <div className="py-3 px-4">
        <div className="max-w-7xl mx-auto flex items-center gap-6">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 text-white font-bold text-2xl min-w-fit">
            <Store className="h-8 w-8" />
            <span className="hidden md:block">AfroMarket UK</span>
            <span className="md:hidden">AfroMart</span>
          </Link>

          {/* Search Bar */}
          <form onSubmit={handleSearch} className="flex-1 max-w-2xl">
            <div className="relative flex shadow-lg">
              <Input
                type="text"
                placeholder="Search for African groceries, brands, and more..."
                className="w-full pr-12 h-12 rounded-r-none border-2 border-white focus-visible:ring-2 focus-visible:ring-orange-400 focus-visible:ring-offset-0 text-base"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <Button
                type="submit"
                className="rounded-l-none bg-orange-500 hover:bg-orange-600 text-white h-12 px-8 text-base font-semibold"
              >
                <Search className="h-5 w-5 mr-2" />
                Search
              </Button>
            </div>
          </form>

          {/* Right Actions */}
          <div className="flex items-center gap-4">
            {/* Account Dropdown */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="text-white hover:bg-emerald-600 gap-2">
                  <User className="h-5 w-5" />
                  <div className="hidden lg:flex flex-col items-start text-xs">
                    <span>Hello, {isAuthenticated ? user?.name?.split(' ')[0] : 'Sign in'}</span>
                    <span className="font-semibold">Account & Lists</span>
                  </div>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                {!isAuthenticated ? (
                  <>
                    <DropdownMenuItem onClick={() => navigate('/login')}>
                      Sign In
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => navigate('/register')}>
                      Create Account
                    </DropdownMenuItem>
                  </>
                ) : (
                  <>
                    <DropdownMenuItem onClick={() => navigate('/profile')}>
                      My Profile
                    </DropdownMenuItem>
                    {user?.role === 'vendor' && (
                      <DropdownMenuItem onClick={() => navigate('/vendor/dashboard')}>
                        <Store className="h-4 w-4 mr-2" />
                        Vendor Dashboard
                      </DropdownMenuItem>
                    )}
                    <DropdownMenuItem onClick={() => navigate('/profile')}>
                      <Package className="h-4 w-4 mr-2" />
                      Orders
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onClick={handleLogout}>
                      Sign Out
                    </DropdownMenuItem>
                  </>
                )}
              </DropdownMenuContent>
            </DropdownMenu>

            {/* Cart */}
            <Button
              variant="ghost"
              className="text-white hover:bg-emerald-600 relative"
              onClick={() => navigate('/cart')}
            >
              <ShoppingCart className="h-6 w-6" />
              {getCartCount() > 0 && (
                <span className="absolute -top-1 -right-1 bg-orange-500 text-white text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center">
                  {getCartCount()}
                </span>
              )}
              <span className="hidden lg:block ml-2">Cart</span>
            </Button>

            {/* Mobile Menu */}
            <Sheet>
              <SheetTrigger asChild>
                <Button variant="ghost" className="lg:hidden text-white hover:bg-emerald-600">
                  <Menu className="h-6 w-6" />
                </Button>
              </SheetTrigger>
              <SheetContent side="left" className="w-80">
                <div className="flex flex-col gap-4 mt-8">
                  <h2 className="font-bold text-lg">Browse Categories</h2>
                  {categories.map((cat) => (
                    <Link
                      key={cat.id}
                      to={`/products?category=${cat.slug}`}
                      className="text-base hover:text-emerald-600 transition-colors py-2 border-b"
                    >
                      {cat.name}
                    </Link>
                  ))}
                </div>
              </SheetContent>
            </Sheet>
          </div>
        </div>
      </div>

      {/* Category Navigation */}
      <div className="bg-emerald-800 py-2 px-4 hidden lg:block">
        <div className="max-w-7xl mx-auto flex items-center gap-6 text-white text-sm">
          <Sheet>
            <SheetTrigger asChild>
              <Button variant="ghost" className="text-white hover:bg-emerald-700 gap-2">
                <Menu className="h-4 w-4" />
                All Categories
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="w-80">
              <div className="flex flex-col gap-2 mt-8">
                <h2 className="font-bold text-lg mb-4">All Categories</h2>
                {categories.map((cat) => (
                  <Link
                    key={cat.id}
                    to={`/products?category=${cat.slug}`}
                    className="text-base hover:text-emerald-600 transition-colors py-3 border-b flex items-center gap-2"
                  >
                    <span className="text-2xl">{cat.icon}</span>
                    {cat.name}
                  </Link>
                ))}
              </div>
            </SheetContent>
          </Sheet>
          {categories.slice(0, 6).map((cat) => (
            <Link
              key={cat.id}
              to={`/products?category=${cat.slug}`}
              className="hover:text-emerald-200 transition-colors"
            >
              {cat.name}
            </Link>
          ))}
        </div>
      </div>
    </header>
  );
};

export default Header;