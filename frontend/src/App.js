import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import { Toaster } from './components/ui/sonner';
import './App.css';
import Home from './pages/Home';
import Products from './pages/Products';
import ProductDetail from './pages/ProductDetail';
import Cart from './pages/Cart';
import Checkout from './pages/Checkout';
import Login from './pages/Login';
import Register from './pages/Register';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import VendorRegister from './pages/VendorRegister';
import VendorDashboard from './pages/VendorDashboard';
import VendorAds from './pages/VendorAds';
import VendorWallet from './pages/VendorWallet';
import VendorSubscription from './pages/VendorSubscription';
import VendorNotificationsPage from './pages/VendorNotificationsPage';
import PremiumMembership from './pages/PremiumMembership';
import Profile from './pages/Profile';
import HelpSupport from './pages/HelpSupport';
import TermsOfService from './pages/TermsOfService';
import PrivacyPolicy from './pages/PrivacyPolicy';
import ShippingInformation from './pages/ShippingInformation';
import ReturnsRefunds from './pages/ReturnsRefunds';
import OrderHistory from './pages/OrderHistory';
import Wishlist from './pages/Wishlist';
import Messages from './pages/Messages';
import AuthCallback from './components/AuthCallback';
import InstallPrompt from './components/InstallPrompt';
import AfroBot from './components/AfroBot';
import AdminDashboard from './pages/AdminDashboard';
import OwnerDashboard from './pages/OwnerDashboard';
import { AuthProvider } from './context/AuthContext';
import { CartProvider } from './context/CartContext';

// Router component that checks for session_id synchronously
function AppRouter() {
  const location = useLocation();
  
  // Check for session_id in URL fragment (synchronous check during render)
  if (location.hash?.includes('session_id=')) {
    return <AuthCallback />;
  }
  
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/products" element={<Products />} />
      <Route path="/product/:id" element={<ProductDetail />} />
      <Route path="/cart" element={<Cart />} />
      <Route path="/checkout" element={<Checkout />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/reset-password" element={<ResetPassword />} />
      <Route path="/vendor/register" element={<VendorRegister />} />
      <Route path="/vendor/dashboard" element={<VendorDashboard />} />
      <Route path="/vendor/ads" element={<VendorAds />} />
      <Route path="/vendor/wallet" element={<VendorWallet />} />
      <Route path="/vendor/subscription" element={<VendorSubscription />} />
      <Route path="/premium" element={<PremiumMembership />} />
      <Route path="/profile" element={<Profile />} />
      <Route path="/orders" element={<OrderHistory />} />
      <Route path="/wishlist" element={<Wishlist />} />
      <Route path="/messages" element={<Messages />} />
      <Route path="/help" element={<HelpSupport />} />
      <Route path="/terms" element={<TermsOfService />} />
      <Route path="/privacy" element={<PrivacyPolicy />} />
      <Route path="/shipping" element={<ShippingInformation />} />
      <Route path="/returns" element={<ReturnsRefunds />} />
      <Route path="/admin/dashboard" element={<AdminDashboard />} />
      <Route path="/owner/dashboard" element={<OwnerDashboard />} />
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <CartProvider>
        <div className="App">
          <BrowserRouter>
            <AppRouter />
          </BrowserRouter>
          <InstallPrompt />
          <AfroBot />
          <Toaster />
        </div>
      </CartProvider>
    </AuthProvider>
  );
}

export default App;